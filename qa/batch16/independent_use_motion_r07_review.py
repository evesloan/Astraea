"""Independent complete use/motion/interface review; source/native inputs read only.

The rotations are certified with conservative exact sinusoidal projection bounds
over closed angle intervals, not inferred from a finite pose grid. Convex hulls
here enclose independently evaluated semantic part triangles; no author helper is
imported. A hull separation therefore safely proves visual separation even before
the recorded source convex-equivalence check. Near-zero boundary contact is
reported separately from interior intrusion.
"""
from pathlib import Path
import sys,json,hashlib,itertools,math
import numpy as np
from scipy.spatial import ConvexHull,cKDTree
from scipy.optimize import linprog
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch16';BASE=ROOT/'assets/auditorium_use'
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import nearest_distances,inside_mesh,segment_triangles,Hull
sys.path.insert(0,str(ROOT/'qa/batch12'));from independent_void_geometry import triangle_box_mask
sys.path.insert(0,str(ROOT/'qa/batch15'));from independent_contact_graph import normal_witness
from independent_sweep_geometry import sweep_contacts
TOL=2e-7
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def cloud(t):return np.unique(np.asarray(t).reshape(-1,3),axis=0)
def equal(a,b):
 a=cloud(a);b=cloud(b)
 return float(max(cKDTree(a).query(b)[0].max(),cKDTree(b).query(a)[0].max()))
def rotate(v,p,angle):
 v=np.asarray(v);p=np.asarray(p);a=np.deg2rad(angle);r=np.array([[1,0,0],[0,np.cos(a),-np.sin(a)],[0,np.sin(a),np.cos(a)]])
 return (v-p)@r.T+p
def pose(v,rec,fraction):
 if rec['kind']=='translation':return np.asarray(v)+np.asarray(rec['axis_source'])*rec['travel']*fraction
 return rotate(v,rec['pivot_source_m'],rec['travel']*fraction)
def unit_axes(a):
 a=np.asarray(a).reshape(-1,3);n=np.linalg.norm(a,axis=1);a=a[n>1e-10]/n[n>1e-10,None]
 return np.unique(np.round(a,12),axis=0)
def axes_for(a,b):
 ha=ConvexHull(a);hb=ConvexHull(b)
 return unit_axes(np.concatenate([np.eye(3),ha.equations[:,:3],hb.equations[:,:3]]))
def interval_projection(v,p,axes,angle0,angle1):
 """Exact extrema of every moving vertex dot every fixed axis over full arc."""
 v=np.asarray(v)-p;a,b=sorted(np.deg2rad([angle0,angle1]));axes=np.asarray(axes)
 const=v[:,0,None]*axes[None,:,0]+np.asarray(p)@axes.T
 co=v[:,1,None]*axes[None,:,1]+v[:,2,None]*axes[None,:,2]
 si=v[:,1,None]*axes[None,:,2]-v[:,2,None]*axes[None,:,1]
 v0=const+co*np.cos(a)+si*np.sin(a);v1=const+co*np.cos(b)+si*np.sin(b)
 lo=np.minimum(v0,v1);hi=np.maximum(v0,v1);base=np.arctan2(si,co)
 for k in range(-3,4):
  t=base+k*np.pi;ok=(t>=a)&(t<=b);val=const+co*np.cos(t)+si*np.sin(t)
  lo=np.where(ok,np.minimum(lo,val),lo);hi=np.where(ok,np.maximum(hi,val),hi)
 return lo.min(0),hi.max(0)
def overlap_radius(a,b):
 """Positive common inscribed radius means true 3D interior intrusion."""
 ha=ConvexHull(a);hb=ConvexHull(b);eq=np.concatenate([ha.equations,hb.equations]);aa=np.column_stack([eq[:,:3],np.ones(len(eq))])
 res=linprog([0,0,0,-1],A_ub=aa,b_ub=-eq[:,3],bounds=[(None,None)]*3+[(None,None)],method='highs')
 return {'common_interior_radius_m':float(res.x[3]),'witness_source_m':res.x[:3].tolist()}if res.success else {'common_interior_radius_m':None,'solver':res.message}
def static_pair(a,b):
 axes=axes_for(a,b);ap=a@axes.T;bp=b@axes.T;g=np.maximum(ap.min(0)-bp.max(0),bp.min(0)-ap.max(0));ix=int(g.argmax())
 if g[ix]>=-TOL:return {'pass':True,'separation_axis':axes[ix].tolist(),'minimum_gap_m':float(g[ix]),'classification':'separated'if g[ix]>TOL else'boundary_or_roundoff_only'}
 ov=overlap_radius(a,b);r=ov['common_interior_radius_m'];return {'pass':r is not None and r<=TOL,**ov,'classification':'interior_intrusion'if r is not None and r>TOL else'boundary_or_roundoff_only'}
def rotation_pair(a,b,rec,max_depth=22):
 p=np.asarray(rec['pivot_source_m']);travel=rec['travel'];leaves=[];bad=[]
 def check(f0,f1,depth):
  aa=pose(a,rec,(f0+f1)/2);axes=axes_for(aa,b);lo,hi=interval_projection(a,p,axes,travel*f0,travel*f1);bp=b@axes.T;g=np.maximum(lo-bp.max(0),bp.min(0)-hi);ix=int(g.argmax())
  if g[ix]>=-TOL:
   leaves.append({'fraction_interval':[f0,f1],'constant_separation_axis':axes[ix].tolist(),'minimum_gap_over_entire_interval_m':float(g[ix]),'classification':'separated'if g[ix]>TOL else'boundary_or_roundoff_only'});return
  # A positive-volume witness at an actual pose is a failure, not a proof from samples.
  ov=overlap_radius(aa,b)
  if ov['common_interior_radius_m'] is not None and ov['common_interior_radius_m']>TOL:
   bad.append({'fraction':(f0+f1)/2,**ov,'classification':'actual_pose_interior_intrusion'});return
  if depth>=max_depth:
   bad.append({'fraction_interval':[f0,f1],'classification':'uncertified_interval'});return
  check(f0,(f0+f1)/2,depth+1);check((f0+f1)/2,f1,depth+1)
 check(0,1,0)
 return {'pass':not bad,'continuous_angle_range_degrees':[0,travel],'certificate_intervals':leaves,'failures':bad}
def linear_pair(a,b,rec):
 swept=np.concatenate([a,pose(a,rec,1)]);r=static_pair(swept,b)
 return {**r,'continuous_translation_source_m':(np.asarray(rec['axis_source'])*rec['travel']).tolist(),'method':'Complete convex swept hull of actual part at both closed translation endpoints; exact for convex part translating on straight segment'}
def motion_pair(a,b,rec):return rotation_pair(a,b,rec)if rec['kind']=='rotation'else linear_pair(a,b,rec)
def boxcloud(lo,hi):return np.array(list(itertools.product(*zip(lo,hi))),float)
def descendants(native,name):
 nodes=native.g.doc['nodes'];root=next(i for i,n in enumerate(nodes)if n.get('name')==name);out=[]
 for i,n in enumerate(nodes):
  k=i
  while k in native.parents:
   k=native.parents[k]
   if k==root:out.append(i);break
 return out
def check_asset(mp):
 m=json.loads(mp.read_text());ident=m['catalogue_id'];sp=BASE/m['source'];gp=BASE/m['export'];rp=OUT/f'independent_source_{ident}.json';s=json.loads(rp.read_text());assert sha(sp)==s['sha256']==m['source_sha256'];assert sha(gp)==m['glb_sha256']
 so={o['name']:o for o in s['objects']};a=np.load(ROOT/s['geometry_cache']);tri=np.asarray(a['triangles'],float);labels=a['object_names'];parts={str(n):tri[labels==n]for n in np.unique(labels)};verts={n:cloud(t)for n,t in parts.items()}
 native=Native(gp);nt=native.tris@C;nodes=native.g.doc['nodes'];ni={n.get('name'):i for i,n in enumerate(nodes)}
 convex=[]
 for n,t in parts.items():
  h=ConvexHull(verts[n]);vol=abs(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6);cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);norm=cross/np.linalg.norm(cross,axis=1)[:,None];planarity=np.max(np.einsum('vti,ti->vt',verts[n][:,None,:]-t[None,:,0],norm))
  convex.append({'part':n,'actual_volume_m3':float(vol),'convex_envelope_volume_m3':float(h.volume),'volume_difference_m3':float(abs(vol-h.volume)),'maximum_source_vertex_outside_any_oriented_triangle_plane_m':float(planarity),'pass':abs(vol-h.volume)<1e-8 and planarity<TOL})
 markers=[]
 for mr in m['physical_and_proposal_markers']:
  p=np.asarray(mr['source_m']);name=mr['name'];i=ni[name];w=native.world[i];target=mr['physical_part'];props=nodes[i].get('extras',{})
  local=np.linalg.inv(np.asarray(so[mr['parent_root']]['matrix_world']))@np.append(p,1)
  r={'name':name,'kind':mr['kind'],'physical_target':target,'source_marker_error_m':float(np.linalg.norm(np.asarray(so[name]['matrix_world'])[:3,3]-p)),'native_marker_error_m':float(np.linalg.norm(w[:3,3]-C@p)),'declared_native_error_m':float(np.linalg.norm(np.asarray(mr['gltf_m'])-C@p)),'declared_parent':mr['parent_root'],'actual_source_parent':so[name]['parent'],'actual_native_parent':nodes[native.parents[i]].get('name'),'source_extras_world_error_m':float(np.linalg.norm(np.asarray(so[name]['properties']['source_position_m'])-p)),'native_extras_world_error_m':float(np.linalg.norm(np.asarray(props['gltf_position_m'])-C@p)),'explicit_parent_local_error_m':float(np.linalg.norm(np.asarray(props['parent_local_source_m'])-local[:3]))}
  if target:
   part=parts[target];role=so[target]['materials'][0];sel=native.tris[native.select(role=role)];n=np.asarray(mr['direction_source']);r.update(source_surface_distance_m=float(nearest_distances([p],part)[0]),native_surface_distance_m=native.nearest(C@p,role=role)['distance_m'],source_normal=normal_witness(p,part,n),native_normal=normal_witness(C@p,sel,C@n));r['surface_pass']=max(r['source_surface_distance_m'],r['native_surface_distance_m'])<TOL and r['source_normal']['pass']and r['native_normal']['pass']
  r['pass']=max(r[k]for k in ['source_marker_error_m','native_marker_error_m','declared_native_error_m','source_extras_world_error_m','native_extras_world_error_m','explicit_parent_local_error_m'])<1e-6 and r.get('surface_pass',True)and r['declared_parent']==r['actual_source_parent']==r['actual_native_parent'];markers.append(r)
 joins=[]
 for j in m['joins']:
  p=np.asarray(j['probe_source_m']);ws=[]
  for ix,n in enumerate(j['parts']):
   t=parts[n];d=float(nearest_distances([p],t)[0]);row={'part':n,'distance_m':d}
   if 'normal_a_source'in j:
    no=np.asarray(j['normal_a_source'if ix==0 else'normal_b_source']);role=so[n]['materials'][0];row.update(source_normal=normal_witness(p,t,no),native_normal=normal_witness(C@p,native.tris[native.select(role=role)],C@no));row['pass']=d<TOL and row['source_normal']['pass']and row['native_normal']['pass']
   else:row['pass']=d<TOL or bool(inside_mesh([p],t)[0])
   ws.append(row)
  joins.append({'name':j['name'],'kind':j['kind'],'parts':j['parts'],'witnesses':ws,'opposing_declared_normal_dot':float(np.dot(j['normal_a_source'],j['normal_b_source']))if'normal_a_source'in j else None,'pass':all(x['pass']for x in ws)})
 motion=[];states=[('closed',{},native)];rotors={r['root']:r for r in m['motion_records']}
 for rec in m['motion_records']:
  root=rec['root'];moving=rec['semantic_parts'];actual=sorted(n for n in parts if so[n]['parent']==root);ids=descendants(native,root);nn=[nodes[i].get('name')for i in ids if'mesh'in nodes[i]];mask=np.isin(native.nodes,nn);mm=np.isin(labels,moving);pairs=[]
  for n in moving:
   for f in parts:
    if f in moving:continue
    pairs.append({'moving_part':n,'fixed_part':f,**motion_pair(verts[n],verts[f],rec)})
  deriv=next(d for d in m['state_derivatives']if d['root']==root);assert sha(BASE/deriv['export'])==deriv['glb_sha256'];opened=Native(BASE/deriv['export']);states.append((root,{root:1},opened));ot=opened.tris@C;expected=nt.copy();expected[mask]=pose(expected[mask],rec,1);marks=[];oi={n.get('name'):i for i,n in enumerate(opened.g.doc['nodes'])}
  for mr in m['physical_and_proposal_markers']:
   move=mr['parent_root']==root;real=ni[mr['name']]in ids;p=np.asarray(mr['source_m']);p=pose(p,rec,1)if move else p;err=float(np.linalg.norm(opened.world[oi[mr['name']]][:3,3]-C@p));row={'name':mr['name'],'expected_moving':move,'native_descendant_of_root':real,'terminal_native_marker_error_m':err,'pass':move==real and err<1e-6}
   if mr['physical_part']:
    direction=np.asarray(mr['direction_source']);direction=rotate(direction,[0,0,0],rec['travel'])if move and rec['kind']=='rotation'else direction;part=pose(parts[mr['physical_part']],rec,1)if move else parts[mr['physical_part']];role=so[mr['physical_part']]['materials'][0];row['terminal_source_surface_distance_m']=float(nearest_distances([p],part)[0]);row['terminal_native_normal']=normal_witness(C@p,opened.tris[opened.select(role=role)],C@direction);row['pass']&=row['terminal_source_surface_distance_m']<TOL and row['terminal_native_normal']['pass']
   marks.append(row)
  # Actual terminal root world delta must equal the declared transform in native basis.
  affine=np.eye(4)
  if rec['kind']=='translation':affine[:3,3]=C@(np.asarray(rec['axis_source'])*rec['travel'])
  else:
   angle=np.deg2rad(rec['travel']);rs=np.array([[1,0,0],[0,np.cos(angle),-np.sin(angle)],[0,np.sin(angle),np.cos(angle)]]);affine[:3,:3]=C@rs@C.T;pg=C@np.asarray(rec['pivot_source_m']);affine[:3,3]=pg-affine[:3,:3]@pg
  actual_affine=opened.world[oi[root]]@np.linalg.inv(native.world[ni[root]]);affine_error=float(np.max(np.abs(actual_affine-affine)));root_extras=nodes[ni[root]].get('extras',{});root_metadata_pass=np.linalg.norm(root_extras['axis_gltf']-C@np.asarray(rec['axis_source']))<1e-8 and root_extras['travel_degrees_or_m']==rec['travel'] and root_extras['motion_type']==rec['kind']
  own=equal(tri[mm],nt[mask]);terminal=equal(expected,ot);r={'root':root,'kind':rec['kind'],'full_range':[0,rec['travel']],'source_moving_parts':actual,'declared_moving_parts':moving,'native_moving_mesh_nodes':nn,'actual_terminal_native_root_affine_error':affine_error,'actual_root_metadata_pass':bool(root_metadata_pass),'moving_source_native_hausdorff_m':own,'terminal_native_geometry_hausdorff_m':terminal,'pairs':pairs,'moving_markers':marks,'pass':actual==sorted(moving)and own<1e-6 and terminal<1e-6 and affine_error<1e-6 and root_metadata_pass and all(x['pass']for x in pairs+marks)}
  # Exact invariant bearing point on the rotation axis and opposite axial normals.
  bearing=[]
  if rec['kind']=='rotation':
   for j in m['joins']:
    if j['kind']!='rotating_endface_bearing'or root not in j['movement_group']:continue
    p=np.asarray(j['probe_source_m']);bearing.append({'join':j['name'],'axis_radial_error_m':float(np.linalg.norm((p-np.asarray(rec['pivot_source_m']))[1:])),'normal_opposition_dot':float(np.dot(j['normal_a_source'],j['normal_b_source'])),'pass':np.linalg.norm((p-np.asarray(rec['pivot_source_m']))[1:])<TOL and abs(j['normal_a_source'][0])==1 and np.dot(j['normal_a_source'],j['normal_b_source'])<-.999})
  r['continuous_bearing_witnesses']=bearing;r['pass']&=all(x['pass']for x in bearing);motion.append(r)
 voids=[];void_motion=[];probes=[]
 for state,transform,nn in states:
  st=tri.copy()
  for root,f in transform.items():st[np.isin(labels,rotors[root]['semantic_parts'])]=pose(st[np.isin(labels,rotors[root]['semantic_parts'])],rotors[root],f)
  gn=nn.tris@C
  for v in m['receiver_voids']:
   if v['state']=='closed'and state!='closed':continue
   if v['state']=='folded'and state!='PAN_HINGE_X':continue
   lo=np.asarray(v['min_source_m']);hi=np.asarray(v['max_source_m'])
   if v['state']=='cover_local'and'REAR_COVER_REMOVE'in transform:lo=pose(lo,rotors['REAR_COVER_REMOVE'],1);hi=pose(hi,rotors['REAR_COVER_REMOVE'],1)
   bv=boxcloud(lo,hi);pairs=[{'part':n,**static_pair(cloud(st[labels==n]),bv)}for n in parts];sm=triangle_box_mask(st,lo+TOL,hi-TOL);nm=triangle_box_mask(gn,lo+TOL,hi-TOL);contains=bool(inside_mesh([(lo+hi)/2],gn)[0]);row={'name':v['name'],'state':state,'exact_bounds_source_m':[lo.tolist(),hi.tolist()],'solid_box_checks':pairs,'source_triangle_interior_intruders':sorted(set(str(x)for x in labels[sm])),'native_triangle_interior_hits':int(nm.sum()),'native_box_midpoint_inside_any_closed_surface':contains,'pass':all(x['pass']for x in pairs)and not sm.any()and not nm.any()and not contains};voids.append(row)
   for ax in range(3):
    p=(lo+hi)/2;q=p.copy();p[ax]=lo[ax];q[ax]=hi[ax];vb=bool(segment_triangles(p,q,st));nb=bool(segment_triangles(p,q,gn));probes.append({'void':v['name'],'state':state,'axis':ax,'segment_source_m':[p.tolist(),q.tolist()],'source_blocked':vb,'native_blocked':nb,'pass':not vb and not nb})
 for v in m['receiver_voids']:
  if v['state']not in ['all','cover_local']:continue
  bv=boxcloud(v['min_source_m'],v['max_source_m'])
  for rec in m['motion_records']:
   checks=[]
   if v['state']=='cover_local'and rec['root']=='REAR_COVER_REMOVE':
    for n in parts:
     if n not in rec['semantic_parts']:checks.append({'part':n,**motion_pair(bv,verts[n],rec)})
    method='Complete moving local void swept against every non-cover part; its own cover geometry is rigid and endpoint checks apply'
   else:
    for n in rec['semantic_parts']:checks.append({'part':n,**motion_pair(verts[n],bv,rec)})
    method='Complete moving part envelope tested against stationary declared empty volume'
   void_motion.append({'name':v['name'],'root':rec['root'],'method':method,'checks':checks,'pass':all(x['pass']for x in checks)})
 # Positive controls use real through-material source/native segments.
 controls=[]
 controlparts=['folding_timber_pan','left_shaped_timber_end']if ident.endswith('003')else['service_column_front_web','supported_clipped_work_tray','removable_rear_service_cover']
 for n in controlparts:
  v=verts[n];centre=v.mean(0);axis=int(np.argmin(np.ptp(v,axis=0)));p=centre.copy();q=centre.copy();p[axis]=v[:,axis].min()-.005;q[axis]=v[:,axis].max()+.005;ss=bool(segment_triangles(p,q,tri));nn=bool(segment_triangles(p,q,nt));controls.append({'part':n,'segment_source_m':[p.tolist(),q.tolist()],'source_blocked':ss,'native_blocked':nn,'pass':ss and nn})
 adjacency=None
 if ident.endswith('003'):
  dx=m['details']['adjacent_QA_only']['translation_source_m'][0];allv=cloud(tri);gap=dx+allv[:,0].min()-allv[:,0].max();adjacency={'translation_source_m':[dx,0,0],'minimum_x_gap_m':float(gap),'proof':'All moving axes are source X; every vertex X is invariant throughout both independent folds. Whole modules have this persistent X separation. Proposed straight parallel modules only, no host row claim.','pass':gap>TOL}
 supplementary=[]
 if 'bearing_geometry'in m['details']or'aim_bearing_geometry'in m['details']:
  seat=ident.endswith('003');sector_suffix='_moving_bearing_sector_'if seat else'_aim_bearing_sector_';pin_suffix='_retained_hinge_pin'if seat else'_retained_aim_pin';cap_suffix='_inner_pin_retainer'if seat else'_aim_pin_inner_retainer';stub_suffix='_fixed_pivot_stub'if seat else'_fixed_aim_stub';sector_count=12 if seat else 8
  hinge=rotors['PAN_HINGE_X'if seat else'LIGHT_AIM_X'];pivot=np.asarray(hinge['pivot_source_m']);bearingrows=[]
  for side in ['left','right']:
   sectors=sorted(n for n in parts if n.startswith(side+sector_suffix));pin=verts[side+pin_suffix];cap=verts[side+cap_suffix];axis=np.array([pin[:,0].mean(),pivot[1],pivot[2]]);pinradius=float(np.linalg.norm(pin[:,1:]-pivot[1:],axis=1).max());boreplanes=[];borecorners=[]
   for n in sectors:
    h=ConvexHull(verts[n]);eq=h.equations;radial=eq[np.abs(eq[:,0])<1e-7];centre_values=radial[:,:3]@axis+radial[:,3];i=int(centre_values.argmax());boreplanes.append(float(centre_values[i]));rr=np.linalg.norm(verts[n][:,1:]-pivot[1:],axis=1);borecorners.extend(rr[np.isclose(rr,rr.min(),atol=1e-7)].tolist())
   inradius=min(boreplanes);circum=max(borecorners);ch=ConvexHull(cap);eq=ch.equations;radial=eq[np.abs(eq[:,0])<1e-7];capin=float(np.min(-(radial[:,:3]@axis+radial[:,3])));clearance=inradius-pinradius;retention=capin-circum
   annular_p=axis+np.array([0,(inradius+pinradius)/2,0]);void_source=not bool(inside_mesh([annular_p],tri)[0]);void_native=not bool(inside_mesh([annular_p],nt)[0]);pin_source=bool(inside_mesh([axis],parts[side+pin_suffix])[0]);pin_native=bool(inside_mesh([axis],nt)[0]);axial=[]
   for target in [side+stub_suffix,side+cap_suffix]:
    tt=verts[target];allsector=np.concatenate([verts[n]for n in sectors]);xgap=max(float(tt[:,0].min()-allsector[:,0].max()),float(allsector[:,0].min()-tt[:,0].max()));ee=ConvexHull(tt).equations;rr=ee[np.abs(ee[:,0])<1e-7];radial_overlap=float(np.min(-(rr[:,:3]@axis+rr[:,3]))-circum);axial.append({'target':target,'x_boundary_gap_m':xgap,'full_angle_retention_radial_overlap_m':radial_overlap,'pass':abs(xgap)<TOL and radial_overlap>TOL})
   bearingrows.append({'side':side,'actual_convex_sector_count':len(sectors),'actual_bore_minimum_inradius_m':inradius,'actual_bore_maximum_inner_corner_radius_m':circum,'actual_pin_maximum_radius_m':pinradius,'full_angle_radial_clearance_lower_bound_m':clearance,'actual_cap_minimum_inradius_m':capin,'full_angle_axial_retention_radial_overlap_lower_bound_m':retention,'actual_axial_end_contacts':axial,'annular_void_probe_source_m':annular_p.tolist(),'annular_gap_empty_in_source_and_native':void_source and void_native,'pin_centre_material_positive_control':pin_source and pin_native,'pass':len(sectors)==sector_count and clearance>TOL and retention>TOL and void_source and void_native and pin_source and pin_native and all(x['pass']for x in axial)})
  supplementary.append({'name':'actual_retained_pin_bore_running_clearance','bearings':bearingrows,'method':'Inner sector-face plane distance from actual axis gives minimum finite bore inradius; all actual pin vertices bound pin circumradius. Rigid X-axis rotation preserves these radii, proving positive full-angle clearance. Actual cap inradius exceeds every bore inner corner radius, proving retained geometry with declared unloaded radial gap.','limits':'No exact radial contact is asserted in the unloaded centered pose. Designed radial load/capture path is distinct from generic triangle-contact graph; no load, wear, spring, fastener or tolerance-under-load acceptance.','pass':all(x['pass']for x in bearingrows)})
 if ident.endswith('004'):
  lamp=rotors['LIGHT_AIM_X'];cover=rotors['REAR_COVER_REMOVE'];lv=cloud(tri[np.isin(labels,lamp['semantic_parts'])]);cv=cloud(tri[np.isin(labels,cover['semantic_parts'])]);lz,_=interval_projection(lv,np.asarray(lamp['pivot_source_m']),np.array([[0,0,1]]),0,lamp['travel']);gap=float(lz[0]-cv[:,2].max());supplementary.append({'name':'simultaneous_independent_lamp_and_cover_motion','method':'Entire continuous lamp arc minimum Z compared with cover maximum Z, invariant throughout all independent cover translations','minimum_z_gap_m':gap,'pass':gap>TOL})
  res=m['details']['access_reservations'][0];swept=np.concatenate([cv,pose(cv,cover,1)]);lo=np.asarray(res['min_source_m']);hi=np.asarray(res['max_source_m']);err=float(max(np.max(lo-swept.min(0)),np.max(swept.max(0)-hi)));supplementary.append({'name':'complete_occupied_cover_removal_reservation','actual_complete_swept_bounds_source_m':[swept.min(0).tolist(),swept.max(0).tolist()],'declared_bounds_source_m':[lo.tolist(),hi.tolist()],'maximum_omission_m':max(0,err),'semantic_distinction':res['kind'],'pass':err<TOL and'occupied'in res['kind']})
  # A bounded geometric service-tool path around the removed cover into its channel.
  opened=next(n for state,_,n in states if state=='REAR_COVER_REMOVE');gn=opened.tris@C;st=tri.copy();mask=np.isin(labels,cover['semantic_parts']);st[mask]=pose(st[mask],cover,1);way=[np.array(p)for p in [[.12,.60,1.10],[.12,.20,1.10],[0,.20,1.10],[0,.16,1.10]]];corr=[]
  for p,q in zip(way,way[1:]):
   lo=np.minimum(p,q)-.005;hi=np.maximum(p,q)+.005;bv=boxcloud(lo,hi);checks=[static_pair(cloud(st[labels==n]),bv)for n in parts];hits=triangle_box_mask(gn,lo+TOL,hi-TOL);corr.append({'box_source_m':[lo.tolist(),hi.tolist()],'native_intruding_triangles':int(hits.sum()),'pass':all(x['pass']for x in checks)and not hits.any()})
  supplementary.append({'name':'service_channel_geometric_access_after_removal','square_tool_width_m':.01,'waypoints_source_m':[p.tolist()for p in way],'complete_corridor_boxes':corr,'limits':'An invented bounded geometric inspection-tool corridor only. This is not a hand, species, servicing procedure or host-reach certificate. Removed cover requires external handling support.','pass':all(x['pass']for x in corr)})
  emitter=next(x for x in m['physical_and_proposal_markers']if x['name']=='PROPOSED_EMITTER_SURFACE');rays=[]
  for fraction in [0,.5,1]:
   st=tri.copy();mm=np.isin(labels,lamp['semantic_parts']);st[mm]=pose(st[mm],lamp,fraction);ng=nt.copy();ids=descendants(native,lamp['root']);names=[nodes[i].get('name')for i in ids if'mesh'in nodes[i]];nm=np.isin(native.nodes,names);ng[nm]=pose(ng[nm],lamp,fraction)
   # At terminal angle use the actual exported terminal triangles independently.
   if fraction==1:ng=next(n for state,_,n in states if state=='LIGHT_AIM_X').tris@C
   for offset in [[0,0,0],[-.025,0,0],[.025,0,0],[0,-.015,0],[0,.015,0]]:
    orig=pose(np.asarray(emitter['source_m'])+offset,lamp,fraction);direction=rotate([0,0,-1],[0,0,0],lamp['travel']*fraction);p=orig+direction*1e-6;q=p+direction*2;first=[]
    for name in parts:
     hs=segment_triangles(p,q,st[labels==name])
     if hs:first.append((hs[0],name))
    first.sort();nh=segment_triangles(p,q,ng);distance_error=abs(first[0][0]-nh[0])*2 if first and nh else None;rays.append({'angle_degrees':lamp['travel']*fraction,'closed_aperture_offset_source_m':offset,'origin_source_m':orig.tolist(),'direction_source':direction.tolist(),'first_source_part':first[0][1]if first else None,'first_native_distance_m':nh[0]*2 if nh else None,'source_native_hit_distance_error_m':distance_error,'pass':bool(first and nh and first[0][1]=='supported_clipped_work_tray'and distance_error<1e-6)})
  # Broader aperture offset is observational: this closed rear ray meets the cue-card front edge.
  bp=np.asarray(emitter['source_m'])+[0,.025,-1e-6];bq=bp+[0,0,-2];bh=[]
  for name in parts:
   hs=segment_triangles(bp,bq,parts[name])
   if hs:bh.append((hs[0],name))
  bh.sort();supplementary.append({'name':'broader_aperture_limit','closed_offset_source_m':[0,.025,0],'first_observed_part':bh[0][1]if bh else None,'scope':'Observation beyond the finite central aperture sample region; partial housing/notes shadowing is not full aperture illumination proof.','pass':True})
  # Positive blocked test: ray toward actual diffuser/hood material.
  p=np.asarray(emitter['source_m'])+[0,0,-1e-6];q=p+[0,0,.12];hits=segment_triangles(p,q,tri);nativehits=segment_triangles(p,q,nt);pc=bool(hits and nativehits);supplementary.append({'name':'finite_emitter_aperture_to_work_tray_paths','rays':rays,'opaque_upward_path_positive_control':pc,'scope':'15 finite central-aperture rays at 0, -12.5, -25 degrees, source plus native terminal geometry. Not continuous aperture coverage, illumination, glare or photometry.','pass':all(x['pass']for x in rays)and pc})
 result={'catalogue_id':ident,'passed':all(x['pass']for x in convex+markers+joins+motion+voids+void_motion+probes+controls+supplementary)and(adjacency is None or adjacency['pass']),'bindings':{k:bind(p)for k,p in [('manifest',mp),('source',sp),('export',gp),('source_audit',rp),('geometry_cache',ROOT/s['geometry_cache'])]},'convex_source_evidence':convex,'physical_and_proposal_markers':markers,'opposing_contact_witnesses':joins,'complete_motion_checks':motion,'complete_endpoint_void_checks':voids,'continuous_all_state_void_checks':void_motion,'clear_access_probes':probes,'real_material_positive_controls':controls,'adjacent_proposed_seat_modules':adjacency,'supplementary_work_service_and_light_checks':supplementary,'numeric_boundary_tolerance_m':TOL,'limits':['Checks concern independently evaluated static geometry and native ownership, not working hinges, powered lamps, wiring flex, locking, load, photometry, bodies, species, room fit or runtime acceptance.','Closed interval rotation certificates cover t=0 and the first micrometre; adaptive subdivisions alone do not constitute clearance proof. Each accepted interval has a fixed separating plane with analytic full-arc extrema.','Source positive convex-volume and oriented-plane checks support interpreting a positive LP overlap as actual material penetration. Convex envelopes are conservative for separation.','Native export full endpoint boxes are checked with all triangles and winding containment; native ownership and complete group vertex agreement bind source motion geometry. Native controls contain only exported terminal states; runtime control is absent.'],'executed_script_sha256':sha(Path(__file__))}
 result['bindings']['state_derivatives']=[bind(BASE/d['export'])for d in m['state_derivatives']]
 result['bindings']['generator']=bind(BASE/m['generator'])
 assert sha(sp)==s['sha256']==m['source_sha256'];assert sha(gp)==m['glb_sha256']
 (OUT/f'independent_use_motion_{ident}.json').write_text(json.dumps(result,indent=2,default=lambda o:o.item())+'\n')
 print(ident,'PASS',result['passed'],'markers',[x['name']for x in markers if not x['pass']],'joins',[x['name']for x in joins if not x['pass']],'motion',[(x['root'],[(z['moving_part'],z['fixed_part'])for z in x['pairs']if not z['pass']])for x in motion],'voids',[(x['name'],x['state'],x['source_triangle_interior_intruders'])for x in voids if not x['pass']],'continuous_voids',[(x['name'],x['root'])for x in void_motion if not x['pass']],flush=True)
 return result
def controls():
 box=boxcloud([-.01,-.01,-.01],[.01,.01,.01]);r={'kind':'rotation','travel':-78,'pivot_source_m':[0,0,0],'axis_source':[1,0,0]};a=box+[0,-.5,0];ob=rotate(a,[0,0,0],-39);endpoints=[static_pair(pose(a,r,t),ob)['pass']for t in [0,1]];caught=rotation_pair(a,ob,r)
 tr={'kind':'translation','travel':.22,'axis_source':[0,1,0]};b=box+[0,.11,0];tc=linear_pair(box,b,tr)
 return {'rotation_mid_arc_only_obstacle':{'endpoints_clear':endpoints,'continuous_check_rejects':not caught['pass'],'result':caught,'pass':all(endpoints)and not caught['pass']},'translation_mid_stroke_only_obstacle':{'endpoints_clear':[static_pair(pose(box,tr,t),b)['pass']for t in[0,1]],'complete_check_rejects':not tc['pass'],'pass':not tc['pass']},'coincident_boundary_is_not_intrusion':{'pass':static_pair(box,box+[.02,0,0])['pass']},'actual_overlap_detected':{'pass':not static_pair(box,box+[.019,0,0])['pass']}}
if __name__=='__main__':
 results=[check_asset(p)for p in sorted(BASE.glob('AST-CUL-*.manifest.json'))];cc=controls();report={'passed':all(x['passed']for x in results)and all(x['pass']for x in cc.values()),'assets':[{'catalogue_id':x['catalogue_id'],'passed':x['passed']}for x in results],'positive_and_negative_controls':cc,'read_only_helper_bindings':[bind(ROOT/p)for p in['qa/batch07/independent_geometry.py','qa/batch08/independent_collision_geometry.py','qa/batch12/independent_void_geometry.py','qa/batch15/independent_contact_graph.py','qa/batch15/independent_sweep_geometry.py']]};(OUT/'independent_use_motion_summary.json').write_text(json.dumps(report,indent=2,default=lambda o:o.item())+'\n');print('OVERALL',report['passed'])
