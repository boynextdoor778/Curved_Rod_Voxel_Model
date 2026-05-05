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
