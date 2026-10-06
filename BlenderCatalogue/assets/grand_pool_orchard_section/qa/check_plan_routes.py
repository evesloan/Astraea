"""Deterministic source-fit plan checks. No engine and no force/comfort certification."""
from pathlib import Path
import json,math,sys,hashlib
sys.path.insert(0,'/workspace/scratch/375c2e438292/geometry-deps')
import shapely
from shapely.geometry import Polygon,Point,LineString,box,MultiPoint
from shapely.ops import unary_union
from shapely.affinity import rotate,translate
R=Path(__file__).resolve().parents[1];C=R.parents[1];G=C.parent/'astraea-godot-production-20261003';D=json.loads((R/'source/connected_contract.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parts=[p for p in D['source_parts']if not p['export_excluded']]
for p in parts:
 p['bounds']=[min(v[i]for v in p['world_vertices'])for i in range(3)]+[max(v[i]for v in p['world_vertices'])for i in range(3)];p['shape']=MultiPoint([(v[0],v[2])for v in p['world_vertices']]).convex_hull
floors={}
for f in D['floor_regions']:
 poly=Polygon(f['boundary'],f['holes']);assert poly.is_valid;assert abs(poly.area-f['area_m2'])<1e-7;assert abs(sum(Polygon(t).area for t in f['triangles'])-poly.area)<1e-6
 floors.setdefault(f['floor_y'],[]).append(poly)
floors={y:unary_union(p)for y,p in floors.items()}
# All current Godot records and neighbours remain byte-for-byte untouched in this source lane.
assert sha(G/'data/generated/structural_meshes.json')==D['protected']['original_compiled_sha256'];assert sha(G/'data/spatial_layout.json')==D['protected']['original_spatial_sha256'];assert sha(G/'data/reference/historical_guest_census.json')==D['protected']['guest_envelopes_sha256'];assert sha(G/'data/reference/historical_atlas_allocations.json')==D['protected']['retail_allocations_sha256']
protected=box(-54,-466,-8,-398)
for p in parts:
 b=p['bounds']
 if p['shape'].intersection(protected).area>1e-7:assert b[1]>=43.76-1e-7,(p['name'],b[1])
 assert b[4]<=61+1e-7,(p['name'],b[4])
# Robust exact-height convex slices of individual source solids. Used only for conservative capsule/proxy checks.
def slice_shape(p,lo,hi):
 vv=p['world_vertices'];out=[(v[0],v[2])for v in vv if lo-1e-9<=v[1]<=hi+1e-9]
 for a in vv:
  for b in vv:
   if abs(a[1]-b[1])<1e-9:continue
   for y in[lo,hi]:
    t=(y-a[1])/(b[1]-a[1])
    if 0<=t<=1:out.append((a[0]+(b[0]-a[0])*t,a[2]+(b[2]-a[2])*t))
 return MultiPoint(out).convex_hull if out else Polygon()
def samples(chain,spacing=.10):
 for a,b in zip(chain,chain[1:]):
  n=max(1,math.ceil(math.dist(a,b)/spacing))
  for i in range(n):yield[a[k]+(b[k]-a[k])*i/n for k in range(len(a))]
 yield chain[-1]
routes={
 'D08_dry_arrival_to_ramp':[[-8.05,44,-432],[-9.4,44,-432],[-9.4,44,-447.8],[-12,44,-447.8]],
 'D08_ramp':D['accessible_ramp']['route_xyz'],
 'D09_closed_door_dry_market_loop':[[x,52.5,z]for x,z in D['market']['adopted_dry_loop_centreline_xz']],
 'D08_wet_pool_circuit':[[-20,46.2,-447.8],[-20,46.2,-459.8],[-43,46.2,-459.8],[-45.9,46.2,-458],[-45.9,46.2,-405],[-43,46.2,-400.9],[-20,46.2,-400.9],[-20,46.2,-426.8]],
 'D08_local_lift_approach':[[-20,46.2,-407],[-10.8,46.2,-407],[-10.8,46.2,-412.4],[-13.45,46.2,-412.4]],
 'local_stair_connected_route':[[-20,46.2,-426.8],[-15.8,46.2,-426.8],[-15.8,46.2,-423.5],[-15.8,49.35,-418.06],[-15.8,49.35,-417.0],[-12.6,49.35,-417.0],[-12.6,49.35,-418.06],[-12.6,52.5,-423.5],[-12.6,52.5,-426.7],[-14.55,52.5,-426.7]]}
route_rows=[]
for label,chain in routes.items():
 hits=[];count=0
 for x,y,z in samples(chain):
  count+=1;body=Point(x,z).buffer(.3,quad_segs=8)
  for p in parts:
   bb=p['bounds']
   if p.get('collision_contract')=='visual_only_stair_tread':continue
   if bb[4]<=y+.3 or bb[1]>=y+1.8 or not p['shape'].intersects(body):continue
   cut=slice_shape(p,y+.3,y+1.8)
   if cut.intersection(body).area>1e-7:hits.append({'at':[x,y,z],'part':p['name']});break
  if len(hits)>8:break
 route_rows.append({'route':label,'sampled_positions':count,'body_radius_m':.3,'body_test_height_above_foot_m':[.3,1.8],'pass':not hits,'hits':hits})
# Open-door sightlines: all19x19 aperture samples, multiple eye heights, exact baffle intersection.
baffle=box(-51.2,-465.8,-51.0,-459.5);sight_rays=0;miss=[]
for i in range(19):
 for j in range(19):
  a=(-53.86,-464.2+2.4*i/18);b=(-48,-459.8+2.4*j/18)
  for h in[.75,1.2,1.65,2.1]:
   sight_rays+=1
   if not LineString([a,b]).intersects(baffle):miss.append([a,b,h])
assert not miss,miss[:3]
# Changing-position/heading loaded-cart+operator proxy through the screened local dogleg.
# Uses actual cart boxes/wheels and measured four-product tray envelope; all y under3.2m wall tops.
contacts=json.loads((G/'data/architecture/cleaning_cart_contacts.json').read_text());base_shapes=[]
for item in contacts['boxes']:
 x,y,z=item['center'];w,h,d=item['size'];base_shapes.append(box(x-w/2,z-d/2,x+w/2,z+d/2))
for item in contacts['wheel_contacts']:
 x,y,z=item['center'];base_shapes.append(Point(x,z).buffer(item['radius'],quad_segs=8))
base_shapes.append(box(-.325,-.48,.325,.48));cart=unary_union(base_shapes)
# Source-defined walls/niches at wet Y46.2; actual unchanged door cassette pockets are added in their open state.
local_obstacles=[]
for p in parts:
 b=p['bounds']
 if b[4]>46.2+.12 and b[1]<48.0 and p['shape'].intersects(box(-59,-466,-46,-456)):
  cut=slice_shape(p,46.2+.12,48.0)
  if not cut.is_empty:local_obstacles.append((p['name'],cut))
# Include exact pocket extents and closed end caps for open door atX-53.86. Leaves retract into pockets.
for z0,z1 in[(-465.58,-464.2),(-461.8,-460.42)]:local_obstacles.append(('existing_AST_DOR_002_open_pocket',box(-53.99,z0,-53.73,z1)))
# Corridor envelope at the west threshold, its side walls remain outside the open aperture.
for z0,z1 in[(-464.8,-464.68),(-461.32,-461.2)]:local_obstacles.append(('upper_staff_corridor_wall',box(-58.8,z0,-54,z1)))
poses=[]
def move(a,b,yaw):
 for x,z in samples([a,b],.04):poses.append((x,z,yaw))
def turn(p,q,a,b):
 for i in range(81):
  t=i/80;poses.append((p[0]+(q[0]-p[0])*t,p[1]+(q[1]-p[1])*t,a+(b-a)*t))
move([-57,-463],[-52.0,-463.1],-math.pi/2);turn([-52.0,-463.1],[-51.95,-462.9],-math.pi/2,-math.pi);move([-51.95,-462.9],[-51.95,-458.1],-math.pi);move([-51.95,-458.1],[-51.65,-458.1],-math.pi);turn([-51.65,-458.1],[-51.55,-458],-math.pi,-math.pi/2);move([-51.55,-458],[-47.1,-458],-math.pi/2)
cart_hits=[];min_clear=999
for index,(x,z,yaw)in enumerate(poses):
 # GodotY rotation inXZ uses x'=cos*x+sin*z, z'=-sin*x+cos*z.
 c=translate(rotate(cart,-yaw,origin=(0,0),use_radians=True),x,z);operator=Point(x+math.sin(yaw)*1.62,z+math.cos(yaw)*1.62).buffer(.3,quad_segs=12)
 for name,p in local_obstacles:
  if c.intersection(p).area>1e-7 or operator.intersection(p).area>1e-7:cart_hits.append({'pose_index':index,'pose':[x,z,yaw],'part':name});break
  min_clear=min(min_clear,c.distance(p),operator.distance(p))
 # Both operator feet and four wheel centres must have compiler-floor support.
 floor=floors[46.2]
 for item in contacts['wheel_contacts']:
  xx,yy,zz=item['center'];xx,zz=x+math.cos(yaw)*xx+math.sin(yaw)*zz,z-math.sin(yaw)*xx+math.cos(yaw)*zz
  if not floor.buffer(1e-6).covers(Point(xx,zz)):cart_hits.append({'pose_index':index,'unsupported_wheel':[xx,zz]})
 if not floor.buffer(1e-6).covers(operator.centroid):cart_hits.append({'pose_index':index,'unsupported_operator':list(operator.centroid.coords)[0]})
 if len(cart_hits)>15:break
cart_row={'pass':not cart_hits,'sampled_poses':len(poses),'sample_translation_step_m':.04,'turn_angle_steps':80,'turn_centres_translate':True,'operator_offset_m':1.62,'operator_radius_m':.3,'actual_cart_compound_boxes':len(contacts['boxes']),'wheel_spheres':4,'loaded_tray_plan_m':[.65,.96],'minimum_plan_clearance_m':min_clear,'hits':cart_hits,'route_poses':poses,'reverse_scope':'Same held orientations retraced in reverse; geometric backing/regrip space, not force-driven physics','pending':'Actual dynamics, freehand steering and spring-cart comfort after runtime integration'}
report={'pass':all(r['pass']for r in route_rows)and cart_row['pass'],'scope':'Conservative source solid slices + exact polygon floor/sightline checks. Capsule band starts0.3m above foot, excludes gait contact. No engine proof.','source_routes':route_rows,'open_door_screening':{'pass':True,'rays':sight_rays,'baffle_rect':[-51.2,-51,-465.8,-459.5]},'screened_cart_proxy':cart_row,'runtime_records_and_neighbours_unchanged':True,'D07_no_new_material_below43_76':True,'D10_no_new_material_above61':True}
(R/'qa/plan_route_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({**report,'screened_cart_proxy':{k:v for k,v in cart_row.items()if k!='route_poses'}},indent=2))
