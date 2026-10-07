from pathlib import Path
import ast,json,sys,hashlib,numpy as np
sys.path.insert(0,'/workspace/scratch/375c2e438292/geometry-deps')
from shapely.geometry import Polygon
from shapely import constrained_delaunay_triangles
B=Path(__file__).parent;S=B.parent;C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');p=S/'pool-opposite-gallery-proposal001/source_blockin001/review_core.py';tree=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='triang_face'],type_ignores=[]),str(p),'exec'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();plan=json.loads((B/'CORE_PLAN.json').read_text());rows={}
for r in plan['parts']:
 vv=np.array(r['vertices_xyz']);ts=[]
 for f in r['faces']:
  for t in triang_face(r['vertices_xyz'],f):
   ids=[]
   for v in t:
    ds=np.linalg.norm(vv-v,axis=1);i=int(ds.argmin());assert ds[i]<1e-8;ids.append(i)
   ts.append(ids)
 rows[r['name']]=ts
(B/'SOURCE_TRIANGLES.json').write_text(json.dumps({'plan_sha256':sha(B/'CORE_PLAN.json'),'triangulation':'Constrained face triangulation with Newell orientation; original coordinates unchanged. Avoids Blender collinear ngon tessellation differences.','parts':rows},indent=2)+'\n')
files=[B/n for n in ['SOURCE_BRIEF.md','CORE_PLAN.json','PURE_GEOMETRY_REVIEW.json','SOURCE_TRIANGLES.json','build_source.py','reopen_source.py','run_source.py','artwork/ORIGINAL_GALLERY_DIRECTORY.png','artwork/CONTENT_MANIFEST.json']]+[Path(plan['source_base']),S/'pool-east-gallery-canopy-correction001/revision001/build_correction.py',S/'pool-opposite-gallery-proposal001/source_blockin001/build_core.py',S/'pool-opposite-gallery-proposal001/reference_programme001/programme_common.py']+[Path(r['source'])for r in plan['retained_furniture']]
for n in ['00','03']:
 files+=[C/f'assets/grand_pool_first_pass/architectural_composition/feature_layers_next/planting/full_mass001/candidate_v001/source/AST-BOT-002_pool_loggia_mass_{n}.blend',C/f'assets/grand_pool_first_pass/comfort_greenery/greenery/candidate_v001/source/AST-BOT-003_pool_basal_{n}.blend']
(B/'SOURCE_JOB_PINS.json').write_text(json.dumps({'status':'SOURCE_ONLY_TWO_THREAD_BUILD_REOPEN','inputs':{str(p):sha(p)for p in files},'old_source_objects_preserved_except_explicit_canopy_mount_subset':True},indent=2)+'\n')
print('Frozen',len(files),'source inputs')
