"""Finite independent collision profile measurements; useful complete voids are checked separately."""
from pathlib import Path
import json,sys,hashlib,numpy as np
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch15';sys.path.insert(0,str(OUT));from independent_collision_adapters import expand
from independent_collision_geometry import sample_triangles,inside_mesh,nearest_distances
def adaptive_surface_samples(tris,spacing):
 stack=list(tris);points=[];step=0.
 while stack:
  t=stack.pop();lengths=[np.linalg.norm(t[i]-t[j])for i,j in [(0,1),(1,2),(2,0)]];k=int(np.argmax(lengths));i,j=[(0,1),(1,2),(2,0)][k]
  if lengths[k]<=spacing:points.extend(t);step=max(step,lengths[k]);continue
  other=3-i-j;mid=(t[i]+t[j])/2;stack.append(np.array([t[i],mid,t[other]]));stack.append(np.array([mid,t[j],t[other]]))
 return np.unique(np.round(points,9),axis=0),step
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();families=sys.argv[1:]or['crew_rest','crew_personal'];rows=[]
for family in families:
 for mp in sorted((ROOT/'assets'/family).glob('AST-*.manifest.json')):
  m=json.loads(mp.read_text());ident=m['catalogue_id'];rp=OUT/f'independent_source_{ident}.json';s=json.loads(rp.read_text());assert sha(ROOT/s['path'])==s['sha256'];a=np.load(ROOT/s['geometry_cache']);tri=a['triangles'];labels=a['object_names'];parts={str(x):tri[labels==x]for x in np.unique(labels)}
  cp=mp.parent/m['collision_proposal_file'];c=json.loads(cp.read_text());c=c.get('assets',c)[ident];hulls=[h for rec in c['shapes']for h in expand(rec)];profiles=[];excluded=[x for x in c['shapes']if not expand(x)]
  for rec in c['shapes']:
   hs=[h for h in hulls if h.record['name']==rec['name']];
   if not hs:continue
   ht=np.concatenate([h.tris for h in hs]);pts,step=adaptive_surface_samples(ht,.060);inside=np.zeros(len(pts),bool)
   for name,t in parts.items():
    lo=t.min((0,1));hi=t.max((0,1));ids=np.where(((pts>=lo-1e-7)&(pts<=hi+1e-7)).all(1))[0]
    if len(ids):inside[ids]|=inside_mesh(pts[ids],t)
   ext=pts[~inside];dist=nearest_distances(ext,tri)if len(ext)else np.array([0.]);j=int(dist.argmax());profiles.append({'name':rec['name'],'proposal_type':rec['type'],'review_subshape_count':len(hs),'review_shape_approximations':[{k:v for k,v in h.record.items()if k.startswith('review_')and k!='review_subshape_index'}for h in hs if any(k.startswith('review_')and k!='review_subshape_index'for k in h.record)],'author_declared_allowance_m':rec.get('conservative_empty_corner_limit_m',rec.get('max_profile_error_m')),'purpose_covered_parts':rec.get('covered_parts'),'approximation_note':rec.get('approximation_note'),'sample_count':len(pts),'max_sample_grid_edge_m':step,'sampled_max_external_inflation_m':float(dist.max()),'worst_sample_source_m':ext[j].tolist()if len(ext)else None})
  coverage=[];ht=np.concatenate([h.tris for h in hulls])
  for name,t in parts.items():
   # Corners, edge midpoints, centroids catch omitted small parts without claiming full coverage.
   pts=np.unique(np.round(np.concatenate([t.reshape(-1,3),t.mean(1),((t[:,0]+t[:,1])/2),((t[:,1]+t[:,2])/2),((t[:,2]+t[:,0])/2)]),9),axis=0);inside=np.any([h.inside(pts)for h in hulls],axis=0);ext=pts[~inside];dist=nearest_distances(ext,ht)if len(ext)else np.array([0.]);coverage.append({'part':name,'sample_count':len(pts),'samples_outside_proposal':int((~inside).sum()),'sampled_max_distance_outside_proposal_m':float(dist.max())})
  result={'passed':all(x['author_declared_allowance_m']is None or x['sampled_max_external_inflation_m']<=x['author_declared_allowance_m']+1e-6 for x in profiles),'catalogue_id':ident,'source_sha256':s['sha256'],'source_audit_sha256':sha(rp),'collision_sha256':sha(cp),'collision_path':str(cp.relative_to(ROOT)),'proposal_shape_count':len(hulls),'top_level_geometry_records':sum(bool(expand(x))for x in c['shapes']),'excluded_geometry_declarations':excluded,'review_convex_subshape_count':len(hulls),'profiles':profiles,'visual_part_sampled_coverage':coverage,'sampled_max_external_inflation_m':max(x['sampled_max_external_inflation_m']for x in profiles),'limits':['Surface inflation is measured with a finite adaptive triangle-vertex mesh no longer than60mm; this is not a continuous distance maximum.','Source coverage samples include every actual triangle vertex, edge midpoint and centroid. They are not a continuous coverage proof. Thin symbol/stock/attachment geometry can intentionally remain noncolliding.','Authored boxes and explicit convex-point hulls are read directly. Curtain neutral panels expand into24 independent thin-normal prisms at the stated pose. Track capsule uses a conservative spherical-grid hull with radial inflation r*(sec(pi/16)-1); this review approximation is separately reported.','Actual complete useful voids and removal paths have separate exact intersection tests. No collision-engine adoption or performance result follows.'],'executed_script_sha256':sha(Path(__file__))};rows.append(result);print(ident,'actual shapes',len(hulls),'external inflation',result['sampled_max_external_inflation_m'],'larger underreach',[(x['part'],x['sampled_max_distance_outside_proposal_m'])for x in coverage if x['sampled_max_distance_outside_proposal_m']>.005],flush=True)
  (OUT/f'independent_collision_profile_{ident}.json').write_text(json.dumps(result,indent=2)+'\n')
