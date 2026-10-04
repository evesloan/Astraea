"""Measured finite samples of collision surface inflation against actual source solids."""
from pathlib import Path
import sys,json,hashlib,itertools,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch11'
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import Hull,inside_mesh,nearest_distances,sample_triangles
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
selected=set(sys.argv[1:]);prior=OUT/'independent_collision_profile_review.json';rows=[x for x in json.loads(prior.read_text())['assets'] if x['catalogue_id'] not in selected] if selected and prior.exists() else []
for family in ['landing_guest','landing_service']:
 cp=ROOT/'assets'/family/'collision_proposals.json';d=json.loads(cp.read_text())
 for ident,c in d.get('assets',d).items():
  if selected and ident not in selected:continue
  rp=OUT/f'independent_source_{ident}.json';r=json.loads(rp.read_text());assert sha(ROOT/r['path'])==r['sha256'];g=np.load(ROOT/r['geometry_cache']);t=g['triangles'];labels=g['object_names'];shapes=[]
  for s in c['shapes']:
   pts=np.asarray(list(itertools.product(*zip(s['min_source_m'],s['max_source_m'])))) if s['type']=='box'else np.asarray(s.get('points_source_m',s.get('vertices_source_m')));h=Hull(pts);q,step=sample_triangles(h.tris,.035);inside=np.zeros(len(q),bool)
   for part in np.unique(labels):
    tr=t[labels==part];lo=tr.reshape(-1,3).min(axis=0);hi=tr.reshape(-1,3).max(axis=0);ids=np.where(((q>=lo)&(q<=hi)).all(axis=1)&~inside)[0]
    if len(ids):inside[ids]=inside_mesh(q[ids],tr)
   outside=q[~inside];dist=nearest_distances(outside,t);maximum=float(dist.max()) if len(dist)else 0.;example=outside[int(np.argmax(dist))].tolist() if len(dist)else None
   shapes.append({'name':s['name'],'shape_type':s['type'],'sample_count':len(q),'maximum_grid_edge_step_m':step,'sampled_max_external_inflation_m':maximum,'maximum_sample_source_m':example,'author_approximation_limit_m':s.get('conservative_empty_corner_limit_m'),'author_reason':s.get('reason')})
  row={'catalogue_id':ident,'source_sha256':r['sha256'],'collision_sha256':sha(cp),'shapes':shapes,'sampled_max_external_inflation_m':max(x['sampled_max_external_inflation_m']for x in shapes)};rows.append(row);print(ident,[(x['name'],round(x['sampled_max_external_inflation_m'],5))for x in shapes])
(OUT/'independent_collision_profile_review.json').write_text(json.dumps({'executed_script_sha256':sha(Path(__file__)),'assets':rows,'limits':'Finite hull-surface samples at <=35mm grid edge. Values are observed sample maxima, not certified continuous upper bounds. Source-solid interior points are excluded. Useful declared voids receive separate continuous triangle-box/convex feasibility checks. No runtime physics or swept actor/cart claims.'},indent=2)+'\n')
