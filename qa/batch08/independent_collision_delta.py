"""Compare added hull expansion against the exact original compound union."""
from pathlib import Path
import sys,json,hashlib,numpy as np
from independent_collision_geometry import Hull,nearest_distances,sample_triangles
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch08'
prior=ROOT/'qa/batch08/counter_collision_revision/original_inputs/assets/hospitality_counters/collision_proposals.json'
current=ROOT/sys.argv[1];old=json.loads(prior.read_text());new=json.loads(current.read_text());results=[]
for ident,r in new.items():
 old_h=[Hull(p['source_points_m'],p) for p in old[ident]['proposals']];new_h=[Hull(p['source_points_m'],p) for p in r['proposals']];retained=[];rows=[]
 for h in old_h:
  candidates=[n for n in new_h if h.record['semantic_part'] in n.record.get('semantic_parts',[n.record['semantic_part']]) and n.record['functional_group']==h.record['functional_group']]
  retained.append(any(n.inside(h.points).all() for n in candidates))
 for h in new_h:
  names=h.record.get('semantic_parts',[h.record['semantic_part']]);candidates=[o for o in old_h if o.record['semantic_part'] in names];oldtris=np.concatenate([c.tris for c in candidates])
  if ident.endswith('002'):points,spacing=sample_triangles(h.tris,.02)
  else:
   weights=np.array([(i/12,j/12,1-(i+j)/12) for i in range(13) for j in range(13-i)])
   points=np.unique(np.round(np.einsum('wi,tij->twj',weights,h.tris).reshape(-1,3),9),axis=0);spacing=None
  inside=np.zeros(len(points),bool)
  for o in candidates:inside|=o.inside(points)
  idx=np.where(~inside)[0];dist=np.zeros(len(points))
  if len(idx):dist[idx]=nearest_distances(points[idx],oldtris)
  k=int(np.argmax(dist));rows.append({'part':h.record['semantic_part'],'section':h.record.get('section'),'sample_count':len(points),'grid_edge_m':spacing,'sampled_max_added_outside_original_compound_m':float(dist[k]),'worst_source_point_m':points[k].tolist()})
 out={'id':ident,'original_hulls':len(old_h),'new_hulls':len(new_h),'every_original_hull_fully_contained_in_matching_new_hull':all(retained),'per_new_hull':rows,'sampled_max_added_expansion_m':max(x['sampled_max_added_outside_original_compound_m'] for x in rows)};results.append(out);print(ident,out['sampled_max_added_expansion_m'],flush=True)
report={'old_path':str(prior.relative_to(ROOT)),'old_sha256':hashlib.sha256(prior.read_bytes()).hexdigest(),'new_path':str(current.relative_to(ROOT)),'new_sha256':hashlib.sha256(current.read_bytes()).hexdigest(),'results':results,'limits':'All original hull-point containment in one new convex hull proves the old compound is continuously covered. Added error is an actual sampled distance to the old compound union, including face interiors; finite surface samples do not prove a global Hausdorff maximum.'}
out=OUT/('independent_collision_delta_'+sys.argv[2]+'.json');out.write_text(json.dumps(report,indent=2)+'\n')
