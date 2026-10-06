import json,pathlib,hashlib
import numpy as np
# Minimal deterministic polygon/rectangle clipping; no external geometry dependency.
import math
class Exterior:
 def __init__(self,p):self.coords=p+[p[0]]
class Shape:
 def __init__(self,polys,holes=[]):self.polys=polys;self.holes=holes;self.exterior=Exterior(polys[0])
 def buffer(self,d):return self
 def intersection(self,other):
  xs=[p[0] for p in self.polys[0]];zs=[p[1] for p in self.polys[0]];r=[min(xs),min(zs),max(xs),max(zs)]
  class Result:pass
  a=Result();a.area=sum(area(clip(poly,r)) for poly in other.polys)-sum(area(clip(poly,r)) for poly in other.holes);return a
 def covers(self,other):
  # Floor covered area from exact supplied constrained triangles is checked separately.
  return all(inside(v,self.polys[0]) and not any(inside(v,h) for h in self.holes) for v in other.polys[0])
def area(p):return abs(sum(a[0]*b[1]-a[1]*b[0]for a,b in zip(p,p[1:]+p[:1])))/2 if p else 0
def clip(poly,r):
 p=[list(v)for v in poly]
 for axis,edge,sgn in [(0,r[0],1),(0,r[2],-1),(1,r[1],1),(1,r[3],-1)]:
  q=[]
  for a,b in zip(p,p[1:]+p[:1]):
   ia=(a[axis]-edge)*sgn>=0;ib=(b[axis]-edge)*sgn>=0
   if ia:q.append(a)
   if ia!=ib:
    t=(edge-a[axis])/(b[axis]-a[axis]);q.append([a[j]+t*(b[j]-a[j])for j in range(2)])
  p=q
 return p
def inside(v,p):
 x,z=v;c=False
 for a,b in zip(p,p[1:]+p[:1]):
  if (a[1]>z)!=(b[1]>z) and x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0]:c=not c
 return c
def box(x0,z0,x1,z1):return Shape([[[x0,z0],[x1,z0],[x1,z1],[x0,z1]]])
def Polygon(boundary,holes):return Shape([boundary],holes)
class LineString:
 def __init__(self,points):self.points=points
 def buffer(self,r):
  polys=[]
  for a,b in zip(self.points,self.points[1:]):
   dx,dz=b[0]-a[0],b[1]-a[1];l=math.hypot(dx,dz);nx,nz=-dz/l*r,dx/l*r
   polys.append([[a[0]+nx,a[1]+nz],[b[0]+nx,b[1]+nz],[b[0]-nx,b[1]-nz],[a[0]-nx,a[1]-nz]])
  for x,z in self.points:polys.append([[x+r*math.cos(t*math.pi/16),z+r*math.sin(t*math.pi/16)]for t in range(32)])
  return Shape(polys)

R=pathlib.Path(__file__).resolve().parent
G=pathlib.Path('/workspace/shared/astraea-godot-production-20261003');C=pathlib.Path('/workspace/shared/astraea-catalogue-continuation-20261002')
contract=json.load(open(G/'data/architecture/GRAND_POOL_SECTION_RUNTIME.json'))
parts=json.load(open(R/'RETAINED_PART_BOUNDS.json'))['parts'];fin=json.load(open(R/'RETAINED_FINISH_BOUNDS.json'));views=json.load(open(R/'PRESERVED_VIEWS.json'))
def write(n,x):(R/n).write_text(json.dumps(x,indent=2,default=lambda o:o.item() if isinstance(o,np.generic) else str(o))+'\n')
def rec(name,b,host,purpose,notes,floor=None):return dict(id=name,bounds_xyz=b,retained_hosts=host,purpose=purpose,conditions=notes,floor_owner=floor)
candidates=[
 rec('lift_west_shallow_landmark',[[-17.90,46.20,-414.32],[-17.52,51.00,-410.48]],['GP_LocalLiftRear'],'A shallow built-out surround/reveal and mounted wayfinding; retain actual opaque back wall.',['Maximum projection 0.38 m into room; this is an additive outer cavity, never a carved shaft niche.','No bulk, new ledge or public floor inside shaft.','Existing continuous wet strip X-21.05..-18.12 remains unchanged.','For a service shelf, reserve a separate operator/guest stance and check the occupied reach; no seat usability claim.'],None),
 rec('lift_west_upper_profile',[[-17.70,51.00,-414.32],[-17.52,55.60,-410.48]],['GP_LocalLiftRear','GP_LocalLiftCap'],'Thin supported continuation tying lower landmark to existing lift cap.', ['This upper addition is fixed to the shaft rear wall; it is over the retained gallery void and must never become a balcony, shelf or walking surface.','Cap at Y55.60..55.74 remains unchanged. Stop at its underside.','Y51.0 is the chosen transition between deeper lower relief and this thinner upper profile, not a retained physical limit.'],None),
 rec('lift_aft_mounted_return',[[-17.30,46.20,-410.20],[-13.55,51.00,-410.00]],['GP_LocalLiftSide.001'],'Camera-facing 0.20 m relief/wayfinding return attached to the shaft side.',['Stop before east gate/jamb/front; never wrap onto east face.','Keep Y51.0..55.74 out of this candidate to avoid claiming an unchecked upper-arrival fit.','The lower lift approach crosses Z-407 and stays unchanged.'],None),
 rec('upper_east_gallery_rest_bay',[[-11.20,52.50,-454.00],[-8.20,57.80,-445.00]],['GP_EastWall.002','COMPILER_FLOOR_D09_orchard_market_gallery'],'Room-scale additive 3.0 m-deep, 9.0 m-long recessed seating/display bay against the actual east enclosure.',['The recess is between new forward returns and retained wall; do not cut wall.','Keep the ordinary dry ring X-17.8..-14.4 and the 3.2 m approach zone X-14.4..-11.2 clear.','Bay is outside fore pier Z-459.14..-456.86, arrival pier Z-441.64..-439.36, and public portal Z-435..-429.','Keep original upper wet/dry glazing at X-18 completely intact.','Retain all roof/perimeter supports; no new room/floor/programme or retail identity.'],'D09_orchard_market_gallery'),
 rec('lower_east_local_rest_service_pocket',[[-9.00,46.20,-427.50],[-8.20,49.10,-424.00]],['GP_EastWall.001','COMPILER_FLOOR_D08_grand_pool_wet'],'Small 0.80 m-deep, 3.50 m-long wall-backed rest/service recess east of the local stair, off the continuous pool walk.',['Reserve a dedicated occupied approach in X-10.40..-9.00, Z-427.50..-424.00; this is outside the retained lower-stair route and lift approach.','Near the stair east stringer, the unoccupied clear lateral gap is about 2.09 m. This is not a new 2.4 m through-route; do not advertise accessibility/seat usability without full source/controller checks.','Keep south end north of the arrival raised-edge guard at Z-428.2.','No movement of staircase, under-stair supports, gallery bypass or floor.','Lower pocket is optional/provisional; prioritize the shaft landmark and upper gallery bay if visual value from the fixed long view is weak.'],'D08_grand_pool_wet')]
# Declared central/safe route protection. Whole design reservations are retained even if current body sample is smaller.
routes=[
 ('continuous_east_wet_strip',46.2,49.2,box(-21.05,-457.7,-18.12,-406.3),'Conservative continuous unchanged strip inferred from existing drain east edge X-21.05 and most protruding ramp-pocket cap X-18.12; 2.93 m wide.'),
 ('ordinary_east_dry_ring',52.5,55.5,box(-17.8,-458,-14.4,-429.5),'Declared 3.4 m dry ring; extended to adopted fore-to-core cross-link.'),
 ('market_dry_bypass',52.5,55.5,box(-10.85,-427.9,-8.45,-410.2),'Declared 2.4 m dry bypass, must function with doors closed.'),
 ('fore_dry_ring',52.5,55.5,box(-47.6,-464.8,-14.4,-461.4),'Declared 3.4 m fore dry ring.'),
 ('aft_dry_ring',52.5,55.5,box(-47.6,-402.6,-8.45,-399.2),'Declared 3.4 m aft dry ring.'),
 ('lower_lift_approach',46.2,48.0,LineString([(-20,-407),(-10.8,-407),(-10.8,-412.4),(-13.45,-412.4)]).buffer(.3),'Retained QA body-radius 0.3 m route, no widening claimed.'),
 ('lower_stair_approach',46.2,48.0,LineString([(-20,-426.8),(-15.8,-426.8),(-15.8,-423.5)]).buffer(.3),'Retained QA body-radius 0.3 m lower stair approach.'),
 ('market_closed_door_crosslink',52.5,54.3,LineString([(-9.65,-429.5),(-15.5,-429.5),(-15.5,-432)]).buffer(.3),'Adopted dry loop cross-link before closed stair door.')]
fr={x['id']:x for x in contract['floor_regions']}
def intersects(a,b,tol=5e-5):return bool(np.all(np.minimum(a[1],b[1])-np.maximum(a[0],b[0])>tol))
def segment_box(a,b,bb):
 a=np.array(a);v=np.array(b)-a;lo,hi=np.array(bb);t0,t1=0.,1.
 for i in range(3):
  if abs(v[i])<1e-10:
   if a[i]<lo[i]or a[i]>hi[i]:return False
  else:
   q0,q1=sorted([(lo[i]-a[i])/v[i],(hi[i]-a[i])/v[i]]);t0=max(t0,q0);t1=min(t1,q1)
   if t0>t1:return False
 return True
for q in candidates:
 b=np.array(q['bounds_xyz']);foot=box(b[0,0],b[0,2],b[1,0],b[1,2]);q['screening']={}
 if q['floor_owner']:
  rect=[b[0,0],b[0,2],b[1,0],b[1,2]];want=(rect[2]-rect[0])*(rect[3]-rect[1]);covered=sum(area(clip(t,rect))for t in fr[q['floor_owner']]['triangles']);q['screening']['whole_footprint_on_retained_floor']=abs(want-covered)<1e-6;q['screening']['footprint_area_m2']=float(want);q['screening']['covered_by_exact_floor_triangles_m2']=float(covered)
 q['screening']['source_part_positive_volume_aabb_hits']=[p['source_name']for p in parts if intersects(b,np.array(p['verified_installed_triangle_bounds_xyz']))]
 q['screening']['finish_snapshot_positive_volume_aabb_hits']=[p['source_name']for p in fin if intersects(b,np.array(p['bounds_xyz']))]
 q['screening']['protected_route_hits']=[name for name,y0,y1,p,_ in routes if min(b[1,1],y1)>max(b[0,1],y0)+1e-5 and foot.intersection(p).area>1e-6]
 q['screening']['existing_wayfinding_bounds_hits']=[x['id']for x in json.load(open(G/'data/architecture/GRAND_POOL_FINISH_RUNTIME.json'))['signs'] if intersects(b,np.array(x['complete_envelope_xyz']))]
 q['screening']['existing_furnishing_bounds_hits']=[x['name']for fn in ['GRAND_POOL_FINISH_RUNTIME.json','GRAND_POOL_FIRST_PASS_RUNTIME.json'] for x in json.load(open(G/'data/architecture'/fn))['placements'] if intersects(b,np.array([x['envelope_min_xyz'],x['envelope_max_xyz']]))]
 q['screening']['preserved_view_segment_hits']=[v['name']for v in views if segment_box(v['eye_xyz'],v['target_xyz'],b)]
 q['screening']['interpretation']='Conservative box screen of proposed free volume only. Touching host faces/floor are permitted. Not detailed source construction, load capacity, contact proof, engine/controller validation or visual acceptance.'
# Explicit rejected alternatives from conceptual handoff.
rejected=[{'id':'upper_overlook_pockets_in_dry_ring','box_xz':[-17.6,-14.0,-454,-439],'reason':'Overlaps retained dry ring X-17.8..-14.4 by 3.2 m of its width; knees/stance would also block it. Keep seating behind X-14.4, not beside glass.'}]
low_rect=[-11.2,-454,-8.2,-445];covered=sum(area(clip(t,low_rect)) for t in fr['D08_grand_pool_wet']['triangles']);rejected.append({'id':'repeat_upper_bay_at_wet_datum','box_xz':[-11.2,-8.2,-454,-445],'area_m2':27,'retained_Y46_2_floor_coverage_m2':covered,'reason':'Upper bay overlaps lower ramp/eastern dry approach/arrival cutouts. Remaining Y46.2 slivers are not a 27m2 supported bay. No new floor may be assumed.'});write('REJECTED_CANDIDATES.json',rejected)
write('ADDITIVE_RESERVATIONS.json',{'status':'SCRATCH_PROPOSAL_ONLY_UNAUTHORED','coordinate_frame':'Godot world XYZ metres','candidates':candidates})
protected={
 'floor_polygons_file':'FLOOR_POLYGONS.json',
 'routes':[{'id':n,'y_m':[y0,y1],'plan_polygon_union_xz':p.polys,'reason':r}for n,y0,y1,p,r in routes],
 'hard_exclusions':[
 {'id':'pool_water_and_shell','bounds_xyz':[[-40.4,44.4,-457.4],[-21.6,46.2,-406.6]],'clear_water_xz':[-40,-22,-457,-407],'water_y':46.05,'rule':'Preserve exact pool footprint, pan, coping and drains; no bridge/island.'},
 {'id':'local_lift_enclosure_and_sweep','bounds_xyz':[[-17.52,45.96,-414.6],[-13.24,55.74,-410.2]],'rule':'Whole shaft reserved. Only named external faces may be touched. Do not alter wall, pit, cap, cabin or sweep; top cabin Y55.44 and cap underside55.60 leave only0.16m.'},
 {'id':'local_lift_east_gate_landing_zone','bounds_xyz':[[-13.6,46.2,-414.6],[-10.4,55.56,-410.2]],'rule':'Conservative no-new-work reservation around both east-facing landing gates, jambs, sills, buttons, stop approaches and lower wayfinding. Does not claim all space is one collision volume.'},
 {'id':'stair_void_and_arrival','bounds_xyz':[[-18.0,46.2,-425.5],[-11.1,55.0,-415.7]],'rule':'Reserve exact stair flights, midlanding, guard/rail, upper compiler-owned landing and connected void. No bridging or service infill.'},
 {'id':'joined_upper_void','boundary_xz':contract['opening']['combined_before_stair_landing_boundary'],'y_m':[52.26,52.50],'retained_upper_landing_xz':[-14,-11.1,-425.5,-423.5],'rule':'Keep existing nonconvex opening and its sole compiler landing. No new slab/shelf/mezzanine over void.'},
 {'id':'upper_stair_door_cassette','bounds_xyz':[[-17.13,52.5,-428.13],[-11.97,55.16,-427.87]],'rule':'Keep full cassette width5.16, both pockets, leaf travel and clear door width2.4; exact unchanged door family.'},
 {'id':'upper_lift_door_cassette','bounds_xyz':[[-17.13,52.5,-407.03],[-11.97,55.16,-406.77]],'rule':'Keep full cassette, upper wet landing and dry arrival.'},
 {'id':'main_east_glazing','bounds_xyz':[[-18.05,52.5,-458],[-17.95,60.76,-428]],'rule':'Do not cover, replace or treat as solid host. The structural fascia below it may host finish separately.'},
 {'id':'local_link_east_glazing','bounds_xyz':[[-11.15,52.5,-428],[-11.05,60.76,-406.9]],'rule':'Full-height environmental glass; dry bypass east, wet arrivals west.'},
 {'id':'local_link_transverse_glazing','planes_z':[-428,-406.9],'x_m':[-18,-11.1],'y_m':[52.5,60.76],'rule':'Retain GP_WetSealDoorSide/Transom/Header and GP_GlazingMullion identities; fit around whole door cassette, not just open leaves.'},
 {'id':'D08_arrival_and_ramp','arrival_xz':contract['public_interfaces']['D08_dry_arrival_bay_rect'],'approach_xz':contract['public_interfaces']['D08_dry_east_approach_clear_rect'],'ramp_xz':contract['accessible_ramp']['gross_envelope'],'rule':'Preserve Y44 arrival/approach, rising ramp1:12, all landings, ceremonial stair and guards. No invented wet-level floor here.'},
 {'id':'public_portals','x_m':[-8.2,-7.72],'z_m':[-435,-429],'clear_y_m':[[44,47.2],[52.5,55.7]],'rule':'Keep both6m wide portals and existing signs/collars clear.'},
 {'id':'deck_programmes','lower_y_limit':43.76,'upper_y_limit':61,'rule':'No new supports through protected D07 or occupied addition above D10. Existing floor ownership remains unchanged.'}
 ],
 'existing_wayfinding':[{'id':s['id'],'bounds_xyz':s['complete_envelope_xyz'],'host':s['primary_support'],'text':s['text_lines']}for s in json.load(open(G/'data/architecture/GRAND_POOL_FINISH_RUNTIME.json'))['signs']]
}
write('PROTECTED_RESERVATIONS.json',protected)
for q in candidates:print(q['id'],q['screening'])
# Hash read set and own outputs. Existing input pins generated by inspect_geometry.py.
write('OUTPUT_HASHES.json',{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(R.iterdir())if p.is_file()and p.name!='OUTPUT_HASHES.json'})
