README
=======================================
Normal usage:
1) Run 'batch_generate_curved_x.m'
2) Run 'batch_repeat444_and_export_inp.m'
3) Import one '.inp' file from the 'Output' folder into Abaqus/CAE, then run 'abaqus_full_preprocess.py'
4) Create a new Job (choose the imported model), then submit it
5) After the job finishes, run 'make_stress_strain_xy.py' to generate the 'Stress_Strain' and 'Force_Displacement' curves

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

3) 'abaqus_full_preprocess.py'
   Abaqus preprocessing script.
   It automatically creates the material, section, section assignment, step, assembly-level top/bottom sets, and compression boundary conditions.

4) 'make_stress_strain_xy.py'
   Abaqus postprocessing script.
   It extracts the top loading response from the '.odb' file and generates:
   - 'Force_Displacement'
   - 'Stress_Strain'