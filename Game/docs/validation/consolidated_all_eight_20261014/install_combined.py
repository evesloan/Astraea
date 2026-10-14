from pathlib import Path
import json,hashlib,subprocess,zipfile,os
P=Path(__file__).parent;C=P.parent;R=Path('/workspace/astraea-protected-integration-20261012');G=R/'Game';sha=lambda b:hashlib.sha256(b).hexdigest()
assert subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip()=='276b59c5983f669c54fd0affb090e8a6bbfb420c'
assert not subprocess.check_output(['git','-C',str(R),'diff','--name-only']).strip()and not subprocess.check_output(['git','-C',str(R),'diff','--cached','--name-only']).strip()
for row in json.loads((C/'RETAINED_UNTRACKED_52_PROTECTION_VERIFICATION.json').read_text())['verified_files']:assert sha((R/row['path']).read_bytes())==row['sha256']
assert json.loads((P/'COMBINED_DEFAULT_RUNTIME.json').read_text())['status']=='PASS_COMBINED_DEFAULT_PHYSICAL_INTEGRATION'
assert json.loads((Path('/workspace/astraea-protected-integration-evidence-20261012')/'all_eight_default_candidate185.json').read_text())['passed']
cp=json.loads((R/'CHECKPOINT.json').read_text());pins=json.loads((P/'CANDIDATE_FILE_PINS.json').read_text())
with zipfile.ZipFile(P/'COMBINED_CANDIDATE_OVERLAY.zip')as z:writes={k:z.read(k)for k in z.namelist()}
for k,b in writes.items():
 assert len(b)==pins[k]['bytes']and sha(b)==pins[k]['sha256']
 if(G/k).exists():assert sha((G/k).read_bytes())==cp['projects']['Godot']['files'][k]
for k,b in writes.items():q=G/k;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
old=C/'TRAM_REMAINING_G8_OVERLAY.zip';tmp=old.with_suffix('.consolidated.tmp')
with zipfile.ZipFile(old)as src,zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=1)as out:
 for e in src.infolist():
  if e.filename not in writes:out.writestr(e,src.read(e.filename))
 for k,b in writes.items():out.writestr(k,b)
os.replace(tmp,old);(P/'ADOPTION.json').write_text(json.dumps({'status':'COMBINED88_PHYSICAL_INSTALLED_STARTUP_PENDING','base':'276b59c5983f669c54fd0affb090e8a6bbfb420c','source_sha256':{k:sha(b)for k,b in writes.items()},'newly_default_models':88,'additional_models_beyond_old_optional_selection':19,'new_sources':31,'new_garden_doors_locked':4,'new_units_or_capacity':0,'original_sources_or_player_changed':False,'unsafe_transit_primary_structure_private_services_or_full_build_accepted':False},indent=2)+'\n');print('COMBINED88_DEFAULT_PHYSICAL_INSTALLED',len(writes),'scopedpaths;0geometryreimports')
