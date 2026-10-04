"""Independent exact collision subset, retained bearing and all-part hood containment review."""
from pathlib import Path
import sys,json,itertools,math,hashlib,numpy as np
from scipy.spatial import ConvexHull
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch17';BASE=ROOT/'assets/housekeeping_equipment'
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import Hull,nearest_distances
sys.path.insert(0,str(OUT));from independent_equipment_motion_review import pose,cloud
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
prec=json.loads((BASE/'collision_proposals.json').read_text());bodies=json.loads((BASE/'actor_proxies/body_collision_subset.json').read_text());rows=[]
for ident in (sys.argv[1:]or['AST-HSK-001','AST-HSK-002']):
 mp=BASE/(ident+'.manifest.json');m=json.loads(mp.read_text());srp=OUT/f'independent_source_{ident}.json';s=json.loads(srp.read_text());assert sha(ROOT/s['path'])==s['sha256'];a=np.load(ROOT/s['geometry_cache']);t=a['triangles'];labels=a['object_names'];parts={str(n):t[labels==n]for n in np.unique(labels)};verts={n:cloud(pt)for n,pt in parts.items()};objects={x['name']:x for x in s['objects']};shapes=prec[ident]['shapes'];subset=bodies[ident];kept=subset['shapes'];by={x['name']:x for x in shapes};keptnames={x['name']for x in kept};allparts={n for x in shapes for n in x['covered_parts']};keptparts={n for x in kept for n in x['covered_parts']};omit={x['part']:x for x in subset['omitted_parts']};literal=all(x==by[x['name']]for x in kept);partition=keptparts.isdisjoint(omit)and keptparts|set(omit)==allparts==set(parts);coll=[]
 for shape in shapes:
  h=Hull(shape['points_source_m']);pt=np.concatenate([parts[n]for n in shape['covered_parts']]);covered=bool(h.inside(pt.reshape(-1,3)).all());v=cloud(pt);hd=float(max(nearest_distances(h.points,pt).max(),np.max(np.abs(np.array(shape['points_source_m'])@np.array([[1,0,0],[0,0,-1],[0,1,0]])-shape['points_gltf_m']))));coll.append({'shape':shape['name'],'owner':shape['parent_root'],'source_triangles_covered':covered,'sampled_hull_vertex_to_visual_distance_m':hd,'passed':covered and hd<2e-6 and all(objects[n]['parent']==shape['parent_root']for n in shape['covered_parts'])})
 # Literal subset preserves all detailed voids under identical rigid ownership for every pose.
 primary=[]
 for mk in m['physical_and_proposal_markers']:
  if not mk['physical_part']:continue
  fine='bearing'in mk['kind'];ret=mk['physical_part']in keptparts;primary.append({'marker':mk['name'],'kind':mk['kind'],'retained':ret,'uses_detailed_mechanism_only':fine and not ret,'passed':ret or fine})
 records={x['root']:x for x in m['motion_records']};fractions=[0,.125,.25,.375,.5,.625,.75,.875,1];poses=[dict(zip(records,fs))for fs in itertools.product(fractions,repeat=len(records))]if omit else [{k:0 for k in records}];under={n:{'part':n,'maximum_observed_undercoverage_m':0.,'declared_maximum_m':float(omit[n]['maximum_distance_to_retained_body_m'])}for n in omit}
 for position in poses:
  hs=[]
  for shape in kept:
   pp=np.array(shape['points_source_m']);owner=shape['parent_root'];pp=pose(pp,records[owner],position[owner])if owner in records else pp;hs.append(Hull(pp))
  ht=np.concatenate([h.tris for h in hs])
  for name in omit:
   pt=parts[name];pp=np.unique(np.concatenate([pt.reshape(-1,3),pt.mean(1),(pt[:,0]+pt[:,1])/2,(pt[:,1]+pt[:,2])/2,(pt[:,2]+pt[:,0])/2]),axis=0);owner=objects[name]['parent'];pp=pose(pp,records[owner],position[owner])if owner in records else pp;inside=np.any([h.inside(pp)for h in hs],axis=0);dd=nearest_distances(pp[~inside],ht)if (~inside).any()else np.array([0.]);value=float(dd.max())
   if value>under[name]['maximum_observed_undercoverage_m']:under[name].update(maximum_observed_undercoverage_m=value,worst_pose_fractions=position)
 bearings=[]
 for b in m['details']['bearing_records']:
  if 'pin'in b:
   axis=np.array(b['pivot_source_m'])[:2];pv=verts[b['pin']];sv=np.concatenate([verts[n]for n in b['sleeves']]);rad=np.linalg.norm(sv[:,:2]-axis,axis=1);inner=np.unique(np.round(sv[np.isclose(rad,rad.min(),atol=2e-6),:2],9),axis=0);ih=ConvexHull(inner);d=-ih.equations[:,2]-ih.equations[:,:2]@axis;bore_min=float(d.min());pin_max=float(np.linalg.norm(pv[:,:2]-axis,axis=1).max());outer_max=float(rad.max());caps=[]
   for cap in b['retainers']:
    cv=verts[cap];ch=ConvexHull(np.unique(cv[:,:2],axis=0));cap_min=float((-ch.equations[:,2]-ch.equations[:,:2]@axis).min());cap_max=float(np.linalg.norm(cv[:,:2]-axis,axis=1).max());zdist=min(abs(cv[:,2].max()-sv[:,2].min()),abs(cv[:,2].min()-sv[:,2].max()));width=cap_min-float(rad.min());caps.append({'part':cap,'axial_plane_error_m':float(zdist),'invariant_complete_annulus_contact_width_m':width,'cap_circumradius_m':cap_max,'passed':zdist<2e-6 and width>.001})
   bearings.append({'bearing':b['name'],'radial_clearance_for_entire_rotation_m':bore_min-pin_max,'actual_pin_axis_endpoints_source_m':[[float(axis[0]),float(axis[1]),float(pv[:,2].min())],[float(axis[0]),float(axis[1]),float(pv[:,2].max())]],'caps':caps,'scope':'Unloaded radial gap plus invariant axial annular contact; retained pin path to fixed bracket separately proven by actual support graph. No loaded bearing/friction or retention strength acceptance.','passed':bore_min-pin_max>0 and all(x['passed']for x in caps)})
  else:
   runner=verts[b['runner']];fixed=verts[b['bearing']];lip=verts[b['retaining_lip']];edge=verts[b['runner'].replace('runner','edge')];zerr=abs(runner[:,2].min()-fixed[:,2].max());rec=records[b['root']];terminal=pose(runner,rec,1);overlap=min(fixed[:,1].max(),terminal[:,1].max())-max(fixed[:,1].min(),terminal[:,1].min());xover=min(fixed[:,0].max(),runner[:,0].max())-max(fixed[:,0].min(),runner[:,0].min());gap=lip[:,2].min()-max(runner[:,2].max(),edge[:,2].max());bearings.append({'bearing':b['name'],'actual_bottom_bearing_plane_error_m':float(zerr),'entire_slide_minimum_y_overlap_m':float(overlap),'actual_x_support_width_m':float(xover),'retaining_lip_vertical_clearance_m':float(gap),'scope':'Straight translation preserves Z bearing contact and X overlap; Y overlap changes linearly and minimum is terminal. No latch, stop, loaded dynamics or hand fit.','passed':zerr<2e-6 and overlap>=float(b['terminal_overlap_m'])-2e-6 and xover>2e-6 and gap>0})
 containment=[]
 if ident.endswith('002'):
  shell=[n for n in parts if n in ['hood_upper_skin','hood_forward_fold','hood_control_forehead','hood_rear_upper_fold','left_hood_end_cheek','right_hood_end_cheek']];outer=Hull(np.concatenate([verts['left_hood_end_cheek'],verts['right_hood_end_cheek']]));external=['original_inactive_rack_control','hood_rear_removable_panel']
  for n,v in verts.items():
   if n in shell:kind='authored_profile_shell';passed=True
   elif n in external:kind='explicit_external_control_or_removable_rear_face';passed=True
   elif v[:,2].max()<=outer.lo[2]+2e-6:kind='entirely_at_or_below_hood_support_plane';passed=True
   else:kind='inner_service_frame_or_support';passed=bool(outer.inside(v,tol=2e-6).all())
   containment.append({'part':n,'classification':kind,'passed':passed})
 result={'catalogue_id':ident,'bindings':{'source':bind(ROOT/s['path']),'manifest':bind(mp),'precise':bind(BASE/'collision_proposals.json'),'body':bind(BASE/'actor_proxies/body_collision_subset.json')},'precise_shape_checks':coll,'literal_body_subset':{'exact_unchanged_shape_dictionaries':literal,'complete_partition':partition,'precise_count':len(shapes),'body_count':len(kept),'omitted_parts':len(omit),'primary_surface_checks':primary,'finite_pose_count':len(poses),'omitted_detail_observations':list(under.values()),'maximum_observed_omitted_detail_distance_m':max([x['maximum_observed_undercoverage_m']for x in under.values()],default=0),'declared_finite_omission_allowances_not_exceeded':all(x['maximum_observed_undercoverage_m']<=x['declared_maximum_m']+2e-6 for x in under.values()),'inheritance':'Every selected source/native shape and actual moving owner equals detailed description; subset cannot introduce a filled chamber, service cavity or other void at any owner pose.','engine_adopted':False},'retained_bearing_checks':bearings,'hood_complete_semantic_inventory_containment':containment,'passed':literal and partition and all(x['passed']for x in coll+primary+bearings+containment)and all(x['maximum_observed_undercoverage_m']<=x['declared_maximum_m']+2e-6 for x in under.values()),'limits':'Finite undercoverage uses9 fractions per independent moving root and all omitted-part vertices, edge midpoints, triangle centroids; it is not a continuous maximum, mechanical acceptance or target-PC performance. Whole void/sweep invariance follows exact subset inclusion, not finite sampling.'};(OUT/f'independent_equipment_collision_bearings_{ident}.json').write_text(json.dumps(result,indent=2,default=lambda x:x.item())+'\n');rows.append(result);print(ident,result['passed'],len(shapes),len(kept),'under',result['literal_body_subset']['maximum_observed_omitted_detail_distance_m'],'bearings',[(x['bearing'],x['passed'])for x in bearings],'containment',[x['part']for x in containment if not x['passed']],flush=True)
rows=[json.loads((OUT/f'independent_equipment_collision_bearings_{i}.json').read_text())for i in ['AST-HSK-001','AST-HSK-002']]
(OUT/'independent_equipment_collision_bearings_review.json').write_text(json.dumps({'passed':all(x['passed']for x in rows),'assets':rows,'executed_script_sha256':sha(Path(__file__))},indent=2)+'\n')
