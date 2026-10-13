from pathlib import Path
import json,zipfile,hashlib
C=Path(__file__).parent;R=Path('/workspace/astraea-protected-integration-20261012/Game');P=C/'g4_theater_receiving_staging';sha=lambda b:hashlib.sha256(b).hexdigest();assert json.loads((C/'G4_THEATER_IMPORT_RECEIPT.json').read_text())['passed'];p=json.loads((R/'data/architecture/GROUP4_THEATER_UPPER_SOURCE_CANDIDATE.json').read_text());root=p['model_root'][6:];writes={}
for q in (P/root).iterdir():
 if q.is_file():writes[str(q.relative_to(P))]=q.read_bytes()
for q in (P/'.godot/imported').iterdir():
 if q.is_file():writes[str(q.relative_to(P))]=q.read_bytes()
for spec in p['exports']:assert sha(writes[root+spec['file']])==spec['sha256']
code=(R/'scripts/group4_theater_upper_approaches.gd').read_text();anchor=' var root:=Node3D.new();root.name="Group4TheaterUpperExteriorProposal";parent.add_child(root)';assert code.count(anchor)==1;code=code.replace(anchor,' for spec in p.exports:\n  assert(FileAccess.get_sha256(p.model_root+spec.file)==spec.sha256)\n'+anchor).replace('light.shadow_enabled=true;light.visible=false','light.shadow_enabled=false;light.visible=false');writes['scripts/group4_theater_upper_approaches.gd']=code.encode();writes['data/architecture/GROUP4_THEATER_UPPER_SOURCE_CANDIDATE.json']=(R/'data/architecture/GROUP4_THEATER_UPPER_SOURCE_CANDIDATE.json').read_bytes()
with zipfile.ZipFile(C/'G4_THEATER_RECEIVING_CANDIDATE_OVERLAY.zip','w',zipfile.ZIP_DEFLATED,compresslevel=1)as z:
 for k,b in writes.items():z.writestr(k,b)
r={'status':'CANDIDATE_ONLY_RECEIVING_PENDING','exports':[{k:v for k,v in row.items()if k!='policies'}for row in p['exports']],'owned_native_floor_m2':366,'sources':6,'model_preflight_before_mutation':True,'original_upper_doors_still_closed_inactive':True,'original_capacity':2200,'new_capacity':0,'new_load_approval':False,'consumer_script_preimage_sha256':sha((R/'scripts/group4_theater_upper_approaches.gd').read_bytes()),'consumer_script_sha256':sha(code.encode()),'portable_files':[k for k in writes if not k.startswith('.godot/')],'production_adoption':False};(C/'G4_THEATER_CANDIDATE.json').write_text(json.dumps(r,indent=2)+'\n');print('candidate',len(writes),'paths')
