# -*- coding: utf-8 -*-
"""
postprocess_summary_and_plots.py

One-click postprocessing for the curved-X voxel Abaqus dataset.

This script does both:
1) Read Results_light/*_force_displacement.csv and *_stress_strain.csv
2) Create summary_metrics.csv
3) Create validation plots in Results_light/figures

Run with normal Python, not Abaqus Python:
    python postprocess_summary_and_plots.py

Optional:
    python postprocess_summary_and_plots.py "D:\\Simulation\\Curved_Rod_Voxel_Model"
"""

from __future__ import print_function

import os
import sys
import csv
import glob
import math


# ============================================================
# USER SETTINGS
# ============================================================

ROOT_DIR = r"D:\Simulation\Curved_Rod_Voxel_Model"
RESULT_DIR_NAME = "Results"

DESIGN_SUMMARY_REL_PATH = os.path.join("batch_curved_x", "summary_random.csv")

SPECIMEN_HEIGHT_MM = 80.0
SPECIMEN_AREA_MM2 = 80.0 * 80.0
SPECIMEN_VOLUME_MM3 = SPECIMEN_HEIGHT_MM * SPECIMEN_AREA_MM2

# Unit: g/cm^3. Change this when real material density is known.
# Set to None if SEA is not needed.
SOLID_DENSITY_G_CM3 = 1.0

INITIAL_FIT_STRAIN_MAX = 0.02
INITIAL_FIT_MIN_POINTS = 3
INITIAL_FIT_FALLBACK_POINTS = 6

CLIP_NEGATIVE_FOR_INTEGRAL = True


# ============================================================
# CSV / NUMERIC HELPERS
# ============================================================

def safe_float(x):
    try:
        if x is None:
            return None
        s = str(x).strip()
        if s == "":
            return None
        v = float(s)
        if math.isnan(v) or math.isinf(v):
            return None
        return v
    except Exception:
        return None


def open_text_for_read(path):
    try:
        return open(path, "r", newline="", encoding="utf-8-sig")
    except TypeError:
        return open(path, "r")


def open_text_for_write(path):
    try:
        return open(path, "w", newline="", encoding="utf-8-sig")
    except TypeError:
        return open(path, "w")


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def read_xy_csv(path, x_candidates, y_candidates):
    rows = []
    f = open_text_for_read(path)
    try:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return rows

        field_map = {}
        for name in reader.fieldnames:
            if name is not None:
                field_map[name.strip().lower()] = name

        x_key = None
        y_key = None

        for cand in x_candidates:
            if cand.lower() in field_map:
                x_key = field_map[cand.lower()]
                break

        for cand in y_candidates:
            if cand.lower() in field_map:
                y_key = field_map[cand.lower()]
                break

        if x_key is None or y_key is None:
            raise RuntimeError("Cannot find required columns in {}. Columns = {}".format(path, reader.fieldnames))

        for r in reader:
            x = safe_float(r.get(x_key))
            y = safe_float(r.get(y_key))
            if x is not None and y is not None:
                rows.append((x, y))
    finally:
        f.close()

    rows.sort(key=lambda p: p[0])

    cleaned = []
    for x, y in rows:
        if cleaned and abs(cleaned[-1][0] - x) < 1e-15:
            cleaned[-1] = (x, y)
        else:
            cleaned.append((x, y))

    return cleaned


def trapezoid_integral(rows, clip_negative=False):
    if len(rows) < 2:
        return 0.0

    area = 0.0
    for i in range(1, len(rows)):
        x0, y0 = rows[i - 1]
        x1, y1 = rows[i]

        if clip_negative:
            y0 = max(0.0, y0)
            y1 = max(0.0, y1)

        dx = x1 - x0
        if dx < 0:
            continue

        area += 0.5 * (y0 + y1) * dx

    return area


def linear_slope(points):
    n = len(points)
    if n < 2:
        return None

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    mx = sum(xs) / float(n)
    my = sum(ys) / float(n)

    den = sum((x - mx) ** 2 for x in xs)
    if abs(den) < 1e-30:
        return None

    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    return num / den


def early_fit_slope(rows, x_max=None, min_points=3, fallback_points=6):
    if len(rows) < 2:
        return None

    valid = [(x, y) for x, y in rows if x is not None and y is not None and x >= 0]
    if len(valid) < 2:
        return None

    fit = []
    if x_max is not None:
        fit = [(x, y) for x, y in valid if x <= x_max]

    if len(fit) < min_points:
        fit = valid[:min(fallback_points, len(valid))]

    if len(fit) < 2:
        return None

    return linear_slope(fit)


def max_y(rows):
    if not rows:
        return None
    return max(y for x, y in rows)


def final_xy(rows):
    if not rows:
        return (None, None)
    return rows[-1]


def fmt(v):
    if v is None:
        return ""
    try:
        return "{:.10g}".format(float(v))
    except Exception:
        return str(v)


# ============================================================
# DESIGN SUMMARY MERGE
# ============================================================

def load_design_summary(summary_path):
    design = {}

    if not os.path.isfile(summary_path):
        print("[WARN] Design summary not found:", summary_path)
        return design

    f = open_text_for_read(summary_path)
    try:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return design

        lower_to_name = {name.strip().lower(): name for name in reader.fieldnames if name is not None}

        case_key = lower_to_name.get("casename") or lower_to_name.get("case_name")
        radius_key = lower_to_name.get("radius")
        bend_key = lower_to_name.get("bendamp") or lower_to_name.get("bend_amp")
        density_key = lower_to_name.get("density")

        if case_key is None:
            print("[WARN] Design summary has no CaseName column:", summary_path)
            return design

        for row in reader:
            base = str(row.get(case_key, "")).strip()
            if not base:
                continue

            info = {
                "base_case_name": base,
                "radius": safe_float(row.get(radius_key)) if radius_key else None,
                "bendAmp": safe_float(row.get(bend_key)) if bend_key else None,
                "relative_density": safe_float(row.get(density_key)) if density_key else None,
            }

            design[base] = info
            design[base + "_rep444"] = info

    finally:
        f.close()

    print("[OK] Loaded design summary keys:", len(design))
    return design


# ============================================================
# SUMMARY METRICS
# ============================================================

def calculate_case_metrics(case_name, result_dir, design_info):
    fd_path = os.path.join(result_dir, case_name + "_force_displacement.csv")
    ss_path = os.path.join(result_dir, case_name + "_stress_strain.csv")

    fd_rows = read_xy_csv(fd_path, ["displacement_mm", "displacement"], ["force_N", "force"])
    ss_rows = read_xy_csv(ss_path, ["strain"], ["stress_MPa", "stress"])

    if len(fd_rows) == 0:
        raise RuntimeError("No force-displacement data: {}".format(fd_path))
    if len(ss_rows) == 0:
        raise RuntimeError("No stress-strain data: {}".format(ss_path))

    final_disp, final_force = final_xy(fd_rows)
    final_strain, final_stress = final_xy(ss_rows)

    max_force = max_y(fd_rows)
    max_stress = max_y(ss_rows)

    energy_nmm = trapezoid_integral(fd_rows, clip_negative=CLIP_NEGATIVE_FOR_INTEGRAL)
    energy_j = energy_nmm * 1e-3

    # MPa = N/mm^2 = MJ/m^3, so the stress-strain integral is MJ/m^3.
    energy_density_mj_m3 = trapezoid_integral(ss_rows, clip_negative=CLIP_NEGATIVE_FOR_INTEGRAL)

    initial_stiffness = early_fit_slope(
        fd_rows,
        x_max=INITIAL_FIT_STRAIN_MAX * SPECIMEN_HEIGHT_MM,
        min_points=INITIAL_FIT_MIN_POINTS,
        fallback_points=INITIAL_FIT_FALLBACK_POINTS,
    )

    initial_modulus = early_fit_slope(
        ss_rows,
        x_max=INITIAL_FIT_STRAIN_MAX,
        min_points=INITIAL_FIT_MIN_POINTS,
        fallback_points=INITIAL_FIT_FALLBACK_POINTS,
    )

    design = design_info.get(case_name, {})
    radius = design.get("radius")
    bend_amp = design.get("bendAmp")
    rel_density = design.get("relative_density")

    mass_g = None
    sea_j_g = None

    if SOLID_DENSITY_G_CM3 is not None and rel_density is not None:
        solid_density_g_mm3 = SOLID_DENSITY_G_CM3 / 1000.0
        mass_g = solid_density_g_mm3 * rel_density * SPECIMEN_VOLUME_MM3
        if mass_g > 0:
            sea_j_g = energy_j / mass_g

    return {
        "case_name": case_name,
        "radius": radius,
        "bendAmp": bend_amp,
        "relative_density": rel_density,
        "n_fd_points": len(fd_rows),
        "n_ss_points": len(ss_rows),
        "final_displacement_mm": final_disp,
        "final_force_N": final_force,
        "final_strain": final_strain,
        "final_stress_MPa": final_stress,
        "max_force_N": max_force,
        "max_stress_MPa": max_stress,
        "initial_stiffness_N_per_mm": initial_stiffness,
        "initial_modulus_MPa": initial_modulus,
        "energy_absorption_Nmm": energy_nmm,
        "energy_absorption_J": energy_j,
        "energy_density_MJ_per_m3": energy_density_mj_m3,
        "solid_density_g_cm3_for_SEA": SOLID_DENSITY_G_CM3,
        "mass_g": mass_g,
        "SEA_J_per_g": sea_j_g,
        "status": "OK",
        "message": "",
    }


def find_cases(result_dir):
    pattern = os.path.join(result_dir, "*_stress_strain.csv")
    ss_files = sorted(glob.glob(pattern))

    cases = []
    suffix = "_stress_strain.csv"

    for path in ss_files:
        name = os.path.basename(path)
        if not name.endswith(suffix):
            continue

        case_name = name[:-len(suffix)]
        fd_path = os.path.join(result_dir, case_name + "_force_displacement.csv")

        if os.path.isfile(fd_path):
            cases.append(case_name)

    return cases


def write_summary(out_path, records):
    header = [
        "case_name",
        "radius", "bendAmp", "relative_density",
        "n_fd_points", "n_ss_points",
        "final_displacement_mm", "final_force_N",
        "final_strain", "final_stress_MPa",
        "max_force_N", "max_stress_MPa",
        "initial_stiffness_N_per_mm", "initial_modulus_MPa",
        "energy_absorption_Nmm", "energy_absorption_J", "energy_density_MJ_per_m3",
        "solid_density_g_cm3_for_SEA", "mass_g", "SEA_J_per_g",
        "status", "message",
    ]

    f = open_text_for_write(out_path)
    try:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()

        for rec in records:
            row = {k: fmt(rec.get(k)) for k in header}
            row["case_name"] = rec.get("case_name", "")
            row["status"] = rec.get("status", "")
            row["message"] = rec.get("message", "")
            writer.writerow(row)

    finally:
        f.close()


def generate_summary(root_dir):
    result_dir = os.path.join(root_dir, RESULT_DIR_NAME)
    design_summary_path = os.path.join(root_dir, DESIGN_SUMMARY_REL_PATH)
    out_path = os.path.join(result_dir, "summary_metrics.csv")

    if not os.path.isdir(result_dir):
        raise RuntimeError("Result folder not found: {}".format(result_dir))

    design_info = load_design_summary(design_summary_path)
    cases = find_cases(result_dir)

    print("[INFO] Result folder:", result_dir)
    print("[INFO] Found cases:", len(cases))

    records = []

    for i, case_name in enumerate(cases):
        print("[{}/{}] {}".format(i + 1, len(cases), case_name))

        try:
            rec = calculate_case_metrics(case_name, result_dir, design_info)
        except Exception as e:
            rec = {
                "case_name": case_name,
                "status": "FAILED",
                "message": str(e),
            }

        records.append(rec)

    write_summary(out_path, records)
    print("[OK] Summary exported:", out_path)

    return out_path


# ============================================================
# PLOTTING
# ============================================================

def import_plot_packages():
    try:
        import pandas as pd
        import matplotlib.pyplot as plt
        return pd, plt
    except Exception as e:
        raise RuntimeError(
            "pandas/matplotlib import failed. Install them first:\n"
            "python -m pip install pandas matplotlib\n"
            "Original error: {}".format(e)
        )


def save_scatter(df, x_col, y_col, out_path, plt):
    if x_col not in df.columns or y_col not in df.columns:
        print("[SKIP] Missing column(s): {} or {}".format(x_col, y_col))
        return

    sub = df[[x_col, y_col]].dropna()
    if sub.empty:
        print("[SKIP] Empty data for: {} vs {}".format(x_col, y_col))
        return

    plt.figure(figsize=(7, 5))
    plt.scatter(sub[x_col], sub[y_col], s=45)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.title("{} vs {}".format(y_col, x_col))
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()

    print("[OK] Saved:", out_path)


def save_line_curve_from_case(case_name, result_dir, fig_dir, pd, plt):
    ss_path = os.path.join(result_dir, "{}_stress_strain.csv".format(case_name))
    fd_path = os.path.join(result_dir, "{}_force_displacement.csv".format(case_name))

    if os.path.exists(ss_path):
        ss = pd.read_csv(ss_path)
        if "strain" in ss.columns and "stress_MPa" in ss.columns:
            plt.figure(figsize=(7, 5))
            plt.plot(ss["strain"], ss["stress_MPa"], marker="o", linewidth=1.5)
            plt.xlabel("strain")
            plt.ylabel("stress_MPa")
            plt.title("Stress-Strain: {}".format(case_name))
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            out_path = os.path.join(fig_dir, "{}_stress_strain_curve.png".format(case_name))
            plt.savefig(out_path, dpi=300)
            plt.close()
            print("[OK] Saved:", out_path)

    if os.path.exists(fd_path):
        fd = pd.read_csv(fd_path)
        if "displacement_mm" in fd.columns and "force_N" in fd.columns:
            plt.figure(figsize=(7, 5))
            plt.plot(fd["displacement_mm"], fd["force_N"], marker="o", linewidth=1.5)
            plt.xlabel("displacement_mm")
            plt.ylabel("force_N")
            plt.title("Force-Displacement: {}".format(case_name))
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            out_path = os.path.join(fig_dir, "{}_force_displacement_curve.png".format(case_name))
            plt.savefig(out_path, dpi=300)
            plt.close()
            print("[OK] Saved:", out_path)


def save_correlation_outputs(df, result_dir, fig_dir, plt):
    numeric_df = df.select_dtypes(include=["number"]).copy()
    if numeric_df.empty:
        print("[SKIP] No numeric columns for correlation.")
        return

    corr = numeric_df.corr()

    corr_path = os.path.join(result_dir, "correlation_matrix.csv")
    corr.to_csv(corr_path, index=True, encoding="utf-8-sig")
    print("[OK] Saved:", corr_path)

    plt.figure(figsize=(10, 8))
    plt.imshow(corr.values, aspect="auto")
    plt.colorbar(label="correlation")
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
    plt.yticks(range(len(corr.index)), corr.index)
    plt.title("Correlation Matrix")
    plt.tight_layout()

    out_path = os.path.join(fig_dir, "correlation_matrix.png")
    plt.savefig(out_path, dpi=300)
    plt.close()

    print("[OK] Saved:", out_path)


def save_top_tables(df, result_dir):
    if "energy_absorption_Nmm" in df.columns:
        top_energy = df.sort_values("energy_absorption_Nmm", ascending=False).head(10)
        out_path = os.path.join(result_dir, "top10_by_energy_absorption.csv")
        top_energy.to_csv(out_path, index=False, encoding="utf-8-sig")
        print("[OK] Saved:", out_path)

    if "SEA_J_per_g" in df.columns:
        top_sea = df.sort_values("SEA_J_per_g", ascending=False).head(10)
        out_path = os.path.join(result_dir, "top10_by_SEA.csv")
        top_sea.to_csv(out_path, index=False, encoding="utf-8-sig")
        print("[OK] Saved:", out_path)


def generate_plots(root_dir):
    pd, plt = import_plot_packages()

    result_dir = os.path.join(root_dir, RESULT_DIR_NAME)
    summary_csv = os.path.join(result_dir, "summary_metrics.csv")
    fig_dir = os.path.join(result_dir, "figures")

    ensure_dir(fig_dir)

    if not os.path.exists(summary_csv):
        raise FileNotFoundError("summary_metrics.csv not found: {}".format(summary_csv))

    df = pd.read_csv(summary_csv)

    print("[INFO] Loaded summary:", summary_csv)
    print("[INFO] Rows:", len(df))

    pairs = [
        ("relative_density", "max_force_N", "density_vs_max_force.png"),
        ("relative_density", "energy_absorption_Nmm", "density_vs_energy_absorption.png"),
        ("relative_density", "initial_stiffness_N_per_mm", "density_vs_initial_stiffness.png"),
        ("radius", "max_force_N", "radius_vs_max_force.png"),
        ("radius", "energy_absorption_Nmm", "radius_vs_energy_absorption.png"),
        ("bendAmp", "max_force_N", "bendAmp_vs_max_force.png"),
        ("bendAmp", "energy_absorption_Nmm", "bendAmp_vs_energy_absorption.png"),
        ("initial_stiffness_N_per_mm", "energy_absorption_Nmm", "stiffness_vs_energy_absorption.png"),
        ("max_stress_MPa", "energy_absorption_Nmm", "max_stress_vs_energy_absorption.png"),
    ]

    for x_col, y_col, out_name in pairs:
        out_path = os.path.join(fig_dir, out_name)
        save_scatter(df, x_col, y_col, out_path, plt)

    save_correlation_outputs(df, result_dir, fig_dir, plt)
    save_top_tables(df, result_dir)

    representative_cases = []

    if "case_name" in df.columns and "energy_absorption_Nmm" in df.columns and len(df) > 0:
        idx = df["energy_absorption_Nmm"].idxmax()
        representative_cases.append(str(df.loc[idx, "case_name"]))

    if "case_name" in df.columns and "SEA_J_per_g" in df.columns and len(df) > 0:
        idx = df["SEA_J_per_g"].idxmax()
        representative_cases.append(str(df.loc[idx, "case_name"]))

    if "case_name" in df.columns and len(df) > 0:
        representative_cases.append(str(df.loc[0, "case_name"]))

    seen = set()
    representative_cases = [x for x in representative_cases if not (x in seen or seen.add(x))]

    for case_name in representative_cases:
        save_line_curve_from_case(case_name, result_dir, fig_dir, pd, plt)

    print("[OK] Figures saved in:", fig_dir)


# ============================================================
# MAIN
# ============================================================

def main():
    root_dir = ROOT_DIR

    if len(sys.argv) >= 2:
        root_dir = sys.argv[1]

    print("============================================================")
    print("Curved-X postprocessing: summary + plots")
    print("ROOT_DIR =", root_dir)
    print("============================================================")

    generate_summary(root_dir)
    generate_plots(root_dir)

    print("\n[DONE] Summary and plots have been updated.")


if __name__ == "__main__":
    main()
