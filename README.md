# Curved Rod Voxel Model

![MATLAB](https://img.shields.io/badge/MATLAB-voxel%20generation-orange)
![Abaqus](https://img.shields.io/badge/Abaqus-compression%20FEM-blue)
![Python](https://img.shields.io/badge/Python-postprocessing-green)
![STL](https://img.shields.io/badge/STL-3D%20printing-lightgrey)
![status](https://img.shields.io/badge/status-V2.0%20dual--scale-brightgreen)

A MATLAB–Abaqus workflow for **curved-rod voxel lattice generation**, dual-scale `2x2x2` / `4x4x4` compression simulation, automatic force–displacement and stress–strain extraction, and STL preparation for 3D printing.

This repository is the original **voxel-based curved-rod lattice workflow**. It is kept as a complete reference pipeline for voxel lattice generation, compact Abaqus `.inp` export, automated compression simulation, and printing-oriented STL export.

---

## Version

**Current version:** `V2.0 Dual-scale simulation and 3D-printing workflow`

Main updates:

- Separated `2x2x2` and `4x4x4` workflows
- Added STL export for Bambu Studio / 3D printing
- Added compact Abaqus `.inp` exporter
- Added separated `Output`, `STL`, `Abaqus_Work`, and `Results` folders
- Added practical 3D printing notes

---

## Main Workflow

```text
curved-X topology
→ voxel lattice generation
→ 2x2x2 / 4x4x4 voxel repetition
→ compact Abaqus INP export
→ Abaqus compression simulation
→ force-displacement and stress-strain curves
→ STL export for 3D printing
```

---

## Repository Structure

```text
Curved_Rod_Voxel_Model/
├─ 2x2x2/
│  ├─ batch_generate_curved_x.m
│  ├─ batch_repeat222_and_export_inp.m
│  ├─ batch_export_mat_voxel_to_stl_222.m
│  ├─ export_mat_voxel_to_abaqus_inp.m
│  ├─ export_one_mat_to_stl.m
│  ├─ export_voxel_to_stl_binary.m
│  ├─ GenerateVoxel.m
│  ├─ write_curved_x_topology.m
│  ├─ save_sample_mat.m
│  ├─ save_repeat222_mat.m
│  ├─ abaqus_batch_run_all.py
│  ├─ postprocess_summary_and_plots.py
│  ├─ batch_curved_x/
│  ├─ Output/
│  ├─ STL/
│  ├─ Abaqus_Work/
│  └─ Results/
│
├─ 4x4x4/
│  ├─ batch_generate_curved_x.m
│  ├─ batch_repeat444_and_export_inp.m
│  ├─ batch_export_mat_voxel_to_stl_444.m
│  ├─ export_mat_voxel_to_abaqus_inp.m
│  ├─ export_one_mat_to_stl.m
│  ├─ export_voxel_to_stl_binary.m
│  ├─ GenerateVoxel.m
│  ├─ write_curved_x_topology.m
│  ├─ save_sample_mat.m
│  ├─ save_repeat444_mat.m
│  ├─ abaqus_batch_run_all.py
│  ├─ postprocess_summary_and_plots.py
│  ├─ batch_curved_x/
│  ├─ Output/
│  ├─ STL/
│  ├─ Abaqus_Work/
│  └─ Results/
│
├─ README.md
└─ 3D_print_note.txt
```

---

## Quick Start

### 1. Generate voxel models in MATLAB

For `2x2x2`:

```matlab
cd('D:\Simulation\Curved_Rod_Voxel_Model\2x2x2')

batch_generate_curved_x
batch_repeat222_and_export_inp
batch_export_mat_voxel_to_stl_222
```

For `4x4x4`:

```matlab
cd('D:\Simulation\Curved_Rod_Voxel_Model\4x4x4')

batch_generate_curved_x
batch_repeat444_and_export_inp
batch_export_mat_voxel_to_stl_444
```

---

### 2. Run Abaqus compression simulation

For `2x2x2`:

```powershell
Set-Location "D:\Simulation\Curved_Rod_Voxel_Model\2x2x2"
abaqus cae noGUI=abaqus_batch_run_all.py
```

For `4x4x4`:

```powershell
Set-Location "D:\Simulation\Curved_Rod_Voxel_Model\4x4x4"
abaqus cae noGUI=abaqus_batch_run_all.py
```

---

### 3. Run Python postprocessing

For `2x2x2`:

```powershell
Set-Location "D:\Simulation\Curved_Rod_Voxel_Model\2x2x2"
python postprocess_summary_and_plots.py
```

For `4x4x4`:

```powershell
Set-Location "D:\Simulation\Curved_Rod_Voxel_Model\4x4x4"
python postprocess_summary_and_plots.py
```

---

## Output Files

| Folder | Description |
|---|---|
| `batch_curved_x/mat/` | Base single-cell voxel `.mat` samples |
| `batch_curved_x/topology/` | Curved-X topology text files |
| `batch_curved_x/preview/` | Preview images for selected samples |
| `batch_curved_x/2x2x2_mat/` | Repeated `2x2x2` voxel `.mat` files |
| `batch_curved_x/4x4x4_mat/` | Repeated `4x4x4` voxel `.mat` files |
| `Output/` | Abaqus `.inp` files |
| `STL/` | STL files for 3D printing |
| `Abaqus_Work/` | Abaqus job folders and ODB files |
| `Results/` | Curve CSV files, summary metrics, and figures |

---

## Main Scripts

| Script | Function |
|---|---|
| `batch_generate_curved_x.m` | Generates random curved-X voxel samples |
| `GenerateVoxel.m` | Converts topology definitions into voxel grids |
| `write_curved_x_topology.m` | Writes curved-X topology files |
| `save_sample_mat.m` | Saves accepted base samples |
| `batch_repeat222_and_export_inp.m` | Builds `2x2x2` repeated specimens and exports Abaqus `.inp` files |
| `batch_repeat444_and_export_inp.m` | Builds `4x4x4` repeated specimens and exports Abaqus `.inp` files |
| `export_mat_voxel_to_abaqus_inp.m` | Converts repeated voxel `.mat` files into compact Abaqus mesh-only `.inp` files |
| `batch_export_mat_voxel_to_stl_222.m` | Exports `2x2x2` STL files |
| `batch_export_mat_voxel_to_stl_444.m` | Exports `4x4x4` STL files |
| `abaqus_batch_run_all.py` | Runs Abaqus compression jobs and extracts curve CSV files |
| `postprocess_summary_and_plots.py` | Generates summary metrics and plots |

---

## Key Parameters

### MATLAB generation

Modify these parameters in `batch_generate_curved_x.m` if needed:

```matlab
targetN
nVoxel
radiusMin / radiusMax
bendMin / bendMax
densityMin / densityMax
desiredWorkers
```

For practical 3D printing, a thicker rod range is recommended:

```matlab
radiusMin = 0.075;   % approximately 3.0 mm rod diameter
radiusMax = 0.100;   % approximately 4.0 mm rod diameter
```

Original smaller simulation setting:

```matlab
radiusMin = 0.032;
radiusMax = 0.041;
```

---

### Repetition scale

```matlab
% 2x2x2 branch
repeatN = [2 2 2];

% 4x4x4 branch
repeatN = [4 4 4];
```

Default voxel size:

```matlab
voxelSize = [0.25 0.25 0.25];
```

---

### Abaqus compression settings

Default compression setup:

```text
2x2x2: H0 = 40 mm, compression displacement = -8 mm
4x4x4: H0 = 80 mm, compression displacement = -16 mm
```

Recommended Abaqus testing setting:

```python
MAX_CASES = 1
```

Run all cases after validation:

```python
MAX_CASES = None
```

---

## Postprocessing Outputs

`postprocess_summary_and_plots.py` reads curve CSV files in `Results/` and generates:

```text
summary_metrics.csv
correlation_matrix.csv
top10_by_energy_absorption.csv
top10_by_SEA.csv
figures/
```

Typical curve outputs include:

```text
*_force_displacement.csv
*_stress_strain.csv
*_all_response.csv
```

---

## 3D Printing Notes

For STL slicing and Bambu Studio settings, see:

```text
3D_print_note.txt
```

Recommended initial workflow:

```text
1) Generate STL files from MATLAB
2) Import one STL file into Bambu Studio
3) Use TPU as the main material
4) Use PVA support if needed
5) Start with 2x2x2 specimens for faster printing tests
```

For practical TPU printing, the original `1.3–1.6 mm` rod diameter may be too thin. A thicker `3–4 mm` rod diameter range is recommended for initial fabrication tests.

---

## Notes

- `2x2x2` is recommended for fast simulation and printing validation.
- `4x4x4` is used for larger-scale mechanical simulation and dataset generation.
- Keep Abaqus work and scratch folders on a large disk rather than the system drive.
- This voxel branch is useful as a complete reference workflow for voxel-based curved-rod lattice generation.
- For faster solid-strut stress contour generation, use the newer `CurviStrut-Lattice` tube-solid workflow.

---

## Version History

### V1.0

Initial MATLAB–Abaqus workflow for curved-rod voxel lattice generation, `4x4x4` specimen export, Abaqus compression simulation, and automatic curve extraction.

### V2.0

Dual-scale simulation and 3D-printing workflow.

Main updates:

- Added separated `2x2x2` and `4x4x4` workflows
- Added STL export for 3D printing
- Added compact Abaqus `.inp` export
- Added separated `Output`, `STL`, `Abaqus_Work`, and `Results` folders
- Added practical 3D printing note

---

## License

This project is released under the MIT License.
