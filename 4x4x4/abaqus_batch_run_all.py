# -*- coding: utf-8 -*-
"""
Abaqus LIGHT batch pipeline for voxel curved-X lattice models.

Fixed-size branch version for 4x4x4.

Purpose:
    Scan one folder for all .inp files, then for each .inp:
    1) Import .inp as Abaqus model
    2) Apply material, section, step, assembly node sets, compression BCs
    3) Replace default output requests with light top-set U/RF output only
    4) Create and submit Job
    5) Wait for Job completion
    6) Read .odb
    7) Export Force-Displacement and Stress-Strain CSV files
    8) Write batch_status.csv and failed_jobs.txt, including elapsed time and ODB size

How to run in Windows command line:
    abaqus cae noGUI=abaqus_batch_run_all.py

Optional: override INP_DIR from command line:
    abaqus cae noGUI=abaqus_batch_run_all.py

Important:
    - Run this with "abaqus cae noGUI=...", not "abaqus python ...".
    - Keep WORK_ROOT on D drive or another large disk, not C drive.
    - Default local folders are Output / Abaqus_Work / Results / Abaqus_Scratch inside this branch folder.
"""
from __future__ import print_function

import os
import sys
import csv
import glob
import traceback
import time

from abaqus import mdb, session
from abaqusConstants import *
import regionToolset


# ============================================================
# USER SETTINGS
# ============================================================

# Root folder of the whole project.
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Choose default branch: '2x2x2' or '4x4x4'.
# Command-line INP_DIR override is still supported and the branch will be inferred
# from the folder/file name when possible.
RUN_SIZE = '4x4x4'

# Folder containing all .inp files exported from MATLAB.
INP_DIR = os.path.join(ROOT_DIR, 'Output')

# Work folder. Job files, odb, dat, msg, sta, etc. will be written here.
# IMPORTANT: do not put this on C drive if models are large.
WORK_ROOT = os.path.join(ROOT_DIR, 'Abaqus_Work')

# Result folder. CSV curves and batch logs will be written here.
RESULT_ROOT = os.path.join(ROOT_DIR, 'Results')

# Names used by your exported INP
PART_NAME = 'LATTICE'
INSTANCE_NAME = 'LATTICE-1'
ELEMENT_SET = 'EALL'
TOP_SET_NAME = 'N_TOP_FIX'
BOT_SET_NAME = 'N_BOTTOM_FIX'

# Assembly-level sets created by this script
TOP_ASM_NAME = 'TOP_ASM_FIX'
BOT_ASM_NAME = 'BOTTOM_ASM_FIX'

# Material / section
MATERIAL_NAME = 'Material-1'
SECTION_NAME = 'Section-1'
E_MODULUS = 2000.0
POISSON_RATIO = 0.30

# Step
STEP_NAME = 'Step-1'
NLGEOM_ON = ON
INITIAL_INC = 0.01
MAX_NUM_INC = 1000
MIN_INC = 1e-8
MAX_INC = 0.1

# Boundary conditions
BC_BOTTOM_NAME = 'BC_bottom_fix'
BC_TOP_NAME = 'BC_top_fix'

# Compression / stress-strain conversion
# 4x4x4: height = 80 mm, compression displacement = -16 mm for 20% strain
# 2x2x2: height = 40 mm, compression displacement = -8 mm for 20% strain
COMPRESSION_STRAIN = 0.20
DEFAULT_H0 = 80.0
DEFAULT_A0 = 80.0 * 80.0

# Job settings
NUM_CPUS = 8
NUM_DOMAINS = 8
MEMORY_PERCENT = 90

# Batch behavior
OVERWRITE_MODEL_AND_JOB = True
SKIP_IF_RESULTS_EXIST = True       # True: skip cases that already have stress-strain and force-displacement CSVs
STOP_ON_ERROR = False              # False: failed case is recorded, then the next .inp continues
REQUIRE_SUCCESSFUL_STA = True      # True: require .sta to contain successful completion message before postprocessing
CREATE_XYDATA_IN_SESSION = False   # False is better for large batch runs to reduce memory usage
DELETE_MODEL_AFTER_EACH_CASE = True
DELETE_JOB_AFTER_EACH_CASE = True

# Light output mode
# Purpose: reduce .odb size by removing default whole-model field output and requesting only
# top-node displacement/reaction data required for force-displacement and stress-strain curves.
LIGHT_OUTPUT_MODE = True
DELETE_EXISTING_OUTPUT_REQUESTS = True
FIELD_OUTPUT_NAME = 'F_TOP_U_RF_ONLY'
FIELD_OUTPUT_FREQUENCY = 1         # 1 = output every accepted increment; keep this for smooth curves

# Optional testing limit. Use None for all files. Use e.g. 1 or 2 for a small test batch.
MAX_CASES = 1


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_cli_inp_dir(default_dir):
    """Read inp folder after --, if provided."""
    args = sys.argv
    if '--' in args:
        idx = args.index('--')
        if len(args) > idx + 1:
            return args[idx + 1]
    return default_dir


def safe_mkdir(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def infer_run_size_from_text(text_value, default_size):
    """Infer 2x2x2 / 4x4x4 from folder, file, model, or case name."""
    lower = str(text_value).lower()
    if '2x2x2' in lower or 'rep222' in lower:
        return '2x2x2'
    if '4x4x4' in lower or 'rep444' in lower:
        return '4x4x4'
    return default_size


def get_specimen_settings(name_value):
    """Return fixed specimen height, area, and compression displacement for this branch."""
    run_size = RUN_SIZE
    h0 = 80
    a0 = 6400
    disp_z = -16
    return {'run_size': run_size, 'H0': h0, 'A0': a0, 'DISP_Z': disp_z}


def configure_roots_for_inp_dir(inp_dir):
    """Use local branch folders: Output, Abaqus_Work, and Results."""
    global WORK_ROOT, RESULT_ROOT
    run_size = RUN_SIZE
    WORK_ROOT = os.path.join(ROOT_DIR, 'Abaqus_Work')
    RESULT_ROOT = os.path.join(ROOT_DIR, 'Results')
    return run_size


def write_csv_rows(csv_path, header, rows, append=False):
    # Compatible with both Abaqus Python 2 and Python 3.
    is_py2 = (sys.version_info[0] == 2)
    if is_py2:
        mode = 'ab' if append else 'wb'
        f = open(csv_path, mode)
    else:
        mode = 'a' if append else 'w'
        f = open(csv_path, mode, newline='')
    try:
        writer = csv.writer(f)
        if header is not None:
            writer.writerow(header)
        writer.writerows(rows)
    finally:
        f.close()


def append_text(path, text):
    f = open(path, 'a')
    try:
        f.write(text)
        if not text.endswith('\n'):
            f.write('\n')
    finally:
        f.close()


def clean_name_from_inp(inp_path):
    base = os.path.basename(inp_path)
    name, ext = os.path.splitext(base)
    # Abaqus model/job names should avoid special characters.
    safe = name.replace(' ', '_').replace('-', '_')
    return safe


def find_repo_key(repo, target_name):
    """Find a key in an Abaqus repository, allowing case-insensitive matching."""
    if target_name in repo.keys():
        return target_name
    target_upper = target_name.upper()
    for k in repo.keys():
        if k.upper() == target_upper:
            return k
    raise KeyError('Cannot find key "{}". Available keys: {}'.format(target_name, list(repo.keys())))


def delete_if_exists(repo, name):
    if name in repo.keys():
        del repo[name]


def list_inp_files(inp_dir):
    files = sorted(glob.glob(os.path.join(inp_dir, '*.inp')))
    if MAX_CASES is not None:
        files = files[:MAX_CASES]
    return files


def result_paths(case_name):
    fd_csv = os.path.join(RESULT_ROOT, case_name + '_force_displacement.csv')
    ss_csv = os.path.join(RESULT_ROOT, case_name + '_stress_strain.csv')
    all_csv = os.path.join(RESULT_ROOT, case_name + '_all_response.csv')
    return fd_csv, ss_csv, all_csv


def results_already_exist(case_name):
    fd_csv, ss_csv, all_csv = result_paths(case_name)
    return os.path.isfile(fd_csv) and os.path.isfile(ss_csv)


def write_batch_status(case_name, inp_path, status, message, n_frames='', elapsed_sec='', odb_mb=''):
    safe_mkdir(RESULT_ROOT)
    status_csv = os.path.join(RESULT_ROOT, 'batch_status.csv')
    file_exists = os.path.isfile(status_csv)
    header = None if file_exists else [
        'case_name', 'inp_path', 'status', 'message', 'n_frames', 'elapsed_sec', 'odb_mb'
    ]
    write_csv_rows(
        status_csv,
        header,
        [[case_name, inp_path, status, message, n_frames, elapsed_sec, odb_mb]],
        append=file_exists
    )


def check_sta_success(sta_path):
    if not os.path.isfile(sta_path):
        return False, 'STA file not found: {}'.format(sta_path)

    try:
        f = open(sta_path, 'r')
        text = f.read()
        f.close()
    except Exception as e:
        return False, 'Cannot read STA file: {}'.format(e)

    upper = text.upper()
    if 'THE ANALYSIS HAS COMPLETED SUCCESSFULLY' in upper:
        return True, 'STA reports successful completion'

    if 'ERROR' in upper or 'THE ANALYSIS HAS NOT BEEN COMPLETED' in upper:
        return False, 'STA does not report successful completion'

    return False, 'STA success message not found'


def cleanup_session(model_name, job_name):
    if DELETE_JOB_AFTER_EACH_CASE:
        try:
            if job_name in mdb.jobs.keys():
                del mdb.jobs[job_name]
        except Exception:
            pass

    if DELETE_MODEL_AFTER_EACH_CASE:
        try:
            if model_name in mdb.models.keys():
                del mdb.models[model_name]
        except Exception:
            pass


# ============================================================
# MAIN PIPELINE FUNCTIONS
# ============================================================

def import_inp_model(inp_path, model_name):
    if not os.path.isfile(inp_path):
        raise IOError('INP file not found: {}'.format(inp_path))

    if OVERWRITE_MODEL_AND_JOB and model_name in mdb.models.keys():
        del mdb.models[model_name]

    print('Importing INP: {}'.format(inp_path))
    mdb.ModelFromInputFile(name=model_name, inputFileName=inp_path)
    print('Imported model: {}'.format(model_name))
    return mdb.models[model_name]


def apply_preprocess(model_name):
    print('Applying preprocessing...')

    m = mdb.models[model_name]
    specimen = get_specimen_settings(model_name)
    disp_z = specimen['DISP_Z']

    part_key = find_repo_key(m.parts, PART_NAME)
    p = m.parts[part_key]

    a = m.rootAssembly
    inst_key = find_repo_key(a.instances, INSTANCE_NAME)
    inst = a.instances[inst_key]

    elem_set_key = find_repo_key(p.sets, ELEMENT_SET)
    top_set_key = find_repo_key(inst.sets, TOP_SET_NAME)
    bot_set_key = find_repo_key(inst.sets, BOT_SET_NAME)

    # ---- material ----
    delete_if_exists(m.materials, MATERIAL_NAME)
    mat = m.Material(name=MATERIAL_NAME)
    mat.Elastic(table=((E_MODULUS, POISSON_RATIO),))

    # ---- section ----
    delete_if_exists(m.sections, SECTION_NAME)
    m.HomogeneousSolidSection(name=SECTION_NAME, material=MATERIAL_NAME, thickness=None)

    # ---- section assignment ----
    region = regionToolset.Region(elements=p.sets[elem_set_key].elements)
    try:
        if len(p.sectionAssignments) > 0:
            del p.sectionAssignments[:]
    except Exception:
        pass

    p.SectionAssignment(region=region, sectionName=SECTION_NAME, offset=0.0,
                        offsetType=MIDDLE_SURFACE, offsetField='',
                        thicknessAssignment=FROM_SECTION)

    # ---- step ----
    delete_if_exists(m.steps, STEP_NAME)
    m.StaticStep(name=STEP_NAME, previous='Initial', nlgeom=NLGEOM_ON,
                 initialInc=INITIAL_INC, maxNumInc=MAX_NUM_INC,
                 minInc=MIN_INC, maxInc=MAX_INC)

    # ---- assembly node sets ----
    delete_if_exists(a.sets, TOP_ASM_NAME)
    delete_if_exists(a.sets, BOT_ASM_NAME)
    a.Set(name=TOP_ASM_NAME, nodes=inst.sets[top_set_key].nodes)
    a.Set(name=BOT_ASM_NAME, nodes=inst.sets[bot_set_key].nodes)

    # ---- BCs ----
    delete_if_exists(m.boundaryConditions, BC_BOTTOM_NAME)
    delete_if_exists(m.boundaryConditions, BC_TOP_NAME)

    m.DisplacementBC(
        name=BC_BOTTOM_NAME,
        createStepName='Initial',
        region=a.sets[BOT_ASM_NAME],
        u1=0.0, u2=0.0, u3=0.0,
        ur1=UNSET, ur2=UNSET, ur3=UNSET
    )

    m.DisplacementBC(
        name=BC_TOP_NAME,
        createStepName=STEP_NAME,
        region=a.sets[TOP_ASM_NAME],
        u1=UNSET, u2=UNSET, u3=disp_z,
        ur1=UNSET, ur2=UNSET, ur3=UNSET
    )

    configure_light_output_requests(m, a)

    print('Preprocess done.')
    print('Model          = {}'.format(model_name))
    print('Part           = {}'.format(part_key))
    print('Instance       = {}'.format(inst_key))
    print('Element set    = {}'.format(elem_set_key))
    print('Top set        = {}'.format(top_set_key))
    print('Bottom set     = {}'.format(bot_set_key))
    print('Run size       = {}'.format(specimen['run_size']))
    print('H0 / A0        = {} / {}'.format(specimen['H0'], specimen['A0']))
    print('Compression U3 = {}'.format(disp_z))


def configure_light_output_requests(m, a):
    """Reduce ODB output to the minimum needed for curve extraction."""
    if not LIGHT_OUTPUT_MODE:
        return

    print('Configuring light output requests...')

    if DELETE_EXISTING_OUTPUT_REQUESTS:
        # Remove default whole-model field/history output requests.
        # This is the main disk/time-saving step for large voxel models.
        for key in list(m.fieldOutputRequests.keys()):
            try:
                del m.fieldOutputRequests[key]
            except Exception:
                pass
        for key in list(m.historyOutputRequests.keys()):
            try:
                del m.historyOutputRequests[key]
            except Exception:
                pass

    # Only request nodal displacement U and reaction force RF on the top assembly node set.
    # The postprocessor computes average U3 and summed RF3 from this set.
    delete_if_exists(m.fieldOutputRequests, FIELD_OUTPUT_NAME)
    m.FieldOutputRequest(
        name=FIELD_OUTPUT_NAME,
        createStepName=STEP_NAME,
        variables=('U', 'RF'),
        region=a.sets[TOP_ASM_NAME],
        frequency=FIELD_OUTPUT_FREQUENCY
    )

    print('Light output active: only U/RF on {}'.format(TOP_ASM_NAME))


def create_and_run_job(model_name, job_name):
    print('Creating job: {}'.format(job_name))

    if OVERWRITE_MODEL_AND_JOB and job_name in mdb.jobs.keys():
        del mdb.jobs[job_name]

    job = mdb.Job(
        name=job_name,
        model=model_name,
        description='Auto compression job for {}'.format(model_name),
        type=ANALYSIS,
        atTime=None,
        waitMinutes=0,
        waitHours=0,
        queue=None,
        memory=MEMORY_PERCENT,
        memoryUnits=PERCENTAGE,
        getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE,
        nodalOutputPrecision=SINGLE,
        echoPrint=OFF,
        modelPrint=OFF,
        contactPrint=OFF,
        historyPrint=OFF,
        userSubroutine='',
        scratch='',
        multiprocessingMode=DEFAULT,
        numCpus=NUM_CPUS,
        numDomains=NUM_DOMAINS,
        numGPUs=0
    )

    print('Submitting job...')
    job.submit(consistencyChecking=OFF)
    job.waitForCompletion()
    print('Job finished: {}'.format(job_name))


def extract_curves_from_odb(odb_path, case_name):
    if not os.path.isfile(odb_path):
        raise IOError('ODB file not found: {}'.format(odb_path))

    print('Reading ODB: {}'.format(odb_path))
    specimen = get_specimen_settings(case_name)
    h0 = specimen['H0']
    a0 = specimen['A0']
    odb = session.openOdb(name=odb_path)

    try:
        if STEP_NAME not in odb.steps.keys():
            raise KeyError('Step not found in ODB: {}'.format(STEP_NAME))

        step = odb.steps[STEP_NAME]
        asm = odb.rootAssembly

        set_key = find_repo_key(asm.nodeSets, TOP_ASM_NAME)
        region = asm.nodeSets[set_key]

        rows_force_disp = []
        rows_stress_strain = []
        rows_all = []

        for frame in step.frames:
            if 'U' not in frame.fieldOutputs.keys() or 'RF' not in frame.fieldOutputs.keys():
                continue

            u_field = frame.fieldOutputs['U'].getSubset(region=region, position=NODAL)
            rf_field = frame.fieldOutputs['RF'].getSubset(region=region, position=NODAL)

            u3_vals = [v.data[2] for v in u_field.values]
            rf3_vals = [v.data[2] for v in rf_field.values]

            if len(u3_vals) == 0 or len(rf3_vals) == 0:
                continue

            avg_u3 = sum(u3_vals) / float(len(u3_vals))
            sum_rf3 = sum(rf3_vals)

            displacement = -avg_u3
            force = -sum_rf3
            strain = -avg_u3 / h0
            stress = -sum_rf3 / a0
            time_value = frame.frameValue

            rows_force_disp.append([displacement, force])
            rows_stress_strain.append([strain, stress])
            rows_all.append([time_value, avg_u3, sum_rf3, displacement, force, strain, stress])

        if len(rows_stress_strain) == 0:
            raise RuntimeError('No valid U/RF data extracted from ODB.')

        safe_mkdir(RESULT_ROOT)

        fd_csv, ss_csv, all_csv = result_paths(case_name)

        write_csv_rows(fd_csv, ['displacement_mm', 'force_N'], rows_force_disp)
        write_csv_rows(ss_csv, ['strain', 'stress_MPa'], rows_stress_strain)
        write_csv_rows(all_csv, ['time', 'avg_u3_mm', 'sum_rf3_N', 'displacement_mm', 'force_N', 'strain', 'stress_MPa'], rows_all)

        if CREATE_XYDATA_IN_SESSION:
            session.XYData(name='Force_Displacement_' + case_name,
                           data=tuple(rows_force_disp))
            session.XYData(name='Stress_Strain_' + case_name,
                           data=tuple(rows_stress_strain))

        print('Curve CSV exported:')
        print('  {}'.format(fd_csv))
        print('  {}'.format(ss_csv))
        print('  {}'.format(all_csv))
        print('Number of valid frames = {}'.format(len(rows_stress_strain)))
        return len(rows_stress_strain)

    finally:
        odb.close()


def run_one_case(inp_path):
    case_start_time = time.time()
    inp_path = os.path.abspath(inp_path)
    model_name = clean_name_from_inp(inp_path)
    case_name = model_name
    job_name = 'Job_' + case_name
    work_dir = os.path.join(WORK_ROOT, case_name)

    safe_mkdir(work_dir)
    safe_mkdir(RESULT_ROOT)

    if SKIP_IF_RESULTS_EXIST and results_already_exist(case_name):
        print('Skipping existing result: {}'.format(case_name))
        write_batch_status(case_name, inp_path, 'SKIPPED', 'Result CSV already exists', '', '', '')
        return 'SKIPPED'

    old_cwd = os.getcwd()
    try:
        os.chdir(work_dir)

        print('------------------------------------------------------------')
        print('CASE START')
        print('INP      = {}'.format(inp_path))
        print('Case     = {}'.format(case_name))
        print('Work dir = {}'.format(work_dir))
        print('------------------------------------------------------------')

        import_inp_model(inp_path, model_name)
        apply_preprocess(model_name)
        create_and_run_job(model_name, job_name)

        sta_path = os.path.join(work_dir, job_name + '.sta')
        if REQUIRE_SUCCESSFUL_STA:
            ok_sta, sta_msg = check_sta_success(sta_path)
            if not ok_sta:
                raise RuntimeError(sta_msg)

        odb_path = os.path.join(work_dir, job_name + '.odb')
        n_frames = extract_curves_from_odb(odb_path, case_name)

        elapsed_sec = round(time.time() - case_start_time, 3)
        odb_mb = ''
        if os.path.isfile(odb_path):
            odb_mb = round(os.path.getsize(odb_path) / (1024.0 * 1024.0), 3)

        write_batch_status(case_name, inp_path, 'SUCCESS', 'Finished', n_frames, elapsed_sec, odb_mb)
        print('CASE SUCCESS: {}'.format(case_name))
        print('Elapsed sec = {}'.format(elapsed_sec))
        print('ODB MB      = {}'.format(odb_mb))
        return 'SUCCESS'

    except Exception as e:
        err_msg = traceback.format_exc()
        print('CASE FAILED: {}'.format(case_name))
        print(err_msg)
        elapsed_sec = round(time.time() - case_start_time, 3)
        write_batch_status(case_name, inp_path, 'FAILED', str(e), '', elapsed_sec, '')
        failed_txt = os.path.join(RESULT_ROOT, 'failed_jobs.txt')
        append_text(failed_txt, case_name + ' | ' + inp_path + ' | ' + str(e))
        if STOP_ON_ERROR:
            raise
        return 'FAILED'

    finally:
        try:
            os.chdir(old_cwd)
        except Exception:
            pass
        cleanup_session(model_name, job_name)


# ============================================================
# MAIN
# ============================================================

def main():
    inp_dir = get_cli_inp_dir(INP_DIR)
    inp_dir = os.path.abspath(inp_dir)
    active_run_size = configure_roots_for_inp_dir(inp_dir)

    safe_mkdir(WORK_ROOT)
    safe_mkdir(RESULT_ROOT)

    inp_files = list_inp_files(inp_dir)

    print('============================================================')
    print('ABAQUS BATCH PIPELINE')
    print('Run size    = {}'.format(active_run_size))
    print('INP dir     = {}'.format(inp_dir))
    print('Work root   = {}'.format(WORK_ROOT))
    print('Result root = {}'.format(RESULT_ROOT))
    print('Found INP   = {}'.format(len(inp_files)))
    print('Skip exists = {}'.format(SKIP_IF_RESULTS_EXIST))
    print('Max cases   = {}'.format(MAX_CASES))
    print('Light output= {}'.format(LIGHT_OUTPUT_MODE))
    print('Field freq  = {}'.format(FIELD_OUTPUT_FREQUENCY))
    print('============================================================')

    if len(inp_files) == 0:
        raise RuntimeError('No .inp files found in: {}'.format(inp_dir))

    n_success = 0
    n_failed = 0
    n_skipped = 0

    for idx, inp_path in enumerate(inp_files):
        print('\n========== [{}/{}] =========='.format(idx + 1, len(inp_files)))
        status = run_one_case(inp_path)
        if status == 'SUCCESS':
            n_success += 1
        elif status == 'SKIPPED':
            n_skipped += 1
        else:
            n_failed += 1

    print('\n============================================================')
    print('BATCH FINISHED')
    print('SUCCESS = {}'.format(n_success))
    print('SKIPPED = {}'.format(n_skipped))
    print('FAILED  = {}'.format(n_failed))
    print('Status CSV: {}'.format(os.path.join(RESULT_ROOT, 'batch_status.csv')))
    print('============================================================')


if __name__ == '__main__':
    main()
