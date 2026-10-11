from pathlib import Path
import json,hashlib
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert json.load(open(W/'PREIMAGE_SUPPORT.json'))['status']=='PASS'
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
F=R/'BlenderCatalogue/assets/d04_port_forward_homes_first_20261010';ns={'__file__':str(F/'build_native.py')};s=(F/'build_native.py').read_text();exec(s[:s.index('\nrecords=[];structure=[]')],ns);ns.update(W=W,R=R,P=P);ns['add_parts'](P['parts'],ns['start']())
# Reuse the already reviewed original source-stair append policy without its
# later wall cutter or source assembly. The rigid4.5m stair is not rescaled.
O=R/'BlenderCatalogue/assets/d04_port_forward_receiving_20261010';s=(O/'build_source.py').read_text();a=s.index('def append_source');b=s.index('\nappend_source({**P');ns['instances']=[];exec(s[a:b],ns);ns['append_source']({**P['stair'],'prefix':'D04SA_Stair'},True)
record=ns['export']('D04StaffCourtApproachSealed.blend','D04_STAFF_COURT_APPROACH_SEALED_r001.glb');record['source_instances']=ns['instances'];P['model_pins']={record['export']:record['export_sha256']};P['native_export_records']=[record];P['structure']={'model_file':record['export'],'model_sha256':record['export_sha256'],'collision_policy':record['collision_policy']}
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
(W/'RUNTIME_PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(R/'Game/data/architecture/D04_STAFF_COURT_APPROACH_SEALED.json').write_text(json.dumps(P,indent=2)+'\n');(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps({'status':'PASS','blender_version':ns['bpy'].app.version_string,'records':[record],'production_active':False},indent=2)+'\n');print('STAFF_APPROACH_NATIVE_PASS',record['mesh_count'])
