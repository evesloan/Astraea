"""Read-only actual source/native storage and mounted task-light interface review."""
from pathlib import Path
import sys,json,hashlib,itertools,numpy as np
from scipy.spatial import cKDTree
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch15';BASE=ROOT/'assets/crew_personal'
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import Hull,nearest_distances,inside_mesh,segment_triangles
sys.path.insert(0,str(ROOT/'qa/batch12'));from independent_void_geometry import triangle_box_mask,hull_box_overlap
sys.path.insert(0,str(OUT));from independent_contact_graph import contact_graph,normal_witness
from independent_sweep_geometry import sweep_contacts
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def equal(a,b):return float(max(cKDTree(a.reshape(-1,3)).query(b.reshape(-1,3))[0].max(),cKDTree(b.reshape(-1,3)).query(a.reshape(-1,3))[0].max()))
results=[]
for mp in sorted(BASE.glob('AST-*.manifest.json')):
 m=json.loads(mp.read_text());ident=m['catalogue_id'];sp=BASE/m['source'];gp=BASE/m['export'];rp=OUT/f'independent_source_{ident}.json';s=json.loads(rp.read_text());assert sha(sp)==s['sha256']==m['source_sha256'];assert sha(gp)==m['glb_sha256'];so={o['name']:o for o in s['objects']};a=np.load(ROOT/s['geometry_cache']);tri=a['triangles'];labels=a['object_names'];native=Native(gp);nt=native.tris@C;nodes=native.g.doc['nodes'];ni={n.get('name'):i for i,n in enumerate(nodes)}
 markers=[]
 for mr in m['physical_and_proposal_markers']:
  p=np.asarray(mr['source_m']);name=mr['name'];i=ni.get(name);world=native.world[i][:3,3]if i is not None else np.zeros(3);target=mr['physical_part'];physical=mr['kind'].startswith('physical')
  r={'name':name,'kind':mr['kind'],'physical_target':target,'source_marker_error_m':float(np.linalg.norm(np.asarray(so[name]['matrix_world'])[:3,3]-p)),'native_marker_present':i is not None,'native_marker_error_m':float(np.linalg.norm(world-C@p)),'declared_native_error_m':float(np.linalg.norm(np.asarray(mr['gltf_m'])-C@p)),'wrong_axis_interpretation_error_m':float(np.linalg.norm(world-p)),'declared_parent':mr['parent_root'],'actual_source_parent':so[name]['parent'],'actual_native_parent':nodes[native.parents[i]].get('name')if i in native.parents else None}
  if physical:
   part=tri[labels==target];assert len(part);role=so[target]['materials'][0];n=np.asarray(mr['direction_source']);sel=native.tris[native.select(role=role)]
   r.update(distance_to_named_source_surface_m=float(nearest_distances([p],part)[0]),distance_to_native_surface_m=native.nearest(C@p,role=role)['distance_m'],source_outward_normal_witness=normal_witness(p,part,n),native_outward_normal_witness=normal_witness(C@p,sel,C@n))
   r['physical_surface_verified']=max(r['distance_to_named_source_surface_m'],r['distance_to_native_surface_m'])<.0002 and r['source_outward_normal_witness']['pass']and r['native_outward_normal_witness']['pass']
  r['pass']=i is not None and max(r['source_marker_error_m'],r['native_marker_error_m'],r['declared_native_error_m'])<1e-6 and r.get('physical_surface_verified',True)and r['declared_parent']==r['actual_source_parent']==r['actual_native_parent'];markers.append(r)
 roots=[o['name']for o in s['objects']if o.get('min_xyz',[0,0,1])[2]<.00002 and o['type']=='MESH']if ident.endswith('003')else['headboard_mount_backplate'];graph=contact_graph(tri,labels,roots)
 joins=[]
 for j in m['joins']:
  p=np.asarray(j['probe_source_m']);r={'name':j['name'],'parts':j['parts'],'kind':j['kind'],'witnesses':[]}
  for ix,name in enumerate(j['parts']):
   t=tri[labels==name];d=float(nearest_distances([p],t)[0]);w={'part':name,'distance_m':d}
   if 'normal_a_source'in j:w['normal']=normal_witness(p,t,j['normal_a_source'if ix==0 else'normal_b_source']);w['pass']=d<.0002 and w['normal']['pass']
   else:w['pass']=d<.0002 or bool(inside_mesh([p],t)[0]);w['inside_or_surface']=w['pass']
   r['witnesses'].append(w)
  r['pass']=all(x['pass']for x in r['witnesses']);joins.append(r)
 cp=BASE/m['collision_proposal_file'];col=json.loads(cp.read_text())[ident];moving_parts=[name for name,o in so.items()if o.get('parent')=='DRAWER_TRANSLATE'and o['type']=='MESH'];moving=np.isin(labels,moving_parts);delta=np.array(m['details'].get('drawer_translation_source_m',[0,0,0]));states=[('closed',0,native)]+[('open',1,Native(BASE/x['export']))for x in m['state_derivatives']];volumes=[];probes=[];graphs=[]
 for state,t,nn in states:
  st=tri.copy();st[moving]+=delta*t;gn=nn.tris@C;hulls=[Hull(np.asarray(x['points_source_m'])+(delta*t if x['movement_group']=='drawer'else 0),x)for x in col['shapes']]
  if state!='closed':graphs.append({'state':state,**contact_graph(st,labels,roots)})
  for v in m['receiver_voids']:
   off=delta*t if v['state']=='drawer_local'else np.zeros(3);lo=np.asarray(v['min_source_m'])+off+.0002;hi=np.asarray(v['max_source_m'])+off-.0002;sm=triangle_box_mask(st,lo,hi);nm=triangle_box_mask(gn,lo,hi);contains=[str(p)for p in np.unique(labels)if inside_mesh([(lo+hi)/2],st[labels==p])[0]];overlaps=[h.record['name']for h in hulls if hull_box_overlap(h,lo,hi)['overlaps']];volumes.append({'name':v['name'],'state':state,'inset_box_source_m':[lo.tolist(),hi.tolist()],'source_intruding_parts':sorted(set(str(x)for x in labels[sm])),'native_intruding_triangles':int(nm.sum()),'midpoint_inside_parts':contains,'collision_intrusions':overlaps,'pass':not sm.any()and not nm.any()and not contains and not overlaps})
   for ax in range(3):
    others=[a for a in range(3)if a!=ax]
    for u,w in itertools.product([.1,.5,.9],repeat=2):
     p=lo.copy();q=hi.copy()
     for a,f in zip(others,[u,w]):p[a]=q[a]=lo[a]+(hi[a]-lo[a])*f
     vb=bool(segment_triangles(p,q,st));nb=bool(segment_triangles(p,q,gn));cb=any(h.segment(p,q)is not None for h in hulls);probes.append({'name':v['name'],'state':state,'segment_source_m':[p.tolist(),q.tolist()],'visual_blocked':vb,'native_blocked':nb,'proposal_blocked':cb,'expected_blocked':False,'pass':not vb and not nb and not cb})
  controls=[('plinth',[0,0,.07],[0,0,.17]),('back',[0,.20,1.1],[0,.25,1.1])]if ident.endswith('003')else[('backplate',[0,-.02,0],[0,.01,0]),('shelf',[0,-.13,-.16],[0,-.13,-.11])]
  for name,p,q in controls:
   vb=bool(segment_triangles(p,q,st));nb=bool(segment_triangles(p,q,gn));cb=any(h.segment(p,q)is not None for h in hulls);probes.append({'name':name,'state':state,'segment_source_m':[p,q],'visual_blocked':vb,'native_blocked':nb,'proposal_blocked':cb,'expected_blocked':True,'pass':vb and nb and cb})
 motion=[]
 if moving.any():
  swept=sweep_contacts(tri[moving],tri[~moving],delta,labels[moving],labels[~moving]);allowed=[];bad=[]
  for x in swept:
   mt=tri[labels==x['moving_part']];ft=tri[labels==x['fixed_part']];axis_separation=[]
   for ax in range(3):
    if abs(delta[ax])>1e-10:continue
    distance=max(float(mt[:, :,ax].min()-ft[:,:,ax].max()),float(ft[:,:,ax].min()-mt[:,:,ax].max()))
    if distance>=-.0000001:axis_separation.append({'axis':ax,'gap_m':distance})
   rec={**x,'constant_axis_boundary_witnesses':axis_separation}
   (allowed if axis_separation or x['translation_fraction_interval'][1]<2e-6 else bad).append(rec)
  penetration=[]
  for mpn in moving_parts:
   mt=tri[labels==mpn];pts=np.concatenate([np.unique(mt.reshape(-1,3),axis=0),mt.mean(1)])
   for fpn in np.unique(labels[~moving]):
    ft=tri[labels==fpn];mask=inside_mesh(pts,ft)&(nearest_distances(pts,ft)>.00002)
    if mask.any():penetration.append({'moving':mpn,'fixed':str(fpn),'contained_samples':int(mask.sum())})
  root=ni['DRAWER_TRANSLATE']
  def desc(ix):
   while ix in native.parents:
    ix=native.parents[ix]
    if ix==root:return True
   return False
  moving_nodes=[nodes[ix].get('name')for ix in native.world if desc(ix)and'mesh'in nodes[ix]];mask=np.isin(native.nodes,moving_nodes);ownership=equal(tri[moving],nt[mask]);opened=states[1][2];ot=opened.tris@C;expected=nt.copy();expected[mask]+=delta;state_error=equal(expected,ot);markrows=[]
  oi={n.get('name'):i for i,n in enumerate(opened.g.doc['nodes'])}
  for mr in m['physical_and_proposal_markers']:
   move=mr['physical_part']in moving_parts;actual=desc(ni[mr['name']]);p=np.asarray(mr['source_m'])+(delta if move else 0);err=float(np.linalg.norm(opened.world[oi[mr['name']]][:3,3]-C@p));markrows.append({'name':mr['name'],'expected_moving':move,'actual_moving':actual,'open_native_error_m':err,'pass':move==actual and err<1e-6})
  # Full linear support overlap at two planar runner faces; all intermediate translations retain >= endpoint overlap.
  bearings=[]
  for side in ['left','right']:
   mt=tri[labels==f'drawer_{side}_sliding_runner'];ft=tri[labels==f'{side}_fixed_drawer_runner'];overlaps=[]
   for fraction in [0,1]:
    moved=mt+delta*fraction;overlaps.append(float(min(moved[:,:,1].max(),ft[:,:,1].max())-max(moved[:,:,1].min(),ft[:,:,1].min())))
   bearings.append({'side':side,'closed_and_open_longitudinal_overlap_m':overlaps,'minimum_through_monotone_stroke_m':min(overlaps),'pass':min(overlaps)>.15})
  continuous_voids=[]
  for v in m['receiver_voids']:
   lo=np.asarray(v['min_source_m'])+.0002;hi=np.asarray(v['max_source_m'])-.0002
   if v['state']=='drawer_local':
    slo=lo+np.minimum(delta,0);shi=hi+np.maximum(delta,0);test=tri[~moving];ln=labels[~moving];ch=[Hull(x['points_source_m'],x)for x in col['shapes']if x['movement_group']!='drawer'];hit=triangle_box_mask(test,slo,shi);cols=[h.record['name']for h in ch if hull_box_overlap(h,slo,shi)['overlaps']]
    continuous_voids.append({'name':v['name'],'method':'Complete axis-aligned monotone swept box against all fixed triangles/profiles; rigid moving interior self-clearance is state-invariant','swept_box_source_m':[slo.tolist(),shi.tolist()],'intruding_fixed_parts':sorted(set(str(x)for x in ln[hit])),'collision_intrusions':cols,'pass':not hit.any()and not cols})
   else:
    mt=tri[moving];slo=np.minimum(mt.min((0,1)),mt.min((0,1))+delta);shi=np.maximum(mt.max((0,1)),mt.max((0,1))+delta);sep=bool(((shi<=lo)|(slo>=hi)).any());continuous_voids.append({'name':v['name'],'method':'Whole moving assembly monotone sweep AABB disjoint from complete fixed declared box','pass':sep})
  motion.append({'root':'DRAWER_TRANSLATE','translation_source_m':delta.tolist(),'moving_source_parts':moving_parts,'moving_native_nodes':moving_nodes,'source_native_moving_geometry_hausdorff_m':ownership,'actual_open_native_geometry_error_m':state_error,'moving_marker_checks':markrows,'continuous_sweep_contacts':len(swept),'permitted_boundary_contacts':len(allowed),'permitted_boundary_part_pairs':sorted(set((x['moving_part'],x['fixed_part'])for x in allowed)),'continuous_obstructing_contacts':bad[:50],'initial_deep_containment':penetration,'runner_support':bearings,'continuous_useful_volume_checks':continuous_voids,'pass':all(x['pass']for x in continuous_voids)and not bad and not penetration and ownership<1e-6 and state_error<1e-6 and all(x['pass']for x in markrows+bearings)})
 wrong=Hull(tri.reshape(-1,3));negative=sum(not x['expected_blocked']and wrong.segment(*x['segment_source_m'])is not None for x in probes)
 result={'catalogue_id':ident,'passed':all(x['pass']for x in markers+joins+volumes+probes+motion)and graph['passed']and all(x['passed']for x in graphs)and negative>0,'bindings':{k:bind(p)for k,p in [('source',sp),('export',gp),('manifest',mp),('collision',cp),('source_audit',rp)]},'markers':markers,'declared_join_witnesses':joins,'all_part_contact_graph':graph,'open_state_contact_graphs':graphs,'collision_shape_count':len(col['shapes']),'complete_empty_volume_checks':volumes,'clear_and_blocked_probes':probes,'motion_checks':motion,'whole_asset_hull_negative_controls':negative,'wrong_axis_negative_control_count':sum(x['wrong_axis_interpretation_error_m']>.001 for x in markers),'limits':['Mount dependency for004 is the actual frame receiver, reviewed separately; graph roots at module mounting backplate.','Triangle-box and convex feasibility check complete endpoint boxes. Complete drawer linear triangle sweep starts at t0, retains witnessed runner boundary sliding, rejects other interior contacts; no cloth or runtime mechanic is implied.','Geometric support, contact and proposed use only; no loads, bodies, reach, inventory or photometry certification.'],'executed_script_sha256':sha(Path(__file__))};results.append(result)
 print(ident,'PASS',result['passed'],'marker failures',[x['name']for x in markers if not x['pass']],'join failures',[x['name']for x in joins if not x['pass']],'isolated',graph['isolated_parts'],'void failures',[(x['name'],x['source_intruding_parts'],x['collision_intrusions'])for x in volumes if not x['pass']],'motion',[(x['pass'],len(x['continuous_obstructing_contacts']))for x in motion],flush=True)
(OUT/'independent_crew_personal_interfaces.json').write_text(json.dumps({'passed':all(x['passed']for x in results),'assets':results},indent=2)+'\n')
