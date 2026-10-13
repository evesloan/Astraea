from pathlib import Path
import json,hashlib,zipfile
P=Path(__file__).parent;S=P/'import/Game';sha=lambda b:hashlib.sha256(b).hexdigest();assert json.loads((P/'IMPORT_RECEIPT.json').read_text())['status']=='PASS_ONE_NEW_CHILDCARE_MODEL_ISOLATED_IMPORT';key='scripts/group2_family_childcare/package.gd';original=(S/key).read_bytes();adapter=(P/'current_receiving_adapter.gd').read_text();lines=[]
for line in adapter.splitlines():
 n=len(line)-len(line.lstrip(' '));lines.append('\t'*n+line[n:])
new=original+b'\n'+('\n'.join(lines)+'\n').encode();w={key:new,'scripts/group2_family_childcare/entry.gd':(S/'scripts/group2_family_childcare/entry.gd').read_bytes(),'docs/validation/g2_childcare_physical_20261013/OWNER_PACKAGE.gd.txt':original,'data/group2_family_childcare/COMPONENT_r001.json':(S/'data/group2_family_childcare/COMPONENT_r001.json').read_bytes()}
for q in (S/'assets').rglob('*'):
 if q.is_file():w[str(q.relative_to(S))]=q.read_bytes()
for q in (S/'.godot/imported').iterdir():
 if q.is_file():w[str(q.relative_to(S))]=q.read_bytes()
for q in (S/'scripts/group2_family_childcare').glob('*.uid'):w[str(q.relative_to(S))]=q.read_bytes()
with zipfile.ZipFile(P/'CANDIDATE_OVERLAY.zip','w',zipfile.ZIP_DEFLATED,compresslevel=1)as z:
 for k,b in w.items():z.writestr(k,b)
(P/'CANDIDATE_RECEIPT.json').write_text(json.dumps({'status':'EXACT_PHYSICAL_CHILDCARE_CANDIDATE_ONLY','source_body_and_fixture_guard_unchanged':new.startswith(original),'source_script_sha256':sha(original),'consumer_sha256':sha(new),'new_model':1,'existing_wide_door':'Raw authored closed default fitting,no backend','fixtures':4,'floor_added_m2':0,'new_registry_rooms_beds_or_capacity':0,'admission_supervision_or_entry_operations_accepted':False,'source_pins':{k:sha(b)for k,b in w.items()if not k.startswith('.godot/')}},indent=2)+'\n');print('CHILDCARE_PHYSICAL_CANDIDATE_READY',len(w),'paths')
