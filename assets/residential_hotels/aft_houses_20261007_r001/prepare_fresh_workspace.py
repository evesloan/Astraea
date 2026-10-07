"""Prepare a new writable reconstruction using the exact retained house PLANs."""
from pathlib import Path
import os,sys,json,shutil,hashlib,ast
P=Path(__file__).resolve().parent;C=next((p for p in P.parents if(p/'catalogue_manifest.json').is_file()),None)
if C is None:C=Path(os.environ['ASTRAEA_CATALOGUE_ROOT']).resolve()
assert(C/'catalogue_manifest.json').is_file();assert len(sys.argv)==2;W=Path(sys.argv[1]);assert W.is_absolute()and not W.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();port=json.loads((P/'RETENTION_PORTABILITY.json').read_text());oldW='/workspace/scratch/375c2e438292';oldG='/workspace/shared/astraea-godot-production-20261003';oldC='/workspace/shared/astraea-catalogue-continuation-20261002'
for src,h in port['source_dependencies'].items():
 rel=Path(src).relative_to(oldC)
 if rel.is_relative_to('assets/residential_hotels/aft_houses_20261007_r001'):continue
 assert sha(C/rel)==h
W.mkdir();S=W/'residential-neighborhood-courts-20261007';S.mkdir()
for sp in port['source_components']:
 src=P/'residential-neighborhood-courts-20261007'/sp['folder'];dst=S/sp['folder'];dst.mkdir()
 for p in src.rglob('*'):
  rel=p.relative_to(src)
  if not p.is_file()or rel.parts[0]=='outputs':continue
  q=dst/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 (dst/'outputs'/sp['house_revision']).mkdir(parents=True);shutil.copy2(src/'outputs'/sp['house_revision']/'PLAN.json',dst/'outputs'/sp['house_revision']/'PLAN.json')
for folder in ['receiving_source_inputs','residential-neighborhood-audit-20261007']:shutil.copytree(P/folder,W/folder)
for rel in ['residential-neighborhood-courts-20261007/source/retained_court_primitives.py','residential-neighborhood-courts-20261007/HOUSE_BUILD_BOUNDARIES.json','residential-batch-neighborhood-20261006/qa/independent_review/geometry_decode.py']:
 q=W/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(P/rel,q)
shared=C/port['shared_generic_family_system'];(W/'residential-batch-neighborhood-20261006/scale_domestic_r011').symlink_to(shared,target_is_directory=True)
ref=W/'reference-window-privacy-20261006/515c9925-2338-485c-866d-c5378a82acb4(2).png';ref.parent.mkdir();ref.symlink_to(C/'references/intimate/image(20261002-000722).png')
changes=[]
for sp in port['source_components']:
 for p in(S/sp['folder']).rglob('*'):
  if not p.is_file()or p.suffix not in['.py','.json']:continue
  old=sha(p);text=p.read_text().replace(oldW,str(W)).replace(oldG,str(W/'receiving_source_inputs')).replace(oldC,str(C))
  if p.suffix=='.py':
   text=text.replace("sys.path.insert(0,str(W/'geometry-deps'))",'').replace("sys.path.insert(0,'"+str(W)+"/geometry-deps')",'');ast.parse(text)
  else:json.loads(text)
  p.write_text(text);changes.append({'file':str(p.relative_to(W)),'retained_sha256':old,'fresh_path_sha256':sha(p)})
(W/'REBUILD_ORDER.txt').write_text('Requires Blender4.3.2 and Python numpy/Shapely2.1+/Pillow/matplotlib; no dependency installation occurs. Use existing corrected maps and exact retained PLAN files. Do not regenerate old plan scripts over current corrections. In a coordinated two-thread source slot, run source/build_interiors.py then source/build_house.py for each house. Pass --background --threads 2 --python-exit-code 1 using separate arguments to Blender. The current PLANs preserve exact accepted source corrections and source reservations; retention-time receiving snapshots are context, not a future live integration baseline. Copied previous QA/summary files are historical evidence until new checks run. No Game or original source overwrite.\n')
(W/'WORKSPACE_PREPARATION.json').write_text(json.dumps({'status':'NEW_SOURCE_WORKSPACE_PREPARED_NO_ENGINE_RUN','current_plan_reconstruction':True,'source_components':port['source_components'],'path_only_fresh_changes':changes,'retained_sources_unchanged':True,'Game_changes':False},indent=2)+'\n');print('NEW_AFT_SOURCE_WORKSPACE_PREPARED',W)
