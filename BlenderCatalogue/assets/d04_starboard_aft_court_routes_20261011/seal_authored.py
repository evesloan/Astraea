from pathlib import Path
import json,hashlib
W=Path(__file__).resolve().parent;R=W.parents[2];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();P=json.load(open(W/'PLAN.json'));g=R/'Game/artifacts/d04_starboard_aft_court_routes_geometry.json';q=json.load(open(g));assert q['status']=='PASS'and q['model_pins']==P['model_pins'];assert not P['active'];assert json.load(open(W/'SOURCE_VISUAL_REVIEW001.json'))['status']=='PARTIAL_SOURCE_DIAGNOSTICS_REVIEWED';P['sealed_receipt_sha256']=sha(g)
files=['Game/artifacts/d04_starboard_aft_court_routes_geometry.json','Game/data/architecture/D04_STARBOARD_AFT_COURT_ROUTES.json','Game/scripts/d04_starboard_aft_court_routes.gd','Game/tests/validate_d04_starboard_aft_court_routes_geometry.gd','Game/tests/validate_d04_starboard_aft_court_routes_connection.gd']
P['phase_evidence']['authored']=sorted({str(f.relative_to(R))for f in W.iterdir()if f.is_file()}|set(files)|{str(f.relative_to(R))for f in (R/'Game/assets/models').glob('D04_STARBOARD_AFT_COURT_*')})
for f in [W/'PLAN.json',W/'RUNTIME_PLAN.json',R/'Game/data/architecture/D04_STARBOARD_AFT_COURT_ROUTES.json']:f.write_text(json.dumps(P,indent=2)+'\n')
print('Verified inactive geometry sealed',q['checks'],P['sealed_receipt_sha256'])
