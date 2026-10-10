from pathlib import Path
import subprocess,json,hashlib
W=Path(__file__).resolve().parent;R=W.parents[2];base='489141f0afcabbdd33f24a81caeb1a9486794ee2';filename='Game/data/architecture/STAR_ATLAS_SPECIALTY_THIRD.json';raw=subprocess.check_output(['git','show',base+':'+filename],cwd=R);before=json.loads(raw);after=json.load(open(R/filename));a=json.loads(json.dumps(before));b=json.loads(json.dumps(after))
for p in [a,b]:
 for room in p['rooms']:
  for k in ['model_file','model_sha256','mesh_count']:room.pop(k)
 for record in p['native_export_records']:
  for k in ['native','native_sha256','export','export_sha256','mesh_count']:record.pop(k)
assert a==b
changed=subprocess.check_output(['git','diff','--name-only',base],cwd=R).decode().splitlines();assert set(changed)<=set([filename,'CHECKPOINT.json','BACKUP_STATUS.json'])
for f in ['Game/data/architecture/STAR_ATLAS_SPECIALTY_FOURTH.json','Game/scripts/star_atlas_specialty_fourth.gd','Game/assets/models/StarAtlasSpecialtyFourthReceiving.glb']:
 assert (R/f).read_bytes()==subprocess.check_output(['git','show',base+':'+f],cwd=R)
p=W/'ACTUAL_SOURCE_CHECK.json';q=json.load(open(p));q.update(runtime_binding_before_sha256=hashlib.sha256(raw).hexdigest(),runtime_binding_after_sha256=hashlib.sha256((R/filename).read_bytes()).hexdigest(),only_model_and_native_export_record_keys_changed=True,fourth_binding_script_receiving_model_unchanged=True,construction_candidates_added=0);p.write_text(json.dumps(q,indent=2)+'\n');print('PASS precise runtime binding scope and retained fourth-batch integration')
