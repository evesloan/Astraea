"""Bind completed pictures from a metadata-rejected run without rewriting that run."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent;RUN=D/'r01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
r=load(RUN/'render_evidence.json');plan=load(D/'plan.json');assert r['execution_complete'] is False and len(r['views'])==4
assert sha(D/'build_inspection.py')==r['executed_script_sha256'] and sha(D/'plan.json')==r['plan_sha256']
changes=[];bindings=[]
for row in r['items']:
 src=next(x for x in plan['items'] if x['key']==row['key'].removesuffix('_alternative'))
 assert sha(R/row['export'])==row['export_sha256'];bindings.append({'path':row['export'],'sha256':row['export_sha256']})
 for key,h in row['base_hashes'].items():
  p=R/src[key]
  if sha(p)==h:bindings.append({'path':src[key],'sha256':h});continue
  assert key=='manifest_path' and src['asset_id'] in ['AST-CRW-001','AST-CRW-002']
  snapshot=RUN/'captured_manifests'/(src['key']+'.json');assert sha(snapshot)==h
  old=load(snapshot);new=load(p);diff=[k for k in old.keys()|new.keys() if old.get(k)!=new.get(k)];assert diff==['generator_sha256'],diff
  changes.append({'path':src[key],'captured_sha256':h,'current_sha256':sha(p),'captured_snapshot':str(snapshot.relative_to(R)),'changed_keys':diff,'old_generator_sha256':old['generator_sha256'],'current_generator_sha256':new['generator_sha256']})
images=[]
for name,v in r['views'].items():
 p=RUN/(name+'.png');assert sha(p)==v['image_sha256'];images.append({'path':str(p.relative_to(R)),'sha256':sha(p)})
assert changes and all(x['passed'] for x in r['empty_space_checks'])
record={'passed':True,'scope':'All four actual pictures and geometric checks completed; original run then rejected metadata drift. This separate record credits only unchanged rendered sources/exports and the explicitly inspected metadata bridge. It does not rewrite or erase the failed final hash guard.','original_run_completed':False,'original_rejection':'001/002 manifest generator_sha256 changed with collision-only generator metadata amendments during render','original_evidence':{'path':str((RUN/'render_evidence.json').relative_to(R)),'sha256':sha(RUN/'render_evidence.json')},'geometry_and_sources_unchanged':bindings,'manifest_amendments':changes,'images':images,'author_collision_revision':{'path':'assets/crew_rest/qa/collision_metadata_revision.json','sha256':sha(R/'assets/crew_rest/qa/collision_metadata_revision.json')},'no_rerender_required_for_visible_geometry':True,'final_collision_rebuild_acceptance':'Separate independent final review required'}
(D/'captured_geometry_metadata_bridge.json').write_text(json.dumps(record,indent=2)+'\n');print('CAPTURE_GEOMETRY_METADATA_BRIDGE_PASS')
