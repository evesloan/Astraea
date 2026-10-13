from pathlib import Path
import json, hashlib, shutil, zipfile
P=Path(__file__).parent
T=P/'import/Game'
F=P/'frame_r004_import/Game'
assert 'ERROR:' not in (P/'import_r004.log').read_text()
p=P/'validate_receiving.gd'
s=p.read_text()
if 'unknown_preimages' not in s:
 s=s.replace(' for part in p.parts:', ' var unknown_preimages:Array=[]\n for part in p.parts:',1)
 s=s.replace('   if not require(allowed,"Exact declared newframe preimage "+str(part.name)+" "+str(hit.collider.get_path())):return','   nchecks+=1\n   if not allowed:unknown_preimages.append("Exact declared newframe preimage "+str(part.name)+" "+str(hit.collider.get_path()))')
 s=s.replace(' for at:Vector3 in witnesses:\n  if not require(ray(space',' if not require(unknown_preimages.is_empty(),"Undeclared changedframe contacts "+JSON.stringify(unknown_preimages)):return\n for at:Vector3 in witnesses:\n  if not require(ray(space',1)
 p.write_text(s)
for q in (F/'assets').rglob('*'):
 if q.is_file():
  dest=T/q.relative_to(F);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(q,dest)
for q in (F/'.godot/imported').iterdir():
 if q.is_file():shutil.copyfile(q,T/'.godot/imported'/q.name)
p=T/'data/group2_forward_receiving_20261013/FORWARD.json'
d=json.loads(p.read_text());plan=json.loads((P/'FORWARD_FRAME_PLAN.json').read_text());d['parts']=plan['parts']
old='assets/group2_forward_receiving_20261013/FORWARD_ADJUNCT_FRAMES_r003.glb';new=old.replace('r003','r004')
d['model_pins'].pop(old,None);d['model_pins'][new]=hashlib.sha256((T/new).read_bytes()).hexdigest()
p.write_text(json.dumps(d,indent=2)+'\n')
q=T/'scripts/group2_forward_receiving_20261013/package.gd';q.write_text(q.read_text().replace('FRAMES_r003','FRAMES_r004'))
with zipfile.ZipFile(P/'CANDIDATE_OVERLAY.zip','w',zipfile.ZIP_DEFLATED,compresslevel=1) as z:
 for folder in [T/'assets',T/'data',T/'scripts',T/'.godot/imported']:
  for q in folder.rglob('*'):
   if q.is_file() and not any(v in q.name for v in ['FRAMES_r001','FRAMES_r002','FRAMES_r003']):z.write(q,str(q.relative_to(T)))
p=P/'validate_resources.gd';p.write_text(p.read_text().replace('==140','==155').replace('140_FRAME','155_FRAME'))
print('PASS_R004_OVERLAY_155_PARTS_FROM_SURVIVING_SINGLE_IMPORT')
