from pathlib import Path
import bpy,bmesh,json,hashlib,sys
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
sys.path.insert(0,str(R/'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011'));from immutable_revision import export_native
import struct,tempfile
bpy.ops.wm.open_mainfile(filepath=str(W/'D04CommonsShortServiceTransitions_r001.blend'));stage=Path(tempfile.mkdtemp(prefix='astraea_short_native_readback_'));bpy.ops.export_scene.gltf(filepath=str(stage/'repeat.glb'),export_format='GLB',export_extras=True,use_selection=False,export_apply=True);raw=(W/P['commons_file']).read_bytes();assert raw==(stage/'repeat.glb').read_bytes()==(R/'Game/assets/models'/P['commons_file']).read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);policy={q['name'].replace('.','_'):{'collide':q.get('extras',{}).get('runtime_collision',True),'opaque':q.get('extras',{}).get('role','')not in['water','hospitality_glass'],'role':q.get('extras',{}).get('role',''),'category':q.get('extras',{}).get('category','')}for q in doc['nodes']if'mesh'in q};short={'native':'D04CommonsShortServiceTransitions_r001.blend','native_sha256':sha(W/'D04CommonsShortServiceTransitions_r001.blend'),'export':P['commons_file'],'export_sha256':sha(W/P['commons_file']),'mesh_count':len(policy),'collision_policy':policy,'fresh_native_repeat_identical':True,'immutable_revision':True,'disposable_repeat_export_staging':str(stage)};P['commons_structure']=short;
bpy.ops.wm.read_factory_settings(use_empty=True);mapping=[]
source_dir=R/'BlenderCatalogue/assets/d04_private_court_controls_and_staff_approach_20261011';phys_dir=R/'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011'
specs=[(source_dir/'D04StaffCourtApproachSealed_r002.blend',set(P['fore_models']['structure']['collision_policy'])-{'D04SA_ServiceLaneScreen_0','D04SA_ServiceLaneScreen_2'}),(source_dir/'D04CourtGateControls_r003.blend',set(P['fore_models']['court']['collision_policy'])),(phys_dir/'D04BoundedPhysicalCuts_r010.blend',set(P['fore_patch_names'])),(phys_dir/'D04PhysicalFittings_r010.blend',set(P['fore_owned_names']))]
def payload(ob):return {'verts':[list(v.co)for v in ob.data.vertices],'faces':[list(q.vertices)for q in ob.data.polygons],'uvs':[[list(v.uv)for v in layer.data]for layer in ob.data.uv_layers],'materials':[m.name for m in ob.data.materials],'world_matrix':[list(v)for v in ob.matrix_world]}
for source,names in specs:
 with bpy.data.libraries.load(str(source),link=False)as(src,dst):dst.objects=src.objects
 matched=set()
 for ob in dst.objects:
  if not ob:continue
  key=ob.name.replace('.','_')
  if key in names:
   assert ob.type=='MESH';pose=ob.matrix_world.copy();before=payload(ob);ob.parent=None;ob.matrix_world=pose;bpy.context.collection.objects.link(ob);mapping.append({'name':ob.name,'normalized_name':key,'native_source':str(source.relative_to(R)),'native_sha256':sha(source),'payload_sha256':hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest(),'payload':before});matched.add(key)
 for ob in dst.objects:
  if ob and ob.name.replace('.','_')not in matched:bpy.data.objects.remove(ob,do_unlink=True)
 assert matched==names,(source,names-matched)
fore=export_native(bpy,W,R,'D04PortForwardStaffCourtConnection_r001.blend','D04_PORT_FORWARD_STAFF_COURT_CONNECTION_r001.glb');P['fore_structure']=fore;P['native_export_records']=[short,fore];P['model_pins']={q['export']:q['export_sha256']for q in P['native_export_records']};P['fore_source_mesh_mappings']=[{k:v for k,v in q.items()if k!='payload'}for q in mapping];P['fore_selected_mesh_count']=len(mapping)
bpy.ops.wm.open_mainfile(filepath=str(W/fore['native']))
for q in mapping:assert payload(bpy.data.objects[q['name']])==q['payload'],q['name']
for f,h in P['source_protected_native_exports'].items():assert sha(R/f)==h,f
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
(W/'EXACT_NATIVE_SOURCE_AUDIT.json').write_text(json.dumps({'status':'PASS','fore_selected_meshes_exact_local_geometry_UVs_materials_world_pose':len(mapping),'new_short_profiles':3,'old_gate_geometry_scaled':False,'old4333_native_export_files_unchanged':True,'native_records':P['native_export_records']},indent=2)+'\n')
for f in [W/'PLAN.json',W/'RUNTIME_PLAN.json',R/'Game/data/architecture/D04_COMMONS_TRANSITION_AND_FORE_STAFF.json']:f.write_text(json.dumps(P,indent=2)+'\n')
print('Distinct short profiles and exact selected fore native assembly saved',len(mapping))
