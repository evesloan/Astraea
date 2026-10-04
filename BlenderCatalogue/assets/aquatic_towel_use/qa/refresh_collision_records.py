"""Refresh collision-only declarations while preserving frozen source/GLB bytes."""
from pathlib import Path
import json,hashlib,runpy
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
protected={str(p.relative_to(ROOT)):sha(p) for folder,pattern in [('source','*.blend'),('exports','*.glb')] for p in (ROOT/folder).glob(pattern)}
mod=runpy.run_path(str(ROOT/'source/build_towel_use.py'));rows=[]
for build in (mod['dry'],mod['returned']):
 info=build();asset=info['catalogue_id'];globals_=build.__globals__
 collision={'catalogue_id':asset,'coordinate_frame':'Blender source metres; shape and movement coordinates require native C mapping','status':'Component geometric proposals only, no engine physics validation','shapes':globals_['COL'],'clear_volumes':info['clear_volumes'],'motion':info.get('motion'),'limitations':info['collision_notes']}
 (ROOT/f'{asset}.collision_proposal.json').write_text(json.dumps(collision,indent=2)+'\n')
 path=ROOT/f'{asset}.manifest.json';old=json.loads(path.read_text());old['collision_notes']=info['collision_notes'];old['generator_sha256']=sha(ROOT/'source/build_towel_use.py');path.write_text(json.dumps(old,indent=2)+'\n');rows.append(old)
mod['dependencies']()
(ROOT/'manifest.json').write_text(json.dumps({'family':'Aquatic towel-use components','batch':'14','unique_design_count':2,'state_derivatives_count_as_designs':False,'assets':[{k:v for k,v in r.items() if k!='parts'} for r in rows]},indent=2)+'\n')
assert all(sha(ROOT/p)==h for p,h in protected.items())
(ROOT/'qa/collision_only_amendment.json').write_text(json.dumps({'scope':'Only collision declarations/metadata and reproducible generator collision records changed','frozen_source_and_export_hashes':protected,'all_protected_bytes_unchanged':True,'generator_sha256':sha(ROOT/'source/build_towel_use.py')},indent=2)+'\n')
print('COLLISION_ONLY_REFRESH_SOURCE_EXPORT_BYTES_UNCHANGED')
