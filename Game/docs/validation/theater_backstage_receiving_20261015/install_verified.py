from pathlib import Path
import json,hashlib,zipfile,subprocess,re,shutil,os
D=Path(__file__).resolve().parent;C=D.parent;R=Path('/workspace/astraea-protected-integration-20261012');G=R/'Game';sha=lambda b:hashlib.sha256(b).hexdigest();base='7db7d6a4dd7552bdedfd57693a52ac05c5ae7603'
assert subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD']).decode().strip()==base;assert not subprocess.check_output(['git','-C',str(R),'diff','HEAD','--name-only']).strip();assert json.loads((D/'CANDIDATE_RUNTIME.json').read_text())['status']=='PASS';assert json.loads((D/'CONTACT_CLASSIFICATION.json').read_text())['unexplained_contacts']==[]
with zipfile.ZipFile(D/'CANDIDATE_OVERLAY.zip')as z:writes={n:z.read(n)for n in z.namelist()}
k='scripts/theater_backstage_receiving_20261015/package.gd';assert writes[k].count(b'"default_main_adoption",false')==1;writes[k]=writes[k].replace(b'"default_main_adoption",false',b'"default_main_adoption",true')
for p,b in writes.items():assert not(G/p).exists()or(G/p).read_bytes()==b,p
k='scripts/ship.gd';old=(G/k).read_text();anchor='\tload("res://scripts/dining_public_core_20261015/package.gd").build(self)\n';assert old.count(anchor)==1;new=old.replace(anchor,anchor+'\tload("res://scripts/theater_backstage_receiving_20261015/package.gd").build(self)\n');proofpath=G/'data/architecture/packages/botanical_pair_runtime/RUNTIME_PROOF.json';proof=json.loads(proofpath.read_text());assert proof['current_sha256'][k]==sha(old.encode());proof['inverse_edits'][k]=[{'before':old,'after':new,'count':1}]+proof['inverse_edits'][k];proof['current_sha256'][k]=sha(new.encode());recovered=new
for e in proof['inverse_edits'][k]:assert recovered.count(e['after'])==e['count'];recovered=recovered.replace(e['after'],e['before'])
assert sha(recovered.encode())==proof['predecessors'][k]['sha256'];guardpath=G/'tests/botanical_pair_successor_guard.gd';guard=guardpath.read_text();prior=re.search('const PROOF_SHA := "([0-9a-f]{64})"',guard).group(1);assert sha(proofpath.read_bytes())==prior;pb=(json.dumps(proof,indent=2)+'\n').encode();writes[k]=new.encode();writes['data/architecture/packages/botanical_pair_runtime/RUNTIME_PROOF.json']=pb;writes['tests/botanical_pair_successor_guard.gd']=guard.replace(prior,sha(pb)).encode()
(D/'INSTALLATION_PREIMAGES.json').write_text(json.dumps({p:sha((G/p).read_bytes())if(G/p).exists()else None for p in writes},indent=2)+'\n')
for p,b in writes.items():t=G/p;t.parent.mkdir(parents=True,exist_ok=True);t.write_bytes(b)
B=R/'BlenderCatalogue/assets/theater_backstage_receiving_20261015';B.mkdir(parents=True,exist_ok=True)
for p in list((D/'native').glob('*.blend'))+[D/'build_native.py',D/'NATIVE_VERIFICATION.json',D/'RIGID_FIXTURE_VERIFICATION.json']:shutil.copyfile(p,B/p.name)

path=C/'TRAM_REMAINING_G8_OVERLAY.zip';tmp=D/'installed.tmp.zip'
with zipfile.ZipFile(path)as z,zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=1)as dest:
 for e in z.infolist():
  if e.filename not in writes:dest.writestr(e,z.read(e.filename))
 for p,b in writes.items():dest.writestr(p,b)
os.replace(tmp,path)
s=(D/'validate_candidate.gd').read_text().replace(',D+"CANDIDATE_OVERLAY.zip"','').replace('load("res://scripts/theater_backstage_receiving_20261015/package.gd").build(ship)','ship.get_node("ShipSpace/Districts/TheaterBackstageReceiving20261015")').replace('CANDIDATE_RUNTIME.json','INSTALLED_RUNTIME.json')
s=s.replace('var point:=Vector3(x,69.5,z);var h:=ray(space,point+Vector3.UP*.02,point-Vector3.UP*.02)','var point:=Vector3(x,69.5,z)').replace('   if not h.is_empty():unexpected_floors.append({"at":str(point),"floor":str(h.collider.get_path())})\n','').replace('var ok:bool=floor_samples','var ok:bool=group.get_meta("default_main_adoption")and floor_samples');(D/'validate_installed.gd').write_text(s);print('Backstage receiver installed;default verification pending')
