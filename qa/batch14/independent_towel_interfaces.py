"""Independent native/source wet-fixture interfaces, all-part support and complete void checks."""
from pathlib import Path
import sys,json,hashlib,itertools,numpy as np
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch14';BASE=ROOT/'assets/aquatic_towel_use'
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import Hull,nearest_distances,inside_mesh,segment_triangles
sys.path.insert(0,str(ROOT/'qa/batch12'));from independent_void_geometry import triangle_box_mask,hull_box_overlap
sys.path.insert(0,str(OUT));from independent_contact_graph import contact_graph,normal_witness
from independent_sweep_geometry import sweep_contacts
from independent_collision_adapters import expand
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
results=[]
for mp in sorted(BASE.glob('AST-*.manifest.json')):
 m=json.loads(mp.read_text());ident=m['catalogue_id'];sp=BASE/m['source'];gp=BASE/m['export'];rp=OUT/f'independent_source_{ident}.json';s=json.loads(rp.read_text());assert sha(sp)==s['sha256']==m['source_sha256'];assert sha(gp)==m['glb_sha256'];so={o['name']:o for o in s['objects']};a=np.load(ROOT/s['geometry_cache']);tri=a['triangles'];labels=a['object_names'];roles=a['material_names'];native=Native(gp);nt=native.tris@C;nodes=native.g.doc['nodes'];ni={n.get('name'):i for i,n in enumerate(nodes)}
 markers=[]
 for mr in m['contacts']:
  p=np.asarray(mr['position_blender_source_m']);name=mr['name'];i=ni.get(name);world=native.world[i][:3,3]if i is not None else np.zeros(3);target=mr['source_part'];physical=mr['kind'].startswith('physical')
  r={'name':name,'kind':mr['kind'],'physical_target':target,'source_world_m':np.asarray(so[name]['matrix_world'])[:3,3].tolist(),'native_world_m':world.tolist(),'source_marker_error_m':float(np.linalg.norm(np.asarray(so[name]['matrix_world'])[:3,3]-p)),'native_marker_present':i is not None,'native_marker_error_m':float(np.linalg.norm(world-C@p)),'declared_native_error_m':float(np.linalg.norm(np.asarray(mr['position_gltf_yup_m'])-C@p)),'wrong_axis_interpretation_error_m':float(np.linalg.norm(world-p))}
  if physical:
   part=tri[labels==target];assert len(part);role=so[target]['materials'][0];n=np.asarray(mr['normal_blender_source']);sel=native.tris[native.select(role=role)]
   r.update(distance_to_named_source_surface_m=float(nearest_distances([p],part)[0]),distance_to_native_surface_m=native.nearest(C@p,role=role)['distance_m'],source_outward_normal_witness=normal_witness(p,part,n),native_outward_normal_witness=normal_witness(C@p,sel,C@n))
   r['physical_surface_verified']=max(r['distance_to_named_source_surface_m'],r['distance_to_native_surface_m'])<.0002 and r['source_outward_normal_witness']['pass']and r['native_outward_normal_witness']['pass']
  r['pass']=i is not None and max(r['source_marker_error_m'],r['native_marker_error_m'],r['declared_native_error_m'])<1e-6 and r.get('physical_surface_verified',True);markers.append(r)
 floor=[o['name']for o in s['objects']if o.get('min_xyz',[0,0,1])[2]<.00002 and o['type']=='MESH'];graph=contact_graph(tri,labels,floor)
 cp=BASE/(ident+'.collision_proposal.json');col=json.loads(cp.read_text());hulls=[h for x in col['shapes']for h in expand(x)]
 volumes=[];probes=[]
 for v in m['clear_volumes']:
  lo=np.asarray(v['min_m']);hi=np.asarray(v['max_m']);vl=lo+.0002;vh=hi-.0002;sm=triangle_box_mask(tri,vl,vh);nm=triangle_box_mask(nt,vl,vh);contains=[]
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
 controls=[('hood_solid',[.58,0,.8],[.70,0,.8]),('shelf_solid',[0,-.19,.60],[0,-.19,.70])]if ident=='AST-AQU-007'else[('fixed_cheek',[.39,0,.8],[.51,0,.8]),('bin_floor',[0,0,.10],[0,0,.16])]
 for name,p,q in controls:
  vb=bool(segment_triangles(p,q,tri));nb=bool(segment_triangles(p,q,nt));cb=any(h.segment(p,q)is not None for h in hulls);probes.append({'name':name,'segment_source_m':[p,q],'visual_blocked':vb,'native_blocked':nb,'proposal_blocked':cb,'expected_blocked':True,'pass':vb and nb and cb})
 removals=[]
 if ident=='AST-AQU-008':
  motion=m['motion'];moving_parts=[x['name']for x in m['parts']if x['motion_group']=='container'];moving=np.isin(labels,moving_parts);delta=np.asarray(motion['direction_blender_source'])*motion['travel_m'];fixed=tri[~moving];fl=labels[~moving]
  swept=sweep_contacts(tri[moving],fixed,delta,labels[moving],fl);pairs={tuple([x['moving_part'],x['fixed_part']])for x in swept}
  ng=Native(BASE/'exports/AST-AQU-008_withdrawn.glb');nn=ng.g.doc['nodes'];nni={n.get('name'):i for i,n in enumerate(nn)};move_name=motion['group'];ix=ni[move_name];jx=nni[move_name];shift=ng.world[jx][:3,3]-native.world[ix][:3,3];hierarchy=[]
  for mr in m['contacts']:
   name=mr['name'];i=ni[name];j=nni[name];d=ng.world[j][:3,3]-native.world[i][:3,3];expected=C@delta if mr['source_part']in moving_parts else np.zeros(3);hierarchy.append({'name':name,'expected_shift_gltf_m':expected.tolist(),'actual_shift_gltf_m':d.tolist(),'pass':float(np.linalg.norm(d-expected))<1e-6})
  support_states=[]
  for t in [0,1]:
   tt=tri.copy();tt[moving]+=t*delta;gg=contact_graph(tt,labels,floor);support_states.append({'travel_m':t*motion['travel_m'],'passed':gg['passed'],'isolated_parts':gg['isolated_parts'],'floor_parts_z_min':{name:float(tt[labels==name].reshape(-1,3)[:,2].min())for name in floor}})
  removals.append({'name':'whole_bin_linear_withdrawal','moving_parts':moving_parts,'translation_source_m':delta.tolist(),'continuous_triangle_sweep':{'contact_count':len(swept),'part_pairs':[list(p)for p in sorted(pairs)],'contacts':swept[:100]},'actual_native_hierarchy_shift_gltf_m':shift.tolist(),'marker_state_checks':hierarchy,'support_states':support_states,'pass':not len(swept)and np.linalg.norm(shift-C@delta)<1e-6 and all(x['pass']for x in hierarchy)and all(x['passed']for x in support_states)})
 wrong=Hull(tri.reshape(-1,3));negative=sum(not x['expected_blocked']and wrong.segment(*x['segment_source_m'])is not None for x in probes)
 result={'catalogue_id':ident,'passed':all(x['pass']for x in markers+volumes+probes+removals)and graph['passed']and negative>0,'bindings':{k:bind(p)for k,p in [('source',sp),('export',gp),('manifest',mp),('collision',cp),('source_audit',rp)]},'markers':markers,'all_part_contact_graph':graph,'collision_shape_count':len(col['shapes']),'review_convex_subshape_count':len(hulls),'complete_empty_volume_checks':volumes,'clear_and_blocked_probes':probes,'removal_checks':removals,'whole_asset_hull_negative_controls':negative,'wrong_axis_negative_control_count':sum(x['wrong_axis_interpretation_error_m']>.001 for x in markers),'limits':['Exact triangle/box intersection and convex feasibility screen stated inset boxes; finite rays supplement them.','The complete linear bin sweep begins at t=0 and includes every actual semantic part including handles/wheels. No forces, wheel rolling behavior, player controls or host fit is certified.','Every semantic part is screened for actual geometric contact to floor support. This does not certify structural strength.'],'executed_script_sha256':sha(Path(__file__))};results.append(result)
 print(ident,'passed',result['passed'],'markers failed',[x['name']for x in markers if not x['pass']],'isolated',graph['isolated_parts'],'void failures',[(x['name'],x['source_intruding_parts'],x['collision_overlaps'])for x in volumes if not x['pass']],'probe failures',[x['name']for x in probes if not x['pass']],'removal failures',[x['name']for x in removals if not x['pass']],flush=True)
(OUT/'independent_aquatic_towel_use_interfaces.json').write_text(json.dumps({'passed':all(x['passed']for x in results),'assets':results},indent=2)+'\n')
