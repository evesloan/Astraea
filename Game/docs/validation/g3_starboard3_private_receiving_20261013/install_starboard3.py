from pathlib import Path
import json,hashlib,re,zipfile,os,subprocess
C=Path(__file__).parent.parent;R=Path('/workspace/astraea-protected-integration-20261012');G=R/'Game';base='a7693e237bbec26214738987925b1bc7761d1b8b';sha=lambda b:hashlib.sha256(b).hexdigest()
assert subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD']).decode().strip()==base
assert not subprocess.check_output(['git','-C',str(R),'diff','--name-only']).strip()
protected=json.loads((C/'RETAINED_UNTRACKED_52_PROTECTION_VERIFICATION.json').read_text());assert protected['source_commit_remote_retention_verified'] and not protected['unresolved']
for row in protected['verified_files']:assert sha((R/row['path']).read_bytes())==row['sha256']
P=C/'g3_starboard3_private_receiving'
check=json.loads((P/'RECEIVING_RUNTIME.json').read_text());assert check['status']=='PASS_CURRENT_STARBOARD3_PHYSICAL_RECEIVING'and check['checks']>1000 and len(check['original_controller_legs'])==6
assert json.loads((Path('/workspace/astraea-protected-integration-evidence-20261012')/'g3_starboard3_receiving136.json').read_text())['passed']
with zipfile.ZipFile(P/'CANDIDATE_OVERLAY.zip')as z:writes={k:z.read(k)for k in z.namelist()}
key='scripts/group3_starboard3_private_20261011/physical_package.gd';writes[key]=writes[key].replace(b'n.set_meta("default_main_adoption",false)',b'n.set_meta("default_main_adoption",true)')
writes['docs/validation/g3_starboard3_private_receiving_20261013/OWNER_PACKAGE.gd.txt']=(P/'OWNER_PACKAGE.gd.txt').read_bytes()
for q in (P/'inputs/BlenderCatalogue/assets/group3_crew_service_20261009/extensions/starboard3_private_landings_batch019/source').iterdir():
 if q.is_file():writes['docs/validation/g3_starboard3_private_receiving_20261013/native/'+q.name]=q.read_bytes()
for k,b in writes.items():assert not(G/k).exists()or(G/k).read_bytes()==b,('Unexpected surviving full clinical source preimage',k)
p=G/'scripts/ship.gd';old=p.read_text();anchor='\tload("res://scripts/group3_clinical_full_20261011/physical_package.gd").build(self)\n';assert old.count(anchor)==1;new=old.replace(anchor,anchor+'\t# Starboard3 exact physicallandings;privategates/lift/consent operationremainheld.\n\tload("res://scripts/group3_starboard3_private_20261011/physical_package.gd").build(self)\n')
proofpath=G/'data/architecture/packages/botanical_pair_runtime/RUNTIME_PROOF.json';proof=json.loads(proofpath.read_text());k='scripts/ship.gd';assert proof['current_sha256'][k]==sha(old.encode());proof['inverse_edits'][k]=[{'before':old,'after':new,'count':1}]+proof['inverse_edits'][k];proof['current_sha256'][k]=sha(new.encode());text=new
for e in proof['inverse_edits'][k]:assert text.count(e['after'])==e['count'];text=text.replace(e['after'],e['before'])
assert sha(text.encode())==proof['predecessors'][k]['sha256'];writes[k]=new.encode()
guard=G/'tests/botanical_pair_successor_guard.gd';s=guard.read_text();h=re.search('const PROOF_SHA := "([0-9a-f]{64})"',s).group(1);assert sha(proofpath.read_bytes())==h and sha(s.replace(h,'<PROOF_SHA>').encode())==proof['normalized_guard_sha256'];pb=(json.dumps(proof,indent=2)+'\n').encode();writes['data/architecture/packages/botanical_pair_runtime/RUNTIME_PROOF.json']=pb;writes['tests/botanical_pair_successor_guard.gd']=s.replace(h,sha(pb)).encode()
for k,b in writes.items():p=G/k;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
zpath=C/'TRAM_REMAINING_G8_OVERLAY.zip';tmp=zpath.with_suffix('.fore.zip')
with zipfile.ZipFile(zpath)as src,zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=1)as out:
 for entry in src.infolist():
  if entry.filename not in writes:out.writestr(entry,src.read(entry.filename))
 for k,b in writes.items():out.writestr(k,b)
os.replace(tmp,zpath)
receipt={'status':'STARBOARD3_PHYSICAL_INSTALLED_STARTUP_PENDING','base':base,'checks':check['checks'],'original_controller_legs':6,'preserved_prior_meshes':check['preserved_prior_meshes'],'preserved_prior_contacts':check['preserved_prior_contacts'],'new_models':4,'new_floor_m2':865.9119999999995,'source_floor_witnesses':170,'new_fixture_sources':17,'landings':17,'original_D04_riser_and_routes_retained':True,'operating_lift_private_gates_or_consent':False,'clinical_streaming_and_support_holds_unchanged':True,'bed_room_crew_capacity_credit':0,'full_build_accepted':False,'source_sha256':{k:sha(b)for k,b in writes.items()if not k.startswith('.godot/')}};(P/'ADOPTION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(writes),'source/cache paths')
