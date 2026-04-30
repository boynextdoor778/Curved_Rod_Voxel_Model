README
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

=======================================
Note:
1) 'batch_generate_curved_x.m'
   Main script for generating random curved-X voxel samples.
   It calls:
   - 'GenerateVoxel.m': builds the voxel model from the topology definition
   - 'write_curved_x_topology.m': writes the curved-X topology file
   - 'save_sample_mat.m': saves each generated sample as a '.mat' file

2) 'batch_repeat444_and_export_inp.m'
   Main script for repeating each sample to a 4x4x4 specimen and exporting mesh-only Abaqus '.inp' files.
   It calls:
   - 'export_mat_voxel_to_abaqus_inp.m': exports the repeated voxel model to Abaqus '.inp'
   - 'save_repeat444_mat.m': saves the repeated 4x4x4 voxel model as a '.mat' file

3) 'abaqus_batch_run_all.py'
   Abaqus batch simulation script.
   It scans all '.inp' files in the 'Output' folder, creates jobs automatically, submits them one by one, and extracts:
   - 'Force_Displacement'
   - 'Stress_Strain'
   Results are saved in the 'Results' folder.
   Abaqus working files are saved in the 'Abaqus_Work' folder.

4) 'postprocess_summary_and_plots.py'
   Normal Python postprocessing script.
   It reads the curve CSV files in 'Results' and generates:
   - 'summary_metrics.csv'
   - validation figures in 'Results/figures'
   - 'correlation_matrix.csv'
   - 'top10_by_energy_absorption.csv'
   - 'top10_by_SEA.csv'

=======================================
Important settings:
1) In 'batch_generate_curved_x.m':
   Modify 'rootDir', 'targetN', 'nVoxel', radius range, bendAmp range, and density filter if needed.

2) In 'batch_repeat444_and_export_inp.m':
   Modify 'rootDir', 'repeatN', and 'voxelSize' if needed.

3) In 'abaqus_batch_run_all.py':
   Modify 'INP_DIR', 'WORK_ROOT', 'RESULT_ROOT', material properties, displacement, CPU settings, and 'MAX_CASES' if needed.

4) In 'postprocess_summary_and_plots.py':
   Modify 'ROOT_DIR' and material density for SEA calculation if needed.

