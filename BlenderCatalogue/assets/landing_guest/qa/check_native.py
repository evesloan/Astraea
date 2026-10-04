"""Native GLB coordinate checks and collider positive/negative controls."""
import json,hashlib,importlib.util
from pathlib import Path
import numpy as np
from scipy.spatial import ConvexHull
from scipy.optimize import linprog
BASE=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('reader',BASE/'qa/validate_glb.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
def nodes(d):
 out={}
 def walk(i,parent):
  n=d['nodes'][i];m=parent@r.matrix(n);out[n['name']]=(n,m)
  for c in n.get('children',[]):walk(c,m)
 for i in d['scenes'][d.get('scene',0)]['nodes']:walk(i,np.eye(4))
 return out
def intersects(sh,lo,hi):
 if sh['type']=='box':return bool(np.all(np.maximum(lo,sh['min_source_m'])<np.minimum(hi,sh['max_source_m'])))
 h=ConvexHull(sh['points_source_m']);return bool(linprog([0,0,0],A_ub=h.equations[:,:3],b_ub=-h.equations[:,3],bounds=list(zip(lo,hi)),method='highs').success)
coll=json.loads((BASE/'collision_proposals.json').read_text());rows=[]
for f in sorted(BASE.glob('AST-LND-*.manifest.json')):
 rec=json.loads(f.read_text());d,b=r.read(BASE/rec['export']);ns=nodes(d);checks=[]
 for m in rec['physical_and_proposal_markers']:
  n,t=ns[m['name']];error=float(np.linalg.norm(t[:3,3]-m['gltf_m']));wrong=float(np.linalg.norm(t[:3,3]-m['source_m']));checks.append({'name':m['name'],'native_position_m':t[:3,3].tolist(),'error_m':error,'wrong_unconverted_position_error_m':wrong,'passes':error<1e-6})
 voids=[];controls=[]
 for v in rec['receiver_voids']:
  lo=np.array(v['min_source_m'])+1e-6;hi=np.array(v['max_source_m'])-1e-6;hits=[sh['name']for sh in coll[rec['catalogue_id']]['shapes']if intersects(sh,lo,hi)]
  bad={'type':'box','min_source_m':lo.tolist(),'max_source_m':hi.tolist()};rejected=intersects(bad,lo,hi)
  voids.append({'name':v['name'],'whole_volume_collision_hits':hits,'intentionally_filled_void_rejected':rejected,'passes':not hits and rejected})
 for sh in coll[rec['catalogue_id']]['shapes']:
  p=(np.array(sh['min_source_m'])+sh['max_source_m'])/2 if sh['type']=='box' else np.mean(sh['points_source_m'],axis=0);det=intersects(sh,p-1e-5,p+1e-5);controls.append({'name':sh['name'],'structural_interior_positive_probe':p.tolist(),'detected':det})
 rows.append({'catalogue_id':rec['catalogue_id'],'glb_sha256':hashlib.sha256((BASE/rec['export']).read_bytes()).hexdigest(),'marker_checks':checks,'void_checks':voids,'collision_positive_controls':controls,'collision_shape_count':len(controls),'passes':all(x['passes']for x in checks+voids)and all(x['detected']for x in controls)})
out={'scope':'Actual GLB native hierarchy and convex/AABB intersection proposals, not engine collision acceptance','assets':rows,'all_passed':all(x['passes']for x in rows)};(BASE/'qa/native_coordinates_and_voids.json').write_text(json.dumps(out,indent=2)+'\n');print('NATIVE_AND_VOIDS_PASS',out['all_passed']);assert out['all_passed']
