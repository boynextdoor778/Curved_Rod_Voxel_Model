# Curved Rod Voxel Model

Author: Alex Lang  
Version: V1.0 Single-scale 4x4x4 Abaqus simulation workflow

This repository provides a MATLAB–Abaqus workflow for generating curved-rod voxel lattice specimens, exporting mesh-only Abaqus `.inp` files, running compression simulations, and automatically extracting force–displacement and stress–strain curves.

The V1.0 version focuses on the `4x4x4` lattice specimen workflow.

---

## Version

Current version: V1.0

Main features:

- Generates random curved-X voxel lattice samples in MATLAB
- Repeats each single-cell sample into a `4x4x4` specimen
- Exports mesh-only Abaqus `.inp` files
- Runs Abaqus compression simulations in batch mode
- Extracts force–displacement and stress–strain curves automatically
- Generates summary metrics and validation figures

---

## Folder structure

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
├─ batch_curved_x/
│  ├─ mat/
│  ├─ topology/
│  ├─ preview/
│  ├─ 4x4x4_mat/
│  └─ summary_random.csv
├─ Output/
├─ Abaqus_Work/
├─ Results/
└─ README.md
```

---

## Normal usage

1. Run `batch_generate_curved_x.m`
2. Run `batch_repeat444_and_export_inp.m`
3. Run `abaqus_batch_run_all.py` in Abaqus/CAE noGUI mode
4. Run `postprocess_summary_and_plots.py` with normal Python
5. Check `Results/` for curves, summary metrics, and figures

---

## Command line usage

### 1. MATLAB

Open MATLAB and set the project folder as the current folder:

```text
D:\Simulation\Curved_Rod_Voxel_Model
```

Then run:

```matlab
batch_generate_curved_x
batch_repeat444_and_export_inp
```

---

### 2. Abaqus batch simulation

Run from CMD:

```cmd
cd /d D:\Simulation\Curved_Rod_Voxel_Model
abaqus cae noGUI=abaqus_batch_run_all.py
```

Run from PowerShell:

```powershell
Set-Location "D:\Simulation\Curved_Rod_Voxel_Model"
abaqus cae noGUI=abaqus_batch_run_all.py
```

---

### 3. Python postprocessing

Run from CMD:

```cmd
cd /d D:\Simulation\Curved_Rod_Voxel_Model
python postprocess_summary_and_plots.py
```

Run from PowerShell:

```powershell
Set-Location "D:\Simulation\Curved_Rod_Voxel_Model"
python postprocess_summary_and_plots.py
```

---

## Output folders

```text
batch_curved_x/mat/          Single-cell voxel .mat files
batch_curved_x/topology/     Curved-X topology .txt files
batch_curved_x/preview/      Preview images
batch_curved_x/4x4x4_mat/    Repeated 4x4x4 voxel .mat files
Output/                      Abaqus .inp files
Abaqus_Work/                 Abaqus job folders, .odb, .sta, .msg, .dat files
Results/                     Curve CSV files, summary metrics, and figures
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

---

### batch_repeat444_and_export_inp.m

Main MATLAB script for repeating each single-cell sample into a `4x4x4` specimen and exporting mesh-only Abaqus `.inp` files.

It calls:

- `export_mat_voxel_to_abaqus_inp.m`: exports the repeated voxel model to Abaqus `.inp`
- `save_repeat444_mat.m`: saves the repeated `4x4x4` voxel model as a `.mat` file

Main outputs:

```text
batch_curved_x/4x4x4_mat/
Output/
```

---

### abaqus_batch_run_all.py

Abaqus batch simulation script.

It automatically:

- scans all `.inp` files in the `Output/` folder
- imports each `.inp` file as an Abaqus model
- creates material, section, step, top/bottom node sets, and compression boundary conditions
- submits Abaqus jobs one by one
- extracts force–displacement and stress–strain curves from `.odb`
- saves result CSV files into `Results/`

Main outputs:

```text
Abaqus_Work/
Results/
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

---

## Important settings

### In batch_generate_curved_x.m

Modify if needed:

```matlab
rootDir
targetN
nVoxel
radiusMin / radiusMax
bendMin / bendMax
densityMin / densityMax
desiredWorkers
```

---

### In batch_repeat444_and_export_inp.m

Modify if needed:

```matlab
rootDir
repeatN
voxelSize
desiredWorkers
overwriteExisting
```

Default 4x4x4 setting:

```matlab
repeatN = [4 4 4];
voxelSize = [0.25 0.25 0.25];
```

---

### In abaqus_batch_run_all.py

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

Default 4x4x4 compression setting:

```python
DISP_Z = -16.0
H0 = 80.0
A0 = 80.0 * 80.0
```

For testing, use:

```python
MAX_CASES = 1
```

For running all cases, use:

```python
MAX_CASES = None
```

---

### In postprocess_summary_and_plots.py

Modify if needed:

```python
ROOT_DIR
RESULT_DIR_NAME
SOLID_DENSITY_G_CM3
```

---

## Version history

### V1.0

Initial MATLAB–Abaqus workflow for curved-rod voxel lattice generation, `4x4x4` specimen export, Abaqus compression simulation, and automatic curve extraction.
