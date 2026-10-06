"""Pure negative controls for the prepared source roundtrip gate. No Blender."""
import copy,json,hashlib
from pathlib import Path
import source_roundtrip_checks as checks
S=Path(__file__).resolve().parent;plan=json.loads((S/'CORE_PLAN.json').read_text());rows=[]
for p in plan['parts']:
    rows.append(dict(name=p['name'],vertices_xyz=[checks.predict_godot_world_for_identity(v)for v in p['vertices_xyz']],local_vertices_blender=[checks.predict_blender_local_from_godot(v)for v in p['vertices_xyz']],matrix_world_blender=copy.deepcopy(checks.IDENTITY_4),faces=p['faces'],evaluated_triangles=[],uv_loops=[[.123456789,.5]],material_indices=[0]*len(p['faces']),material_states=[dict(role=p['material_role'],packed_test_hash='unchanged')],source_transform=dict(location=[0.,0.,0.],rotation_euler=[0.,0.,0.],scale=[1.,1.,1.])))
positive=checks.compare_reopened_parts(rows,copy.deepcopy(rows));conversion=checks.verify_core_plan_conversion(rows,plan['parts']);assert all(p['plan_already_float32']for p in conversion)
controls=[]
def reject(label,callback):
    try:callback()
    except AssertionError:controls.append(dict(name=label,rejected=True))
    else:raise AssertionError('Negative control accepted: '+label)
for field in checks.EXACT_FIELDS:
    changed=copy.deepcopy(rows);changed[0][field]=['CHANGED']
    reject('changed_'+field,lambda a=changed:checks.compare_reopened_parts(a,rows))
changed=copy.deepcopy(rows);changed[0]['matrix_world_blender'][0][3]=.00001
reject('unexpected_transform_not_hidden_by_epsilon',lambda:checks.verify_core_plan_conversion(changed,plan['parts']))
changed=copy.deepcopy(rows);changed[0]['vertices_xyz'][0][2]+=1e-9
reject('one_nanometre_value_change_is_not_tolerated',lambda:checks.compare_reopened_parts(changed,rows))
# The check must quantize ideal values explicitly, not compare them to a broad
# tolerance or accidentally treat large-world decimal input as native floats.
ideal=dict(name='ideal_world_test',vertices_xyz=[[-8.2,54.2,-450.99]])
fake=copy.deepcopy(rows[0]);fake['name']=ideal['name'];fake['local_vertices_blender']=[checks.predict_blender_local_from_godot(v)for v in ideal['vertices_xyz']];fake['vertices_xyz']=[checks.predict_godot_world_for_identity(v)for v in ideal['vertices_xyz']]
assert checks.verify_core_plan_conversion([fake],[ideal])[0]['plan_already_float32']is False
extra=copy.deepcopy(rows[0]);extra['name']='retained_programme_object';checks.compare_reopened_parts(rows+[extra],rows+[extra],part_names=[p['name']for p in rows]);checks.verify_core_plan_conversion(rows+[extra],plan['parts'])
report=dict(status='PASS_PURE_ROUNDTRIP_HELPER_TESTS',scope='Pure synthetic/canonical conversion tests only; no Blender source build or reopen executed',core_parts_checked=len(rows),core_vertices_checked=sum(len(p['vertices_xyz'])for p in rows),plan_explicitly_float32=True,exact_fields=list(checks.EXACT_FIELDS),negative_controls=controls,combined_subset_accepts_extra_retained_objects=True,identity_transform_contract_only=True,contact_safety_unchanged=True)
(S/'ROUNDTRIP_GATE_PURE_TESTS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
