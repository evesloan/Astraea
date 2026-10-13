from pathlib import Path
import json,zipfile,hashlib
P=Path(__file__).parent;S=P/'import/Game';sha=lambda b:hashlib.sha256(b).hexdigest();assert json.loads((P/'IMPORT_RECEIPT.json').read_text())['status']=='PASS_TWO_MODEL_ISOLATED_IMPORT';key='scripts/group2_garden_quiet/package.gd';original=(S/key).read_bytes();new=original+b'\n'+(P/'current_receiving_adapter.gd').read_bytes();w={key:new,'docs/validation/g2_garden_quiet_receiving_20261013/OWNER_PACKAGE.gd.txt':original,'data/group2_garden_quiet/COMPONENTS_r002.json':(S/'data/group2_garden_quiet/COMPONENTS_r002.json').read_bytes()}
for q in S.rglob('*'):
 if q.is_file()and(q.suffix in ['.glb','.png','.import','.uid']or'.godot/imported'in str(q)):w[str(q.relative_to(S))]=q.read_bytes()
with zipfile.ZipFile(P/'CANDIDATE_OVERLAY.zip','w',zipfile.ZIP_DEFLATED,compresslevel=1)as z:
 for k,b in w.items():z.writestr(k,b)
(P/'CANDIDATE_RECEIPT.json').write_text(json.dumps({'status':'EXACT_R002_TWO_EXISTING_RECEIVER_CANDIDATE','source_script_sha256':sha(original),'consumer_sha256':sha(new),'source_body_guard_unchanged':new.startswith(original),'floor_added_m2':0,'capacity_credit':0,'service_operation':False,'fixtures':2,'source_pins':{k:sha(b)for k,b in w.items()if not k.startswith('.godot/')}},indent=2)+'\n');print('GARDEN_QUIET_CANDIDATE_READY',len(w),'paths')
