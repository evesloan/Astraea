from pathlib import Path
import bpy,json,hashlib
W=Path(__file__).resolve().parent;R=W.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=json.load(open(W/'RUNTIME_PLAN.json'));pins={r['native']:sha(W/r['native'])for r in prior['native_export_records']}
s=(W/'build_native.py').read_text();exec(compile(s[:s.index("\nvariant=json")],'<reviewed immutable helper definitions>','exec'))
mats=start();add_parts(P['assemblies']['CombinedStructure'],mats);instances=[]
for group in ['NR','SR']:instances+=components(P['bindings'][group],'PA'+group+'_')
rec=export_native(bpy,W,R,'D04PortAftCombinedStructure_r002.blend','D04_PORT_AFT_COMBINEDSTRUCTURE_r002.glb');rec['source_instances']=instances
records=[r for r in prior['native_export_records']if r['export']!='D04_PORT_AFT_COMBINEDSTRUCTURE_r001.glb']+[rec]
P['combinedstructure_structure']={'model_file':rec['export'],'model_sha256':rec['export_sha256'],'mesh_count':rec['mesh_count'],'collision_policy':rec['collision_policy']};P['native_export_records']=records;P['model_pins']={r['export']:r['export_sha256']for r in records}
for f,h in pins.items():assert sha(W/f)==h,f
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
(W/'RUNTIME_PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(W/'CORE_NATIVE_REVISION002_CHECK.json').write_text(json.dumps({'status':'PASS_IMMUTABLE_REVISION','record':rec,'all23_native_revisions_retained':True,'prior22_native_sha256_unchanged':pins,'original_registered_sources_unchanged':True,'active':False},indent=2)+'\n');print('AFT_CORE_CORRECTION_EXPORTED_IMMUTABLY',flush=True)
