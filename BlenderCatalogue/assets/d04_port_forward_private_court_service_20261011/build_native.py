from pathlib import Path
import json,hashlib
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert json.load(open(W/'PREIMAGE_SUPPORT.json'))['status']=='PASS'
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
O=R/'BlenderCatalogue/assets/d04_port_forward_homes_first_20261010'
ns={'__file__':str(O/'build_native.py')};s=(O/'build_native.py').read_text();exec(s[:s.index('\nrecords=[];structure=[]')],ns);ns.update(W=W,R=R,P=P)
ns['add_parts'](P['fixed_parts']+P['successor_parts']+P['gate_parts'],ns['start']())
record=ns['export']('D04PrivateCourtServiceCandidate.blend','D04_PORT_FORWARD_PRIVATE_COURT_SERVICE_CANDIDATE_r001.glb')
P['model_pins']={record['export']:record['export_sha256']};P['native_export_records']=[record];P['structure']={'model_file':record['export'],'model_sha256':record['export_sha256'],'collision_policy':record['collision_policy']}
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
(W/'RUNTIME_PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(R/'Game/data/architecture/D04_PORT_FORWARD_PRIVATE_COURT_SERVICE_CANDIDATE.json').write_text(json.dumps(P,indent=2)+'\n')
(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps({'status':'PASS','blender_version':ns['bpy'].app.version_string,'records':[record],'protected_pins':len(P['source_pins']),'production_active':False},indent=2)+'\n');print('PRIVATE_COURT_NATIVE_PASS',record['mesh_count'])
