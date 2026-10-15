from pathlib import Path
import json,hashlib,zipfile,subprocess,re,shutil,os
D=Path(__file__).resolve().parent;C=D.parent;R=Path('/workspace/astraea-protected-integration-20261012');G=R/'Game';sha=lambda b:hashlib.sha256(b).hexdigest();base='545508881af6d5251e0723c837555a217b95b7fd'
assert subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD']).decode().strip()==base;assert not subprocess.check_output(['git','-C',str(R),'diff','HEAD','--name-only']).strip();assert json.loads((D/'CANDIDATE_RUNTIME.json').read_text())['status'].startswith('PASS');assert json.loads((D/'CANDIDATE_RUNTIME.json').read_text())['unexplained_contacts']==[];assert json.loads((D/'NATIVE_GEOMETRY_VERIFICATION.json').read_text())['status'].startswith('PASS');assert json.loads((D/'OUTSIDE_GEOMETRY_VERIFICATION.json').read_text())['status'].startswith('PASS')
with zipfile.ZipFile(D/'CANDIDATE_OVERLAY.zip')as z:writes={n:z.read(n)for n in z.namelist()if not n.startswith('validation/')}
k='scripts/orchard_external_receiving_20261015/package.gd';assert writes[k].count(b'"default_main_adoption",false')==1;writes[k]=writes[k].replace(b'"default_main_adoption",false',b'"default_main_adoption",true')
for p,b in writes.items():assert not(G/p).exists()or(G/p).read_bytes()==b,p
k='scripts/ship.gd';old=(G/k).read_text();anchor='\tload("res://scripts/dining_service_receiving_20261015/package.gd").build(self)\n';assert old.count(anchor)==1;new=old.replace(anchor,anchor+'\tload("res://scripts/orchard_external_receiving_20261015/package.gd").build(self)\n');proofpath=G/'data/architecture/packages/botanical_pair_runtime/RUNTIME_PROOF.json';proof=json.loads(proofpath.read_text());assert proof['current_sha256'][k]==sha(old.encode());proof['inverse_edits'][k]=[{'before':old,'after':new,'count':1}]+proof['inverse_edits'][k];proof['current_sha256'][k]=sha(new.encode());recovered=new
for e in proof['inverse_edits'][k]:assert recovered.count(e['after'])==e['count'];recovered=recovered.replace(e['after'],e['before'])
assert sha(recovered.encode())==proof['predecessors'][k]['sha256'];guardpath=G/'tests/botanical_pair_successor_guard.gd';guard=guardpath.read_text();prior=re.search('const PROOF_SHA := "([0-9a-f]{64})"',guard).group(1);assert sha(proofpath.read_bytes())==prior;pb=(json.dumps(proof,indent=2)+'\n').encode();writes[k]=new.encode();writes['data/architecture/packages/botanical_pair_runtime/RUNTIME_PROOF.json']=pb;writes['tests/botanical_pair_successor_guard.gd']=guard.replace(prior,sha(pb)).encode()
(D/'INSTALLATION_PREIMAGES.json').write_text(json.dumps({p:sha((G/p).read_bytes())if(G/p).exists()else None for p in writes},indent=2)+'\n')
for p,b in writes.items():t=G/p;t.parent.mkdir(parents=True,exist_ok=True);t.write_bytes(b)
B=R/'BlenderCatalogue/assets/orchard_external_receiving_20261015';B.mkdir(parents=True,exist_ok=True)
for p in list((D/'native').glob('*.blend'))+list((D/'import/Game/assets/orchard_external_receiving_20261015').glob('*.glb'))+list(D.glob('*.py')):
 shutil.copyfile(p,B/p.name)
path=D/'INSTALLED_OVERLAY.zip'
with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=1)as dest:
 for p,b in writes.items():dest.writestr(p,b)
shutil.copyfile(path,C/'ORCHARD_RECEIVING_ADOPTION_OVERLAY.zip')

for name in ['NATIVE_PLAN.json','NATIVE_VERIFICATION.json','OUTSIDE_GEOMETRY_VERIFICATION.json','NATIVE_GEOMETRY_VERIFICATION.json','ORCHARD_SOURCE_RECEIVING_SURVEY.json']:shutil.copyfile(D/name,B/name)
shutil.copytree(D/'visual_review',B/'visual_review',dirs_exist_ok=True)
s=(D/'validate_candidate.gd').read_text().replace('D+"CANDIDATE_OVERLAY.zip"','D+"INSTALLED_OVERLAY.zip"').replace('load("res://scripts/orchard_external_receiving_20261015/package.gd").build(ship)','ship.get_node("ShipSpace/OrchardExternalReceiving20261015")').replace('CANDIDATE_RUNTIME.json','INSTALLED_RUNTIME.json').replace('preserved=preserved and changed_names==expected','preserved=preserved and changed_names.is_empty()and group.get_meta("exact_selected_wall_preimages").size()==2').replace('var ok:bool=preimages','var ok:bool=group.get_meta("default_main_adoption")and preimages');(D/'validate_installed.gd').write_text(s);print('ORCHARD_INSTALLED_DEFAULT_CHECK_PENDING')
