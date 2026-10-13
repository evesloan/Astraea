from pathlib import Path
import json,hashlib,re,zipfile,os,subprocess
C=Path(__file__).parent.parent;R=Path('/workspace/astraea-protected-integration-20261012');G=R/'Game';base='9fe069e0b8af42869dbf49b4b97d69d95b2ab63d';sha=lambda b:hashlib.sha256(b).hexdigest()
assert subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD']).decode().strip()==base
assert not subprocess.check_output(['git','-C',str(R),'diff','--name-only']).strip()
protected=json.loads((C/'RETAINED_UNTRACKED_52_PROTECTION_VERIFICATION.json').read_text());assert protected['source_commit_remote_retention_verified'] and not protected['unresolved']
for row in protected['verified_files']:assert sha((R/row['path']).read_bytes())==row['sha256']
P=C/'g2_last_three_pairs_20261013'
check=json.loads((P/'CENTRAL_RECEIVING_RUNTIME.json').read_text());assert check['status']=='PASS_CURRENT_PORTCENTRAL_ADJUNCT_CARE_RECEIVING'and check['checks']>100 and len(check['legs'])==12
assert json.loads((Path('/workspace/astraea-protected-integration-evidence-20261012')/'g2_portcentral_receiving181.json').read_text())['passed']
with zipfile.ZipFile(P/'CANDIDATE_OVERLAY.zip')as z:writes={k:z.read(k)for k in z.namelist()}
key='scripts/group2_portcentral_receiving_20261013/package.gd';writes[key]=writes[key].replace(b'n.set_meta("default_main_adoption",false)',b'n.set_meta("default_main_adoption",true)')
writes={k:b for k,b in writes.items()if 'PORTCENTRAL_RECEIVING_FRAME_r001'not in k and 'PORTCENTRAL_RECEIVING_FRAME_r002'not in k and 'PORTCENTRAL_RECEIVING_FRAME_r003'not in k}
for q in (P/'native').iterdir():
 if q.is_file()and q.name not in ['PORTCENTRAL_RECEIVING_FRAME_r001.blend','PORTCENTRAL_RECEIVING_FRAME_r002.blend','PORTCENTRAL_RECEIVING_FRAME_r001.blend1','PORTCENTRAL_RECEIVING_FRAME_r002.blend1','PORTCENTRAL_RECEIVING_FRAME_r003.blend','PORTCENTRAL_RECEIVING_FRAME_r003.blend1']:writes['docs/validation/g2_portcentral_receiving_20261013/native/'+q.name]=q.read_bytes()
shared_uid='scripts/group2_care_programmes/package.gd.uid'
if (G/shared_uid).exists():
 assert (G/'scripts/group2_care_programmes/package.gd').read_bytes()==writes['scripts/group2_care_programmes/package.gd']
 writes[shared_uid]=(G/shared_uid).read_bytes()
 (P/'SHARED_CARE_UID_RETENTION.json').write_text(json.dumps({'status':'PASS_EXISTING_IDENTICAL_SHARED_SCRIPT_UID_RETAINED','path':shared_uid,'sha256':sha(writes[shared_uid]),'staging_generated_uid_not_adopted':True},indent=2)+'\n')
for k,b in writes.items():assert not(G/k).exists()or(G/k).read_bytes()==b,('Unexpected surviving source preimage',k)
p=G/'scripts/ship.gd';old=p.read_text();anchor='\tload("res://scripts/group2_forward_receiving_20261013/package.gd").build(self)\n';assert old.count(anchor)==1;new=old.replace(anchor,anchor+'\t# Port-central sourceadjunct/care pair;lower-stub bearing andwestvestibule fit,operational/engineering holds remain.\n\tload("res://scripts/group2_portcentral_receiving_20261013/package.gd").build(self)\n')
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
receipt={'status':'PORTCENTRAL_PHYSICAL_INSTALLED_STARTUP_PENDING','base':base,'checks':check['checks'],'original_controller_legs':len(check['legs']),'completion_adjuncts_selected':1,'completion_homes_selected':0,'care_kits_selected':1,'source_floor_m2':80.,'new_connections_m2':30.06,'lower_stub_slab_bearings':6,'upper_arrival_slab_bearings':4,'native_frame_parts':len(__import__('json').loads((P/'PORTCENTRAL_FRAME_PLAN.json').read_text())['parts']),'primary_models_walls_piers_slabs_and_prior_doors_unchanged':True,'original_guard_node_body_material_identities_retained':True,'guard_window_width_m':1.8,'ordinary_retained_source_lights':2,'operating_private_admission_care_service_or_structuralcapacity':False,'bed_room_crew_capacity_credit':0,'remaining_aft_pairs_not_adopted':True,'clinical_streaming_support_network_andtram_holds_unchanged':True,'full_build_accepted':False,'source_sha256':{k:sha(b)for k,b in writes.items()if not k.startswith('.godot/')}};(P/'ADOPTION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(writes),'source/cache paths')
