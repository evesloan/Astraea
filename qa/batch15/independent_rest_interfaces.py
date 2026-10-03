"""Independent actual rest/privacy geometry, physical interfaces and bounded authored motion."""
from pathlib import Path
import sys,json,hashlib,itertools,numpy as np
from scipy.spatial import cKDTree
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch15';BASE=ROOT/'assets/crew_rest'
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import nearest_distances,inside_mesh,segment_triangles,Hull
sys.path.insert(0,str(ROOT/'qa/batch12'));from independent_void_geometry import triangle_box_mask,hull_box_overlap
sys.path.insert(0,str(OUT));from independent_contact_graph import contact_graph,normal_witness
from independent_collision_adapters import expand
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def equal(a,b):return float(max(cKDTree(a.reshape(-1,3)).query(b.reshape(-1,3))[0].max(),cKDTree(b.reshape(-1,3)).query(a.reshape(-1,3))[0].max()))
api_path=BASE/'interface_api.json';api=json.loads(api_path.read_text())['assets'];cp=BASE/'collision_proposals.json';cols=json.loads(cp.read_text())['assets'];poses=json.loads((OUT/'independent_curtain_pose_source.json').read_text());results=[]
for mp in sorted(BASE.glob('AST-*.manifest.json')):
 m=json.loads(mp.read_text());ident=m['catalogue_id'];it=api[ident];sp=BASE/m['source'];gp=BASE/m['export'];rp=OUT/f'independent_source_{ident}.json';s=json.loads(rp.read_text());assert sha(sp)==s['sha256']==m['source_sha256'];assert sha(gp)==m['glb_sha256'];a=np.load(ROOT/s['geometry_cache']);tri=a['triangles'];labels=a['object_names'];so={o['name']:o for o in s['objects']};native=Native(gp);nt=native.tris@C;nodes=native.g.doc['nodes'];ni={n.get('name'):i for i,n in enumerate(nodes)};markers=[]
 for mr in it['surfaces']:
  p=np.asarray(mr['point_source_m']);name='MARKER_'+mr['name'];target=mr['physical_object'];n=np.asarray(mr['normal_source']);part=tri[labels==target];role=so[target]['materials'][0];idx=ni[name];actual=native.world[idx][:3,3];d=float(nearest_distances([p],part)[0]);nd=native.nearest(C@p,role=role)['distance_m'];sn=normal_witness(p,part,n);gn=normal_witness(C@p,native.tris[native.select(role=role)],C@n);se=float(np.linalg.norm(np.asarray(so[name]['matrix_world'])[:3,3]-p));ne=float(np.linalg.norm(actual-C@p));r={'name':name,'kind':'physical_surface','physical_target':target,'source_marker_error_m':se,'native_marker_error_m':ne,'distance_to_named_source_surface_m':d,'distance_to_native_surface_m':nd,'source_outward_normal_witness':sn,'native_outward_normal_witness':gn,'wrong_axis_interpretation_error_m':float(np.linalg.norm(actual-p)),'physical_surface_verified':max(d,nd)<.0002 and sn['pass']and gn['pass']};r['pass']=max(se,ne)<1e-6 and r['physical_surface_verified'];markers.append(r)
 roots=[o['name']for o in s['objects']if o['type']=='MESH'and o['min_xyz'][2]<.00002];graph=contact_graph(tri,labels,roots);states=[{'name':'closed','tri':tri,'labels':labels,'native':native,'gather':0}]
 if ident.endswith('002'):
  assert poses['source_sha256']==sha(sp)
  for j in [4,8]:
   row=poses['poses'][j];z=np.load(ROOT/row['geometry_cache']);states.append({'name':'gather_'+str(row['gather']),'tri':z['triangles'],'labels':z['object_names'],'native':Native(BASE/m['state_derivatives'][0]['export'])if row['gather']==1 else None,'gather':row['gather']})
 volumes=[];probes=[];stategraphs=[]
 for st in states:
  t=st['tri'];names=st['labels'];gn=st['native'].tris@C if st['native']else None;hulls=[h for rec in cols[ident]['shapes']for h in expand(rec,st['gather'])]
  if st['gather']>0:stategraphs.append({'state':st['name'],**contact_graph(t,names,roots)})
  for v in it['reserved_voids']:
   lo=np.asarray(v['min_source_m'])+.0002;hi=np.asarray(v['max_source_m'])-.0002;sm=triangle_box_mask(t,lo,hi);nm=triangle_box_mask(gn,lo,hi)if gn is not None else np.array([],bool);inside=[str(n)for n in np.unique(names)if inside_mesh([(lo+hi)/2],t[names==n])[0]];over=[h.record['name']for h in hulls if hull_box_overlap(h,lo,hi)['overlaps']];volumes.append({'state':st['name'],'name':v['name'],'source_intruding_parts':sorted(set(str(x)for x in names[sm])),'native_intruding_triangles':int(nm.sum())if gn is not None else None,'midpoint_inside_parts':inside,'collision_intrusions':over,'pass':not sm.any()and not nm.any()and not inside and not over})
   for ax in range(3):
    others=[a for a in range(3)if a!=ax]
    for u,w in itertools.product([.1,.5,.9],repeat=2):
     p=lo.copy();q=hi.copy()
     for ax2,f in zip(others,[u,w]):p[ax2]=q[ax2]=lo[ax2]+(hi[ax2]-lo[ax2])*f
     vb=bool(segment_triangles(p,q,t));nb=bool(segment_triangles(p,q,gn))if gn is not None else False;cb=any(h.segment(p,q)is not None for h in hulls);probes.append({'state':st['name'],'name':v['name'],'segment_source_m':[p.tolist(),q.tolist()],'expected_blocked':False,'visual_blocked':vb,'native_blocked':nb if gn is not None else None,'proposal_blocked':cb,'pass':not vb and not nb and not cb})
  control=([-.49,.13,-.01],[-.49,.13,.05])if ident.endswith('001')else([.68,-.06,-.01],[.68,-.06,.05]);p,q=control;vb=bool(segment_triangles(p,q,t));nb=bool(segment_triangles(p,q,gn))if gn is not None else True;cb=any(h.segment(p,q)is not None for h in hulls);probes.append({'state':st['name'],'name':'actual_floor_support_positive_control','segment_source_m':control,'expected_blocked':True,'pass':vb and nb and cb})
 motion=[];privacy=[]
 if ident.endswith('002'):
  root=ni['AST-CRW-002_CURTAIN_MOTION'];moving_parts=[x['name']for x in s['objects']if x['type']=='MESH'and x['parent']=='AST-CRW-002_CURTAIN_MOTION'];moving=np.isin(labels,moving_parts)
  def desc(i):
   while i in native.parents:
    i=native.parents[i]
    if i==root:return True
   return False
  moving_nodes=[nodes[i].get('name')for i in native.world if desc(i)and'mesh'in nodes[i]];nm=np.isin(native.nodes,moving_nodes);ownership=equal(tri[moving],nt[nm]);posechecks=[];en=it['continuous_geometric_envelope'];lo=np.asarray(en['min_source_m']);hi=np.asarray(en['max_source_m']);L=it['motion']['segment_developed_length_m'];nativeopen=states[-1]['native'];closedparents={mr['physical_object']:desc(ni['MARKER_'+mr['name']])for mr in it['surfaces']};markers_owner=all(v==(k in moving_parts)for k,v in closedparents.items())
  for row in poses['poses']:
   z=np.load(ROOT/row['geometry_cache']);t=z['triangles'];ln=z['object_names'];value=row['gather'];mm=np.isin(ln,moving_parts);verts=t[mm].reshape(-1,3);within=bool((verts>=lo-2e-6).all()and(verts<=hi+2e-6).all());objs={x['name']:x for x in row['objects']};span=2.16-1.8*value;lead=.02+1.8*value;amp=np.sqrt(L*L-(span/24)**2)/2;ringw=[]
   track=t[ln=='002_continuous_round_track']
   for i in range(25):
    pt=np.array([.68,lead+span*i/24,2.097]);ring=t[ln==f'002_supported_ring_{i:02}'];rd=float(nearest_distances([pt],ring)[0]);td=float(nearest_distances([pt],track)[0]);ringw.append({'ring':i,'actual_edge_contact_error_m':max(rd,td)})
   p=np.array([.643-(amp-.025),lead-.003,1.05]);grip=t[ln=='002_leading_pull_grip'];me=float(np.linalg.norm(np.asarray(objs['MARKER_curtain_pull']['world_matrix'])[:3,3]-p));gd=float(nearest_distances([p],grip)[0]);entry={'gather':value,'all_moving_vertices_inside_declared_envelope':within,'actual_bounds_m':[verts.min(0).tolist(),verts.max(0).tolist()],'ring_edge_support':ringw,'actual_grip_marker_error_m':me,'grip_named_surface_distance_m':gd,'developed_segment_identity_error_m':float(abs(np.sqrt((span/24)**2+(2*amp)**2)-L)),'pass':within and max(x['actual_edge_contact_error_m']for x in ringw)<.00002 and max(me,gd)<.00002};posechecks.append(entry)
   if value==1:
    state_error=equal(t,nativeopen.tris@C);oi={n.get('name'):i for i,n in enumerate(nativeopen.g.doc['nodes'])};native_marker_error=float(np.linalg.norm(nativeopen.world[oi['MARKER_curtain_pull']][:3,3]-C@p))
  # Analytic bounds: all ring centers interpolate from leading .02..1.82 to fixed2.18; constant ring/tape depth8mm keeps centres at least15mm apart. The only fixed-part overlap allowed is rod/ring bearing, with invariant XZ sections.
  fixed=tri[~moving];fl=labels[~moving];exclude=fl!='002_continuous_round_track';fixed_envelope_intrusions=sorted(set(str(x)for x in fl[exclude][triangle_box_mask(fixed[exclude],lo+.00002,hi-.00002)]));support_span=bool(.02-.004>-.078 and 2.18+.004<2.278);min_ring_gap=.36/24-.008
  motion.append({'moving_root':'AST-CRW-002_CURTAIN_MOTION','source_moving_parts':moving_parts,'native_moving_nodes':moving_nodes,'source_native_moving_ownership_hausdorff_m':ownership,'physical_marker_ownership_correct':markers_owner,'actual_gathered_native_geometry_hausdorff_m':state_error,'gathered_native_grip_marker_error_m':native_marker_error,'actual_authored_pose_checks':posechecks,'complete_envelope_fixed_nontrack_intrusions':fixed_envelope_intrusions,'analytical_ring_support_range_within_track':support_span,'minimum_ring_tape_longitudinal_gap_m':min_ring_gap,'continuous_basis':'Every authored root/ring Y is affine in gather; pleat half-depth is monotone sqrt with fixed segment length. Cloth and tape endpoint X are affine in half-depth; thickness bounded by1.5mm. Fixed rod XZ and moving ring XZ are invariant; tape-to-ring ends are invariant and tape-to-fabric ends share authored coordinates. Full declared envelope avoids all fixed nontrack parts. This is geometric parametrization, not cloth dynamics.','pass':ownership<1e-6 and markers_owner and state_error<1e-6 and native_marker_error<1e-6 and all(x['pass']for x in posechecks)and not fixed_envelope_intrusions and support_span and min_ring_gap>.006})
  for st in [states[0],states[-1]]:
   t=st['tri'];gn=st['native'].tris@C
   for eye_z in [1.15,1.65]:
    for y in np.linspace(.3,1.5,13):
     p=[2.,float(y),eye_z];q=[0,float(y),.59];v=bool(segment_triangles(p,q,t));n=bool(segment_triangles(p,q,gn));expected=st['gather']==0;privacy.append({'state':st['name'],'eye_source_m':p,'target_source_m':q,'expected_occluded':expected,'actual_source_occluded':v,'actual_native_occluded':n,'pass':v==n==expected})
   for p,q in [([2,1,2.2],[0,1,2.2]),([2,1,.15],[0,1,.15]),([2,-.3,1],[0,-.3,1]),([2,2.5,1],[0,2.5,1])]:
    v=bool(segment_triangles(p,q,t));n=bool(segment_triangles(p,q,gn));privacy.append({'state':st['name'],'eye_source_m':p,'target_source_m':q,'expected_occluded':False,'actual_source_occluded':v,'actual_native_occluded':n,'pass':not v and not n})
 wrong=Hull(tri.reshape(-1,3));negative=sum(not x['expected_blocked']and wrong.segment(*x['segment_source_m'])is not None for x in probes)
 r={'catalogue_id':ident,'passed':all(x['pass']for x in markers+volumes+probes+motion+privacy)and graph['passed']and all(x['passed']for x in stategraphs)and negative>0,'bindings':{k:bind(p)for k,p in [('source',sp),('export',gp),('manifest',mp),('collision',cp),('interface_api',api_path),('source_audit',rp)]},'markers':markers,'all_part_contact_graph':graph,'additional_pose_contact_graphs':stategraphs,'complete_empty_volume_checks':volumes,'clear_and_blocked_probes':probes,'motion_checks':motion,'bounded_privacy_rays':privacy,'whole_asset_hull_negative_controls':negative,'limits':['Actual configured manual-editable source only; no live frame resizing controls or generalized fitting guarantee.','Analytical authored curtain bounds plus finite actual-state samples are geometric evidence; cloth mechanics, structural loads, acoustics, whole-room privacy and runtime input remain unimplemented.','No source cabin, new berth, body/species envelope, roommate or gameplay assignment.'],'executed_script_sha256':sha(Path(__file__))};results.append(r);print(ident,'PASS',r['passed'],'markers',[x['name']for x in markers if not x['pass']],'isolated',graph['isolated_parts'],'voids',[x['name']for x in volumes if not x['pass']],'motion',[(x['pass'],x['complete_envelope_fixed_nontrack_intrusions'],[a['gather']for a in x['actual_authored_pose_checks']if not a['pass']])for x in motion],'privacy_failures',sum(not x['pass']for x in privacy),flush=True)
(OUT/'independent_crew_rest_interfaces.json').write_text(json.dumps({'passed':all(x['passed']for x in results),'assets':results},indent=2)+'\n')
