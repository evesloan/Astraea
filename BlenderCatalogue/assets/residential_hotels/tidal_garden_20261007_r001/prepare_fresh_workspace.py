"""Prepare a separate writable Tidal rebuild; never writes this retained package.
Usage: python prepare_fresh_workspace.py /absolute/new/workspace
Then follow REBUILD_ORDER.txt there, with a coordinated Blender slot.
"""
from pathlib import Path
import sys,os,json,hashlib,shutil,ast
P=Path(__file__).resolve().parent
C=next((p for p in P.parents if (p/'catalogue_manifest.json').is_file()),None)
if C is None:
 C=Path(os.environ['ASTRAEA_CATALOGUE_ROOT']).resolve()
assert (C/'catalogue_manifest.json').is_file()
assert len(sys.argv)==2,'Supply one new absolute workspace directory'
W=Path(sys.argv[1]);assert W.is_absolute() and not W.exists(),'Never overwrite a surviving workspace'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
port=json.loads((P/'RETENTION_PORTABILITY.json').read_text())
for absolute,digest in port['source_dependencies'].items():
 old=Path(absolute);parts=old.parts;i=parts.index('astraea-catalogue-continuation-20261002');rel=Path(*parts[i+1:])
 if str(rel).startswith('assets/residential_hotels/tidal_garden_20261007_r001/'):continue
 assert sha(C/rel)==digest,rel
W.mkdir();S=W/'residential-neighborhood-courts-20261007';T=S/'tidal_garden_house';T.mkdir(parents=True)
source=P/'residential-neighborhood-courts-20261007/tidal_garden_house'
for name in ['source','qa']:
 (T/name).mkdir()
 for f in (source/name).glob('*.py'):shutil.copy2(f,T/name/f.name)
for name in ['TIDAL_GARDEN_85_PLACEMENT_MAP.json','REST_SLOT_PROVENANCE.json','DESIGN_PLAN.md','README.md']:shutil.copy2(source/name,T/name)
(T/'outputs').mkdir()
for rel in ['residential-neighborhood-courts-20261007/source/retained_court_primitives.py','residential-neighborhood-courts-20261007/HOUSE_BUILD_BOUNDARIES.json','residential-batch-neighborhood-20261006/qa/independent_review/geometry_decode.py']:
 dst=W/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(P/rel,dst)
for folder in ['receiving_source_inputs','residential-neighborhood-audit-20261007']:shutil.copytree(P/folder,W/folder)
shared=C/port['shared_generic_family_system'];(W/'residential-batch-neighborhood-20261006/scale_domestic_r011').symlink_to(shared,target_is_directory=True)
ref=W/'reference-window-privacy-20261006/515c9925-2338-485c-866d-c5378a82acb4(2).png';ref.parent.mkdir(parents=True);ref.symlink_to(C/'references/intimate/image(20261002-000722).png')
oldW='/workspace/scratch/375c2e438292';oldG='/workspace/shared/astraea-godot-production-20261003';oldC='/workspace/shared/astraea-catalogue-continuation-20261002'
repairs=[]
for f in T.rglob('*.py'):
 before=sha(f);text=f.read_text();text=text.replace(oldG,str(W/'receiving_source_inputs')).replace(oldC,str(C)).replace("sys.path.insert(0,'/workspace/scratch/375c2e438292/geometry-deps')",'').replace("sys.path.insert(0,str(W/'geometry-deps'))",'')
 ast.parse(text);f.write_text(text);repairs.append({'path':str(f.relative_to(W)),'source_sha256':before,'working_sha256':sha(f)})
mapfile=T/'TIDAL_GARDEN_85_PLACEMENT_MAP.json';text=mapfile.read_text().replace(oldW+'/residential-batch-neighborhood-20261006/scale_domestic_r011',str(W/'residential-batch-neighborhood-20261006/scale_domestic_r011'));mapfile.write_text(text)
(W/'REBUILD_ORDER.txt').write_text('Dependencies: Blender 4.3.2; ordinary Python with numpy, Shapely 2.1+, Pillow, matplotlib for source screens/plan drawing. No software is installed by this helper.\nUse the retained corrected mapping as supplied; do not rerun plan_interiors.py over it, because that script preserves the earlier pre-correction proposal.\n1. With a coordinated two-thread source slot: blender --background --threads 2 --python-exit-code 1 --python residential-neighborhood-courts-20261007/tidal_garden_house/source/build_interiors.py\n2. Source check_interiors.py and validate_bindings.py require their named outputs; run house planning before the final binding check.\n3. python residential-neighborhood-courts-20261007/tidal_garden_house/source/plan_house.py\n4. With the same coordinated slot: blender --background --threads 2 --python-exit-code 1 --python residential-neighborhood-courts-20261007/tidal_garden_house/source/build_house.py\n5. Source export/geometry/binding checks are in source/ and qa/. Their writes target only this new workspace.\nNo Game adoption or source completeness is implied. Exact old receiving inputs are reconstruction evidence; future integration must rebase to actual current owners. The historical reference paths in qa/review_geometry.py refer to the preserved document/reference inputs.\n')
(W/'WORKSPACE_PREPARATION.json').write_text(json.dumps({'status':'NEW_REBUILD_WORKSPACE_PREPARED_NO_BUILD_RUN','retained_package':str(P),'catalogue':str(C),'path_substitutions':repairs,'corrected_map_source_sha256':sha(source/'TIDAL_GARDEN_85_PLACEMENT_MAP.json'),'corrected_map_working_sha256':sha(mapfile),'retained_package_writes':False,'Game_writes':False},indent=2)+'\n')
print('NEW_REBUILD_WORKSPACE_PREPARED',W)
