"""Read native GLB hierarchy and independent source triangles; finite interface/collision tests."""
from pathlib import Path
import sys,json,hashlib,itertools,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch10'
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
controls={
 'AST-SAL-001':[('left_jamb',[-2.42,.64,-.02],[-2.42,.64,.1]),('header',[0,.64,3.2],[0,.64,3.6])],
 'AST-SAL-002':[('cove_shell',[1.2,.08,3.0],[1.2,.08,3.6])],
 'AST-SAL-003':[('floor_plinth',[0,2.35,-.02],[0,2.35,.2]),('seat',[0,2.08,.3],[0,2.08,.51]),('shelf',[-2.775,1.83,.90],[-2.775,1.83,.98]),('rear_back',[0,2.85,1.6],[0,3.3,1.6])],
 'AST-SAL-004':[('floor_pier',[-1.32,.455,-.02],[-1.32,.455,.08]),('seat_contact',[-1,.34,.38],[-1,.34,.51]),('rear_spine',[0,1.40,.5],[0,1.65,.5]),('end_perch',[1.36,.32,.7],[1.36,.32,.8])],
 'AST-SAL-005':[('middle_post',[0,.10,.60],[0,.38,.60]),('left_floor_shoe',[-1.32,.24,-.02],[-1.32,.24,.12]),('handrest',[-.66,.24,1.08],[-.66,.24,1.18])],
 'AST-SAL-006':[('left_floor_shoe',[-1.32,.5,-.02],[-1.32,.5,.07]),('shelf0',[0,.6,.20],[0,.6,.29]),('guest_spine',[0,-.1,1.5],[0,.4,1.5]),('low_turn',[1.32,.9,.55],[1.32,1.4,.55])],
}
for mp in sorted((ROOT/'assets'/family).glob('AST-*.manifest.json')):
 m=json.loads(mp.read_text());ident=m['catalogue_id'];sp=mp.parent/m['source'];gp=mp.parent/m['export'];srp=OUT/f'independent_source_{ident}.json';s=json.loads(srp.read_text())
 assert sha(sp)==s['sha256']==m['source_sha256'];assert sha(gp)==m.get('glb_sha256',m.get('export_sha256'))
 a=np.load(ROOT/s['geometry_cache']);tris=a['triangles'];labels=a['object_names'];native=Native(gp);native_source_tris=native.tris@C;nodes=native.g.doc['nodes'];ni={n.get('name'):i for i,n in enumerate(nodes)};so={o['name']:o for o in s['objects']}
 markers=[];joins=[]
 for original_mr in m.get('physical_and_proposal_markers',m.get('positions_and_normals',[])):
  mr=dict(original_mr)
  if 'node_name' in mr:
   mr.update(name=mr['node_name'],source_m=mr['source_blender_xyz_m'],gltf_m=mr['exchange_gltf_yup_m'],normal_source=mr['normal_source_blender'],normal_gltf=mr['normal_exchange_gltf'],description=mr['meaning'])
  name=mr['name'];p=np.asarray(mr['source_m']);i=ni[name];sn=np.asarray(so[name]['matrix_world']);gn=native.world[i];world=gn[:3,3]
  r={'name':name,'kind':mr['kind'],'meaning':mr.get('description',''),'part':mr.get('physical_part'),'source_world_m':sn[:3,3].tolist(),'native_world_m':world.tolist(),'source_marker_error_m':float(np.linalg.norm(sn[:3,3]-p)),'native_marker_error_m':float(np.linalg.norm(world-C@p)),'wrong_axis_interpretation_error_m':float(np.linalg.norm(world-p)),'declared_native_error_m':float(np.linalg.norm(np.asarray(mr['gltf_m'])-C@p)),'source_parent':so[name]['parent'],'native_parent':nodes[native.parents[i]].get('name') if i in native.parents else None,'extras':nodes[i].get('extras',{})}
  ns=mr.get('normal_source',mr.get('direction_source'));ng=mr.get('normal_gltf',mr.get('direction_gltf'))
  if ns is not None:r['direction_conversion_error']=float(np.linalg.norm(C@ns-np.asarray(ng)))
  if mr.get('physical_part'):
   selected=tris[labels==mr['physical_part']];assert len(selected),mr['physical_part'];r['distance_to_named_source_surface_m']=float(nearest_distances([p],selected)[0]);r['inside_named_source_solid']=bool(inside_mesh([p],selected)[0]);r['distance_to_native_surface_m']=native.nearest(C@p)['distance_m']
   if mr['kind'].startswith('physical_'):
    r['physical_contact_on_named_surface']=r['distance_to_named_source_surface_m']<.002 and r['distance_to_native_surface_m']<.002
    if ns is not None:r['physical_normal_witness']=normal_witness(p,selected,ns)
  r['pass']=max(r['source_marker_error_m'],r['native_marker_error_m'],r['declared_native_error_m'],r.get('direction_conversion_error',0))<1e-6 and r.get('physical_contact_on_named_surface',True) and r.get('physical_normal_witness',{}).get('pass',True)
  markers.append(r)
 for j in m.get('joins',[]):
  p=np.asarray(j['probe_source_m']);partrows=[]
  for part in j['parts']:
   t=tris[labels==part];assert len(t),part;d=float(nearest_distances([p],t)[0]);ins=bool(inside_mesh([p],t)[0]);partrows.append({'name':part,'probe_surface_distance_m':d,'probe_inside_solid':ins,'contains_probe':ins or d<.0002})
  joins.append({'name':j['name'],'source_probe_m':p.tolist(),'parts':partrows,'pass':all(x['contains_probe']for x in partrows)})
 cp=mp.parent/m['collision_proposal_file'];doc=json.loads(cp.read_text());cr=doc.get('assets',doc)[ident];hulls=[];frame=[]
 for shape in cr.get('shapes',cr.get('hulls',[])):
  if shape['type']=='box':
   lo,hi=np.array(shape['min_source_m']),np.array(shape['max_source_m']);pts=np.asarray(list(itertools.product(*zip(lo,hi))));gpts=pts@C.T
   frame.append(max(np.max(np.abs(gpts.min(axis=0)-shape['min_gltf_m'])),np.max(np.abs(gpts.max(axis=0)-shape['max_gltf_m']))))
  else:
   pts=np.asarray(shape.get('points_source_m',shape.get('points_m')));gdecl=shape.get('points_gltf_m',shape.get('points_exchange_m',shape.get('points_exchange_gltf_yup_m')));frame.append(float(np.max(np.abs(pts@C.T-gdecl))) if gdecl is not None else float('inf'))
  hulls.append(Hull(pts,shape))
 tests=[]
 def test(label,p,q,expected):
  visual=bool(segment_triangles(p,q,tris));actual_glb=bool(segment_triangles(p,q,native_source_tris));coll=any(h.segment(p,q)is not None for h in hulls)
  tests.append({'name':label,'source_segment_m':[list(p),list(q)],'visual_blocked':visual,'native_glb_blocked':actual_glb,'compound_blocked':coll,'expected_blocked':expected,'pass':visual==expected and actual_glb==expected and coll==expected})
 for original_void in cr.get('preserve_voids',cr.get('preserved_voids',[])):
  void=dict(original_void)
  if 'min_gltf_m' not in void:void.update(min_gltf_m=void['min_exchange_gltf_yup_m'],max_gltf_m=void['max_exchange_gltf_yup_m'])
  lo,hi=np.asarray(void['min_source_m'],float),np.asarray(void['max_source_m'],float);assert np.all(hi>lo)
  gpts=np.asarray(list(itertools.product(*zip(lo,hi))))@C.T
  frame.append(max(np.max(np.abs(gpts.min(axis=0)-void['min_gltf_m'])),np.max(np.abs(gpts.max(axis=0)-void['max_gltf_m']))))
  for axis in range(3):
   others=[x for x in range(3) if x!=axis]
   for u,v in itertools.product([.07,.3,.5,.7,.93],repeat=2):
    p=lo+(hi-lo)*.01;q=hi-(hi-lo)*.01
    for ax,f in zip(others,[u,v]):p[ax]=q[ax]=lo[ax]+(hi[ax]-lo[ax])*f
    test(void['name']+'_axis'+str(axis),p,q,False)
 for label,p,q in controls[ident]:test('blocked_'+label,p,q,True)
 wrong=Hull(tris.reshape(-1,3));negative=sum(not t['visual_blocked'] and wrong.segment(*t['source_segment_m'])is not None for t in tests)
 row={'id':ident,'bindings':{k:binding(p)for k,p in [('source',sp),('export',gp),('manifest',mp),('collision',cp),('source_audit',srp)]},'markers':markers,'joins':joins,'collision_shape_count':len(hulls),'collision_frame_max_error_m':float(max(frame)),'void_and_blocked_tests':tests,'whole_asset_hull_wrongly_blocks_clear_controls':negative,'wrong_axis_negative_control_count':sum(x['wrong_axis_interpretation_error_m']>.001 for x in markers),'native_animation_clips':len(native.g.doc.get('animations',[])),'native_skin_count':len(native.g.doc.get('skins',[])),'pass':all(x['pass']for x in markers+joins+tests) and max(frame)<1e-6 and sum(x['wrong_axis_interpretation_error_m']>.001 for x in markers)>0 and (negative>0 or ident=='AST-SAL-002'),'negative_control_scope':'Whole-hull filling test applies to enclosed component voids. SAL002 has a below-span void outside its overhead hull; its deliberate blocked shell control and wrong-frame marker discrimination are the relevant controls.'}
 rows.append(row);print(ident,'marker failures',[(x['name'],x.get('distance_to_named_source_surface_m'))for x in markers if not x['pass']],'join failures',[(x['name'],x['parts'])for x in joins if not x['pass']],'void/control failures',[(x['name'],x['visual_blocked'],x['native_glb_blocked'],x['compound_blocked'])for x in tests if not x['pass']][:20],'negative controls',negative)
result={'passed':bool(rows)and all(r['pass']for r in rows),'assets':rows,'method':'Independent evaluated source triangles, exact native GLB node transforms, paired source-to-native direction conversion, named source-part contact and solid-join witnesses. Finite clear rays are sampled in all three axes of every declared preserved void, with independent blocked structural controls. Actual source and native visual intersections are compared with collision compounds; a whole-component hull supplies negative controls.','limits':['Finite probes are not continuous coverage/error certification, engine physics, real host moving-door fit, service procedure, guard compliance or universal actor/cart fit.','Source markers classify fixed physical surfaces separately from optional receivers, openings and pose datums. Native clips/skins are counted; no absent motion is inferred.']}
(OUT/('independent_'+family+'_interfaces.json')).write_text(json.dumps(result,indent=2)+'\n')
