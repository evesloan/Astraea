from pathlib import Path
import json,hashlib,re,zipfile,os,subprocess
C=Path(__file__).parent;R=Path('/workspace/astraea-protected-integration-20261012');G=R/'Game';sha=lambda b:hashlib.sha256(b).hexdigest();base='e77bd145d5b4743e2f0697a34638bd3dcafbbf0e'
assert subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD']).decode().strip()==base
assert not subprocess.check_output(['git','-C',str(R),'diff','--name-only']).strip()
protected=json.loads((C/'RETAINED_UNTRACKED_52_PROTECTION_VERIFICATION.json').read_text());assert protected['source_commit_remote_retention_verified'] and not protected['unresolved']
for row in protected['verified_files']:assert sha((R/row['path']).read_bytes())==row['sha256'],row['path']
assert json.loads((C/'G3_LABELLED_BANK_RECEIVING_RUNTIME.json').read_text())['status']=='PASS_EXACT_LABELLED_BANK_PHYSICAL_RECEIVING'
with zipfile.ZipFile(C/'G3_LABELLED_BANK_CANDIDATE_OVERLAY.zip')as z:writes={k:z.read(k)for k in z.namelist()}
key='scripts/group3_completion_20261011/labelled_bank.gd';writes[key]=writes[key].replace(b'n.set_meta("default_main_adoption",false)',b'n.set_meta("default_main_adoption",true)')
original=C/'g3_receiving_metadata/Game/scripts/group3_completion_20261011/labelled_bank.gd';writes['docs/validation/g3_labelled_bank_installed_20261013/LABELLED_BANK_OWNER_SOURCE.gd.txt']=original.read_bytes()
for k,b in writes.items():assert not (G/k).exists()or(G/k).read_bytes()==b,('Unexpected surviving bank preimage',k)
ship=G/'scripts/ship.gd';old=ship.read_text();anchor='\tload("res://scripts/group3_completion_20261011/d03_precinct.gd").build(self)\n';assert old.count(anchor)==1
new=old.replace(anchor,anchor+'\t# Exact supported labelled bank;unassigned rest surfaces,unknown private entry refused.\n\tload("res://scripts/group3_completion_20261011/labelled_bank.gd").build(self)\n')
p=G/'data/architecture/packages/botanical_pair_runtime/RUNTIME_PROOF.json';proof=json.loads(p.read_text());k='scripts/ship.gd';assert proof['current_sha256'][k]==sha(old.encode());proof['inverse_edits'][k]=[{'before':old,'after':new,'count':1}]+proof['inverse_edits'][k];proof['current_sha256'][k]=sha(new.encode());text=new
for e in proof['inverse_edits'][k]:assert text.count(e['after'])==e['count'];text=text.replace(e['after'],e['before'])
assert sha(text.encode())==proof['predecessors'][k]['sha256'];writes[k]=new.encode()
guard=G/'tests/botanical_pair_successor_guard.gd';s=guard.read_text();h=re.search('const PROOF_SHA := "([0-9a-f]{64})"',s).group(1);assert sha(p.read_bytes())==h and sha(s.replace(h,'<PROOF_SHA>').encode())==proof['normalized_guard_sha256'];pb=(json.dumps(proof,indent=2)+'\n').encode();writes['data/architecture/packages/botanical_pair_runtime/RUNTIME_PROOF.json']=pb;writes['tests/botanical_pair_successor_guard.gd']=s.replace(h,sha(pb)).encode()
for k,b in writes.items():q=G/k;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
zpath=C/'TRAM_REMAINING_G8_OVERLAY.zip';tmp=zpath.with_suffix('.bank.zip')
with zipfile.ZipFile(zpath)as src,zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=1)as out:
 for entry in src.infolist():
  if entry.filename not in writes:out.writestr(entry,src.read(entry.filename))
 for k,b in writes.items():out.writestr(k,b)
os.replace(tmp,zpath)
receipt={'status':'EXACT_SUPPORTED_BANK_INSTALLED_COMBINED_STARTUP_PENDING','base':base,'source_revision':'6f2d0da67429ea940edf7011348ec08a346f37db','native_models':3,'native_missing_floor_m2':2589.124004486059,'source_floor_witnesses':158,'focused_current_scene_checks':424,'original_player_legs':2,'owned_sources':48,'authored_gates':16,'outside_unknown_permission_refused':True,'inside_egress_preserved':True,'unassigned_rest_surfaces':32,'registered_berths_added':0,'new_compiler_owners':0,'person_berth_save_species_migration_external_admission_accepted':False,'source_sha256':{k:sha(b)for k,b in writes.items()if not k.startswith('.godot/')},'retained_untracked_files_unchanged':True};(C/'G3_LABELLED_BANK_ADOPTION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(writes),'source/cache paths')
