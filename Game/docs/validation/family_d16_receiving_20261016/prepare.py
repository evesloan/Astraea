from pathlib import Path
import json,hashlib,shutil
R=Path('/workspace/Astraea');E=Path('/workspace/family-d16-integration');D=R/'BlenderCatalogue/assets/family_d16_staff_receiving_20261016';assert not D.exists();D.mkdir();prior=R/'BlenderCatalogue/assets/family_d15_staff_receiving_20261016';p=json.load(open(prior/'PLAN.json'));p['base_commit']='e1ce100298c4c3458d0ddfe7b2203974e76f3bf0';p['floor_y']=97.5;p['walls']=[r for r in json.load(open(E/'RUNTIME_PREIMAGES.json'))if r['owner']=='house'];p['revision_reason']='Family D16 staff receiving through the existing native fore lobby opening; preserve all Family D13–D15, Quiet D13–D16 and approved D17 sources.';p['derivation']='Rigid +4.5m Y and Z-reflected derivative of the44 inactive Quiet D15 r001 architectural components; new source-verified joints, proper rigid fixture assemblies, sockets and aperture finishes.'
for v in p['protected_endpoints'].values():v['owner']=v['owner'].replace('D15','D16');v['y']=97.5
for f in ['Game/assets/family_d15_receiving_20261016/FAMILY_D15_STAFF_RECEIVING_r001.glb','Game/scripts/family_d15_receiving_20261016/package.gd','Game/data/family_d15_receiving_20261016/RECEIPT.json','Game/assets/models/D17_STARBOARD_STANDARD_FRAME_r002.glb','Game/scripts/d17_starboard_standard_20261019/package.gd','Game/data/architecture/D17_STARBOARD_STANDARD_CANDIDATE_20261019.json']:p['source_pins'][f]=hashlib.sha256((R/f).read_bytes()).hexdigest()
for f,h in p['source_pins'].items():assert hashlib.sha256((R/f).read_bytes()).hexdigest()==h,f
(D/'PLAN.json').write_text(json.dumps(p,indent=2)+'\n')
for name in ['build.py','verify_native.py']:
 s=(prior/name).read_text().replace('family-d15','family-d16').replace('FAMILY_D15','FAMILY_D16').replace('FamilyD15','FamilyD16').replace('F15_','F16_').replace('(0,0,0)','(0,0,4.5)').replace('(x,95.1,483.9)','(x,99.6,483.9)');(D/name).write_text(s)
for name in ['NATIVE_SURVEY.json','NATIVE_WALL_SURVEY.json','RUNTIME_PREIMAGES.json','LOBBY_HEADER_PREIMAGE.json']:shutil.copy2(E/name,D/name)
shutil.copy2(prior/'REOPENED_MASTER_CHAPTERS.json',D/'REOPENED_MASTER_CHAPTERS.json')
for name in ['verify_patch.py','verify_uv.py']:(E/name).write_text(Path('/workspace/family-d15-integration/'+name).read_text().replace('family_d15_staff_receiving_20261016','family_d16_staff_receiving_20261016'))
print('D16 source preimages and preserved sources verified')
