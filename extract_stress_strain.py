from odbAccess import openOdb
from abaqusConstants import NODAL

odb_path = r'D:\temp\Job-1.odb'   # 改成你的 odb 路径
step_name = 'Step-1'
set_name = 'TOP_ASM_FIX'          # 你现在真正加载的顶部装配级节点集

H0 = 80.0                         # 试样高度 mm
A0 = 80.0 * 80.0                  # 外包截面积 mm^2

odb = openOdb(odb_path)
step = odb.steps[step_name]
region = odb.rootAssembly.nodeSets[set_name]

csv_path = odb_path.replace('.odb', '_stress_strain.csv')

with open(csv_path, 'w') as f:
    f.write('frame,time,avg_u3,sum_rf3,strain,stress\n')

    for i, frame in enumerate(step.frames):
        if 'U' not in frame.fieldOutputs or 'RF' not in frame.fieldOutputs:
            continue

        u_field = frame.fieldOutputs['U'].getSubset(region=region, position=NODAL)
        rf_field = frame.fieldOutputs['RF'].getSubset(region=region, position=NODAL)

        u3_vals = [v.data[2] for v in u_field.values]
        rf3_vals = [v.data[2] for v in rf_field.values]

        if len(u3_vals) == 0 or len(rf3_vals) == 0:
            continue

        avg_u3 = sum(u3_vals) / float(len(u3_vals))
        sum_rf3 = sum(rf3_vals)

        strain = -avg_u3 / H0
        stress = -sum_rf3 / A0   # 若单位是 N 和 mm，则这里单位是 MPa

        f.write('{},{:.12g},{:.12g},{:.12g},{:.12g},{:.12g}\n'.format(
            i, frame.frameValue, avg_u3, sum_rf3, strain, stress
        ))

odb.close()
print('Saved:', csv_path)