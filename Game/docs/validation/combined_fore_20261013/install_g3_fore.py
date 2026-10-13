from pathlib import Path
import json,hashlib,re,zipfile,os,subprocess
C=Path(__file__).parent;R=Path('/workspace/astraea-protected-integration-20261012');G=R/'Game';base='962315b7414588806c57c2eb311166acdcde02e2';sha=lambda b:hashlib.sha256(b).hexdigest()
assert subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD']).decode().strip()==base
assert not subprocess.check_output(['git','-C',str(R),'diff','--name-only']).strip()
protected=json.loads((C/'RETAINED_UNTRACKED_52_PROTECTION_VERIFICATION.json').read_text());assert protected['source_commit_remote_retention_verified'] and not protected['unresolved']
for row in protected['verified_files']:assert sha((R/row['path']).read_bytes())==row['sha256']
check=json.loads((C/'G3_FORE_RECEIVING_RUNTIME.json').read_text());assert check['status']=='PASS_EXACT_FORE_STARBOARD_PHYSICAL_RECEIVING' and check['checks']>=400 and len(check['observations'])==10
with zipfile.ZipFile(C/'G3_FORE_CANDIDATE_OVERLAY.zip')as z:writes={k:z.read(k)for k in z.namelist()}
key='scripts/group3_fore_starboard_clinical_20261011/physical_package.gd';writes[key]=writes[key].replace(b'n.set_meta("default_main_adoption",false)',b'n.set_meta("default_main_adoption",true)');uid=C/'g3_fore_staging/Game'/ (key+'.uid');assert uid.exists();writes[key+'.uid']=uid.read_bytes();writes['docs/validation/g3_fore_installed_20261013/FORE_OWNER_SOURCE.gd.txt']=(C/'g3_receiving_metadata/Game'/key).read_bytes()
for k,b in writes.items():assert not(G/k).exists()or(G/k).read_bytes()==b,('Unexpected surviving service preimage',k)
p=G/'scripts/ship.gd';old=p.read_text();anchor='\tload("res://scripts/group3_d03_port2_20261011/physical_package.gd").build(self,{},true)\n';assert old.count(anchor)==1;new=old.replace(anchor,anchor+'\t# Exact supported fore-starboard physical receiving;operating identities remain unassigned.\n\tload("res://scripts/group3_fore_starboard_clinical_20261011/physical_package.gd").build(self)\n')
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
receipt={'status':'EXACT_SUPPORTED_FORE_STARBOARD_PHYSICAL_PACKAGE_INSTALLED_STARTUP_PENDING','base':base,'source_revision':'6f2d0da67429ea940edf7011348ec08a346f37db','native_models':7,'native_floor_m2':1826.9919999999981,'floor_parts':17,'floor_triangle_witnesses':152,'current_scene_checks':check['checks'],'original_controller_legs':10,'independent_lobby_or_clinical_setup_cases':3,'owned_fixture_sources':34,'operating_lift_gates_dispatch_and_clinical_protocol_admitted':False,'source_closed_static_leaf_models_preserved':True,'all17_canonical_deck_datums_match':True,'original_cart_identity_or_position_changed':False,'programme_capacity_or_new_compiler_owner_credit':0,'original_player_source_unchanged':True,'prior_packages_and53_retained_payloads_preserved':True,'source_sha256':{k:sha(b)for k,b in writes.items()if not k.startswith('.godot/')}};(C/'G3_FORE_ADOPTION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(writes),'source/cache paths')
