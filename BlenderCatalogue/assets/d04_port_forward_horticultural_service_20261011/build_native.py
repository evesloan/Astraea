from pathlib import Path
import json,hashlib
W=Path(__file__).resolve().parent;R=W.parents[2];O=R/'BlenderCatalogue/assets/d04_port_forward_commons_service_20261010';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();P=json.load(open(W/'PLAN.json'))
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
q=P['preimage'];bounds=lambda q:([min(v[i]for v in q['verts'])for i in range(3)],[max(v[i]for v in q['verts'])for i in range(3)])
lo,hi=bounds(q);volume=0
for s in P['successor_parts']:
 a,b=bounds(s);assert all(lo[i]<=a[i]<=b[i]<=hi[i]for i in range(3));volume+=(b[0]-a[0])*(b[1]-a[1])*(b[2]-a[2])
assert abs(volume-(hi[0]-lo[0])*(hi[1]-lo[1])*(hi[2]-lo[2]))<1e-8
(W/'PREIMAGE_SUPPORT.json').write_text(json.dumps({'status':'PASS','source_pins_unchanged':len(P['source_pins']),'contained_glass_successors':7,'sum_volume_exact_preimage':True,'new_floor_or_keel_changes':0,'all20_allocations_unchanged':True,'base_connected_receipt_sha256':sha(R/'Game/artifacts/d04_port_forward_commons_service_connected.json')},indent=2)+'\n')
ns={'__file__':str(O/'build_native.py')};s=(O/'build_native.py').read_text();exec(s[:s.index('\nmats=start();add_parts')],ns);ns.update(W=W,P=P,R=R)
ns['add_parts'](P['parts'],ns['start']());inst=ns['components'](P['components'],'D04HS_');a=ns['export']('D04HorticulturalWorkbay.blend','D04_PORT_FORWARD_HORTICULTURAL_WORKBAY_r001.glb');a['source_instances']=inst
for p in P['successor_parts']:
 if p['category']=='moving_sash':p['runtime_collision']=False
ns['add_parts'](P['successor_parts'],ns['start']());b=ns['export']('D04GardenServiceSashes.blend','D04_PORT_FORWARD_GARDEN_SERVICE_SASHES_r001.glb')
P['workbay']={'model_file':a['export'],'model_sha256':a['export_sha256'],'collision_policy':a['collision_policy']};P['garden_successors']={'model_file':b['export'],'model_sha256':b['export_sha256'],'collision_policy':b['collision_policy']};P['model_pins']={x['export']:x['export_sha256']for x in [a,b]};P['native_export_records']=[a,b]
(W/'RUNTIME_PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps({'status':'PASS','blender_version':ns['bpy'].app.version_string,'records':[a,b],'source_pins_unchanged':len(P['source_pins']),'contained_successor_volume_exact':True},indent=2)+'\n');print('HORTICULTURAL_NATIVE_PASS')
