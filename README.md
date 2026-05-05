README
=======================================
Curved_Rod_Voxel_Model/
├─ 2x2x2/
│  ├─ batch_generate_curved_x.m
│  ├─ batch_repeat222_and_export_inp.m
│  ├─ batch_export_mat_voxel_to_stl_222.m
│  ├─ abaqus_batch_run_all.py
│  ├─ postprocess_summary_and_plots.py
│  ├─ batch_curved_x/
│  ├─ Output/
│  ├─ STL/
│  ├─ Abaqus_Work/
│  └─ Results/
└─ 4x4x4/
   ├─ batch_generate_curved_x.m
   ├─ batch_repeat444_and_export_inp.m
   ├─ batch_export_mat_voxel_to_stl_444.m
   ├─ abaqus_batch_run_all.py
   ├─ postprocess_summary_and_plots.py
   ├─ batch_curved_x/
   ├─ Output/
   ├─ STL/
   ├─ Abaqus_Work/
   └─ Results/

=======================================
2x2x2 usage:
1) Open MATLAB and set current folder to:
   D:\Simulation\Curved_Rod_Voxel_Model\2x2x2

2) Run:
   batch_generate_curved_x
   batch_repeat222_and_export_inp
   batch_export_mat_voxel_to_stl_222

3) Abaqus batch simulation:
   CMD:
   cd /d D:\Simulation\Curved_Rod_Voxel_Model\2x2x2
   abaqus cae noGUI=abaqus_batch_run_all.py

4) Python postprocessing:
   CMD:
   cd /d D:\Simulation\Curved_Rod_Voxel_Model\2x2x2
   python postprocess_summary_and_plots.py

5) Check:
   Output/        Abaqus .inp files
   STL/           3D-print STL files
   Abaqus_Work/   Abaqus job folders
   Results/       force-displacement, stress-strain, summary, and figures

=======================================
4x4x4 usage:
1) Open MATLAB and set current folder to:
   D:\Simulation\Curved_Rod_Voxel_Model\4x4x4

2) Run:
   batch_generate_curved_x
   batch_repeat444_and_export_inp
   batch_export_mat_voxel_to_stl_444

3) Abaqus batch simulation:
   CMD:
   cd /d D:\Simulation\Curved_Rod_Voxel_Model\4x4x4
   abaqus cae noGUI=abaqus_batch_run_all.py

4) Python postprocessing:
   CMD:
   cd /d D:\Simulation\Curved_Rod_Voxel_Model\4x4x4
   python postprocess_summary_and_plots.py

5) Check:
   Output/        Abaqus .inp files
   STL/           3D-print STL files
   Abaqus_Work/   Abaqus job folders
   Results/       force-displacement, stress-strain, summary, and figures

=======================================
Notes:
1) 2x2x2 and 4x4x4 are now independent branches.
   Do not mix Output, STL, Abaqus_Work, or Results between the two folders.

2) The Abaqus script in each branch is fixed-size:
   2x2x2: H0 = 40 mm, A0 = 40 x 40 mm^2, compression U3 = -8 mm
   4x4x4: H0 = 80 mm, A0 = 80 x 80 mm^2, compression U3 = -16 mm

3) 'export_mat_voxel_to_abaqus_inp.m' is the compact exporter.
   It exports only active voxel nodes and active voxel elements.
   If old 4x4x4 .inp files are still very large, delete the old Output/*.inp and rerun:
   batch_repeat444_and_export_inp

4) In 'abaqus_batch_run_all.py':
   MAX_CASES = 1 is for testing one case.
   Set MAX_CASES = None for the full batch.

5) In 'abaqus_batch_run_all.py':
   DELETE_ODB_AFTER_EXTRACT = True saves disk space after CSV extraction.
   Set it to False if you need to reopen ODB files in Abaqus/CAE.

6) In 'postprocess_summary_and_plots.py':
   Change SOLID_DENSITY_G_CM3 when the real material density is known.

=======================================
Script summary:
1) 'batch_generate_curved_x.m'
   Generates random curved-X unit-cell voxel samples.
   Output: batch_curved_x/mat, batch_curved_x/topology, batch_curved_x/preview.

2) 'batch_repeat222_and_export_inp.m' / 'batch_repeat444_and_export_inp.m'
   Repeats unit cells to 2x2x2 or 4x4x4.
   Output: batch_curved_x/2x2x2_mat or batch_curved_x/4x4x4_mat, plus Output/*.inp.

3) 'batch_export_mat_voxel_to_stl_222.m' / 'batch_export_mat_voxel_to_stl_444.m'
   Converts repeated MAT voxel models into STL files for Bambu Studio.
   Output: STL/*.stl.

4) 'abaqus_batch_run_all.py'
   Imports all Output/*.inp files, creates Abaqus jobs, extracts force-displacement and stress-strain CSVs.
   Output: Abaqus_Work and Results.

5) 'postprocess_summary_and_plots.py'
   Reads Results CSV files and generates summary_metrics.csv, figures, correlation matrix, and top-10 tables.
