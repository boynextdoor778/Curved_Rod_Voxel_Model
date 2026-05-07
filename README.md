# Curved Rod Voxel Model

Author: Alex Lang  
Version: V2.0 Dual-scale simulation and 3D-printing workflow

This repository provides a MATLAB–Abaqus workflow for generating curved-rod voxel lattice specimens, exporting compact mesh-only Abaqus `.inp` files, running compression simulations, extracting force–displacement and stress–strain curves, and preparing STL files for 3D printing.

The current version contains two separated branches:

- `2x2x2`: small-scale specimen for fast simulation and 3D-printing tests
- `4x4x4`: full-size specimen for mechanical simulation and dataset generation

---

## Version

Current version: V2.0

Main updates:

- Added separated `2x2x2` and `4x4x4` workflows
- Added STL export branch for Bambu Studio / 3D printing
- Added compact Abaqus `.inp` exporter to reduce unnecessary nodes
- Added separated `Output`, `STL`, `Abaqus_Work`, and `Results` folders
- Added `3D_print_note` for practical slicing and printing settings

---

## Folder structure

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

## 2x2x2 usage

### 1. MATLAB generation and export

Open MATLAB and set the current folder to:

```text
D:\Simulation\Curved_Rod_Voxel_Model\2x2x2
```

Then run:

```matlab
batch_generate_curved_x
batch_repeat222_and_export_inp
batch_export_mat_voxel_to_stl_222
```

### 2. Abaqus batch simulation

Run from CMD:

```cmd
cd /d D:\Simulation\Curved_Rod_Voxel_Model\2x2x2
abaqus cae noGUI=abaqus_batch_run_all.py
```

Run from PowerShell:

```powershell
Set-Location "D:\Simulation\Curved_Rod_Voxel_Model\2x2x2"
abaqus cae noGUI=abaqus_batch_run_all.py
```

### 3. Python postprocessing

Run from CMD:

```cmd
cd /d D:\Simulation\Curved_Rod_Voxel_Model\2x2x2
python postprocess_summary_and_plots.py
```

Run from PowerShell:

```powershell
Set-Location "D:\Simulation\Curved_Rod_Voxel_Model\2x2x2"
python postprocess_summary_and_plots.py
```

### 4. Check outputs

```text
Output/        Abaqus .inp files
STL/           STL files for 3D printing
Abaqus_Work/   Abaqus job folders
Results/       force-displacement curves, stress-strain curves, summary files, and figures
```

---

## 4x4x4 usage

### 1. MATLAB generation and export

Open MATLAB and set the current folder to:

```text
D:\Simulation\Curved_Rod_Voxel_Model\4x4x4
```

Then run:

```matlab
batch_generate_curved_x
batch_repeat444_and_export_inp
batch_export_mat_voxel_to_stl_444
```

### 2. Abaqus batch simulation

Run from CMD:

```cmd
cd /d D:\Simulation\Curved_Rod_Voxel_Model\4x4x4
abaqus cae noGUI=abaqus_batch_run_all.py
```

Run from PowerShell:

```powershell
Set-Location "D:\Simulation\Curved_Rod_Voxel_Model\4x4x4"
abaqus cae noGUI=abaqus_batch_run_all.py
```

### 3. Python postprocessing

Run from CMD:

```cmd
cd /d D:\Simulation\Curved_Rod_Voxel_Model\4x4x4
python postprocess_summary_and_plots.py
```

Run from PowerShell:

```powershell
Set-Location "D:\Simulation\Curved_Rod_Voxel_Model\4x4x4"
python postprocess_summary_and_plots.py
```

### 4. Check outputs

```text
Output/        Abaqus .inp files
STL/           STL files for 3D printing
Abaqus_Work/   Abaqus job folders
Results/       force-displacement curves, stress-strain curves, summary files, and figures
```

---

## Notes

### batch_generate_curved_x.m

Main MATLAB script for generating random curved-X voxel samples.

It calls:

- `GenerateVoxel.m`: builds the voxel model from the topology definition
- `write_curved_x_topology.m`: writes the curved-X topology file
- `save_sample_mat.m`: saves each generated sample as a `.mat` file

Main outputs:

```text
batch_curved_x/mat/
batch_curved_x/topology/
batch_curved_x/preview/
batch_curved_x/summary_random.csv
```

Main parameters to modify if needed:

```matlab
rootDir
targetN
nVoxel
radiusMin / radiusMax
bendMin / bendMax
densityMin / densityMax
desiredWorkers
```

For 3D printing, the rod diameter can be increased by modifying:

```matlab
radiusMin = 0.075;   % approximately 3.0 mm rod diameter
radiusMax = 0.100;   % approximately 4.0 mm rod diameter
```

The original smaller setting was approximately:

```matlab
radiusMin = 0.032;
radiusMax = 0.041;
```

---

### batch_repeat222_and_export_inp.m / batch_repeat444_and_export_inp.m

These scripts repeat each single-cell voxel sample into either a `2x2x2` or `4x4x4` specimen and export compact mesh-only Abaqus `.inp` files.

They call:

- `export_mat_voxel_to_abaqus_inp.m`: exports the repeated voxel model to Abaqus `.inp`
- `save_repeat222_mat.m` or `save_repeat444_mat.m`: saves the repeated voxel model as a `.mat` file

Main outputs:

```text
batch_curved_x/2x2x2_mat/ or batch_curved_x/4x4x4_mat/
Output/
```

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

### batch_export_mat_voxel_to_stl_222.m / batch_export_mat_voxel_to_stl_444.m

These scripts convert repeated voxel `.mat` files into STL files for 3D printing.

Main output:

```text
STL/
```

The STL export is intended for slicers such as Bambu Studio.

---

### abaqus_batch_run_all.py

Abaqus batch simulation script.

It automatically:

- imports `.inp` files from `Output/`
- creates material, section, step, node sets, and compression boundary conditions
- submits Abaqus jobs one by one
- extracts force–displacement and stress–strain curves from `.odb`
- writes result CSV files into `Results/`

Main outputs:

```text
Abaqus_Work/
Results/
```

Main parameters to modify if needed:

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

The default compression settings are:

```text
2x2x2: H0 = 40 mm, compression displacement = -8 mm
4x4x4: H0 = 80 mm, compression displacement = -16 mm
```

---

### postprocess_summary_and_plots.py

Normal Python postprocessing script.

It reads the curve CSV files in `Results/` and generates:

```text
summary_metrics.csv
correlation_matrix.csv
top10_by_energy_absorption.csv
top10_by_SEA.csv
figures/
```

Main parameters to modify if needed:

```python
ROOT_DIR
SOLID_DENSITY_G_CM3
```

---

## 3D printing

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

## GitHub upload rule

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

## Version history

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
