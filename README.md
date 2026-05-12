# Curved Rod Voxel Model

![MATLAB](https://img.shields.io/badge/MATLAB-voxel%20generation-orange)
![Abaqus](https://img.shields.io/badge/Abaqus-compression%20FEM-blue)
![Python](https://img.shields.io/badge/Python-postprocessing-green)
![Version](https://img.shields.io/badge/version-V1.0-lightgrey)
![Workflow](https://img.shields.io/badge/workflow-4x4x4%20voxel%20baseline-brightgreen)

**Author:** Alex Lang  
**Version:** V1.0 Single-scale 4x4x4 Abaqus simulation workflow

A MATLAB–Abaqus workflow for generating curved-rod voxel lattice specimens, exporting mesh-only Abaqus `.inp` files, running compression simulations, and automatically extracting force–displacement and stress–strain curves.

This V1.0 repository focuses on the original **4x4x4 voxel-based curved-rod lattice FEM workflow**.

---

## Final Workflow in V1.0

```text
curved-X topology
→ voxel lattice generation
→ 4x4x4 voxel repetition
→ Abaqus mesh-only INP export
→ Abaqus compression simulation
→ force-displacement and stress-strain curves
→ summary metrics and figures
```

---

## Folder Structure

```text
Curved_Rod_Voxel_Model/
├─ batch_generate_curved_x.m
├─ batch_repeat444_and_export_inp.m
├─ export_mat_voxel_to_abaqus_inp.m
├─ abaqus_batch_run_all.py
├─ postprocess_summary_and_plots.py
├─ GenerateVoxel.m
├─ write_curved_x_topology.m
├─ save_sample_mat.m
├─ save_repeat444_mat.m
│
├─ batch_curved_x/
│  ├─ mat/
│  ├─ topology/
│  ├─ preview/
│  ├─ 4x4x4_mat/
│  └─ summary_random.csv
│
├─ Output/
├─ Abaqus_Work/
├─ Results/
└─ README.md
```

---

## Quick Start

### 1. Generate voxel samples in MATLAB

Open MATLAB and set the current folder to:

```text
D:\Simulation\Curved_Rod_Voxel_Model
```

Run:

```matlab
batch_generate_curved_x
batch_repeat444_and_export_inp
```

---

### 2. Run Abaqus batch simulation

From CMD:

```cmd
cd /d D:\Simulation\Curved_Rod_Voxel_Model
abaqus cae noGUI=abaqus_batch_run_all.py
```

From PowerShell:

```powershell
Set-Location "D:\Simulation\Curved_Rod_Voxel_Model"
abaqus cae noGUI=abaqus_batch_run_all.py
```

---

### 3. Run Python postprocessing

From CMD:

```cmd
cd /d D:\Simulation\Curved_Rod_Voxel_Model
python postprocess_summary_and_plots.py
```

From PowerShell:

```powershell
Set-Location "D:\Simulation\Curved_Rod_Voxel_Model"
python postprocess_summary_and_plots.py
```

---

## Main Scripts

| Script | Function |
|---|---|
| `batch_generate_curved_x.m` | Generates random curved-X voxel samples. |
| `GenerateVoxel.m` | Converts curved-X topology into voxel geometry. |
| `write_curved_x_topology.m` | Writes the curved-X center/topology definition. |
| `save_sample_mat.m` | Saves accepted single-cell voxel samples. |
| `batch_repeat444_and_export_inp.m` | Repeats each sample into a 4x4x4 specimen and exports Abaqus `.inp`. |
| `save_repeat444_mat.m` | Saves repeated 4x4x4 voxel `.mat` files. |
| `export_mat_voxel_to_abaqus_inp.m` | Exports repeated voxel models into mesh-only Abaqus `.inp` files. |
| `abaqus_batch_run_all.py` | Runs Abaqus compression jobs and extracts response curves. |
| `postprocess_summary_and_plots.py` | Generates summary metrics, rankings, and figures. |

---

## Output Folders

| Folder | Content |
|---|---|
| `batch_curved_x/mat/` | Single-cell voxel `.mat` files. |
| `batch_curved_x/topology/` | Curved-X topology `.txt` files. |
| `batch_curved_x/preview/` | Preview images of generated voxel structures. |
| `batch_curved_x/4x4x4_mat/` | Repeated 4x4x4 voxel `.mat` files. |
| `Output/` | Abaqus `.inp` files. |
| `Abaqus_Work/` | Abaqus job folders and `.odb`, `.sta`, `.msg`, `.dat` files. |
| `Results/` | Curve CSV files, summary metrics, and figures. |

---

## Important Parameters

### In `batch_generate_curved_x.m`

Modify these parameters if needed:

```matlab
rootDir
targetN
nVoxel
radiusMin / radiusMax
bendMin / bendMax
densityMin / densityMax
desiredWorkers
```

Default purpose:

```text
Generate random curved-X voxel samples and save accepted cases.
```

---

### In `batch_repeat444_and_export_inp.m`

Main 4x4x4 settings:

```matlab
repeatN = [4 4 4];
voxelSize = [0.25 0.25 0.25];
```

Modify if needed:

```matlab
rootDir
repeatN
voxelSize
desiredWorkers
overwriteExisting
```

---

### In `abaqus_batch_run_all.py`

Default 4x4x4 compression settings:

```python
DISP_Z = -16.0
H0 = 80.0
A0 = 80.0 * 80.0
```

Modify if needed:

```python
INP_DIR
WORK_ROOT
RESULT_ROOT
E_MODULUS
POISSON_RATIO
DISP_Z
H0
A0
NUM_CPUS
NUM_DOMAINS
MAX_CASES
```

For testing:

```python
MAX_CASES = 1
```

For all cases:

```python
MAX_CASES = None
```

---

### In `postprocess_summary_and_plots.py`

Modify if needed:

```python
ROOT_DIR
RESULT_DIR_NAME
SOLID_DENSITY_G_CM3
```

---

## Generated Results

The workflow can generate:

```text
force-displacement curves
stress-strain curves
summary_metrics.csv
correlation_matrix.csv
top10_by_energy_absorption.csv
top10_by_SEA.csv
figures/
```

---

## Notes

- V1.0 is the original single-scale **4x4x4 voxel FEM workflow**.
- The Abaqus `.inp` files are exported as mesh-only models.
- Material, step, boundary conditions, job submission, and curve extraction are handled automatically by `abaqus_batch_run_all.py`.
- This version is useful as the original voxel baseline and as a reference for later tube-solid or centerline-based workflows.

---

## Version History

### V1.0

Initial MATLAB–Abaqus workflow for curved-rod voxel lattice generation, 4x4x4 specimen export, Abaqus compression simulation, and automatic force–displacement / stress–strain curve extraction.
