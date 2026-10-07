"""Create a new writable source reconstruction beside an installed Catalogue.
Run: python prepare_fresh_workspace.py /absolute/new/workspace
This prepares source only. It does not run Blender, install dependencies or edit Game.
"""
from pathlib import Path
import json,sys,os,shutil,hashlib,ast
P=Path(__file__).resolve().parent;C=next((p for p in P.parents if (p/'catalogue_manifest.json').is_file()),None)
if C is None:C=Path(os.environ['ASTRAEA_CATALOGUE_ROOT']).resolve()
assert(C/'catalogue_manifest.json').is_file();assert len(sys.argv)==2;W=Path(sys.argv[1]);assert W.is_absolute()and not W.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();port=json.loads((P/'RETENTION_PORTABILITY.json').read_text());oldW='/workspace/scratch/375c2e438292';oldC='/workspace/shared/astraea-catalogue-continuation-20261002';oldG='/workspace/shared/astraea-godot-production-20261003'
for source,h in port['source_dependencies'].items():assert sha(C/Path(source).relative_to(oldC))==h
W.mkdir();S=W/'residential-neighborhood-courts-20261007';S.mkdir()
for row in port['source_components']:
 src=P/'residential-neighborhood-courts-20261007'/row['folder'];dst=S/row['folder'];dst.mkdir()
 for p in src.rglob('*'):
  rel=p.relative_to(src)
  if not p.is_file()or rel.parts[0]=='outputs':continue
  q=dst/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 (dst/'outputs').mkdir()
for folder in ['receiving_source_inputs','residential-neighborhood-audit-20261007','reference-window-privacy-20261006']:
 if(P/folder).is_dir():shutil.copytree(P/folder,W/folder)
for rel in ['residential-neighborhood-courts-20261007/HOUSE_BUILD_BOUNDARIES.json','residential-batch-neighborhood-20261006/qa/independent_review/geometry_decode.py']:
 q=W/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(P/rel,q)
shared=C/port['shared_generic_family_system'];q=W/'residential-batch-neighborhood-20261006/scale_domestic_r011';q.symlink_to(shared,target_is_directory=True)
changes=[]
for row in port['source_components']:
 root=S/row['folder']
 for p in root.rglob('*'):
  if not p.is_file()or p.suffix not in ['.py','.json']:continue
  before=sha(p);s=p.read_text();s=s.replace(oldW,str(W)).replace(oldG,str(W/'receiving_source_inputs')).replace(oldC,str(C))
  if p.suffix=='.py':
   s=s.replace("sys.path.insert(0,str(W/'geometry-deps'))",'').replace("sys.path.insert(0,'"+str(W)+"/geometry-deps')",'');ast.parse(s)
  else:json.loads(s)
  p.write_text(s);changes.append({'file':str(p.relative_to(W)),'retained_sha256':before,'fresh_path_sha256':sha(p)})
(W/'REBUILD_ORDER.txt').write_text('Requires Blender4.3.2 and ordinary Python numpy/Shapely2.1+/Pillow/matplotlib. Nothing is installed by this helper. Use the supplied corrected maps; do not regenerate earlier plan scripts over them. All retained QA and RESULT files copied into this workspace are predecessor evidence, not a pass for new output.\nBuild each component with a coordinated two-thread source slot:\nblender --background --threads 2 --python-exit-code 1 --python residential-neighborhood-courts-20261007/star_atlas_interiors/source/build_star_atlas.py\nblender --background --threads 2 --python-exit-code 1 --python residential-neighborhood-courts-20261007/night_garden_interiors/source/build_night_garden.py\nThen use the component current source checks and verify new hashes. Receiving owner snapshots are exact reconstruction inputs, not live future integration authority. No Game or Catalogue writes are authorized by these scripts.\n')
(W/'WORKSPACE_PREPARATION.json').write_text(json.dumps({'status':'NEW_WORKSPACE_PREPARED_NO_BUILD_RUN','catalogue':str(C),'retained_package':str(P),'source_components':port['source_components'],'path_only_fresh_changes':changes,'source_packages_unchanged':True,'Game_writes':False},indent=2)+'\n');print('NEW_WORKSPACE_PREPARED_NO_BUILD_RUN',W)
