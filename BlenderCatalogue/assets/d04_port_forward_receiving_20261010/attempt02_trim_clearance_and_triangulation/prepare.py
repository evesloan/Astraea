from pathlib import Path
import json,hashlib,math
from shapely.geometry import box,Polygon,mapping
from shapely.geometry.polygon import orient
from shapely import constrained_delaunay_triangles
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[3];W=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parts=[]
faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def add(name,vs,fs,role='champagne_metal',category='frame'):
    parts.append({'name':name,'verts':vs,'faces':fs,'role':role,'category':category,'runtime_collision':True})
def cube(name,lo,hi,role='champagne_metal',category='frame'):
    x,y,z=lo;X,Y,Z=hi
    add(name,[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)],faces,role,category)
def prism(name,poly,lo,hi,axis='y',role='warm_stone',category='floor'):
    poly=orient(poly,sign=1);vs=[];fs=[]
    def point(u,v,w):return [u,w,v]if axis=='y'else([w,v,u]if axis=='x'else[u,v,w])
    for tri in constrained_delaunay_triangles(poly).geoms:
        q=list(orient(tri,sign=1).exterior.coords)[:3];i=len(vs)
        vs.extend([point(u,v,w)for w in [lo,hi]for u,v in q]);fs.extend([[i,i+2,i+1],[i+3,i+4,i+5]])
    for ring in [poly.exterior,*poly.interiors]:
        for a,b in zip(ring.coords,list(ring.coords)[1:]):
            i=len(vs);vs.extend([point(*a,lo),point(*b,lo),point(*b,hi),point(*a,hi)]);fs.append([i,i+1,i+2,i+3])
    if axis in ['x','y']:fs=[list(reversed(f))for f in fs]
    add(name,vs,fs,role,category)
def segment(name,a,b,width=.12,depth=.12,role='champagne_metal',category='truss_brace'):
    # Rectangular longitudinal member, all endpoint faces retained for exact joints.
    import numpy as np
    a=np.array(a,float);b=np.array(b,float);w=(b-a)/np.linalg.norm(b-a)
    aux=np.array([1,0,0])if abs(w[0])<.9 else np.array([0,0,1])
    u=np.cross(w,aux);u/=np.linalg.norm(u);v=np.cross(w,u)
    # Local coordinates use right-handed u,v,w; bottom/top winding stays positive.
    vs=[(p+sx*u*width/2+sy*v*depth/2).tolist()for p in [a,b]for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    add(name,vs,faces,role,category)

# Exact independent geographic neighborhood. These are allocation/proposal keys,
# never guessed recovered room/save identities or assigned species.
C='BlenderCatalogue/assets/residential_hotels/central_room_families_20261007_r001/residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json'
records=json.load(open(R/C))['records'];units=[r for r in records if r['house']=='port_forward_lower_habitat_house'];assert len(units)==20
public=box(-44,-406.9,-4,-403.5);street=box(-46.05,-445.2,-41.95,-366);link=box(-67,-372.6,-44,-367.2);bay=box(-70,-376,-63,-364)
floor=unary_union([public,street,link,bay]);lower=box(-65.1,-381.4,-58.8,-367.2)
stair_void=box(-64.8,-381.3,-58.8,-370.8);roof=floor.union(box(-65.1,-381.4,-55.2,-367.2));floor=floor.difference(stair_void)
for r in units:
 assert floor.intersection(box(r['allocation_x'][0],r['allocation_z'][0],r['allocation_x'][1],r['allocation_z'][1])).area<1e-8
crew=json.load(open(R/'BlenderCatalogue/assets/group3_crew_service_20261009/source/CREW_BANK_PLACEMENTS_PROPOSAL.json'))
for a in crew['instances']:
 e=a['source_envelope'];assert lower.intersection(box(e['x'][0],e['z'][0],e['x'][1],e['z'][1])).area<1e-8
prism('D04PF_ReceivedFloor',floor,16.26,16.5)
prism('D04PF_ReceivedRoof',roof,20.48,20.70,role='ivory_enamel',category='roof')
prism('D04PF_StaffLowerLanding',lower,11.76,12,role='warm_stone',category='staff_floor')
feet=[]
for x in [-43.7,-32.,-20.,-8.5]:
 for z in [-406.65,-403.75]:feet.append(dict(x=x,z=z,y=12.,owner='D03_protected_crew_cover',wall_contact_allowed=False))
for x in [-58.62,-55.38]:
 for z in [-442.,-424.,-406.,-388.,-370.]:feet.append(dict(x=x,z=z,y=12.,owner='D03_port_forward_staff_floor_0',wall_contact_allowed=True))
for x in [-58.62,-55.38]:
 for z in [-379.5,-373.5,-367.5]:feet.append(dict(x=x,z=z,y=12.,owner='D03_port_forward_staff_floor_0',wall_contact_allowed=True))
for i,f in enumerate(feet):cube(f'D04PF_BearingPier_{i:02d}',[f['x']-.14,f['y'],f['z']-.14],[f['x']+.14,16.3,f['z']+.14])
for i,z in enumerate([-442.,-424.,-406.,-388.,-370.]):
 cube(f'D04PF_StreetTransfer_{i}',[-58.76,15.98,z-.16],[-41.95,16.3,z+.16])
 segment(f'D04PF_TransferRaker_{i}',[-58.62,13.8,z],[-46.05,16.14,z],.18,.18)
for x in [-45.8,-42.2]:cube('D04PF_StreetLong_'+str(x),[x-.14,15.98,-445.2],[x+.14,16.3,-366])
for z in [-406.65,-403.75]:cube('D04PF_PublicLong_'+str(z),[-44,15.98,z-.14],[-4,16.3,z+.14])
for i,x in enumerate([-43.7,-32,-20,-8.5]):cube(f'D04PF_PublicCross_{i}',[x-.14,15.98,-406.9],[x+.14,16.3,-403.5])
for z in [-373.5,-367.5]:
 cube('D04PF_CommonsTransfer_'+str(z),[-70,15.98,z-.14],[-44,16.3,z+.14])
 segment('D04PF_CommonsRaker_'+str(z),[-58.62,12.1,z],[-69.6,16.14,z],.2,.2)
for x in [-69.7,-63.3]:cube('D04PF_BayLong_'+str(x),[x-.14,15.98,-376],[x+.14,16.3,-364])
for z in [-379.5,-373.5,-367.5]:
 cube('D04PF_LowerLandingTransfer_'+str(z),[-65.1,11.48,z-.14],[-55.24,11.8,z+.14])
 cube('D04PF_UpperStairTransfer_'+str(z),[-65.1,20.18,z-.14],[-55.24,20.50,z+.14])
 cube('D04PF_LandingSuspension_'+str(z),[-65.1,11.48,z-.10],[-64.9,20.32,z+.10])
 cube('D04PF_ServicePierUpperWest_'+str(z),[-58.76,16.3,z-.14],[-58.48,20.32,z+.14])
 cube('D04PF_ServicePierUpperEast_'+str(z),[-55.52,16.3,z-.14],[-55.24,20.32,z+.14])
# Existing4.5m stair sits on its own supported landing. Its source ramp/contact
# semantics are reused by the runtime builder, not a convex filled stair void.
for x in [-64.96,-58.94]:cube('D04PF_LowerLandingLong_'+str(x),[x-.14,11.48,-381.3],[x+.14,11.8,-367.2])
segment('D04PF_StairRakerWest',[-64.6,11.8,-370.8],[-64.6,14.05,-380.9],.22,.22)
segment('D04PF_StairRakerEast',[-59.0,16.28,-370.8],[-59.0,14.05,-380.9],.22,.22)
# Roof posts continue the received floor frame; they avoid the recorded north
# room entry profiles rather than putting a support in a future doorway.
for side,x in enumerate([-45.8,-42.2]):
 for i,z in enumerate([-445.,-423.,-408.5,-389.5,-373.5]):
  cube(f'D04PF_StreetRoofPost_{side}_{i}',[x-.12,16.3,z-.12],[x+.12,20.50,z+.12])
for x in [-43.7,-32.,-20.,-8.5]:
 for z in [-406.65,-403.75]:cube('D04PF_PublicRoofPost_'+str(x)+'_'+str(z),[x-.12,16.3,z-.12],[x+.12,20.50,z+.12])
for z in [-373.5,-367.5]:
 cube('D04PF_BayRoofTransfer_'+str(z),[-70,20.18,z-.14],[-55.24,20.50,z+.14])
 cube('D04PF_BayWestPost_'+str(z),[-69.82,15.98,z-.12],[-69.58,20.50,z+.12])
# Exact original stair rise and simplified walking surface, with source treads
# kept visual and source guards collidable. Hidden ramp geometry is real physics.
def ramp(name,q):
 add(name,[[x,y-.24,z]for x,y,z in q]+q,faces,'warm_stone','stair_walk_surface')
 parts[-1]['runtime_visual']=False
ramp('D04PF_StairWalkLower',[[-64.8,12,-370.8],[-62.3,12,-370.8],[-62.3,14.25,-378.3],[-64.8,14.25,-378.3]])
cube('D04PF_StairWalkLanding',[-64.8,14.01,-381.3],[-58.8,14.25,-378.3],role='warm_stone',category='stair_walk_surface');parts[-1]['runtime_visual']=False
ramp('D04PF_StairWalkUpper',[[-61.3,16.5,-370.8],[-58.8,16.5,-370.8],[-58.8,14.25,-378.3],[-61.3,14.25,-378.3]])
# Guard every exposed boundary; selected public interface remains fully open.
guards=[]
def guard(name,a,b,y):
 if a[0]==b[0]:lo=[a[0]-.04,y+.12,min(a[1],b[1])];hi=[a[0]+.04,y+1.12,max(a[1],b[1])]
 else:lo=[min(a[0],b[0]),y+.12,a[1]-.04];hi=[max(a[0],b[0]),y+1.12,a[1]+.04]
 cube(name,lo,hi,role='hospitality_glass',category='guard');cube(name+'_Base',[lo[0],y,lo[2]],[hi[0],y+.14,hi[2]],category='guard');cube(name+'_Cap',[lo[0],y+1.10,lo[2]],[hi[0],y+1.18,hi[2]],category='guard');guards.append(name)
for ring in [floor.exterior]:
 for i,(a,b) in enumerate(zip(ring.coords,list(ring.coords)[1:])):
  if abs(a[0]+4)<1e-7 and abs(b[0]+4)<1e-7:continue
  if abs(a[1]+370.8)<1e-7 and abs(b[1]+370.8)<1e-7:
   line=box(min(a[0],b[0]),a[1]-.001,max(a[0],b[0]),a[1]+.001)
   left=max(min(a[0],b[0]),-64.8);right=min(max(a[0],b[0]),-61.3)
   if right>left:guard(f'D04PF_UpperStairMouthGuard_{i:02d}',(left,a[1]),(right,a[1]),16.5)
   continue
  guard(f'D04PF_UpperGuard_{i:02d}',a,b,16.5)
# Lower landing has a source wall/door at its east edge, full guards elsewhere.
for i,(a,b) in enumerate(zip(lower.exterior.coords,list(lower.exterior.coords)[1:])):
 if abs(a[0]+58.8)<1e-7 and abs(b[0]+58.8)<1e-7:continue
 guard(f'D04PF_LowerGuard_{i:02d}',a,b,12)
# A quiet bounded west commons edge, with a framed local-directory panel and
# source benches; no fabricated exterior window or assigned biology.
cube('D04PF_CommonsWestDado',[-70,16.5,-376],[-69.82,17.25,-364],role='warm_walnut',category='wall')
cube('D04PF_CommonsDirectoryFrame',[-69.85,17.3,-371.45],[-69.60,19.3,-368.55],category='fitting')
cube('D04PF_CommonsDirectoryFace',[-69.60,17.4,-371.35],[-69.57,19.2,-368.65],role='ivory_enamel',category='fitting')
lights=[]
for i,(x,z) in enumerate([(-12,-405.2),(-24,-405.2),(-36,-405.2),(-44,-437),(-44,-420),(-44,-405),(-44,-388),(-44,-370),(-55,-370),(-66,-370)]):
 cube(f'D04PF_LampHousing_{i}',[x-.3,20.18,z-.3],[x+.3,20.48,z+.3],category='fitting')
 cube(f'D04PF_LampLens_{i}',[x-.26,20.15,z-.26],[x+.26,20.18,z+.26],role='opal_glow',category='fitting');lights.append(dict(name=f'D04PF_LampLens_{i}',at=[x,20.12,z]))
paths=[C,'Game/data/reference/historical_guest_census.json','Game/data/whole_ship_layout.json','Game/data/generated/structural_meshes.json','Game/data/spatial_layout.json','Game/docs/master_source/MASTER_CURRENT_APPLICATION.json','Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json','Game/assets/models/AST-STF-009_pool_market_home_equipment.glb','Game/assets/models/AST-CIR-001_H450.glb','BlenderCatalogue/assets/circulation_architecture/source/AST-CIR-001_H450.blend','Game/assets/models/AST-DOR-002.glb','Game/scripts/lower_staff_network.gd','Game/data/architecture/LOWER_STAFF_NETWORK.json','BlenderCatalogue/assets/group3_crew_service_20261009/source/CREW_BANK_PLACEMENTS_PROPOSAL.json','BlenderCatalogue/assets/furniture/AST-FUR-001_day_window_bench.blend','BlenderCatalogue/assets/staff_workbay/AST-STF-007_supply_work_cabinet.blend','BlenderCatalogue/references/landings/staff_corridor_services.png','BlenderCatalogue/references/residential_20261004/Guest_suite_corridor_8077.jpg']
P={'schema':1,'baseline_commit':'e6ec477987fa1f3a973ec81e8a6c0729717d4737','scope':'Connected port-forward D04 receiving streets and commons entry bay with D03 staff stair; rooms remain unadopted','house_id':'port_forward_lower_habitat_house','commons_programme_key':'D04_directory_01','units':units,'unit_count':20,'proposed_rest_count':sum(r['proposed_rest_place_count']for r in units),'floor_y':16.5,'floor_geometry':mapping(floor),'roof_geometry':mapping(roof),'stair_void_geometry':mapping(stair_void),'lower_landing_geometry':mapping(lower),'new_upper_floor_area_m2':floor.area,'new_lower_floor_area_m2':lower.area,'parts':parts,'lights':lights,'guards':guards,'feet':feet,'receiving_model':'D04_PORT_FORWARD_RECEIVING_r001.glb','source_pins':{p:sha(R/p)for p in paths},'staff_wall_cut':{'source_model':'AST-STF-009_pool_market_home_equipment.glb','meshes':['HOME_BATCH_015_ASTRAEA_staff_bluegrey_paint','HOME_BATCH_182_ASTRAEA_staff_white_paint','HOME_BATCH_132_ASTRAEA_staff_rubber'],'min':[-58.805,11.99,-369.79],'max':[-58.675,14.5,-368.21]},'staff_door':{'origin':[-58.93,12,-369.0],'yaw':-math.pi/2,'model':'AST-DOR-002.glb','persistent_id':'D04_port_forward_staff_receiving_door_candidate'},'stair':{'origin':[-64.8,12,-370.8],'yaw':0,'model':'AST-CIR-001_H450.glb','source':'BlenderCatalogue/assets/circulation_architecture/source/AST-CIR-001_H450.blend'},'source_fittings':[{'source':'BlenderCatalogue/assets/furniture/AST-FUR-001_day_window_bench.blend','prefix':'D04PF_BenchNorth','origin':[-68.3,16.5,-374.9],'yaw':0},{'source':'BlenderCatalogue/assets/furniture/AST-FUR-001_day_window_bench.blend','prefix':'D04PF_BenchSouth','origin':[-68.3,16.5,-365.1],'yaw':math.pi},{'source':'BlenderCatalogue/assets/staff_workbay/AST-STF-007_supply_work_cabinet.blend','prefix':'D04PF_ServiceCabinet','origin':[-68.3,16.5,-372.5],'yaw':0}],'limits':['Geometric support only; primary structural/load/cantilever sizing remains held','Twenty room allocations/proposal IDs and25 proposed rests preserved; no recovered identities, new beds or species assignment','Commons entry bay is partial; complete neighborhood, interiors/privacy/environmental support/outlook/enclosure and other five neighborhoods remain construction','Staff stair is walking access; independent cart-safe service vertical operation remains open','Static cabinet is physical source fitting; stock/save/service operation held','D17 complete-room/privacy/outlook work and every eight-group obligation remain open','Ordinary Godot/CRT/hardware acceptance held'],'staff_shaft_D04_D07_blank':True,'public_core_walls_unchanged':True,'rooms_adopted':0,'open_staff_gateway':False}
(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n');print(json.dumps({'parts':len(parts),'upper_floor_area':floor.area,'lower_floor_area':lower.area,'rooms_adopted':0,'source_pins':len(paths)}))
