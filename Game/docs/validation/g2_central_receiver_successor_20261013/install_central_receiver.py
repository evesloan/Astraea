from pathlib import Path
import json,hashlib,re,zipfile,os,subprocess
C=Path(__file__).parent.parent;R=Path('/workspace/astraea-protected-integration-20261012');G=R/'Game';base='403ccf17ddff1e3fa1e987a67d69048583c73366';sha=lambda b:hashlib.sha256(b).hexdigest()
assert subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD']).decode().strip()==base
assert not subprocess.check_output(['git','-C',str(R),'diff','--name-only']).strip()
protected=json.loads((C/'RETAINED_UNTRACKED_52_PROTECTION_VERIFICATION.json').read_text());assert protected['source_commit_remote_retention_verified'] and not protected['unresolved']
for row in protected['verified_files']:assert sha((R/row['path']).read_bytes())==row['sha256']
P=C/'g2_central_receiver_successor_20261013'
check=json.loads((P/'RECEIVING_RUNTIME.json').read_text());assert check['status']=='PASS_CURRENT_CENTRAL_ADJUNCT_CARE_RECEIVING'and check['checks']>100 and len(check['original_controller_legs'])==12
assert json.loads((Path('/workspace/astraea-protected-integration-evidence-20261012')/'g2_central_receiver_r004_receiving150.json').read_text())['passed']
with zipfile.ZipFile(P/'CANDIDATE_OVERLAY.zip')as z:writes={k:z.read(k)for k in z.namelist()}
key='scripts/group2_central_receiving_20261013/package.gd';writes[key]=writes[key].replace(b'n.set_meta("default_main_adoption",false)',b'n.set_meta("default_main_adoption",true)')
for q in (P/'native').iterdir():
 if q.is_file():writes['docs/validation/g2_central_receiver_successor_20261013/native/'+q.name]=q.read_bytes()
for k,b in writes.items():assert not(G/k).exists()or(G/k).read_bytes()==b,('Unexpected surviving full clinical source preimage',k)
p=G/'scripts/ship.gd';old=p.read_text();anchor='\tload("res://scripts/group3_starboard3_private_20261011/physical_package.gd").build(self)\n';assert old.count(anchor)==1;new=old.replace(anchor,anchor+'\t# One supported sourceadjunct/care receiver via westerncirculation;all structuralcapacity/service/consent holds remain.\n\tload("res://scripts/group2_central_receiving_20261013/package.gd").build(self)\n')
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
receipt={'status':'CENTRAL_ADJUNCT_CARE_PHYSICAL_INSTALLED_STARTUP_PENDING','base':base,'checks':check['checks'],'original_controller_legs':12,'completion_adjuncts_selected':1,'completion_homes_selected':0,'care_kits_selected':1,'source_floor_m2':80,'missing_connector_m2':39.654,'actual_positive_bearings':14,'native_frame_parts':104,'primary_profilewall_cuts':0,'bounded_source_guard_successor_parts':3,'guard_aperture_width_m':1.8,'original_profilewalls_and_slab_preserved':True,'new_compiler_owners':0,'ordinary_retained_source_lights':2,'operating_private_admission_or_service':False,'primary_structure_capacity_or_lower_section_accepted':False,'bed_room_crew_capacity_credit':0,'clinical_streaming_support_and_network_holds_unchanged':True,'full_build_accepted':False,'source_sha256':{k:sha(b)for k,b in writes.items()if not k.startswith('.godot/')}};(P/'ADOPTION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(writes),'source/cache paths')
