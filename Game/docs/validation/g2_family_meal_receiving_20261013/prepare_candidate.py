from pathlib import Path
import json,hashlib,zipfile
P=Path(__file__).parent;S=P/'import/Game';sha=lambda b:hashlib.sha256(b).hexdigest();assert json.loads((P/'IMPORT_RECEIPT.json').read_text())['status']=='PASS_ONE_MODEL_ISOLATED_IMPORT';key='scripts/group2_family_meal/package.gd';original=(S/key).read_bytes();adapter=(P/'current_receiving_adapter.gd').read_text();lines=[]
for line in adapter.splitlines():
 n=len(line)-len(line.lstrip(' '));lines.append('\t'*n+line[n:])
new=original+b'\n'+('\n'.join(lines)+'\n').encode();w={key:new,'docs/validation/g2_family_meal_receiving_20261013/OWNER_PACKAGE.gd.txt':original}
for p in (S/'data/group2_family_meal').iterdir():
 if p.is_file():w[str(p.relative_to(S))]=p.read_bytes()
for q in S.rglob('*'):
 if q.is_file()and(q.suffix in ['.glb','.png','.import','.uid']or'.godot/imported'in str(q)):w[str(q.relative_to(S))]=q.read_bytes()
with zipfile.ZipFile(P/'CANDIDATE_OVERLAY.zip','w',zipfile.ZIP_DEFLATED,compresslevel=1)as z:
 for k,b in w.items():z.writestr(k,b)
(P/'CANDIDATE_RECEIPT.json').write_text(json.dumps({'status':'EXACT_FAMILY_MEAL_CURRENT_TABLE_CANDIDATE','source_body_and_fixture_guard_unchanged':new.startswith(original),'source_script_sha256':sha(original),'consumer_sha256':sha(new),'model_sha256':sha((S/'assets/group2_family_meal/FAMILY_MEAL_FITTINGS_r001.glb').read_bytes()),'settings':12,'old_tables':3,'new_chairs_floor_or_capacity':0,'food_or_service_or_dining_programme_admitted':False,'source_pins':{k:sha(b)for k,b in w.items()if not k.startswith('.godot/')}},indent=2)+'\n');print('FAMILY_MEAL_CANDIDATE_READY',len(w),'paths')
