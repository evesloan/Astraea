"""Prepare one immutable capture input freeze after all three root-owned focused gates pass."""
from pathlib import Path
import json,hashlib,argparse,datetime,subprocess
B=Path(__file__).resolve().parent;BASE=B.parent
ap=argparse.ArgumentParser();ap.add_argument('--game',default='/workspace/shared/Astraea_recovery_20261007_AXWr5x/Game');ap.add_argument('--architecture-receipt',required=True);ap.add_argument('--lighting-receipt',required=True);ap.add_argument('--access-receipt',required=True);args=ap.parse_args();G=Path(args.game).resolve();OUT=B/'FINAL_CURRENT_FREEZE.json';assert not OUT.exists(),'Preserve every existing freeze/capture attempt'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipts={}
for label,p in [('grand_pool_architecture',Path(args.architecture_receipt)),('lighting_budget',Path(args.lighting_receipt)),('grand_pool_access',Path(args.access_receipt))]:
 d=json.loads(p.read_text());assert all(r['passed'] and r['exit_code']==0 and not r['errors'] for r in d['checks']),p;assert len([r for r in d['checks']if r['check']==label])==1,p;receipts[label]={'path':str(p.resolve()),'sha256':sha(p),'checks':d['checks']}
inputs={};cache={}
for p in sorted(G.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(G)
 if rel.parts[0]in['.git','artifacts']:continue
 if rel.parts[0]=='.godot':
  if len(rel.parts)>1 and rel.parts[1]=='imported':cache[str(rel)]=sha(p)
 else:inputs[str(rel)]=sha(p)
contract=json.loads((G/'data/architecture/GRAND_POOL_EAST_GALLERY_RUNTIME.json').read_text())
for a in contract['models'].values():assert inputs['assets/models/'+a['file']]==a['sha256']
proof=json.loads((G/'docs/GRAND_POOL_CONNECTED_FINISH_SUCCESSOR.json').read_text())
for rel,row in proof['files'].items():assert inputs[rel]==row['after_sha256']
for rel,h in proof['required_new_files'].items():assert inputs[rel]==h
state=Path('/workspace/shared/Astraea_backup_session_20261007_kTSSf7/state.json');backup=json.loads(state.read_text());assert backup['status']=='healthy'
freeze={'status':'PINNED_CURRENT_INSTALLED_INPUTS_AFTER_THREE_FOCUSED_PASSES','prepared_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'game_root':str(G),'game_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=G,text=True).strip(),'prepared_files':{'capture.gd':sha(B/'capture.gd'),'write_freeze.py':sha(Path(__file__)),'run_capture.py':sha(B/'run_capture.py')},'focused_receipt_sha256':receipts['grand_pool_architecture']['sha256'],'required_focused_receipts':receipts,'game_inputs':inputs,'import_cache_inputs':cache,'game_input_count':len(inputs),'import_cache_input_count':len(cache),'backup_state_at_preparation':{'path':str(state),'sha256':sha(state),'remote_commit':backup['remote_commit'],'verified_utc':backup['verified_utc']},'output_directory_must_be_absent':str(B/'output'),'capture_policy':'Same three prior normal/effects-off camera poses; natural source selection only; unsaved original-material/outside-floor parity comparison restores current material; no source save/import','native_visual_acceptance':False}
assert not (B/'output').exists();OUT.write_text(json.dumps(freeze,indent=2)+'\n');print('CAPTURE_FREEZE_READY',OUT,sha(OUT),len(inputs),len(cache))
