README

## Version
Current version: V2.0

Main updates:
- Added separated 2x2x2 and 4x4x4 workflows
- Added STL export branch for Bambu Studio / 3D printing
- Added compact Abaqus INP exporter to reduce unnecessary nodes
- Added separated Output, STL, Abaqus_Work, and Results folders
- Added 3D_print_note for practical slicing and printing settings

=======================================
Normal usage:
1) Run 'batch_generate_curved_x.m'
2) Run 'batch_repeat444_and_export_inp.m'
3) Run 'abaqus_batch_run_all.py' in Abaqus/CAE noGUI mode
4) Run 'postprocess_summary_and_plots.py' with normal Python
5) Check 'Result' for curves, summary metrics, and figures

Command line usage:
1) MATLAB
   Open MATLAB, set the project folder as current folder, then run:
   batch_generate_curved_x
   batch_repeat444_and_export_inp

2) Abaqus batch simulation
   CMD:
   cd /d D:\Simulation\Curved_Rod_Voxel_Model
   abaqus cae noGUI=D:\Simulation\Curved_Rod_Voxel_Model\abaqus_batch_run_all.py

   PowerShell:
   Set-Location "D:\Simulation\Curved_Rod_Voxel_Model"
   abaqus cae noGUI=D:\Simulation\Curved_Rod_Voxel_Model\abaqus_batch_run_all.py

3) Python postprocessing
   CMD:
   cd /d D:\Simulation\Curved_Rod_Voxel_Model
   python postprocess_summary_and_plots.py

   PowerShell:
   Set-Location "D:\Simulation\Curved_Rod_Voxel_Model"
   python postprocess_summary_and_plots.py
