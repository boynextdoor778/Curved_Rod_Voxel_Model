from abaqus import mdb
from abaqusConstants import *
import regionToolset

# =========================
# USER SETTINGS
# =========================
MODEL_NAME     = 'cx_rand_00002_b114_r038_rep444'# 根据模型名修改
PART_NAME      = 'LATTICE'
INSTANCE_NAME  = 'LATTICE-1' #可能会出现变化，关注结构树里instance_name

# material / section
MATERIAL_NAME  = 'Material-1'
SECTION_NAME   = 'Section-1'
ELEMENT_SET    = 'EALL'
E_MODULUS      = 2000.0
POISSON_RATIO  = 0.30

# step
STEP_NAME      = 'Step-1'
NLGEOM_ON      = ON
INITIAL_INC    = 0.01
MAX_NUM_INC    = 1000
MIN_INC        = 1e-8
MAX_INC        = 0.1

# boundary sets
TOP_SET_NAME   = 'N_TOP_FIX'
BOT_SET_NAME   = 'N_BOTTOM_FIX'
TOP_ASM_NAME   = 'TOP_ASM_FIX'
BOT_ASM_NAME   = 'BOTTOM_ASM_FIX'

# BC names
BC_BOTTOM_NAME = 'BC_bottom_fix'
BC_TOP_NAME    = 'BC_top_fix'
DISP_Z         = -16.0 #压缩高度

# =========================
# MAIN
# =========================
m = mdb.models[MODEL_NAME]
p = m.parts[PART_NAME]
a = m.rootAssembly
inst = a.instances[INSTANCE_NAME]

# ---- material ----
if MATERIAL_NAME in m.materials.keys():
    del m.materials[MATERIAL_NAME]

mat = m.Material(name=MATERIAL_NAME)
mat.Elastic(table=((E_MODULUS, POISSON_RATIO),))

# ---- section ----
if SECTION_NAME in m.sections.keys():
    del m.sections[SECTION_NAME]

m.HomogeneousSolidSection(name=SECTION_NAME, material=MATERIAL_NAME, thickness=None)

# ---- section assignment to EALL ----
region = regionToolset.Region(elements=p.sets[ELEMENT_SET].elements)
if len(p.sectionAssignments) > 0:
    del p.sectionAssignments[:]

p.SectionAssignment(region=region, sectionName=SECTION_NAME, offset=0.0,
                    offsetType=MIDDLE_SURFACE, offsetField='',
                    thicknessAssignment=FROM_SECTION)

# ---- step ----
if STEP_NAME in m.steps.keys():
    del m.steps[STEP_NAME]

m.StaticStep(name=STEP_NAME, previous='Initial', nlgeom=NLGEOM_ON,
             initialInc=INITIAL_INC, maxNumInc=MAX_NUM_INC,
             minInc=MIN_INC, maxInc=MAX_INC)

# ---- assembly sets ----
if TOP_ASM_NAME in a.sets.keys():
    del a.sets[TOP_ASM_NAME]
if BOT_ASM_NAME in a.sets.keys():
    del a.sets[BOT_ASM_NAME]

a.Set(name=TOP_ASM_NAME, nodes=inst.sets[TOP_SET_NAME].nodes)
a.Set(name=BOT_ASM_NAME, nodes=inst.sets[BOT_SET_NAME].nodes)

# ---- BCs ----
if BC_BOTTOM_NAME in m.boundaryConditions.keys():
    del m.boundaryConditions[BC_BOTTOM_NAME]
if BC_TOP_NAME in m.boundaryConditions.keys():
    del m.boundaryConditions[BC_TOP_NAME]

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
    u1=UNSET, u2=UNSET, u3=DISP_Z,
    ur1=UNSET, ur2=UNSET, ur3=UNSET
)

print('Done.')
print('Model          = {}'.format(MODEL_NAME))
print('Part           = {}'.format(PART_NAME))
print('Instance       = {}'.format(INSTANCE_NAME))
print('Material       = {}'.format(MATERIAL_NAME))
print('Section        = {}'.format(SECTION_NAME))
print('Assigned set   = {}'.format(ELEMENT_SET))
print('Top asm set    = {}'.format(TOP_ASM_NAME))
print('Bottom asm set = {}'.format(BOT_ASM_NAME))
print('BC bottom      = {}'.format(BC_BOTTOM_NAME))
print('BC top         = {}'.format(BC_TOP_NAME))
