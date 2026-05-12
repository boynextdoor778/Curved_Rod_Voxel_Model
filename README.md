# Curved Rod Voxel Model

![MATLAB](https://img.shields.io/badge/MATLAB-voxel%20generation-orange)
![Abaqus](https://img.shields.io/badge/Abaqus-compression%20FEM-blue)
![Python](https://img.shields.io/badge/Python-postprocessing-green)
![3D Printing](https://img.shields.io/badge/STL-3D%20printing-purple)
![Version](https://img.shields.io/badge/version-V2.0-brightgreen)

**Author:** Alex Lang  
**Version:** V2.0 Dual-scale simulation and 3D-printing workflow

A MATLAB–Abaqus workflow for curved-rod voxel lattice generation, dual-scale `2x2x2` / `4x4x4` compression simulation, compact Abaqus `.inp` export, automatic force–displacement and stress–strain extraction, and STL preparation for 3D printing.

---

## Overview

This repository contains the voxel-based workflow developed before the final tube-solid route. It supports two separated specimen scales:

| Branch | Purpose |
|---|---|
| `2x2x2` | Small-scale specimen for fast simulation and 3D-printing tests |
| `4x4x4` | Full-size specimen for mechanical simulation and dataset generation |

Main workflow:

```text
curved-X topology
→ voxel lattice generation
→ repeated 2x2x2 / 4x4x4 specimen
→ Abaqus mesh-only INP export
→ Abaqus compression simulation
→ force-displacement and stress-strain curves
→ STL export for 3D printing
```

---

## Version

**Current version:** V2.0

Main updates:

- Added separated `2x2x2` and `4x4x4` workflows
- Added STL export branch for Bambu Studio / 3D printing
- Added compact Abaqus `.inp` exporter
- Added separated `Output`, `STL`, `Abaqus_Work`, and `Results` folders
- Added `3D_print_note.txt` for practical slicing and printing settings
- Added GitHub upload rules for excluding large simulation files

---

## Folder Structure

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

### 2x2x2 workflow

Open MATLAB and set the current folder to:

```text
D:\Simulation\Curved_Rod_Voxel_Model\2x2x2
```

Run:

```matlab
batch_generate_curved_x
batch_repeat222_and_export_inp
batch_export_mat_voxel_to_stl_222
```

Then run Abaqus from CMD:

```cmd
cd /d D:\Simulation\Curved_Rod_Voxel_Model\2x2x2
abaqus cae noGUI=abaqus_batch_run_all.py
```

Or from PowerShell:

```powershell
Set-Location "D:\Simulation\Curved_Rod_Voxel_Model\2x2x2"
abaqus cae noGUI=abaqus_batch_run_all.py
```

Run Python postprocessing:

```cmd
python postprocess_summary_and_plots.py
```

---

### 4x4x4 workflow

Open MATLAB and set the current folder to:

```text
D:\Simulation\Curved_Rod_Voxel_Model\4x4x4
```

Run:

```matlab
batch_generate_curved_x
batch_repeat444_and_export_inp
batch_export_mat_voxel_to_stl_444
```

Then run Abaqus from CMD:

```cmd
cd /d D:\Simulation\Curved_Rod_Voxel_Model\4x4x4
abaqus cae noGUI=abaqus_batch_run_all.py
```

Or from PowerShell:

```powershell
Set-Location "D:\Simulation\Curved_Rod_Voxel_Model\4x4x4"
abaqus cae noGUI=abaqus_batch_run_all.py
```

Run Python postprocessing:

```cmd
python postprocess_summary_and_plots.py
```

---

## Output Folders

| Folder | Content |
|---|---|
| `batch_curved_x/mat/` | Single-cell voxel `.mat` files |
| `batch_curved_x/topology/` | Curved-X topology `.txt` files |
| `batch_curved_x/preview/` | Preview images |
| `batch_curved_x/2x2x2_mat/` | Repeated `2x2x2` voxel `.mat` files |
| `batch_curved_x/4x4x4_mat/` | Repeated `4x4x4` voxel `.mat` files |
| `Output/` | Abaqus `.inp` files |
| `STL/` | STL files for 3D printing |
| `Abaqus_Work/` | Abaqus job folders and ODB-related files |
| `Results/` | Curve CSV files, summary metrics, and figures |

---

## Main Scripts

| Script | Function |
|---|---|
| `batch_generate_curved_x.m` | Generates random curved-X voxel samples |
| `GenerateVoxel.m` | Builds voxel model from topology definition |
| `write_curved_x_topology.m` | Writes curved-X topology file |
| `save_sample_mat.m` | Saves accepted single-cell samples |
| `batch_repeat222_and_export_inp.m` | Repeats samples into `2x2x2` specimens and exports INP |
| `batch_repeat444_and_export_inp.m` | Repeats samples into `4x4x4` specimens and exports INP |
| `export_mat_voxel_to_abaqus_inp.m` | Exports repeated voxel model to Abaqus `.inp` |
| `batch_export_mat_voxel_to_stl_222.m` | Exports `2x2x2` voxel specimens to STL |
| `batch_export_mat_voxel_to_stl_444.m` | Exports `4x4x4` voxel specimens to STL |
| `abaqus_batch_run_all.py` | Runs Abaqus compression jobs and extracts response curves |
| `postprocess_summary_and_plots.py` | Generates summary metrics, rankings, and figures |

---

## Key Parameters

### MATLAB generation

Modify in `batch_generate_curved_x.m`:

```matlab
rootDir
targetN
nVoxel
radiusMin / radiusMax
bendMin / bendMax
densityMin / densityMax
desiredWorkers
```

For 3D printing, a thicker rod diameter is recommended. Example:

```matlab
radiusMin = 0.075;   % approximately 3.0 mm rod diameter
radiusMax = 0.100;   % approximately 4.0 mm rod diameter
```

Original smaller setting:

```matlab
radiusMin = 0.032;
radiusMax = 0.041;
```

---

### Repetition and Abaqus export

Default repeat settings:

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

### Abaqus batch simulation

Modify in `abaqus_batch_run_all.py` if needed:

```python
ROOT_DIR
E_MODULUS
POISSON_RATIO
NUM_CPUS
NUM_DOMAINS
MAX_CASES
DELETE_ODB_AFTER_EXTRACT
```

Recommended testing setting:

```python
MAX_CASES = 1
```

For running all cases:

```python
MAX_CASES = None
```

Default compression setting:

```text
2x2x2: H0 = 40 mm, compression displacement = -8 mm
4x4x4: H0 = 80 mm, compression displacement = -16 mm
```

---

## 3D Printing

For STL slicing and Bambu Studio settings, see:

```text
3D_print_note.txt
```

Recommended workflow:

```text
1) Generate STL files from MATLAB
2) Import one STL file into Bambu Studio
3) Use TPU as the main material
4) Use PVA support if needed
5) Start with 2x2x2 specimens for faster printing tests
```

For practical printing, the original 1.3–1.6 mm rod diameter may be too thin. A thicker range of approximately 3–4 mm is recommended for initial printing tests.

---

## GitHub Upload Rule

Do not upload large simulation result files to GitHub.

Recommended to exclude:

```text
*.inp
*.odb
*.stl
*.dat
*.msg
*.sta
*.lck
*.sim
*.stt
*.mdl
Abaqus_Work/
Results/
Output/
STL/
Abaqus_Scratch/
batch_curved_x/*_mat/
```

Only upload source code, README files, printing notes, and small sample files.

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
- Added GitHub upload rule
