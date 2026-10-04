"""Independent native/source wet-fixture interfaces, all-part support and complete void checks."""
from pathlib import Path
import sys,json,hashlib,itertools,numpy as np
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch14';BASE=ROOT/'assets/aquatic_wet_use'
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import Hull,nearest_distances,inside_mesh,segment_triangles
sys.path.insert(0,str(ROOT/'qa/batch12'));from independent_void_geometry import triangle_box_mask,hull_box_overlap
sys.path.insert(0,str(OUT));from independent_contact_graph import contact_graph,normal_witness
from independent_sweep_geometry import sweep_contacts
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
results=[]
for mp in sorted(BASE.glob('AST-*.manifest.json')):
 m=json.loads(mp.read_text());ident=m['catalogue_id'];sp=BASE/m['source'];gp=BASE/m['export'];rp=OUT/f'independent_source_{ident}.json';s=json.loads(rp.read_text());assert sha(sp)==s['sha256']==m['source_sha256'];assert sha(gp)==m['glb_sha256'];so={o['name']:o for o in s['objects']};a=np.load(ROOT/s['geometry_cache']);tri=a['triangles'];labels=a['object_names'];roles=a['material_names'];native=Native(gp);nt=native.tris@C;nodes=native.g.doc['nodes'];ni={n.get('name'):i for i,n in enumerate(nodes)}
 markers=[]
 for mr in m['physical_and_proposal_markers']:
  p=np.asarray(mr['source_m']);name=mr['name'];i=ni.get(name);world=native.world[i][:3,3]if i is not None else np.zeros(3);target=mr['physical_part'];physical=mr['kind'].startswith('physical')
  r={'name':name,'kind':mr['kind'],'physical_target':target,'source_world_m':np.asarray(so[name]['matrix_world'])[:3,3].tolist(),'native_world_m':world.tolist(),'source_marker_error_m':float(np.linalg.norm(np.asarray(so[name]['matrix_world'])[:3,3]-p)),'native_marker_present':i is not None,'native_marker_error_m':float(np.linalg.norm(world-C@p)),'declared_native_error_m':float(np.linalg.norm(np.asarray(mr['gltf_m'])-C@p)),'wrong_axis_interpretation_error_m':float(np.linalg.norm(world-p))}
  if physical:
   part=tri[labels==target];assert len(part);role=so[target]['materials'][0];n=np.asarray(mr['surface_normal_source']);sel=native.tris[native.select(role=role)]
   r.update(distance_to_named_source_surface_m=float(nearest_distances([p],part)[0]),distance_to_native_surface_m=native.nearest(C@p,role=role)['distance_m'],source_outward_normal_witness=normal_witness(p,part,n),native_outward_normal_witness=normal_witness(C@p,sel,C@n))
   r['physical_surface_verified']=max(r['distance_to_named_source_surface_m'],r['distance_to_native_surface_m'])<.0002 and r['source_outward_normal_witness']['pass']and r['native_outward_normal_witness']['pass']
  r['pass']=i is not None and max(r['source_marker_error_m'],r['native_marker_error_m'],r['declared_native_error_m'])<1e-6 and r.get('physical_surface_verified',True);markers.append(r)
 floor=[o['name']for o in s['objects']if o.get('min_xyz',[0,0,1])[2]<.00002 and o['type']=='MESH'];graph=contact_graph(tri,labels,floor)
 cp=BASE/m['collision_proposal_file'];col=json.loads(cp.read_text())[ident];hulls=[Hull(x['points_source_m'],x)for x in col['shapes']]
 volumes=[];probes=[]
 for v in m['receiver_voids']:
  lo=np.asarray(v['min_source_m']);hi=np.asarray(v['max_source_m']);vl=lo+.0002;vh=hi-.0002;sm=triangle_box_mask(tri,vl,vh);nm=triangle_box_mask(nt,vl,vh);contains=[]
  for part in np.unique(labels):
   if inside_mesh([(vl+vh)/2],tri[labels==part])[0]:contains.append(str(part))
  overlaps=[h.record['name']for h in hulls if hull_box_overlap(h,vl,vh)['overlaps']]
  volumes.append({'name':v['name'],'source_box_m':[lo.tolist(),hi.tolist()],'source_intruding_parts':sorted(set(str(x)for x in labels[sm])),'source_intruding_triangles':int(sm.sum()),'native_intruding_triangles':int(nm.sum()),'midpoint_inside_named_solids':contains,'collision_overlaps':overlaps,'pass':not sm.any()and not nm.any()and not contains and not overlaps})
  for ax in range(3):
   others=[a for a in range(3)if a!=ax]
   for u,w in itertools.product([.08,.3,.5,.7,.92],repeat=2):
    p=vl.copy();q=vh.copy()
    for a,f in zip(others,[u,w]):p[a]=q[a]=vl[a]+(vh[a]-vl[a])*f
    vb=bool(segment_triangles(p,q,tri));nb=bool(segment_triangles(p,q,nt));cb=any(h.segment(p,q)is not None for h in hulls);probes.append({'name':v['name'],'segment_source_m':[p.tolist(),q.tolist()],'visual_blocked':vb,'native_blocked':nb,'proposal_blocked':cb,'expected_blocked':False,'pass':not vb and not nb and not cb})
 # Independent positive controls in the real floor/plinth, back web and physical controls.
 controls=[('floor_solid',[0,0,-.01],[0,0,.04]),('upper_back_web',[0,.08,1.25],[0,.21,1.25])]
 for name,p,q in controls:
  vb=bool(segment_triangles(p,q,tri));nb=bool(segment_triangles(p,q,nt));cb=any(h.segment(p,q)is not None for h in hulls);probes.append({'name':name,'segment_source_m':[p,q],'visual_blocked':vb,'native_blocked':nb,'proposal_blocked':cb,'expected_blocked':True,'pass':vb and nb and cb})
 removals=[]
 for rem in m['removal_proposals']:
  moving=np.isin(labels,rem['parts']);d=np.asarray(rem['translation_source_m']);lo=np.asarray(rem['reserve']['min_source_m']);hi=np.asarray(rem['reserve']['max_source_m']);fixed=tri[~moving];fl=labels[~moving]
  sm=triangle_box_mask(fixed,lo+.0002,hi-.0002);contains=[str(part)for part in np.unique(fl)if inside_mesh([(lo+hi)/2],fixed[fl==part])[0]]
  swept=sweep_contacts(tri[moving],fixed,d,labels[moving],fl)
  obstructing=[x for x in swept if x['translation_fraction_interval'][1]>2e-6];seating=[x for x in swept if x['translation_fraction_interval'][1]<=2e-6]
  penetration=[]
  for mpn in rem['parts']:
   mt=tri[labels==mpn];pts=np.concatenate([np.unique(mt.reshape(-1,3),axis=0),mt.mean(1)])
   for fpn in np.unique(fl):
    ft=fixed[fl==fpn];mask=inside_mesh(pts,ft)&(nearest_distances(pts,ft)>.00002)
    if mask.any():penetration.append({'moving_part':mpn,'fixed_part':str(fpn),'contained_samples':int(mask.sum())})
  pairs={tuple([x['moving_part'],x['fixed_part']])for x in swept}
  overlaps=[h.record['name']for h in hulls if not set(h.record['covered_parts'])<=set(rem['parts']) and hull_box_overlap(h,lo+.0002,hi-.0002)['overlaps']]
  rootrec=next(x for x in m['independent_removable_roots']if set(x['parts'])==set(rem['parts']));rix=ni[rootrec['name']]
  def desc(ix):
   while ix in native.parents:
    ix=native.parents[ix]
    if ix==rix:return True
   return False
  moving_nodes=[nodes[ix].get('name')for ix in native.world if desc(ix)and 'mesh'in nodes[ix]];nmove=np.isin(native.nodes,moving_nodes);nsweep=sweep_contacts(nt[nmove],nt[~nmove],d,native.nodes[nmove],native.nodes[~nmove]);nobstruct=[x for x in nsweep if x['translation_fraction_interval'][1]>2e-6]
  from scipy.spatial import cKDTree
  sv=tri[moving].reshape(-1,3);nv=nt[nmove].reshape(-1,3);ownership_error=float(max(cKDTree(sv).query(nv)[0].max(),cKDTree(nv).query(sv)[0].max()))
  marker_hierarchy=[]
  for mr in m['physical_and_proposal_markers']:
   expected=mr['physical_part']in rem['parts'];actual=desc(ni[mr['name']]);marker_hierarchy.append({'marker':mr['name'],'moves_with_plate':actual,'expected_to_move_with_plate':expected,'pass':actual==expected})
  root_error=float(np.linalg.norm(native.world[rix][:3,3]-C@np.asarray(rootrec['zero_pose_source_m'])));vector_error=float(np.linalg.norm(np.asarray(nodes[rix]['extras']['removal_vector_gltf_m'])-C@d))
  hierarchy={'root':rootrec['name'],'actual_native_zero_pose_gltf_m':native.world[rix][:3,3].tolist(),'zero_pose_error_m':root_error,'vector_error_m':vector_error,'moving_native_mesh_nodes':moving_nodes,'source_native_moving_geometry_hausdorff_m':ownership_error,'marker_hierarchy':marker_hierarchy,'native_continuous_obstructing_contacts':len(nobstruct),'pass':root_error<1e-6 and vector_error<1e-6 and ownership_error<1e-6 and not nobstruct and all(x['pass']for x in marker_hierarchy)}
  removals.append({'name':rem['name'],'actual_native_removable_hierarchy':hierarchy,'moving_parts':rem['parts'],'translation_source_m':d.tolist(),'continuous_triangle_sweep_from_closed_pose':{'contact_count':len(swept),'permitted_initial_boundary_contacts':len(seating),'obstructing_contact_count':len(obstructing),'initial_interpenetration_samples':penetration,'part_pairs':[list(p)for p in sorted(pairs)],'contacts':swept[:100],'full_tested_triangle_pairs_method':'Continuous separating-axis intervals for every candidate triangle pair; no finite pose sampling'},'reserve_fixed_intrusions':sorted(set(str(x)for x in fl[sm])),'reserve_midpoint_inside_fixed_parts':contains,'collision_intrusions':overlaps,'pass':hierarchy['pass']and not len(obstructing)and not penetration and not sm.any()and not contains and not overlaps})
 wrong=Hull(tri.reshape(-1,3));negative=sum(not x['expected_blocked']and wrong.segment(*x['segment_source_m'])is not None for x in probes)
 result={'catalogue_id':ident,'passed':all(x['pass']for x in markers+volumes+probes+removals)and graph['passed']and negative>0,'bindings':{k:bind(p)for k,p in [('source',sp),('export',gp),('manifest',mp),('collision',cp),('source_audit',rp)]},'markers':markers,'all_part_contact_graph':graph,'collision_shape_count':len(hulls),'complete_empty_volume_checks':volumes,'clear_and_blocked_probes':probes,'removal_checks':removals,'whole_asset_hull_negative_controls':negative,'wrong_axis_negative_control_count':sum(x['wrong_axis_interpretation_error_m']>.001 for x in markers),'limits':['Exact triangle/box intersection and convex feasibility screen stated inset boxes; finite rays supplement them.','Complete extraction sweep begins at the closed pose. Only departing boundary contacts ending within0.8micrometre are tolerated; initial sampled deep containment is separately rejected. No release mechanism, force, player controls, plumbing or host fit is certified.','Every semantic part is screened for actual geometric contact to floor support. This does not certify structural strength.'],'executed_script_sha256':sha(Path(__file__))};results.append(result)
 print(ident,'passed',result['passed'],'markers failed',[x['name']for x in markers if not x['pass']],'isolated',graph['isolated_parts'],'void failures',[(x['name'],x['source_intruding_parts'],x['collision_overlaps'])for x in volumes if not x['pass']],'probe failures',[x['name']for x in probes if not x['pass']],'removal failures',[(x['name'],x['reserve_fixed_intrusions'],x['collision_intrusions'],x['continuous_triangle_sweep_from_closed_pose']['part_pairs'])for x in removals if not x['pass']],flush=True)
(OUT/'independent_aquatic_wet_use_interfaces.json').write_text(json.dumps({'passed':all(x['passed']for x in results),'assets':results},indent=2)+'\n')
