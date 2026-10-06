"""Independent fresh-process source reopen. No source save/export/render."""
import bpy,json,hashlib,math,importlib.util
from pathlib import Path
S=Path(__file__).resolve().parent;OUT=S/'build001';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
receipt=json.loads((OUT/'qa/BUILD_RECEIPT.json').read_text());assert receipt['build_script_sha256']==sha(S/'build_core.py')
sp=importlib.util.spec_from_file_location('core_build_helpers',S/'build_core.py');helper=importlib.util.module_from_spec(sp);sp.loader.exec_module(helper)
path=Path(receipt['source']);assert sha(path)==receipt['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene;scene.view_layers[0].update();plan=json.loads((S/'CORE_PLAN.json').read_text());assert sha(S/'CORE_PLAN.json')==receipt['plan_sha256']
actual=helper.snapshot(scene,plan);expected={p['name']:p for p in plan['parts']};checks=[]
for p in actual:
    ob=scene.objects[p['name']];r=expected[p['name']];assert not ob.modifiers and not ob.constraints and ob.parent is None;assert ob.location.length<1e-9 and ob.rotation_euler.to_quaternion().angle<1e-9 and all(abs(x-1)<1e-9 for x in ob.scale)
    assert len(ob.data.materials)==1 and len(ob.data.uv_layers)==1;assert helper.mat_state(ob.data.materials[0])==receipt['material_provenance'][p['material_role']]['material_state'];assert ob['parent_design_id']=='AST-AQU-016'and not ob['new_floor_owner'];assert json.loads(ob['support_json'])==r['support']
    deviation=max(math.dist(a,b)for a,b in zip(p['vertices_xyz'],r['vertices_xyz']));assert deviation<1e-8,(p['name'],deviation);checks.append(dict(name=p['name'],max_vertex_deviation_m=deviation,closed=True,positive_volume_m3=p['signed_volume_m3'],minimum_triangle_area_m2=p['minimum_triangle_area_m2'],minimum_uv_area=p['minimum_uv_area'],retained_packed_material_unchanged=True))
meshes=[o for o in scene.objects if o.type=='MESH'];assert len(meshes)==len(expected);assert len([o for o in scene.objects if o.type=='EMPTY'])==5;assert not [o for o in scene.objects if o.type=='LIGHT'];assert sha(path)==receipt['source_sha256']
for p,h in receipt['input_sha256'].items():assert sha(p)==h,p
out=OUT/'qa/INDEPENDENT_REOPEN.json';assert not out.exists();actualpath=OUT/'qa/ACTUAL_CORE_PLAN.json';assert not actualpath.exists();actualpath.write_text(json.dumps(dict(plan,parts=actual,status='INDEPENDENTLY_REOPENED_CORE_SOURCE'),indent=2)+'\n');out.write_text(json.dumps(dict(status='PASS_INDEPENDENT_CORE_REOPEN',source=str(path),source_sha256=sha(path),source_unchanged=True,plan_sha256=receipt['plan_sha256'],actual_plan_sha256=sha(actualpath),checks=checks,limitations=['Core only; no retained programme, source composition or native integration acceptance.','Run the same pure solid/contact/route review over this actual reopened plan.']),indent=2)+'\n');print('PASS_INDEPENDENT_CORE_REOPEN',len(checks),'source objects; no source save/export/render')
