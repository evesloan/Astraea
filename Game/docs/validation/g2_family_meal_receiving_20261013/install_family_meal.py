from pathlib import Path
import json,hashlib,re,zipfile,os,subprocess
C=Path(__file__).parent.parent;R=Path('/workspace/astraea-protected-integration-20261012');G=R/'Game';base='dafa10902c184e1f3aee8ce60e0ebaf47d1d2b0d';sha=lambda b:hashlib.sha256(b).hexdigest()
assert subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD']).decode().strip()==base
assert not subprocess.check_output(['git','-C',str(R),'diff','--name-only']).strip()
protected=json.loads((C/'RETAINED_UNTRACKED_52_PROTECTION_VERIFICATION.json').read_text());assert protected['source_commit_remote_retention_verified'] and not protected['unresolved']
for row in protected['verified_files']:assert sha((R/row['path']).read_bytes())==row['sha256']
P=C/'g2_family_meal_receiving'
check=json.loads((P/'RECEIVING_RUNTIME.json').read_text());assert check['status']=='PASS_CURRENT_FAMILY_MEAL_PHYSICAL_RECEIVING' and check['checks']>3000 and len(check['original_controller_legs'])==6
assert json.loads((Path('/workspace/astraea-protected-integration-evidence-20261012')/'g2_family_meal_receiving115.json').read_text())['passed']
with zipfile.ZipFile(P/'CANDIDATE_OVERLAY.zip')as z:writes={k:z.read(k)for k in z.namelist()}
key='scripts/group2_family_meal/package.gd';writes[key]=writes[key].replace(b'root.set_meta("default_main_adoption",false)',b'root.set_meta("default_main_adoption",true)')
for q in (P/'native').iterdir():
 if q.is_file():writes['docs/validation/g2_family_meal_receiving_20261013/native/'+q.name]=q.read_bytes()
for k,b in writes.items():assert not(G/k).exists()or(G/k).read_bytes()==b,('Unexpected surviving meal preimage',k)
p=G/'scripts/ship.gd';old=p.read_text();anchor='\tload("res://scripts/group2_garden_quiet/package.gd").build_on_current_receivers(self)\n';assert old.count(anchor)==1;new=old.replace(anchor,anchor+'\t# Exact retained tabletop child fitout;food/staff services and dining designation stay held.\n\tload("res://scripts/group2_family_meal/package.gd").build_on_current_receiver(self)\n')
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
receipt={'status':'FAMILY_MEAL_INSTALLED_STARTUP_PENDING','base':base,'checks':check['checks'],'original_controller_legs':6,'retained_meshes':check['retained_meshes'],'models':1,'original_tables':3,'settings':12,'new_chairs_floor_or_capacity':0,'food_stock_hygiene_or_staff_operation':False,'programme_or_dining_designation':False,'historical_criteria':13,'unaccepted_G3_joins':184,'G5_address_joins':84,'G7_limitations_unchanged':True,'full_build_accepted':False,'source_sha256':{k:sha(b)for k,b in writes.items()if not k.startswith('.godot/')}};(P/'ADOPTION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(writes),'source/cache paths')
