"""New scratch derivative: exactly56 cushion face/UV-loop reversals, no vertex change."""
from pathlib import Path
import bpy,json,hashlib,sys,copy
W=Path(__file__).resolve().parent;R=W.parents[1];D=R/'printed_materials001';P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section');sys.path.insert(0,str(P/'source/firstpass_001'));from firstpass_common import baseline_snapshot,compare_subset,mesh_record,digest
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_text())
old_report=D/'authored_preview001/BUILD_REPORT.json';build=read(old_report);old=Path(build['source']);assert sha(old)==build['sha256']=='54433eb9a9efba6509e79e783deaf9a5fe27c43d449ee63ad1e1bad257c2be72'
plan=read(W/'WINDING_REPAIR_PLAN.json');contract=read(W/'COURT_A_GEOMETRY_CONTRACT_WINDING_SUCCESSOR.json');assert sha(W/'COURT_A_GEOMETRY_CONTRACT_WINDING_SUCCESSOR.json')=='4f3d39cf85d9a16fb170699c1dc5c51ca5c0674c821f4f81d25613de94bc156b';assert plan['face_indices_to_reverse']==list(range(56))and plan['affected_object']=='A4_W_crowned_cushion'
out=W/'authored_source001';out.mkdir(exist_ok=False);target=out/contract['standalone_source_proposal'];assert not target.exists()
bpy.ops.wm.open_mainfile(filepath=str(old),use_scripts=False);before=baseline_snapshot(bpy);name=plan['affected_object'];ob=bpy.data.objects[name];me=ob.data;prior=mesh_record(me);expected=next(x for x in contract['objects']if x['name']==name)
assert digest(prior)==build['mesh_uv_fingerprints'][name]
faces=copy.deepcopy(prior['faces']);uvs=copy.deepcopy(prior['uvs'])
for i in plan['face_indices_to_reverse']:
 faces[i].reverse()
 for layer in uvs:uvs[layer][i].reverse()
assert faces==expected['faces'];assert uvs['MetricUV']==[[[float(__import__('struct').unpack('f',__import__('struct').pack('f',c))[0])for c in uv]for uv in face]for face in expected['face_uv']]
new=bpy.data.meshes.new(me.name+'_winding001');new.from_pydata(prior['vertices'],[],faces);new.update()
for material in me.materials:new.materials.append(material)
for i,poly in enumerate(new.polygons):poly.material_index=prior['face_materials'][i];poly.use_smooth=prior['smooth'][i]
for layer,face_uvs in uvs.items():
 uv=new.uv_layers.new(name=layer);uv.active_render=True
 for poly,coords in zip(new.polygons,face_uvs):
  for li,p in zip(poly.loop_indices,coords):uv.data[li].uv=p
ob.data=new;ob['closed_volume_m3']=expected['closed_volume_m3'];ob['source_winding_correction']='Only cap faces0–55 reversed, per-corner UV association retained'
after=baseline_snapshot(bpy);protected=copy.deepcopy(before);del protected['objects'][name];errors=compare_subset(protected,after);assert not errors,errors[:10]
actual=mesh_record(new);assert actual['vertices']==prior['vertices']and actual['materials']==prior['materials']and actual['face_materials']==prior['face_materials']and actual['smooth']==prior['smooth'];assert actual['faces']==faces and actual['uvs']==uvs
for i,face in enumerate(prior['faces']):
 for layer in prior['uvs']:assert sorted(zip(face,prior['uvs'][layer][i]))==sorted(zip(actual['faces'][i],actual['uvs'][layer][i]))
bpy.context.scene['court_A_winding_correction']='Source-only new derivative, preserved original54433eb9, exact56face correction';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
assert sha(old)==build['sha256']
result=copy.deepcopy(build);result.update(status='STANDALONE_SOURCE_WINDING_CORRECTED_REOPEN_PENDING',source=str(target),sha256=sha(target),previous_source=str(old),previous_source_sha256=sha(old),previous_build_report_sha256=sha(old_report),winding_repair_plan_sha256=sha(W/'WINDING_REPAIR_PLAN.json'),geometry_contract_sha256=sha(W/'COURT_A_GEOMETRY_CONTRACT_WINDING_SUCCESSOR.json'),preserved_non_target_snapshot=protected,only_face_winding_and_matching_uv_order_changed=True)
result['mesh_uv_fingerprints'][name]=digest(actual)
(out/'BUILD_REPORT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'source':str(target),'sha256':sha(target),'affected_object':name,'reversed_faces':56,'unchanged_vertices':len(new.vertices),'protected_objects':len(protected['objects']),'protected_materials':len(protected['materials'])}))
