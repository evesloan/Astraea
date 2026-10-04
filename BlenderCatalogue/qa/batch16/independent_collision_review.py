"""Review actual collision compounds against semantic surfaces and explicit numeric limits."""
from pathlib import Path
import sys,json,hashlib,itertools,numpy as np
from scipy.spatial import cKDTree,ConvexHull
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch16'
sys.path.insert(0,str(ROOT/'qa/batch15'));from independent_collision_adapters import expand
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import Hull,inside_mesh,nearest_distances,triangle_uncovered_area
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();TOL=.00002

def samples(tris,spacing=.06):
 stack=list(tris);points=[];step=0
 while stack:
  t=stack.pop();pairs=[(0,1),(1,2),(2,0)];lengths=[np.linalg.norm(t[i]-t[j])for i,j in pairs];k=int(np.argmax(lengths));i,j=pairs[k]
  if lengths[k]<=spacing:points.extend(t);step=max(step,lengths[k]);continue
  o=3-i-j;m=(t[i]+t[j])/2;stack.extend([np.array([t[i],m,t[o]]),np.array([m,t[j],t[o]])])
 return np.unique(np.round(points,9),axis=0),step

def meshconvex(t):
 v=np.unique(t.reshape(-1,3),axis=0);h=Hull(v);cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(cross,axis=1)/2;norm=cross/np.maximum(area*2,1e-30)[:,None];cen=t.mean(1);signed=float(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6);plane=cen@h.planes[:,:3].T+h.planes[:,3];d=abs(plane).min(1);score=norm@h.planes[:,:3].T;goodnormal=np.max(np.where(abs(plane)<TOL,score,-np.inf),axis=1)
 es=t[:,[[0,1],[1,2],[2,0]]].reshape(-1,2,3).copy();flip=np.asarray([tuple(x[0])>tuple(x[1])for x in es]);es[flip]=es[flip,::-1];_,counts=np.unique(np.round(es,8),axis=0,return_counts=True)
 r={'triangles':len(t),'closed_edge_manifold':bool(np.all(counts==2)),'nondegenerate':bool(np.all(area>1e-12)),'positive_signed_volume_m3':signed,'convex_hull_volume_m3':float(h.hull.volume),'volume_difference_m3':abs(signed-h.hull.volume),'maximum_centroid_distance_from_convex_boundary_m':float(d.max()),'minimum_outward_normal_dot':float(goodnormal.min()),'surface_area_difference_m2':abs(float(area.sum())-float(h.hull.area))};r['exact_convex_surface']=r['closed_edge_manifold']and r['nondegenerate']and signed>0 and r['volume_difference_m3']<1e-7 and r['surface_area_difference_m2']<1e-6 and d.max()<TOL and goodnormal.min()>.99999;return r,h
rows=[]
for family in sys.argv[1:]or['auditorium_arrival','auditorium_use']:
 for mp in sorted((ROOT/'assets'/family).glob('AST-*.manifest.json')):
  m=json.loads(mp.read_text());ident=m['catalogue_id'];sp=mp.parent/m['source'];rp=OUT/f'independent_source_{ident}.json';s=json.loads(rp.read_text());assert sha(sp)==s['sha256'];a=np.load(ROOT/s['geometry_cache']);tri=a['triangles'];labels=a['object_names'];parts={str(n):tri[labels==n]for n in np.unique(labels)};cp=mp.parent/m['collision_proposal_file'];cs=json.loads(cp.read_text());cs=cs.get('assets',cs)[ident];records=cs['shapes'];hulls=[h for rec in records for h in expand(rec)];profiles=[];claims=[];geometry={}
  for name,t in parts.items():
   try:geometry[name]=meshconvex(t)[0]
   except Exception as e:geometry[name]={'exact_convex_surface':False,'error':str(e)}
  for rec in records:
   hs=expand(rec)
   if not hs:continue
   ht=np.concatenate([h.tris for h in hs]);pts,step=samples(ht);inside=np.zeros(len(pts),bool)
   for name,t in parts.items():
    ids=np.where(((pts>=t.min((0,1))-1e-7)&(pts<=t.max((0,1))+1e-7)).all(1))[0]
    if len(ids):inside[ids]|=inside_mesh(pts[ids],t)
   ext=pts[~inside];ds=nearest_distances(ext,tri)if len(ext)else np.array([0]);allow=rec.get('allowed_inflation_m',rec.get('maximum_outward_inflation_m',rec.get('conservative_empty_corner_limit_m',rec.get('max_profile_error_m'))));cov=rec.get('covered_parts',[]);exact=False;verror=None
   if len(cov)==1 and cov[0]in parts and len(hs)==1:
    p=parts[cov[0]].reshape(-1,3);q=hs[0].points;verror=float(max(cKDTree(p).query(q)[0].max(),cKDTree(q).query(p)[0].max()));exact=geometry[cov[0]]['exact_convex_surface']and verror<1e-6
   profile={'name':rec['name'],'covered_parts':cov,'type':rec['type'],'review_subshape_count':len(hs),'allowed_inflation_m':allow,'allowed_omission_m':rec.get('allowed_omission_m',rec.get('omission_m')),'observed_sampled_max_external_inflation_m':float(ds.max()),'sample_count':len(pts),'max_sample_triangle_edge_m':step,'exact_named_convex_source_profile':bool(exact),'source_hull_vertex_cloud_error_m':verror,'numeric_limit_declared':allow is not None,'pass':allow is not None and ds.max()<=allow+TOL};profiles.append(profile)
  coverage=[];ht=np.concatenate([h.tris for h in hulls])
  excluded=cs.get('excluded_geometry',cs.get('omitted_parts',[]))
  for name,t in parts.items():
   relevant=[h for h in hulls if name in h.record.get('covered_parts',[])];pts=np.unique(np.round(np.concatenate([t.reshape(-1,3),t.mean(1),(t[:,0]+t[:,1])/2,(t[:,1]+t[:,2])/2,(t[:,2]+t[:,0])/2]),9),axis=0);inside=np.any([h.inside(pts)for h in hulls],axis=0);ext=pts[~inside];d=nearest_distances(ext,ht)if len(ext)else np.array([0]);uncovered=sum(triangle_uncovered_area(x,hulls)for x in t);declared=max([h.record.get('allowed_omission_m',h.record.get('omission_m',0))for h in relevant],default=0);omission=next((x for x in excluded if isinstance(x,dict)and x.get('part')==name),None);coverage.append({'part':name,'explicit_covering_shapes':[h.record['name']for h in relevant],'sampled_max_underreach_m':float(d.max()),'source_triangles_uncovered_area_m2':float(uncovered),'declared_omission_m':declared,'explicit_entire_part_omission':omission,'actual_omitted_part_bounds_m':[t.min((0,1)).tolist(),t.max((0,1)).tolist()]if omission else None,'pass':(bool(relevant)and d.max()<=declared+TOL and uncovered<1e-7)or bool(omission)})
  row={'catalogue_id':ident,'source_sha256':sha(sp),'source_audit_sha256':sha(rp),'collision_path':str(cp.relative_to(ROOT)),'collision_sha256':sha(cp),'proposal_shape_count':len(hulls),'top_level_geometry_records':len(records),'profile_checks':profiles,'part_surface_geometry':geometry,'visual_part_coverage':coverage,'excluded_geometry_declarations':excluded,'comparison_tolerance_m':TOL,'passed':all(x['pass']for x in profiles+coverage)};rows.append(row);(OUT/f'independent_collision_profile_{ident}.json').write_text(json.dumps(row,indent=2,default=lambda x:x.item())+'\n');print(ident,row['passed'],'profile failures',[x['name']for x in profiles if not x['pass']],'coverage failures',[x['part']for x in coverage if not x['pass']],'max finite inflation',max(x['observed_sampled_max_external_inflation_m']for x in profiles),flush=True)
report={'passed':all(x['passed']for x in rows),'assets':rows,'limits':['Hull-surface sampling is a finite observation at <=60mm triangle edges, not full Hausdorff or a continuous maximum.','When a named solid is a closed outward convex manifold and explicit hull vertices match, the exact convex-profile equivalence is independently distinguished from sampled distance observations.','Continuous source-triangle union subtraction checks omitted surface area; finite source vertices, edge midpoints and centroids measure declared underreach.','No engine physics adoption, contact stability, mechanical load or runtime performance is established.'],'executed_script_sha256':sha(Path(__file__))};(OUT/'independent_collision_review.json').write_text(json.dumps(report,indent=2,default=lambda x:x.item())+'\n')
