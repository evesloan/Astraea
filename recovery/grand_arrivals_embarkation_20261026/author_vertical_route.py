"""Author the approved lower-hall route alignment; no original geometry is cut.

Conservative sampled floor screening selects the receiving work, not admission.
Uses standard Python only, retained source triangles and the selected upper route.
"""
import hashlib,json,math,pathlib
R=pathlib.Path(__file__).resolve().parents[2]
D=R/'Game/grand_arrivals_tram_20261026/r001'
assert not D.exists(), 'Preserve previous authored revision'
source_paths=['Game/aquatic_tram_interior_20261026/r009/PLAN.json','Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json','Game/data/architecture/D01_D02_arrivals_fusion.json','Game/data/architecture/FORWARD_PUBLIC_CORE.json','Game/scripts/group4_tram_source_actuator.gd','Game/scripts/group4_loaded_tram_actuator.gd','Game/data/architecture/GROUP4_BOARDING_SAFETY_CANDIDATE.json']
pins={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in source_paths}
upper=json.loads((R/source_paths[0]).read_text())
points=[]
def line(a,b):
 n=max(1,math.ceil(math.dist(a,b)/.5))
 for i in range(n):
  f=i/n;points.append([a[j]+(b[j]-a[j])*f for j in range(2)])
def arc(c,r,a,b):
 n=max(1,math.ceil(abs(b-a)*r/.25))
 for i in range(n):
  t=a+(b-a)*i/n;points.append([c[0]+r*math.cos(t),c[1]+r*math.sin(t)])
# FORWARD lower-hall station boards west, facing north. Existing upper
# Orchard/aquatic route is traversed in reverse after the long scenic ascent.
line([-12,-443],[-12,-455]);arc([-7.2,-455],4.8,math.pi,1.5*math.pi)
line([-7.2,-459.8],[.8,-459.8]);arc([.8,-455],4.8,-math.pi/2,0)
ascent_start=len(points);line([5.6,-455],[5.6,450]);ascent_end=len(points)
arc([0,450],5.6,0,math.pi)
retained=list(reversed(upper['route_points_xz']))
retained=[p for p in retained if p[1]<=450 and p[1]>=-412]
# Original path is not monotonic in Z within stations. Filter only its outer
# end ranges; every selected Orchard/aquatic detour remains in sequence.
line([-5.6,450],retained[0])
for a,b in zip(retained,retained[1:]):line(a,b)
points.append(retained[-1])
def height(z):
 # Zero grade at both ends; 40m cosine easements. 7.273% maximum is an
 # authored geometric target, not proven vehicle traction/rider acceptance.
 lo=-410.;hi=400.;ease=40.;rise=56.;g=rise/(hi-lo-ease)
 t=max(0.,min(hi-lo,z-lo));L=hi-lo
 if t<ease:return .1+g*(t/2-ease*math.sin(math.pi*t/ease)/(2*math.pi))
 if t>L-ease:
  u=L-t;return 56.1-g*(u/2-ease*math.sin(math.pi*u/ease)/(2*math.pi))
 return .1+g*(t-ease/2)
xyz=[[p[0],height(p[1]) if ascent_start<=i<=ascent_end else (.1 if i<ascent_start else 56.1),p[1]] for i,p in enumerate(points)]
length=sum(math.dist(a,b) for a,b in zip(xyz,xyz[1:]))
grades=[abs(b[1]-a[1])/math.hypot(b[0]-a[0],b[2]-a[2]) for a,b in zip(xyz,xyz[1:]) if math.hypot(b[0]-a[0],b[2]-a[2])>1e-8]
assert max(grades)<.08 and all(math.dist(a,b)<.51 for a,b in zip(xyz,xyz[1:])), 'Discontinuous route or grade'
def overlaps(t,rect):
 # Exact convex SAT for this triangle and the axis-aligned screening square.
 box=[(rect[0],rect[1]),(rect[2],rect[1]),(rect[2],rect[3]),(rect[0],rect[3])]
 axes=[(1,0),(0,1)]+[(a[1]-b[1],b[0]-a[0]) for a,b in zip(t,t[1:]+t[:1])]
 for x,z in axes:
  ta=[p[0]*x+p[1]*z for p in t];ba=[p[0]*x+p[1]*z for p in box]
  if max(ta)<min(ba) or max(ba)<min(ta):return False
 return True
hits=[]
for source in source_paths[1:3]:
 for floor in json.loads((R/source).read_text())['regions']:
  triangles=floor['triangles'];y=floor['floor_y'];bottom=y-floor.get('thickness',.24)
  candidates=[p for p in xyz[:ascent_end] if p[1]-.6<=y and p[1]+3.3>=bottom]
  if not candidates:continue
  xs=[v[0] for t in triangles for v in t];zs=[v[1] for t in triangles for v in t]
  if not xs:continue
  witnesses=[]
  for p in candidates:
   rect=[p[0]-2.8,p[2]-2.8,p[0]+2.8,p[2]+2.8]
   if rect[2]<min(xs) or rect[0]>max(xs) or rect[3]<min(zs) or rect[1]>max(zs):continue
   if any(overlaps(t,rect) for t in triangles):witnesses.append(p)
  if witnesses:hits.append({'source':source,'floor':floor['id'],'floor_y':y,'first_xyz':witnesses[0],'last_xyz':witnesses[-1],'sample_count':len(witnesses)})
plan={'schema':'astraea.grand_arrivals.lower_route.r001','status':'AUTHORED_ALIGNMENT_UNSELECTED_RECEIVING_REQUIRED','active':False,'owner_authorization':'Sentinel_296cfa10e6fc8191b3f827646f0b8cd7','baseline':'3c7396efab5f3169ff277ebceaecb2c93f824c93','source_pins':pins,'route_xyz':xyz,'route_length_m':length,'maximum_grade':max(grades),'minimum_authored_horizontal_radius_m':4.8,'vertical_easement_m':40,'rise_m':56,'grade_acceptance':'provisional geometric target; original trucks have no proved pitch joint or grade acceptance','station':{'identity':'FORWARD','catchment_z':-432,'dock_xyz':[-12,.1,-449],'heading':'north','door_side_world':'west','platform_xz':[-20.2,-454,-14.2,-444],'platform_y':.1,'platform_gross_m2':60,'passenger_capacity':None,'accessible_approach':'D01 hall, ground-level baggage/reception; .1m rise needs exact transition; original visitor lift and 17-stop core remain','baggage':'Retained staffed interface at X-40/Z-452, no public entry into service suite','service_separation':'Preserve west staff street and opaque service boundary','waiting':'Separate wider hall pockets must be reconciled with reception, arch piers and exhibit view axes; gross platform area is not arrival-wave capacity'},'rail_sequence':['Lower Grand Arrivals FORWARD','Long starboard-spine ascent','Upper AFT','Upper AFT_MIDSHIP aquatic','Upper CENTRAL','Upper FORE_MIDSHIP Orchard'],'source_screening':{'scope':'Sampled conservative 5.6m-square/3.9m-high reservation against retained generated floor triangles only. Not original vehicle swept geometry, complete selected world, walls, supports or clearance proof. Ground floor contacts are expected and require supported rail recesses. No floor has been cut.','contacts':hits},'remaining':['Exact lower station/wall/rail recess receiving and west boarding/cart flow','Continuous complete original vehicle/cart/door and bogie grade envelope','Resolve named deck crossings with supported circulation-preserving interfaces','Grade/pitch-capable successor retaining original departure/restraint/fault authority','Structural bearings, protected core and all walls/bridges','Guest materials, planting, waiting/relaxation and baggage flow','Installed boarding, moving route, capacity/headways, hardware performance and matching Windows']}
D.mkdir(parents=True)
(D/'PLAN.json').write_bytes((json.dumps(plan,indent=2)+'\n').encode())
print(json.dumps({k:plan[k] for k in ['route_length_m','maximum_grade','minimum_authored_horizontal_radius_m']},indent=2));print(json.dumps(hits,indent=2))
