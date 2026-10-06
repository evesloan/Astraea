"""Read-only retained raw triangles + actual compiler floors; pure scratch QA.
Conservative continuous capsule and cart/load/operator enclosures are stronger
than centerline-only checks; Godot contacts/dynamics remain a separate gate.
"""
from pathlib import Path
import sys,json,math,hashlib
sys.dont_write_bytecode=True
import numpy as np
from shapely.geometry import Polygon,Point,LineString,box
from shapely.ops import unary_union
R=Path(__file__).resolve().parent;A=R.parents[1]
C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');P=C/'assets/grand_lantern_theater_section';G=Path('/workspace/shared/astraea-godot-production-20261003')
sys.path.insert(0,str(P/'source/firstpass_003/dependencies'))
from geometry_review import glb,Query
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
contract=read(R/'COURT_A_GEOMETRY_CONTRACT.json');E=P/'source/firstpass_003/exports_run005';rec=read(E/'EXPORT_RECEIPT.json');data=read(G/'data/architecture/THEATER_RUNTIME_STAGE001.json')
batches={b['name']:b for b in rec['batches']};scene=[];all_source=[];models={}
for kind in ['static','prototype']:
 models[kind]=glb(E/f'AST-CUL-005_{kind}_003.glb')
 expected=next(r['sha256']for r in rec['export_records']if r['kind']==kind)
 assert models[kind]['sha256']==expected

def crop(mesh):
 t=mesh['triangles'];mask=np.all(t.max(1)>[-79,69.50001,-148],axis=1)&np.all(t.min(1)<[-63,74,-128],axis=1)
 if mask.any():return dict(mesh,triangles=t[mask])

for m in models['static']['meshes']:
 # Cosmetic artwork/textile is not credited as collision. All actual solids are.
 b=batches[m['node']];m=dict(m,node='retained/'+m['node'],semantic_ids=b['semantic_ids'])
 q=crop(m)
 if q:scene.append(q)
 all_source.append(m)
proto_mesh={m['node']:m for m in models['prototype']['meshes']}
proto_root={n['extras']['definition_id']:n['world_matrix']for n in models['prototype']['nodes']if'definition_id'in n['extras']}
for entry in data['instances']:
 definition=data['prototypes'][entry['definition']]
 if not definition['collides']:continue
 tr=np.array(entry['native_matrix'])@np.linalg.inv(proto_root[entry['definition']])
 for name in definition['batches']:
  m=proto_mesh[name];v=m['triangles'];tri=(np.c_[v.reshape(-1,3),np.ones(v.size//3)]@tr.T)[:,:3].reshape(-1,3,3)
  q=crop(dict(m,node='retained/'+entry['id']+'/'+name,triangles=tri,semantic_ids=[entry['id']]))
  if q:scene.append(q)

def triangles(o):
 v=np.array(o['vertices_world']);return np.array([[v[f[0]],v[f[k]],v[f[k+1]]]for f in o['faces']for k in range(1,len(f)-1)])
new_scene=[]
for o in contract['objects']:
 if o['collides']:new_scene.append({'node':o['name'],'primitive':0,'triangles':triangles(o),'semantic_ids':[o['name']]})
cached={};retained_meshes={}
for row in contract['retained_instances']:
 asset=row['asset']
 if asset not in cached:cached[asset]=glb(row['export']);assert cached[asset]['sha256']==row['export_sha256']
 c,s=math.cos(row['yaw_radians']),math.sin(row['yaw_radians']);basis=np.array([[c,0,s],[0,1,0],[-s,0,c]])
 ms=[dict(m,node=row['id']+'/'+m['node'],triangles=m['triangles']@basis.T+np.array(row['position_world']),semantic_ids=[row['id']])for m in cached[asset]['meshes']]
 retained_meshes[row['id']]=ms
 if not asset.startswith('AST-BOT'):new_scene+=ms
q=Query(scene+new_scene)

# FLOOR: exact current compiler triangle union at Y69.5, including Court A.
compiled=read(G/'data/generated/structural_meshes.json');floor_rows=[r for r in compiled['regions']if abs(r['floor_y']-69.5)<1e-6]
floor=unary_union([Polygon(t)for r in floor_rows for t in r['triangles']])
floor_witnesses=[];failures=[];warnings=[]
for row in contract['grounded_supports']:
 p=Polygon(row['polygon_xz']);missing=p.difference(floor).area
 floor_witnesses.append({'id':row['id'],'missing_floor_m2':missing,'floor_y':69.5})
 if missing>1e-7:failures.append({'kind':'floor_support','id':row['id'],'missing_m2':missing})
stance_points=[(s['id'],s['standing_point_world'])for s in contract['seats']]
counter=next(i for i in contract['retained_instances']if i['asset']=='AST-CUL-002')
stance_points += [(k,counter[k])for k in['service_standing_world','public_standing_world','low_writing_standing_world']]
for name,p in stance_points:
 missing=Point(p[0],p[2]).buffer(.3).difference(floor).area
 hits=q.prism_hits([p[0]-.3,69.51,p[2]-.3,p[0]+.3,71.3,p[2]+.3])
 owners=sorted({q.meshes[q.owner[h['triangle_index']]]['node']for h in hits})
 floor_witnesses.append({'id':name,'point_world':p,'capsule_footprint_unsupported_m2':missing,'capsule_bounding_prism_contacts':owners})
 if missing>1e-7 or owners:failures.append({'kind':'stance','id':name,'unsupported_m2':missing,'contacts':owners})

# Reservations checked against full triangles, including retained old counters.
reservations=[]
for row in contract['reservations']:
 p=Polygon(row['polygon_xz']);x0,z0,x1,z1=p.bounds
 # Oblique seat approaches need polygon clipping, not their enclosing AABB.
 candidates=q.prism_hits([x0,69.51,z0,x1,row['y'][1],z1]);hits=[]
 for h in candidates:
  t=q.tri[h['triangle_index']];proj=Polygon(t[:,[0,2]])
  if proj.is_valid and proj.intersection(p.buffer(-.0001)).area>1e-9:hits.append(q.meshes[q.owner[h['triangle_index']]]['node'])
 reservations.append({'id':row['id'],'collision_contacts':sorted(set(hits)),'missing_floor_m2':p.difference(floor).area})
 if hits:failures.append({'kind':'reservation','id':row['id'],'contacts':sorted(set(hits))})

poses=[]
def line(a,b):
 a,b=np.array(a),np.array(b);d=b-a;n=max(1,math.ceil(np.linalg.norm(d)/.04));yaw=math.atan2(-d[0],-d[1])
 for i in range(n+1):poses.append([*(a+(b-a)*i/n).tolist(),yaw])
def arc(c,r,a,b):
 n=math.ceil(abs(b-a)*r/.035)
 for i in range(n+1):
  t=a+(b-a)*i/n;p=np.array(c)+r*np.array([math.cos(t),math.sin(t)]);d=np.sign(b-a)*np.array([-math.sin(t),math.cos(t)])
  poses.append([*p.tolist(),math.atan2(-d[0],-d[1])])
line([-77.5,-137.5],[-77.5,-137.43]);arc([-75.5,-137.43],2,math.pi,math.pi/2)
line([-75.5,-135.43],[-71.5,-135.43]);arc([-71.5,-137.43],2,math.pi/2,0)
line([-69.5,-137.43],[-69.5,-138.95])
contacts=read(G/'data/architecture/cleaning_cart_contacts.json')
cart_hits=[];unsupported=[];capsule_hits=[];sweep_polys=[];min_margin=1e9
# Actual contact boxes plus a conservative carried-load boundary. Buffering by
# 55 mm covers <=40 mm translation plus a <=20 mm farthest-corner rotation,
# with a tighter exact measured between-pose displacement bound below.
max_step=0.
for aa,bb in zip(poses,poses[1:]):
 dy=abs((bb[2]-aa[2]+math.pi)%math.tau-math.pi)
 max_step=max(max_step,math.dist(aa[:2],bb[:2])+2.02*dy)
guard=max_step+.002
for i,(x,z,yaw)in enumerate(poses):
 c,s=math.cos(yaw),math.sin(yaw);basis=np.array([[c,0,s],[0,1,0],[-s,0,c]]);origin=np.array([x,69.5,z])
 tri=(q.tri-origin)@basis;local=Query([{'node':'all','primitive':0,'triangles':tri}])
 boxes=[]
 for b in contacts['boxes']:
  cc=np.array(b['center']);half=np.array(b['size'])/2;lo=cc-half;hi=cc+half;lo[[0,2]]-=guard;hi[[0,2]]+=guard;lo[1]=max(.01,lo[1]);boxes.append(np.r_[lo,hi].tolist())
 boxes += [[-.43-guard,.01,-.72-guard,.43+guard,1.35,.83+guard],[-.3-guard,.01,1.32-guard,.3+guard,1.8,1.92+guard]]
 hits=set()
 for b in boxes:
  for h in local.prism_hits(b):hits.add(int(h['triangle_index']))
 if hits:cart_hits.append({'pose':i,'xz_yaw':[x,z,yaw],'contacts':sorted({q.meshes[q.owner[h]]['node']for h in hits})})
 # Actual wheel centers and operator ground disk must be on real floor.
 for center in [w['center']for w in contacts['wheel_contacts']]+[[0,0,1.62]]:
  p=origin+basis@np.array([center[0],0,center[2]])
  if not floor.covers(Point(p[0],p[2]).buffer(.3 if center==[0,0,1.62]else.02)):unsupported.append({'pose':i,'point_world':p.tolist()})
 for lo,hi in [([-.43,-.72],[.43,.83]),([-.3,1.32],[.3,1.92])]:
  p=np.array([[a,0,b]for a,b in[(lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1])]])@basis.T+origin
  sweep_polys.append(Polygon(p[:,[0,2]]).buffer(guard))
 # Headroom proof at actual player/capsule diameter, conservatively full-height.
 h=q.prism_hits([x-.3-guard,69.51,z-.3-guard,x+.3+guard,71.3,z+.3+guard])
 if h:capsule_hits.append({'pose':i,'contacts':sorted({q.meshes[q.owner[k['triangle_index']]]['node']for k in h})})
if cart_hits:failures.append({'kind':'cart_dogleg','poses':len(cart_hits),'examples':cart_hits[:8]})
if capsule_hits:failures.append({'kind':'capsule_dogleg','poses':len(capsule_hits),'examples':capsule_hits[:8]})
if unsupported:failures.append({'kind':'dogleg_floor','examples':unsupported[:8]})
sweep=unary_union(sweep_polys);old_staff=[]
for row in read(A/'FURNITURE_ARCHITECTURE_STANCE_SCREEN.json')['witnesses']:
 if row['module'] not in ['D11_usher_0','D11_usher_1']:continue
 p=Polygon(row['polygon_xz']);overlap=sweep.intersection(p).area
 old_staff.append({'module':row['module'],'stance':row['stance'],'overlap_m2':overlap,'clearance_m':sweep.distance(p)})
 if overlap>1e-8:failures.append({'kind':'retained_usher_stance_vs_cart','record':old_staff[-1]})

# Existing main route protection: broad conservative 3.4 m horizontal corridor
# around all unchanged main route legs. This tests NEW additions only.
mainroute=LineString(contract['routes']['old_main_route_preserved']).buffer(1.7,cap_style=2,join_style=2)
main_hits=[]
for m in new_scene:
 t=m['triangles'];mask=(t[:,:,1].min(1)<72.5)&(t[:,:,1].max(1)>69.51)
 if mask.any():
  poly=Polygon(t[mask,:][:,:,[0,2]].reshape(-1,2)).convex_hull
  if poly.intersects(mainroute):main_hits.append(m['node'])
if main_hits:failures.append({'kind':'old_main_route_intrusion','contacts':main_hits})

# Full basal/soil screen. Source root disks, requested planting patch, minimum
# depth, actual transformed basal vertices and every foliage vertex are checked.
soils={r['id']:r for r in contract['soil_receivers']};root_rows=[]
for row in contract['retained_instances']:
 if'root_receiver'not in row:continue
 soil=soils[row['root_receiver']];p=Polygon(soil['polygon_xz']);ms=retained_meshes[row['id']];verts=np.concatenate([m['triangles'].reshape(-1,3)for m in ms]);root=np.array(row['position_world']);basal=verts[verts[:,1]<=soil['top_y']+1e-5]
 root_disk=Point(root[0],root[2]).buffer(row['root_radius_m'],resolution=32);patch=Point(root[0],root[2]).buffer(row['soil_patch_radius_m'],resolution=32)
 outside_leaf=sum(not p.buffer(.001).covers(Point(v[0],v[2]))for v in verts)
 basal_outside=sum(not p.buffer(.0001).covers(Point(v[0],v[2]))for v in basal)
 rr={'instance':row['id'],'soil':row['root_receiver'],'root_world':root.tolist(),'embed_m':soil['top_y']-root[1],'available_soil_depth_m':soil['top_y']-soil['bottom_y'],'minimum_depth_m':row['minimum_soil_depth_m'],'basal_vertices_tested':len(basal),'basal_vertices_outside':basal_outside,'root_disk_outside_m2':root_disk.difference(p).area,'planting_patch_outside_m2':patch.difference(p).area,'all_transformed_vertices_tested':len(verts),'foliage_vertices_outside_soil_projection':outside_leaf}
 root_rows.append(rr)
 if basal_outside or rr['root_disk_outside_m2']>1e-9 or rr['planting_patch_outside_m2']>1e-9 or rr['available_soil_depth_m']<rr['minimum_depth_m']:failures.append({'kind':'root_receiver','record':rr})
 if outside_leaf:warnings.append({'kind':'foliage_projection_exceeds_soil','instance':row['id'],'vertex_count':outside_leaf,'note':'Not accepted as fitted yet; inspect blades against rim/seat using source mesh height, do not whole-plant scale.'})

# Exact fresh old/new solid contact screen by new convex-piece prisms. AABB is
# only candidate evidence, so report rather than falsely certifying concave forms.
oldq=Query(scene);contact_candidates=[]
for row in contract['objects']:
 if not row['collides']or row['role']=='plant_root_receiver':continue
 lo,hi=row['bounds_world'];lo=list(lo);lo[1]=max(lo[1],69.501)
 hits=oldq.prism_hits(lo+hi)
 if hits:contact_candidates.append({'new':row['name'],'retained_candidates':sorted({oldq.meshes[oldq.owner[h['triangle_index']]]['node']for h in hits}),'classification':'AABB candidates only; exact mesh contacts required before build'})
if contact_candidates:warnings.append({'kind':'old_new_contact_candidates','count':len(contact_candidates)})

# Root-to-root clearance against ALL preserved collars, not just one origin per
# BOT-009. Check requested new whole plants and the optional fuller mass as well.
root_circles=[]
for row in read(A/'PLANTED_COURT_GEOMETRY_002.json')['plant_instances']:
 if not row['id'].startswith('FP2_D11_GROVE_A_'):continue
 x,y,z=row['position_world'];c,s=math.cos(row['yaw_radians']),math.sin(row['yaw_radians'])
 if row['asset']=='AST-BOT-009':
  mf=read(C/'assets/botanical_cluster/AST-BOT-009.manifest.json')
  for k,rr in enumerate(mf['planting_and_placement']['individual_root_reservations']):
   u,v=rr['center_source_xy_m'];root_circles.append({'id':row['id']+'_collar'+str(k),'xz':[x+c*u-s*v,z-s*u-c*v],'radius':rr['actual_soil_contact_radius_m'],'retained':True})
 else:root_circles.append({'id':row['id'],'xz':[x,z],'radius':{'AST-BOT-007':.17,'AST-BOT-002':.032,'AST-BOT-003':.035}[row['asset']],'retained':True})
for row in contract['retained_instances']:
 if'root_receiver'in row:root_circles.append({'id':row['id'],'xz':[row['position_world'][0],row['position_world'][2]],'radius':row['root_radius_m'],'retained':False})
optional=R/'FULLER_REAR_MASS_CANDIDATE.json'
if optional.exists():
 for row in read(optional)['fit']['roots']:root_circles.append({'id':row['part'],'xz':[row['world'][0],row['world'][2]],'radius':row['root_radius_m'],'retained':False,'optional_unbuilt':True})
root_pairs=[]
for i,a in enumerate(root_circles):
 for b in root_circles[i+1:]:
  if a['retained']and b['retained']:continue
  clearance=math.dist(a['xz'],b['xz'])-a['radius']-b['radius']
  root_pairs.append({'a':a['id'],'b':b['id'],'edge_clearance_m':clearance})
  if clearance<-.0001:failures.append({'kind':'root_overlap','record':root_pairs[-1]})

out={'status':'PURE_GEOMETRY_SCREEN_WITH_EXPLICIT_PENDING_GATES','contract_sha256':sha(R/'COURT_A_GEOMETRY_CONTRACT.json'),'base_source_unchanged':sha(contract['base_source'])==contract['base_source_sha256'],'engine_or_blender_started':False,'failures':failures,'warnings':warnings,'floor_witnesses':floor_witnesses,'reservation_checks':reservations,'roots':root_rows,'old_new_contact_candidates':contact_candidates,'route':{'entry_cart_poses':len(poses),'minimum_turn_radius_m':2.,'maximum_between_pose_corner_displacement_bound_m':max_step,'continuous_sweep_guard_m':guard,'cart_contact_pose_count':len(cart_hits),'capsule_contact_pose_count':len(capsule_hits),'unsupported_wheel_operator_points':len(unsupported),'cart_pose_contacts':cart_hits,'capsule_pose_contacts':capsule_hits,'cart_operator_sweep_polygon_xz':[list(poly.exterior.coords)for poly in ([unary_union(sweep_polys)]if unary_union(sweep_polys).geom_type=='Polygon'else unary_union(sweep_polys).geoms)],'poses_xzyaw':poses,'existing_main_route_new_intrusions':main_hits},'explicit_dimensions':{'central_inner_spine_width_m':3.1,'front_reserved_cross_aisle_depth_m':1.5,'counter_rear_closed_to_basin_m':1.425,'counter_open_drawer_handle_to_basin_front_m':1.181,'service_stance_capsule_to_basin_m':.4,'side_soffit_headroom_m':3.35,'bracket_headroom_m':3.12,'central_open_ceiling_min_width_m':4.1,'old_portal_top_y':74.15,'D12_underside_y':77.55},'limits':['Numerical retained triangle screen only, no physics contacts/dynamics or broad-species fit','New actual source must be reopened and exact material/UV/preservation checked','Original SunCorp graphic is pending artwork; no visual acceptance','Full foliage acceptance requires retained source and image review; unretained pool prototype unused'],'input_sha256':{str(p):sha(p)for p in [Path(__file__),G/'data/generated/structural_meshes.json',G/'data/architecture/cleaning_cart_contacts.json',G/'data/architecture/THEATER_RUNTIME_STAGE001.json',E/'EXPORT_RECEIPT.json']}}
out['route']['retained_usher_work_reservations']=old_staff
out['all_preserved_and_new_root_collars']={'circles':root_circles,'checked_pairs':len(root_pairs),'minimum_new_to_any_root_edge_clearance_m':min(x['edge_clearance_m']for x in root_pairs),'nearest_pairs':sorted(root_pairs,key=lambda x:x['edge_clearance_m'])[:12]}
(R/'COURT_A_PURE_SCREEN.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'failures':failures,'warnings':warnings,'route_counts':{k:v for k,v in out['route'].items()if k.endswith('count')or k.endswith('points')},'old_contacts':contact_candidates},indent=2))
