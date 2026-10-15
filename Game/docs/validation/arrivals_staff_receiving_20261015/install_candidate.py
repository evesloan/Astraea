from pathlib import Path
import json,subprocess,hashlib,re,zipfile,shutil
D=Path(__file__).resolve().parent;R=Path('/workspace/astraea-protected-integration-20261012');G=R/'Game';sha=lambda b:hashlib.sha256(b).hexdigest();assert subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip()=='97f8f890574633ded92c1bd0c8280be6c029e494';assert not subprocess.check_output(['git','-C',str(R),'diff','HEAD','--name-only']).strip();assert json.loads((D/'NATIVE_GEOMETRY_VERIFICATION.json').read_text())['status'].startswith('PASS');assert'ERROR:'not in(D/'IMPORT001.log').read_text();writes={};T=D/'import/Game'
for p in T.rglob('*'):
 rel=p.relative_to(T).as_posix()
 if p.is_file()and rel.startswith(('assets/','scripts/','data/','.godot/imported/')):writes[rel]=p.read_bytes()
for path,b in writes.items():assert not(G/path).exists()or(G/path).read_bytes()==b,path
k='scripts/ship.gd';old=(G/k).read_text();anchor='\tload("res://scripts/aquatic_external_receiving_20261015/package.gd").build.call_deferred(self)\n';assert old.count(anchor)==1;new=old.replace(anchor,anchor+'\tload("res://scripts/arrivals_staff_receiving_20261015/package.gd").build.call_deferred(self)\n');pp=G/'data/architecture/packages/botanical_pair_runtime/RUNTIME_PROOF.json';proof=json.loads(pp.read_text());assert proof['current_sha256'][k]==sha(old.encode());proof['inverse_edits'][k]=[{'before':old,'after':new,'count':1}]+proof['inverse_edits'][k];proof['current_sha256'][k]=sha(new.encode());s=new
for e in proof['inverse_edits'][k]:assert s.count(e['after'])==e['count'];s=s.replace(e['after'],e['before'])
assert sha(s.encode())==proof['predecessors'][k]['sha256'];gp=G/'tests/botanical_pair_successor_guard.gd';guard=gp.read_text();prior=re.search('const PROOF_SHA := "([0-9a-f]{64})"',guard).group(1);assert sha(pp.read_bytes())==prior;pb=(json.dumps(proof,indent=2)+'\n').encode();writes[k]=new.encode();writes['data/architecture/packages/botanical_pair_runtime/RUNTIME_PROOF.json']=pb;writes['tests/botanical_pair_successor_guard.gd']=guard.replace(prior,sha(pb)).encode();(D/'INSTALLATION_PREIMAGES.json').write_text(json.dumps({p:sha((G/p).read_bytes())if(G/p).exists()else None for p in writes},indent=2)+'\n')
for path,b in writes.items():p=G/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
B=R/'BlenderCatalogue/assets/arrivals_staff_receiving_20261015';B.mkdir(parents=True,exist_ok=True)
for p in list((D/'native').glob('*.blend'))+list(D.glob('*.py'))+[D/'AUTHORING_COMPONENTS_r001.glb']+list((T/'assets/arrivals_staff_receiving_20261015').glob('*.glb')):shutil.copyfile(p,B/p.name)
for name in ['NATIVE_PLAN.json','NATIVE_VERIFICATION.json','NATIVE_GEOMETRY_VERIFICATION.json','OUTSIDE_GEOMETRY_VERIFICATION.json','NATIVE_VERIFICATION_COUNT_CORRECTION.json']:shutil.copyfile(D/name,B/name)
with zipfile.ZipFile(D/'INSTALLED_OVERLAY.zip','w',zipfile.ZIP_DEFLATED,compresslevel=1)as z:
 for path,b in writes.items():z.writestr(path,b)
shutil.copyfile(D/'INSTALLED_OVERLAY.zip',D.parent/'ARRIVALS_STAFF_ADOPTION_OVERLAY.zip');(D/'INSTALLED_FILES.json').write_text(json.dumps({p:{'bytes':len(b),'sha256':sha(b)}for p,b in writes.items()},indent=2)+'\n');print('ARRIVALS_STAFF_RECEIVER_CANDIDATE_INSTALLED_FINAL_PHYSICS_PENDING',len(writes))
