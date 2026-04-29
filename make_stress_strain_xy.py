from odbAccess import openOdb
from abaqus import session
from abaqusConstants import NODAL

# =========================
# USER SETTINGS
# =========================
odb_path  = r'D:\temp\Job-1.odb'   # 改成自己的 odb 路径
step_name = 'Step-1'
set_name  = 'TOP_ASM_FIX'          # 你现在顶部加载用的装配级节点集

H0 = 80.0                          # 初始高度 mm
A0 = 80.0 * 80.0                   # 外包截面积 mm^2

# =========================
# READ ODB
# =========================
odb = session.openOdb(name=odb_path)
step = odb.steps[step_name]
region = odb.rootAssembly.nodeSets[set_name]

x_time   = []
y_avg_u3 = []
y_sum_rf3 = []
y_strain = []
y_stress = []

for frame in step.frames:
    if 'U' not in frame.fieldOutputs or 'RF' not in frame.fieldOutputs:
        continue

    u_field  = frame.fieldOutputs['U'].getSubset(region=region, position=NODAL)
    rf_field = frame.fieldOutputs['RF'].getSubset(region=region, position=NODAL)

    u3_vals  = [v.data[2] for v in u_field.values]
    rf3_vals = [v.data[2] for v in rf_field.values]

    if len(u3_vals) == 0 or len(rf3_vals) == 0:
        continue

    avg_u3  = sum(u3_vals) / float(len(u3_vals))
    sum_rf3 = sum(rf3_vals)

    strain = -avg_u3 / H0
    stress = -sum_rf3 / A0

    x_time.append(frame.frameValue)
    y_avg_u3.append(avg_u3)
    y_sum_rf3.append(sum_rf3)
    y_strain.append(strain)
    y_stress.append(stress)

# =========================
# CREATE XY DATA IN ABAQUS
# =========================
xy_force_disp = session.XYData(
    name='Force_Displacement',
    data=tuple(zip(y_avg_u3, [-v for v in y_sum_rf3]))
)

xy_stress_strain = session.XYData(
    name='Stress_Strain',
    data=tuple(zip(y_strain, y_stress))
)

print('Created XY data: Force_Displacement')
print('Created XY data: Stress_Strain')
print('Number of points =', len(y_strain))