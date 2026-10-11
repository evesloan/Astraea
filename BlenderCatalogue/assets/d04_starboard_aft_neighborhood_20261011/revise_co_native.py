from pathlib import Path
import bpy,json,hashlib
W=Path(__file__).resolve().parent;R=W.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();prior=json.load(open(W/'RUNTIME_PLAN.json'));pins={r['native']:sha(W/r['native'])for r in prior['native_export_records']}
s=(W/'build_native.py').read_text();exec(compile(s[:s.index("\nrecords=[]")],'<reviewed immutable native helper definitions>','exec'))
mats=start();add_parts(P['assemblies']['CO'],mats);instances=components(P['bindings']['CO'],'SAC_');rec=export_native(bpy,W,R,'D04StarboardAftCO_r002.blend','D04_STARBOARD_AFT_CO_r002.glb');rec['source_instances']=instances;records=[r for r in prior['native_export_records']if r['export']!='D04_STARBOARD_AFT_CO_r001.glb']+[rec]
P['co_structure']={'model_file':rec['export'],'model_sha256':rec['export_sha256'],'mesh_count':rec['mesh_count'],'collision_policy':rec['collision_policy']}
for name in P['stair_detailed_contact_replacements']:assert name in P['co_structure']['collision_policy']and P['co_structure']['collision_policy'][name]['collide'];P['co_structure']['collision_policy'][name]['collide']=False
P['native_export_records']=records;P['model_pins']={r['export']:r['export_sha256']for r in records}
for f,h in pins.items():assert sha(W/f)==h,f
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
for f in [W/'PLAN.json',W/'RUNTIME_PLAN.json',R/'Game/data/architecture/D04_STARBOARD_AFT_NEIGHBORHOOD.json']:f.write_text(json.dumps(P,indent=2)+'\n')
(W/'ENCLOSURE_NATIVE_REVISION002_CHECK.json').write_text(json.dumps({'status':'PASS_IMMUTABLE_REVISION','record':rec,'all23_native_revisions_retained':True,'prior22_native_sha256_unchanged':pins,'original_registered_sources_unchanged':True,'active':False},indent=2)+'\n');print('STARBOARD_AFT_ENCLOSURE_CORRECTION_EXPORTED_IMMUTABLY',flush=True)
