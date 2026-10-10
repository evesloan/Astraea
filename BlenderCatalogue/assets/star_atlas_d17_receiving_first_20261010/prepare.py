from pathlib import Path
import json,hashlib,math
from shapely.geometry import box,Polygon,mapping
from shapely.geometry.polygon import orient
from shapely import constrained_delaunay_triangles
R=Path(__file__).resolve().parents[3];W=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert json.loads((W/'PREIMAGE_SUPPORT.json').read_text())['status']=='PASS'
base='c1942ee89f83a7c5a14dc4e31821b9dc6e1433b9'
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
floor=box(-67.1,14,-60,17.5).union(box(-63,17.5,-60,39.2))
prism('D17R_ReceivedFloor',floor,101.76,102)
prism('D17R_ReceivedRoof',floor,106.26,106.5,role='ivory_enamel',category='roof')
south=box(-97,102,-63,106.26).difference(box(-65.79,102,-64.21,104.5)).difference(box(-66.9,105.98,-66.5,106.26))
prism('D17R_SouthWallReceived',south,13.78,14,axis='z',role='ivory_enamel',category='wall_replacement')
east=box(3.2,102,14,106.26).difference(box(12.54,105.98,12.86,106.26))
prism('D17R_EastWallReceived',east,-63.22,-63,axis='x',role='ivory_enamel',category='wall_replacement')
cube('D17R_SourceEastTransfer',[-64.02,105.98,12.54],[-60,106.26,12.86])
cube('D17R_SourceWestTransfer',[-66.9,105.98,12.88],[-66.5,106.26,17.5])
cube('D17R_VestibuleRoofCross',[-66.9,105.98,17.1],[-60,106.26,17.5])
# A paired overhead truss receives the hanging street. Four distinct D16 slab
# bearings support its central frame; the original commons frame supports fore.
# Cantilever sizing/load certification remains explicit unfinished engineering.
piers=[]
for x in [-62.75,-60.25]:
    for z in [29.2,31]:
        name=f'D17R_D16Pier_{len(piers):02d}';cube(name,[x-.16,97.5,z-.16],[x+.16,105.98,z+.16]);piers.append({'name':name,'x':x,'z':z,'source_owner':'D16_STAR_ATLAS_MISSING_STREET_1','floor_y':97.5})
for side,x in enumerate([-62.75,-60.25]):
    cube(f'D17R_TrussUpper_{side}',[x-.16,105.98,12.86],[x+.16,106.26,39.2])
    cube(f'D17R_TrussLower_{side}',[x-.16,104.8,12.86],[x+.16,105.04,39.2])
    stations=[12.86,17.3,22,26.6,29.2,31,35.5,39.2]
    for j,z in enumerate(stations):cube(f'D17R_TrussPost_{side}_{j:02d}',[x-.12,104.8,z-.1],[x+.12,106.26,z+.1])
    for i,(a,b)in enumerate(zip(stations,stations[1:])):
        segment(f'D17R_TrussDiag_{side}_{i:02d}',[x,104.92 if i%2==0 else 106.12,a],[x,106.12 if i%2==0 else 104.92,b],.12,.14)
    for i,z in enumerate([15.8,22,26.6,29.2,31,33.1 if side==0 else 35.5,39.0]):
        if z not in [29.2,31]:cube(f'D17R_Hanger_{side}_{i:02d}',[x-.12,101.48,z-.12],[x+.12,104.92,z+.12])
        if side==0:cube(f'D17R_FloorCross_{i:02d}',[-63,101.48,z-.12],[-60,101.78,z+.12])
cube('D17R_VestibuleWestHanger',[-66.82,101.48,15.68],[-66.58,105.98,15.92])
cube('D17R_VestibuleFloorWest',[-67.1,101.48,14],[-66.6,101.78,17.5])
cube('D17R_VestibuleFloorNorth',[-67.1,101.48,14],[-60,101.78,14.3])
cube('D17R_VestibuleFloorSouth',[-67.1,101.48,17.2],[-60,101.78,17.5])
for side,x in enumerate([-62.75,-60.25]):cube(f'D17R_FloorLong_{side}',[x-.16,101.48,17.5],[x+.16,101.78,39.2])
# Cross-frame bracing stays above2.8m free headroom, with transverse rails at
# the pier stations and above the source-connected vestibule.
for i,z in enumerate([17.3,29.2,31,39]):
    cube(f'D17R_RoofCross_{i}',[-62.91,105.98,z-.12],[-60.09,106.26,z+.12])
    segment(f'D17R_RoofPlanBrace_{i}',[-62.75,106.12,z-.12],[-60.25,106.12,z+.12],.1,.1)
guards=[]
def guard(name,a,b,role='hospitality_glass'):
    x,z=a;X,Z=b;dx=X-x;dz=Z-z;length=math.hypot(dx,dz);u=-dz/length*.04;v=dx/length*.04
    poly=Polygon([(x+u,z+v),(X+u,Z+v),(X-u,Z-v),(x-u,z-v)])
    prism(name+'_Base',poly,102.0,102.08,role='champagne_metal',category='guard_base')
    prism(name,poly,102.08,103.12,role=role,category='guard')
    prism(name+'_Cap',poly.buffer(.015,join_style=2),103.12,103.18,role='champagne_metal',category='guard')
    guards.append({'name':name,'a':a,'b':b})
guard('D17R_GuardNorth',[-62.96,14.06],[-60.06,14.06])
guard('D17R_GuardOuter',[-60.06,14.06],[-60.06,39.14])
guard('D17R_GuardEnd',[-60.06,39.14],[-62.94,39.14])
guard('D17R_GuardInnerFore',[-62.94,17.44],[-62.94,33.8])
guard('D17R_HeldRoom823',[-62.94,33.8],[-62.94,37.4],role='warm_walnut')
guard('D17R_GuardInnerAft',[-62.94,37.4],[-62.94,39.14])
guard('D17R_GuardVestSouth',[-66.98,17.44],[-62.94,17.44])
guard('D17R_GuardVestWest',[-67.04,14],[-67.04,17.44])
lights=[]
for i,(x,z)in enumerate([(-65,15.8),(-61.5,22),(-61.5,30),(-61.5,35.6)]):
    cube(f'D17R_LightHousing_{i}',[x-.16,105.84,z-.16],[x+.16,106.01,z+.16],category='light_fixture')
    cube(f'D17R_LightLens_{i}',[x-.13,105.82,z-.13],[x+.13,105.84,z+.13],role='opal_glow',category='light_fixture')
    lights.append({'name':f'D17R_LightLens_{i}','position':[x,105.82,z]})
models=json.load(open(R/'Game/data/architecture/STAR_ATLAS_UNITS.json'));recipe=next(p for p in models['prototypes']if p['key']=='SA_r001__standard__offset_index__R')
records=json.load(open(R/'BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json'))['records'];allocation=next(r for r in records if r['source_envelope_index']==823)
paths=['Game/data/architecture/STAR_ATLAS_UNITS.json','Game/data/architecture/STAR_ATLAS_UPPER_COMMONS.json','Game/data/architecture/D17_LUXURY_HOUSES_PROPOSAL.json','Game/data/architecture/CENTRAL_RESIDENTIAL_STREETS.json','Game/assets/models/STAR_ATLAS_UPPER_COMMONS_r001.glb','Game/assets/models/AST-DOR-002.glb','Game/scripts/guest_entry_door.gd','Game/scripts/service_door.gd','Game/data/architecture/cleaning_cart_contacts.json','Game/scripts/cleaning_cart.gd','BlenderCatalogue/assets/star_atlas_upper_commons_20261009/source/StarAtlasUpperCommons.blend','BlenderCatalogue/assets/star_atlas_upper_commons_20261009/PLAN.json','BlenderCatalogue/assets/guest_entry_door/source/AST-DOR-002.blend','BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json',recipe['editable_source'],'Game/assets/models/'+recipe['model_file'],'Game/docs/master_source/MASTER_CURRENT_APPLICATION.json','Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json','BlenderCatalogue/references/intimate/image(20261002-000722).png']
P={'schema':'astraea.d17_receiving.first.v1','base_commit':base,'parts':parts,'source_pins':{p:sha(R/p)for p in paths},'receiving_model':'STAR_ATLAS_D17_RECEIVING_FIRST_r001.glb','floor_geometry':mapping(floor),'new_floor_area_m2':floor.area,'piers':piers,'guards':guards,'lights':lights,'source_wall_replacements':['SA_D17_SouthWall_0','SA_D17_EastWall_1'],'commons_door':{'origin':[-65,102,14.13],'yaw':0,'persistent_id':'D17_standard_house_receiving_entry_candidate','model':'AST-DOR-002.glb'},'first_room':{'allocation':allocation,'recipe':recipe,'origin':[-63.05,102,35.6],'yaw':math.pi/2,'entry_recess_m':.175,'entry_receiver_cut_native_box':{'min':[-1.75,-.05,.025],'max':[1.75,.30,2.66]},'entry_receiver_shell_meshes':['SUI_EntryHeader','SUI_EntryJamb_-3.5','SUI_EntryJamb_0.8','SUI_BathInnerForward'],'shower_shift_west_m':.21,'bath_corner_shift_west_m':.30,'entry_origin':[-63.175,102,35.6],'bath_origin':[-65.95,102,36.3],'entry_yaw':math.pi/2,'bath_yaw':math.pi,'adopted':False,'rest_slots_unchanged':allocation['proposed_rest_slot_ids']},'new_units':0,'new_rest_places':0,'opposite_house_platform_used':False,'court_void_extended':False,'roof_max_y':106.5,'primary_engineering_load_accepted':False,'limits':['Explicit geometric source-to-pier/truss/hanger/frame contacts do not certify primary transfer/slab loads or cantilever sizing','First823 room entry fitting receives a contained native recess; its full interior/support/private garden/environment and final ordinary runtime/CRT/hardware acceptance remain unadopted','All other nine standard rooms and seven VIPs remain held; no completed Group1 claimed'],'master_review':{'complete_chapters':[5,6,7],'reference':paths[-1]}}
(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n');print(json.dumps({'parts':len(parts),'floor_area_m2':floor.area,'piers':len(piers),'source_pins':len(paths),'source_room':823}))
