"""Read native GLB hierarchy and independent source triangles; finite interface/collision tests."""
from pathlib import Path
import sys,json,hashlib,itertools,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch12'
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import Hull,nearest_distances,inside_mesh,segment_triangles
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def binding(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def normal_witness(p,tris,n):
 p=np.asarray(p);t=np.asarray(tris);a,b,c=t[:,0],t[:,1],t[:,2];ab=b-a;ac=c-a;cross=np.cross(ab,ac);nn=np.einsum('ij,ij->i',cross,cross)
 proj=p-cross*(np.einsum('ij,ij->i',p-a,cross)/np.maximum(nn,1e-30))[:,None];v=proj-a;d00=np.einsum('ij,ij->i',ab,ab);d01=np.einsum('ij,ij->i',ab,ac);d11=np.einsum('ij,ij->i',ac,ac);d20=np.einsum('ij,ij->i',v,ab);d21=np.einsum('ij,ij->i',v,ac);den=d00*d11-d01*d01
 u=(d11*d20-d01*d21)/np.maximum(den,1e-30);vv=(d00*d21-d01*d20)/np.maximum(den,1e-30);ds=np.where((u>=0)&(vv>=0)&(u+vv<=1)&(nn>1e-20),np.sum((proj-p)**2,axis=1),np.inf)
 for x,y in [(a,b),(b,c),(c,a)]:
  e=y-x;f=np.clip(np.einsum('ij,ij->i',p-x,e)/np.maximum(np.einsum('ij,ij->i',e,e),1e-30),0,1);q=x+f[:,None]*e;ds=np.minimum(ds,np.sum((q-p)**2,axis=1))
 normal=cross/np.maximum(np.sqrt(nn),1e-30)[:,None];near=np.sqrt(ds)<=np.sqrt(ds.min())+.0002;cos=normal@np.asarray(n);best=int(np.argmax(np.where(near,cos,-np.inf)))
 return {'nearby_named_triangle_count':int(near.sum()),'best_declared_outward_normal_cosine':float(cos[best]),'actual_surface_normal_source':normal[best].tolist(),'pass':bool(cos[best]>.999)}

family=sys.argv[1];rows=[]
controls={}
sys.path.insert(0,str(OUT));from independent_void_geometry import triangle_box_mask,hull_box_overlap

for mp in sorted((ROOT/'assets'/family).glob('AST-*.manifest.json')):
 m=json.loads(mp.read_text());ident=m['catalogue_id'];sp=mp.parent/m['source'];gp=mp.parent/m['export'];srp=OUT/f'independent_source_{ident}.json';s=json.loads(srp.read_text());api={}
 if m.get('interface_api'):
  api=json.loads((mp.parent/m['interface_api']).read_text())['assets'][ident]
  m['physical_and_proposal_markers']=[{'name':'MARKER_'+x['name'],'kind':'physical_surface','physical_part':x['physical_object'],'source_m':x['point_source_m'],'gltf_m':x['point_glb_m'],'normal_source':x['normal_source'],'normal_gltf':x['normal_glb'],'description':x.get('purpose','')}for x in api['surfaces']]
  m['joins']=[{'name':x['a']+'_to_'+x['b'],'parts':[x['a'],x['b']],'probe_source_m':x['witness_source_m'],'probe_gltf_m':(C@x['witness_source_m']).tolist(),'type':x.get('type')}for x in api.get('joins',[])]
 assert sha(sp)==s['sha256']==m['source_sha256'];assert sha(gp)==m.get('glb_sha256',m.get('export_sha256'))
 a=np.load(ROOT/s['geometry_cache']);tris=a['triangles'];labels=a['object_names'];native=Native(gp);native_source_tris=native.tris@C;nodes=native.g.doc['nodes'];ni={n.get('name'):i for i,n in enumerate(nodes)};so={o['name']:o for o in s['objects']}
 markers=[];joins=[]
 for original_mr in m.get('physical_and_proposal_markers',m.get('positions_and_normals',[])):
  mr=dict(original_mr)
  if 'node_name' in mr:
   mr.update(name=mr['node_name'],source_m=mr['source_blender_xyz_m'],gltf_m=mr['exchange_gltf_yup_m'],normal_source=mr['normal_source_blender'],normal_gltf=mr['normal_exchange_gltf'],description=mr['meaning'])
  name=mr['name'];p=np.asarray(mr['source_m']);i=ni.get(name);sn=np.asarray(so[name]['matrix_world']);gn=native.world[i] if i is not None else np.eye(4);world=gn[:3,3] if i is not None else C@p
  r={'native_marker_present':i is not None,'name':name,'kind':mr['kind'],'meaning':mr.get('description',''),'part':mr.get('physical_part'),'source_world_m':sn[:3,3].tolist(),'native_world_m':world.tolist(),'source_marker_error_m':float(np.linalg.norm(sn[:3,3]-p)),'native_marker_error_m':float(np.linalg.norm(world-C@p)),'wrong_axis_interpretation_error_m':float(np.linalg.norm(world-p)),'declared_native_error_m':float(np.linalg.norm(np.asarray(mr['gltf_m'])-C@p)),'source_parent':so[name]['parent'],'native_parent':nodes[native.parents[i]].get('name') if i in native.parents else None,'extras':nodes[i].get('extras',{}) if i is not None else {}}
  ns=mr.get('normal_source',mr.get('direction_source'));ng=mr.get('normal_gltf',mr.get('direction_gltf'))
  if ns is not None:r['direction_conversion_error']=float(np.linalg.norm(C@ns-np.asarray(ng)));r['declared_direction_length']=float(np.linalg.norm(ns))
  if mr.get('physical_part'):
   selected=tris[labels==mr['physical_part']];assert len(selected),mr['physical_part'];r['distance_to_named_source_surface_m']=float(nearest_distances([p],selected)[0]);r['inside_named_source_solid']=bool(inside_mesh([p],selected)[0]);roles=so[mr['physical_part']]['materials'];role=roles[0] if len(roles)==1 else None;r['native_role']=role;r['source_part_roles']=roles;native_part_node=ident+'__'+mr['physical_part'] if so[mr['physical_part']]['properties'].get('individual_control') else None;r['native_bound_part_node']=native_part_node;r['distance_to_native_surface_m']=native.nearest(C@p,role=role,node=native_part_node)['distance_m']
   if mr['kind'].startswith('physical_'):
    r['physical_contact_on_named_surface']=r['distance_to_named_source_surface_m']<.0002 and r['distance_to_native_surface_m']<.0002
    if ns is not None:
     r['physical_normal_witness']=normal_witness(p,selected,ns);r['native_physical_normal_witness']=normal_witness(C@p,native.tris[native.select(role=role,node=native_part_node)],C@ns)
  r['pass']=r['native_marker_present'] and max(r['source_marker_error_m'],r['native_marker_error_m'],r['declared_native_error_m'],r.get('direction_conversion_error',0))<1e-6 and r.get('physical_contact_on_named_surface',True) and r.get('physical_normal_witness',{}).get('pass',True) and r.get('native_physical_normal_witness',{}).get('pass',True) and (abs(r.get('declared_direction_length',1)-1)<1e-4 or not mr.get('physical_part'))
  markers.append(r)
 for j in m.get('joins',[]):
  p=np.asarray(j['probe_source_m']);partrows=[]
  for side,part in zip(['a','b'],j['parts']):
   t=tris[labels==part];assert len(t),part;d=float(nearest_distances([p],t)[0]);ins=bool(inside_mesh([p],t)[0]);pr={'name':part,'probe_surface_distance_m':d,'probe_inside_solid':ins,'contains_probe':ins or d<.0002}
   if 'normal_'+side+'_source' in j:
    ns=np.asarray(j['normal_'+side+'_source']);role=so[part]['materials'][0];pr['named_normal_witness']=normal_witness(p,t,ns);pr['native_normal_witness']=normal_witness(C@p,native.tris[native.select(role=role)],C@ns);pr['direction_conversion_error']=float(np.linalg.norm(C@ns-j['normal_'+side+'_gltf']));pr['physical_boundary_witness_pass']=d<.0002 and pr['named_normal_witness']['pass'] and pr['native_normal_witness']['pass'] and pr['direction_conversion_error']<1e-6
   partrows.append(pr)
  joins.append({'name':j['name'],'source_probe_m':p.tolist(),'parts':partrows,'pass':all(x['contains_probe'] and x.get('physical_boundary_witness_pass',True)for x in partrows)})
 cp=mp.parent/m['collision_proposal_file'];doc=json.loads(cp.read_text());cr=doc.get('assets',doc)[ident];hulls=[];frame=[0.]
 if api:cr['preserve_voids']=api.get('reserved_voids',[])
 for shape in cr.get('shapes',cr.get('hulls',[])):
  if shape['type']=='box':
   lo,hi=np.array(shape['min_source_m']),np.array(shape['max_source_m']);pts=np.asarray(list(itertools.product(*zip(lo,hi))));gpts=pts@C.T
   if 'min_gltf_m' in shape:frame.append(max(np.max(np.abs(gpts.min(axis=0)-shape['min_gltf_m'])),np.max(np.abs(gpts.max(axis=0)-shape['max_gltf_m']))))
  else:
   pts=np.asarray(shape.get('points_source_m',shape.get('points_m',shape.get('vertices_source_m'))));gdecl=shape.get('points_gltf_m',shape.get('points_exchange_m',shape.get('points_exchange_gltf_yup_m')));frame.append(float(np.max(np.abs(pts@C.T-gdecl))) if gdecl is not None else 0. if 'source' in cr.get('frame','').lower() else float('inf'))
  hulls.append(Hull(pts,shape))
 tests=[];volumes=[]
 def test(label,p,q,expected):
  visual=bool(segment_triangles(p,q,tris));actual_glb=bool(segment_triangles(p,q,native_source_tris));coll=any(h.segment(p,q)is not None for h in hulls)
  tests.append({'name':label,'source_segment_m':[list(p),list(q)],'visual_blocked':visual,'native_glb_blocked':actual_glb,'compound_blocked':coll,'expected_blocked':expected,'pass':visual==expected and actual_glb==expected and coll==expected})
 for original_void in cr.get('preserve_voids',cr.get('preserved_voids',[])):
  void=dict(original_void)
  if void.get('state','all') not in ['all','closed']:continue
  if 'min_gltf_m' not in void and 'min_exchange_gltf_yup_m' in void:void.update(min_gltf_m=void['min_exchange_gltf_yup_m'],max_gltf_m=void['max_exchange_gltf_yup_m'])
  lo,hi=np.asarray(void['min_source_m'],float),np.asarray(void['max_source_m'],float);assert np.all(hi>lo)
  gpts=np.asarray(list(itertools.product(*zip(lo,hi))))@C.T
  if 'min_gltf_m' in void:frame.append(max(np.max(np.abs(gpts.min(axis=0)-void['min_gltf_m'])),np.max(np.abs(gpts.max(axis=0)-void['max_gltf_m']))))
  vl=lo+.0002;vh=hi-.0002;sm=triangle_box_mask(tris,vl,vh);gm=triangle_box_mask(native_source_tris,vl,vh);mid=(vl+vh)/2;contains=[]
  for part in np.unique(labels):
   if inside_mesh([mid],tris[labels==part])[0]:contains.append(str(part))
  overlaps=[{'name':h.record['name'],**hull_box_overlap(h,vl,vh)}for h in hulls];overlaps=[x for x in overlaps if x['overlaps']]
  volumes.append({'name':void['name'],'source_box_m':[lo.tolist(),hi.tolist()],'inset_for_surface_tolerance_m':.0002,'source_surface_intruding_parts':sorted(set(str(x)for x in labels[sm])),'source_surface_triangle_count':int(sm.sum()),'native_surface_triangle_count':int(gm.sum()),'midpoint_inside_source_solids':contains,'collision_compound_overlaps':overlaps,'pass':not sm.any() and not gm.any() and not contains and not overlaps})
  for axis in range(3):
   others=[x for x in range(3) if x!=axis]
   for u,v in itertools.product([.07,.3,.5,.7,.93],repeat=2):
    p=lo+(hi-lo)*.01;q=hi-(hi-lo)*.01
    for ax,f in zip(others,[u,v]):p[ax]=q[ax]=lo[ax]+(hi[ax]-lo[ax])*f
    test(void['name']+'_axis'+str(axis),p,q,False)
 for mr in m.get('physical_and_proposal_markers',[]):
  if mr.get('physical_part') and ('floor' in mr['kind'] or 'floor' in mr['name'].lower()):
   p=np.asarray(mr['source_m']);n=np.asarray(mr.get('direction_source',mr.get('normal_source',[0,0,-1])));test('blocked_'+mr['name'],p-n*.012,p+n*.012,True)
 for label,p,q in controls.get(ident,[]):test('blocked_'+label,p,q,True)
 wrong=Hull(tris.reshape(-1,3));negative=sum(not t['visual_blocked'] and wrong.segment(*t['source_segment_m'])is not None for t in tests)
 row={'id':ident,'bindings':{k:binding(p)for k,p in [('source',sp),('export',gp),('manifest',mp),('collision',cp),('source_audit',srp)]+([('interface_api',mp.parent/m['interface_api'])] if m.get('interface_api')else [])},'markers':markers,'joins':joins,'collision_shape_count':len(hulls),'collision_frame_max_error_m':float(max(frame)),'void_and_blocked_tests':tests,'empty_volume_checks':volumes,'whole_asset_hull_wrongly_blocks_clear_controls':negative,'wrong_axis_negative_control_count':sum(x['wrong_axis_interpretation_error_m']>.001 for x in markers),'native_animation_clips':len(native.g.doc.get('animations',[])),'native_skin_count':len(native.g.doc.get('skins',[])),'pass':all(x['pass']for x in markers+joins+tests+volumes) and max(frame)<1e-6 and sum(x['wrong_axis_interpretation_error_m']>.001 for x in markers)>0 ,'negative_control_scope':'Whole-hull filling is an advisory negative control for enclosed voids; unbounded outside approaches need not intersect it. Blocked floor controls and wrong-frame marker checks remain required.'}
 rows.append(row);print(ident,'marker failures',[(x['name'],x.get('distance_to_named_source_surface_m'))for x in markers if not x['pass']],'join failures',[(x['name'],x['parts'])for x in joins if not x['pass']],'void/control failures',[(x['name'],x['visual_blocked'],x['native_glb_blocked'],x['compound_blocked'])for x in tests if not x['pass']][:20],'negative controls',negative)
result={'executed_script_sha256':sha(Path(__file__)),'read_only_helper_bindings':[binding(p)for p in [ROOT/'qa/inspect_glb_independent.py',ROOT/'qa/batch07/independent_geometry.py',ROOT/'qa/batch08/independent_collision_geometry.py',OUT/'independent_void_geometry.py']],'passed':bool(rows)and all(r['pass']for r in rows),'assets':rows,'method':'Independent evaluated source triangles, exact native GLB node transforms, paired source-to-native direction conversion, named source-part contact and solid-join witnesses. Empty boxes additionally undergo triangle/box SAT, source solid containment and exact convex halfspace feasibility. Finite clear rays are sampled in all three axes of every declared preserved void, with independent blocked structural controls. Actual source and native visual intersections are compared with collision compounds; a whole-component hull supplies negative controls.','limits':['Finite probes are not continuous coverage/error certification, engine physics, real host moving-door fit, service procedure, guard compliance or universal actor/cart fit.','Source markers classify fixed physical surfaces separately from optional receivers, openings and pose datums. Native clips/skins are counted; no absent motion is inferred.']}
(OUT/('independent_'+family+'_interfaces.json')).write_text(json.dumps(result,indent=2)+'\n')
