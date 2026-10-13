from pathlib import Path
import json,hashlib,re,zipfile,os,subprocess
C=Path(__file__).parent.parent;R=Path('/workspace/astraea-protected-integration-20261012');G=R/'Game';base='55515312100034de6ce37f5e72ce966980006668';sha=lambda b:hashlib.sha256(b).hexdigest()
assert subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD']).decode().strip()==base
assert not subprocess.check_output(['git','-C',str(R),'diff','--name-only']).strip()
protected=json.loads((C/'RETAINED_UNTRACKED_52_PROTECTION_VERIFICATION.json').read_text());assert protected['source_commit_remote_retention_verified'] and not protected['unresolved']
for row in protected['verified_files']:assert sha((R/row['path']).read_bytes())==row['sha256']
P=C/'g2_childcare_physical_receiving'
check=json.loads((P/'RECEIVING_RUNTIME.json').read_text());assert check['status']=='PASS_CURRENT_CHILDCARE_PHYSICAL_RECEIVING'and check['checks']>3000 and len(check['original_controller_legs'])==6
assert json.loads((Path('/workspace/astraea-protected-integration-evidence-20261012')/'g2_childcare_receiving121.json').read_text())['passed']
with zipfile.ZipFile(P/'CANDIDATE_OVERLAY.zip')as z:writes={k:z.read(k)for k in z.namelist()}
key='scripts/group2_family_childcare/package.gd';writes[key]=writes[key].replace(b'root.set_meta("default_main_adoption",false)',b'root.set_meta("default_main_adoption",true)')
for q in (P/'native').iterdir():
 if q.is_file():writes['docs/validation/g2_childcare_physical_20261013/native/'+q.name]=q.read_bytes()
for k,b in writes.items():assert not(G/k).exists()or(G/k).read_bytes()==b,('Unexpected surviving child fitout preimage',k)
p=G/'scripts/ship.gd';old=p.read_text();anchor='\tload("res://scripts/group2_family_meal/package.gd").build_on_current_receiver(self)\n';assert old.count(anchor)==1;new=old.replace(anchor,anchor+'\t# Physical child fitout only;closed authored entry,guardian/admission/services remain held.\n\tload("res://scripts/group2_family_childcare/package.gd").build_on_current_receiver(self)\n')
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
receipt={'status':'CHILDCARE_PHYSICAL_INSTALLED_STARTUP_PENDING','base':base,'checks':check['checks'],'original_controller_legs':6,'retained_meshes':check['retained_meshes'],'retained_contacts':check['retained_contacts'],'new_models':1,'existing_wide_fitting':1,'fixtures':4,'site_m2':57.66,'proposed_day_rest_fittings':4,'new_floor_rooms_beds_or_capacity':0,'guardian_supervision_child_programme_or_admission':False,'entry_or_inside_egress_operation':False,'source_fixture_id_bound_to_production':False,'food_hygiene_or_staff_services':False,'full_build_accepted':False,'source_sha256':{k:sha(b)for k,b in writes.items()if not k.startswith('.godot/')}};(P/'ADOPTION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(writes),'source/cache paths')
