"""Finite optional actor-proxy undercoverage observations from actual frozen source triangles."""
from pathlib import Path
import sys,itertools,math,numpy as np
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'qa/batch08'))
from independent_collision_geometry import Hull,nearest_distances,triangle_uncovered_area

def matrix(move,fraction):
 if move['kind']=='translation':return np.eye(3),np.array(move['axis_source'])*move['travel']*fraction
 axis=np.array(move['axis_source'],float);axis/=np.linalg.norm(axis);angle=math.radians(move['travel'])*fraction;x,y,z=axis;K=np.array([[0,-z,y],[z,0,-x],[-y,x,0]]);R=np.eye(3)+math.sin(angle)*K+(1-math.cos(angle))*(K@K);p=np.array(move['pivot_source_m']);return R,p-R@p

def transform(points,owner,manifest,pose):
 move=next((x for x in manifest['motion_records']if x['root']==owner),None)
 if move is None:return np.asarray(points)
 R,t=matrix(move,pose[owner]);return np.asarray(points)@R.T+t

def surface_samples(tris):
 return np.unique(np.round(np.concatenate([tris.reshape(-1,3),tris.mean(1),(tris[:,0]+tris[:,1])/2,(tris[:,1]+tris[:,2])/2,(tris[:,2]+tris[:,0])/2]),10),axis=0)

def inspect(source_triangles,labels,manifest,selected_shapes):
 parts={str(n):source_triangles[labels==n]for n in np.unique(labels)};owners={n:next((x['root']for x in manifest['motion_records']if n in x['semantic_parts']),manifest['catalogue_id'])for n in parts};retained={n for x in selected_shapes for n in x['covered_parts']};fractions=[0,.001,.25,.5,.75,1];poses=[dict(zip([x['root']for x in manifest['motion_records']],f))for f in itertools.product(fractions,repeat=len(manifest['motion_records']))];samples={n:surface_samples(t)for n,t in parts.items()};observations=[];perpart={n:{'part':n,'retained':n in retained,'sample_count_per_pose':len(samples[n]),'maximum_observed_undercoverage_m':0.,'worst_pose_fractions':None,'worst_sample_source_m':None}for n in parts}
 for pose in poses:
  hulls=[Hull(transform(x['points_source_m'],x['parent_root'],manifest,pose),x)for x in selected_shapes];ht=np.concatenate([x.tris for x in hulls]);summary={'pose_fractions':pose,'maximum_observed_undercoverage_m':0.}
  for name,points in samples.items():
   pts=transform(points,owners[name],manifest,pose);inside=np.any([h.inside(pts)for h in hulls],axis=0);ex=pts[~inside];ds=nearest_distances(ex,ht)if len(ex)else np.array([0.]);value=float(ds.max());summary['maximum_observed_undercoverage_m']=max(summary['maximum_observed_undercoverage_m'],value)
   if value>perpart[name]['maximum_observed_undercoverage_m']:
    perpart[name].update(maximum_observed_undercoverage_m=value,worst_pose_fractions=pose,worst_sample_source_m=ex[int(ds.argmax())].tolist())
  observations.append(summary)
 # Every retained source triangle is continuously covered by its literal unchanged declared hull.
 exact=[]
 for name in sorted(retained):
  hs=[Hull(x['points_source_m'],x)for x in selected_shapes if name in x['covered_parts']];area=sum(triangle_uncovered_area(t,hs)for t in parts[name]);exact.append({'part':name,'continuous_uncovered_surface_area_m2':float(area),'pass':area<1e-7})
 return {'pose_fractions':fractions,'pose_count':len(poses),'per_pose_observations':observations,'per_part_undercoverage':list(perpart.values()),'retained_part_complete_surface_coverage':exact,'maximum_observed_undercoverage_m':max(x['maximum_observed_undercoverage_m']for x in observations),'retained_part_coverage_passed':all(x['pass']for x in exact),'limits':['Every actual source triangle vertex, edge midpoint and centroid is inspected at the stated finite pose fractions. This is not continuous undercoverage, a full Hausdorff distance, collision-engine adoption or performance acceptance.','Complete retained-triangle union subtraction is invariant under the inherited rigid owner transform; primary shape surfaces are unchanged.','All complete empty-volume/motion nonintrusion proofs are inherited by exact subset inclusion, not established merely by these finite observations.']}
