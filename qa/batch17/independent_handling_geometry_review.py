"""Reviewer actual source/native marker, complete void and literal collision-subset checks."""
from pathlib import Path
import sys,json,hashlib,itertools,numpy as np
from scipy.optimize import linprog
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch17';BASE=ROOT/'assets/housekeeping_handling'
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,SourceCache,C
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import Hull,nearest_distances,inside_mesh,clip_polygon,polygon_area
sys.path.insert(0,str(ROOT/'qa/batch15'));from independent_contact_graph import normal_witness
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def box_planes(lo,hi):return np.concatenate([np.column_stack([np.eye(3),-np.array(hi)]),np.column_stack([-np.eye(3),np.array(lo)])])
def void_test(t,lo,hi,parts=None):
 lo=np.asarray(lo)+1e-6;hi=np.asarray(hi)-1e-6;planes=box_planes(lo,hi);hits=[]
 cand=np.where(((t.max(1)>=lo)&(t.min(1)<=hi)).all(1))[0]
 for i in cand:
  poly=t[i]
  for pl in planes:
   if len(poly)<3:break
   poly=clip_polygon(poly,pl,tol=0)
  if len(poly)>=3 and polygon_area(poly)>1e-11:hits.append(int(i))
 inside=[]
 if parts:
  for name,pt in parts.items():
   center=(lo+hi)/2
   if ((center>=pt.min((0,1)))&(center<=pt.max((0,1)))).all()and inside_mesh([center],pt)[0]:inside.append(name)
 return {'triangle_intrusion_count':len(hits),'first_intruding_triangles':hits[:12],'containing_parts':inside,'passed':not hits and not inside}
def hull_box(h,lo,hi):
 pl=np.concatenate([h.planes,box_planes(lo,hi)]);A=np.column_stack([pl[:,:3],np.ones(len(pl))]);r=linprog([0,0,0,-1],A_ub=A,b_ub=-pl[:,3],bounds=[(None,None)]*3+[(0,None)],method='highs');return float(r.x[-1])if r.success else 0.
rows=[]
for ident in ['AST-HSK-003','AST-HSK-004']:
 mp=BASE/(ident+'.manifest.json');m=json.loads(mp.read_text());sp=BASE/m['source'];gp=BASE/m['export'];srp=OUT/f'independent_source_{ident}.json';s=json.loads(srp.read_text());assert s['sha256']==sha(sp);cache=np.load(ROOT/s['geometry_cache']);t=cache['triangles'];labels=cache['object_names'];parts={str(n):t[labels==n]for n in np.unique(labels)};native=Native(gp);nt=native.tris@C;ns=SourceCache(srp);node_by={x.get('name'):i for i,x in enumerate(native.g.doc['nodes'])};markers=[]
 for a in m['physical_and_proposal_markers']:
  p=np.array(a['source_m']);ng=np.array(a['gltf_m']);nidx=node_by[a['name']];world=native.world[nidx][:3,3];o=next(x for x in s['objects']if x['name']==a['name']);sourceworld=np.array(o['matrix_world'])[:3,3];row={'name':a['name'],'kind':a['kind'],'metadata_native_position_error_m':float(np.linalg.norm(ng-C@p)),'actual_native_node_position_error_m':float(np.linalg.norm(world-C@p)),'actual_source_node_position_error_m':float(np.linalg.norm(sourceworld-p))};row['passed']=max(row[k]for k in row if k.endswith('error_m'))<1e-6
  if a['kind'].startswith('physical'):
   src=ns.nearest(C@p,node=a['physical_part']);nat=native.nearest(C@p);row.update(source_named_surface=src,native_surface=nat);row['passed']&=src['distance_m']<2e-5 and nat['distance_m']<2e-5
   if 'normal_source'in a:
    n=np.array(a['normal_source']);norm=normal_witness(p,parts[a['physical_part']],n);row.update(outward_normal=norm,normal_frame_error=float(np.linalg.norm(C@n-a['normal_gltf'])));row['passed']&=norm['pass']and row['normal_frame_error']<1e-6
  markers.append(row)
 joins=[]
 for j in m['joins']:
  p=np.array(j['probe_source_m']);res=[]
  for name in j['parts']:
   d=float(nearest_distances([p],parts[name])[0]);inside=bool(inside_mesh([p],parts[name])[0]);res.append({'part':name,'boundary_distance_m':d,'point_inside':inside,'covered':d<2e-5 or inside})
  joins.append({'name':j['name'],'kind':j['kind'],'parts':res,'passed':all(x['covered']for x in res)})
 c=json.loads((BASE/'collision_proposals.json').read_text())[ident];shapes=c['precise_reference'];hulls=[Hull(x['points_source_m'],x)for x in shapes];voids=[]
 for v in m['receiver_voids']:
  lo=v['min_source_m'];hi=v['max_source_m'];sv=void_test(t,lo,hi,parts);nv=void_test(nt,lo,hi);collision=[{'shape':h.record['name'],'interior_radius_m':hull_box(h,lo,hi)}for h in hulls if ((h.hi>lo)&(h.lo<hi)).all()];collision=[x for x in collision if x['interior_radius_m']>1e-6];voids.append({'name':v['name'],'source':sv,'native':nv,'collision_intrusions':collision,'passed':sv['passed']and nv['passed']and not collision})
 # Positive occupied control is a real part interior selected from the lowest planar plate.
 control_part='bench_folded_work_deck'if ident.endswith('003')else'liner_supported_bottom';pt=parts[control_part];center=(pt.min((0,1))+pt.max((0,1)))/2;control=void_test(t,center-.003,center+.003,parts);assert not control['passed']
 collision=[]
 for h in hulls:
  st=parts[h.record['source_part']];covered=bool(h.inside(st.reshape(-1,3)).all());vv=np.unique(np.concatenate([h.tris.reshape(-1,3),h.tris.mean(1)],axis=0),axis=0);dist=nearest_distances(vv,st);collision.append({'shape':h.record['name'],'source_part':h.record['source_part'],'all_evaluated_source_triangles_contained':covered,'finite_max_outer_hull_to_visual_surface_m':float(dist.max()),'declared_bevel_m':h.record['edge_easing_max_m'],'native_point_frame_error_m':float(np.max(np.abs(np.array(h.record['points_source_m'])@C.T-h.record['points_gltf_m']))),'passed':covered})
 subset=c['optional_body_candidate'];kept=[x for x in shapes if x['name']in subset['retained_shape_names']];omitted=[x for x in shapes if x['name']in subset['omitted_shape_names']];kh=[Hull(x['points_source_m'],x)for x in kept];kt=np.concatenate([h.tris for h in kh]);under=[]
 for shape in omitted:
  pt=parts[shape['source_part']];samples=np.unique(np.concatenate([pt.reshape(-1,3),pt.mean(1),(pt[:,0]+pt[:,1])/2,(pt[:,1]+pt[:,2])/2,(pt[:,2]+pt[:,0])/2]),axis=0);inside=np.any([h.inside(samples)for h in kh],axis=0);points=samples[~inside];dist=nearest_distances(points,kt)if len(points)else np.array([0]);under.append({'omitted_shape':shape['name'],'samples':len(samples),'finite_max_undercoverage_m':float(dist.max())})
 primary=[];keptparts={x['source_part']for x in kept}
 for mark in m['physical_and_proposal_markers']:
  if mark['kind'].startswith('physical'):
   retain=mark['physical_part']in keptparts;primary.append({'marker':mark['name'],'kind':mark['kind'],'retained':retain,'fine_identification_surface':mark['kind']=='physical_identification_surface','passed':retain or mark['kind']=='physical_identification_surface'})
 partition=set(subset['retained_shape_names']).isdisjoint(subset['omitted_shape_names'])and set(subset['retained_shape_names'])|set(subset['omitted_shape_names'])=={x['name']for x in shapes}
 body={'base_shape_count':len(shapes),'retained_shape_count':len(kept),'omitted_shape_count':len(omitted),'literal_subset_partition':partition,'primary_contacts':primary,'omitted_detail_undercoverage':under,'finite_max_undercoverage_m':max([x['finite_max_undercoverage_m']for x in under],default=0),'void_inheritance':'Literal unchanged subset cannot add any intrusion into complete voids of detailed union','passed':partition and all(x['passed']for x in primary)}
 row={'catalogue_id':ident,'bindings':{'source':bind(sp),'export':bind(gp),'manifest':bind(mp),'collision':bind(BASE/'collision_proposals.json'),'source_audit':bind(srp)},'marker_checks':markers,'declared_join_probe_checks':joins,'complete_useful_void_checks':voids,'occupied_positive_control':{'part':control_part,'result':control,'rejected_as_expected':not control['passed']},'collision_checks':collision,'optional_body_candidate':body,'passed':all(x['passed']for x in markers+joins+voids+collision)and body['passed'],'limits':['Complete source/native triangle clipping covers each stated box, with named-solid enclosure tests and real-solid positive control. It proves only those proposed component voids.','Geometric contacts and closed hull coverage do not certify load, cloth tension, rolling dynamics or structural strength.','Finite omitted-detail and hull-inflation observations are not continuous Hausdorff bounds or performance acceptance.','Identification plates remain detailed visual/service surfaces, separate from body subset.']};rows.append(row);(OUT/f'independent_handling_geometry_{ident}.json').write_text(json.dumps(row,indent=2)+'\n');print(ident,row['passed'],'markers',[x['name']for x in markers if not x['passed']],'joins',[x['name']for x in joins if not x['passed']],'voids',[x['name']for x in voids if not x['passed']],'collision',[x['shape']for x in collision if not x['passed']])
(OUT/'independent_handling_geometry_review.json').write_text(json.dumps({'passed':all(x['passed']for x in rows),'assets':rows,'executed_script_sha256':sha(Path(__file__))},indent=2)+'\n')
