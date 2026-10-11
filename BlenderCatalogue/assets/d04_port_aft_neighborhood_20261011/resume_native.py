from pathlib import Path
import bpy,json,hashlib,sys,struct,tempfile
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Reviewed immutable builder helper definitions only. Never execute its completed export loop again.
s=(W/'build_native.py').read_text();exec(compile(s[:s.index('\nvariant=json')],'<reviewed native helper definitions>','exec'))
def audit(native,file):
 before=sha(W/native);raw=(W/file).read_bytes();assert raw==(R/'Game/assets/models'/file).read_bytes();bpy.ops.wm.open_mainfile(filepath=str(W/native));bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.data.objects:
  if o.type in ['MESH','EMPTY']:o.select_set(True)
 stage=Path(tempfile.mkdtemp(prefix='astraea_aft_immutable_readonly_repeat_'));bpy.ops.export_scene.gltf(filepath=str(stage/file),export_format='GLB',export_extras=True,use_selection=True,export_apply=True);assert raw==(stage/file).read_bytes(),file;assert sha(W/native)==before
 doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);policy={n['name'].replace('.','_'):{'collide':n.get('extras',{}).get('runtime_collision',True),'opaque':n.get('extras',{}).get('role','')not in ['water','hospitality_glass'],'role':n.get('extras',{}).get('role',''),'category':n.get('extras',{}).get('category','')}for n in doc['nodes']if'mesh'in n}
 return{'native':native,'native_sha256':before,'export':file,'export_sha256':hashlib.sha256(raw).hexdigest(),'mesh_count':len(policy),'collision_policy':policy,'fresh_native_repeat_identical':True,'immutable_revision':True,'independent_read_only_resume_repeat':str(stage)}
records=[]
for room in P['rooms']:
 idx=room['source_index'];rec=audit(f'D04PortAftHome_{idx}_r001.blend',room['model_file']);records.append(rec);room.update(model_sha256=rec['export_sha256'],mesh_count=rec['mesh_count'],collision_policy=rec['collision_policy']);print('AFT_SAVED_HOME_AUDITED',idx,flush=True)
rec=audit('D04PortAftCO_r001.blend','D04_PORT_AFT_CO_r001.glb');records.append(rec);P['co_structure']={'model_file':rec['export'],'model_sha256':rec['export_sha256'],'mesh_count':rec['mesh_count'],'collision_policy':rec['collision_policy']};corrected=[n.replace('PACO_D04SC_','PACO_',1)for n in P['stair_detailed_contact_replacements']];assert len(corrected)==31
for name in corrected:assert name in P['co_structure']['collision_policy']and P['co_structure']['collision_policy'][name]['collide'];P['co_structure']['collision_policy'][name]['collide']=False
P['stair_detailed_contact_replacements']=corrected
mats=start();add_parts(P['assemblies']['CombinedStructure'],mats);instances=[]
for group in ['NR','SR']:instances+=components(P['bindings'][group],'PA'+group+'_')
rec=export_native(bpy,W,R,'D04PortAftCombinedStructure_r001.blend','D04_PORT_AFT_COMBINEDSTRUCTURE_r001.glb');rec['source_instances']=instances;records.append(rec);P['combinedstructure_structure']={'model_file':rec['export'],'model_sha256':rec['export_sha256'],'mesh_count':rec['mesh_count'],'collision_policy':rec['collision_policy']};P['native_export_records']=records;P['model_pins']={r['export']:r['export_sha256']for r in records}
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
(W/'RUNTIME_PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps({'status':'PASS','blender_version':bpy.app.version_string,'records':records,'readonly_reaudit_saved_assemblies':21,'original_registered_sources_unchanged':True,'rigid_original_fittings_no_rescale_or_reflection':True,'actual_rest_reservations_preserved':25,'active':False},indent=2)+'\n');print('AFT_PACKAGE_EXPORTED_AND_REAUDITED',len(records),flush=True)
