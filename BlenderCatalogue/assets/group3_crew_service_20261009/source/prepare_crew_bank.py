"""Source-only construction proposal. Never writes Game or registers people."""
from pathlib import Path
import json, hashlib, math, sys
sys.path.insert(0, '/workspace/shared/astraea_python_deps')
import shapely
from shapely.geometry import box, Polygon
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
GAME = ROOT / 'Game'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest = json.loads((ROOT / 'BlenderCatalogue/catalogue_manifest.json').read_text())
assert not any(r['catalogue_id'] == 'AST-CRW-G3-001' for r in manifest['assets']), 'Catalogue ID has another owner'
parts = []
def cube(name, x0, x1, y0, y1, z0, z1, role='staff_white_paint', category='architecture'):
    assert x1 > x0 and y1 > y0 and z1 > z0
    parts.append({'name':name, 'aabb':[x0,x1,y0,y1,z0,z1], 'role':role, 'category':category})

# Canonical 12 x 9.5 m allocation. All shell thickness stays inside it.
# Entry is on +X, centered Z=0. Sleep is quiet and offset from the threshold.
for name, b in [('Rear',[-6,-5.84,-4.75,4.75]),('North',[-5.84,6,-4.75,-4.59]),('South',[-5.84,6,4.59,4.75]),('EntryNorth',[5.84,6,-4.59,-1.4]),('EntrySouth',[5.84,6,1.4,4.59])]:
    x0,x1,z0,z1=b
    cube('WallLow_'+name,x0,x1,0,1.02,z0,z1,'staff_bluegrey_paint')
    cube('WallHigh_'+name,x0,x1,1.02,3.2,z0,z1)
cube('EntryLintel',5.84,6,2.8,3.2,-1.4,1.4)
cube('Ceiling',-6,6,3.2,3.34,-4.75,4.75,'staff_bluegrey_paint')
for z in [-3.85,0,3.85]:
    cube('RoofRib_'+str(z),-5.84,5.84,3.05,3.2,z-.06,z+.06,'staff_zinc')
# Deep sleeping alcoves and low serviceable overhead, independent curtains.
for side,z0,z1 in [('A',-4.59,-1.05),('B',1.05,4.59)]:
    cube('SleepAlcoveReturn_'+side,-5.84,-1.15,0,2.4,(z1-.14 if side=='A' else z0),(z1 if side=='A' else z0+.14))
    cube('SleepAlcoveHeadPanel_'+side,-4.2,-1.5,1.22,2.55,(-4.59 if side=='A' else 4.45),(-4.45 if side=='A' else 4.59),'staff_bluegrey_paint')
    cube('SleepAlcoveSoffit_'+side,-5.84,-1.15,2.6,2.74,z0,z1,'staff_bluegrey_paint')
# Wash/change room is a real enclosed annex, with clear south-facing doorway.
cube('WashWest',1.0,1.14,0,3.05,-4.59,-1.5)
cube('WashNorth',1.14,2.8,0,3.05,-1.64,-1.5)
cube('WashNorthReturn',4.2,5.84,0,3.05,-1.64,-1.5)
cube('WashDoorLintel',2.8,4.2,2.55,3.05,-1.64,-1.5)
cube('ChangeScreen',1.7,1.84,0,2.35,-4.0,-2.4)
cube('ShowerRear',2.05,3.55,0,2.45,-4.4,-4.28)
cube('ShowerSide',2.05,2.17,0,2.45,-4.28,-2.9)
# Thin raised shower pan, with declared bounded sill and no slab duplication.
cube('ShowerPan',2.05,3.55,0,.045,-4.28,-2.9,'staff_floor','fixture')
cube('ShowerDrain',2.69,2.91,.045,.047,-3.67,-3.45,'staff_zinc','fixture')
cube('ShowerRail',2.73,2.79,.7,2.15,-4.25,-4.18,'staff_zinc','fixture')
cube('ShowerHeadArm',2.73,2.79,2.09,2.15,-4.18,-3.85,'staff_zinc','fixture')
cube('ShowerHead',2.61,2.91,2.02,2.09,-4.02,-3.77,'staff_zinc','fixture')
cube('ShowerControl',3.05,3.28,1.05,1.18,-4.23,-4.17,'staff_zinc','fixture')
# Separate toilet compartment: split entrance and rear cistern support.
cube('ToiletScreen',3.8,3.94,0,2.35,-4.3,-2.5)
cube('ToiletPlinth',4.55,5.12,0,.36,-4.2,-3.45,'staff_white_paint','fixture')
cube('ToiletRear',4.53,5.14,.36,.91,-4.38,-4.18,'staff_white_paint','fixture')
for name,b in [('SeatL',[4.5,4.62,-4.2,-3.4]),('SeatR',[5.06,5.18,-4.2,-3.4]),('SeatBack',[4.62,5.06,-4.2,-4.08]),('SeatFront',[4.62,5.06,-3.52,-3.4])]:
    cube('Toilet_'+name,b[0],b[1],.36,.42,b[2],b[3],'staff_white_paint','fixture')
cube('BasinCabinet',4.8,5.5,0,.75,-2.55,-1.82,'staff_bluegrey_paint','fixture')
cube('BasinBase',4.76,5.54,.75,.81,-2.6,-1.78,'staff_white_paint','fixture')
for name,b in [('L',[4.76,4.86,-2.6,-1.78]),('R',[5.44,5.54,-2.6,-1.78]),('Back',[4.86,5.44,-2.6,-2.5]),('Front',[4.86,5.44,-1.88,-1.78])]:
    cube('BasinRim_'+name,b[0],b[1],.81,.96,b[2],b[3],'staff_white_paint','fixture')
cube('BasinTap',5.1,5.16,.96,1.18,-2.48,-2.42,'staff_zinc','fixture')
cube('BasinSpout',5.1,5.16,1.12,1.18,-2.42,-2.16,'staff_zinc','fixture')
# Activity edge deliberately faces inward; no unverified exterior window.
cube('DeskTop',1.75,4.25,.73,.81,3.76,4.4,'staff_white_paint','furniture')
for x in [1.83,4.07]: cube('DeskLeg_'+str(x),x,x+.1,0,.73,3.85,4.26,'staff_zinc','furniture')
cube('SeatBase',1.9,4.1,0,.42,2.72,3.28,'staff_bluegrey_paint','furniture')
cube('SeatPad',1.87,4.13,.42,.52,2.7,3.3,'staff_rubber','furniture')
cube('SeatBack',1.9,4.1,.52,1.12,2.7,2.8,'staff_bluegrey_paint','furniture')
cube('LinenShelfBack',4.84,5.5,.15,2.15,3.88,4.48,'staff_bluegrey_paint','furniture')
for i,y in enumerate([.22,.8,1.38,1.96]): cube('LinenShelf_'+str(i),4.84,5.5,y,y+.055,3.35,3.88,'staff_white_paint','furniture')
fixtures = []
for i,(x,z) in enumerate([(3.4,0),(3.2,-2.2),(2.9,3.55)]):
    cube('LightHousing_'+str(i),x-.45,x+.45,2.99,3.05,z-.13,z+.13,'staff_zinc','lighting_fixture')
    cube('LightDiffuser_'+str(i),x-.4,x+.4,2.96,2.99,z-.1,z+.1,'staff_opal','lighting_fixture')
    fixtures.append({'name':'CeilingLight'+str(i),'position':[x,2.94,z],'color':[.8,.88,1],'range_m':4.5,'energy':.85,'budget_owner':'existing receiving_source_lights.gd / lighting_budget.gd'})
for p in parts:
    if p['name']=='Ceiling' or p['name'].startswith(('RoofRib_','SleepAlcoveSoffit_')):p['category']='overhead'

beds = [{'local_place':'A','position':[-2.9,0,-1.8],'yaw':0,'rest_surface':[0,.565,-.9],'curtain_position':[-2.9,0,-1.8],'curtain_yaw':0}, {'local_place':'B','position':[-2.9,0,1.8],'yaw':math.pi,'rest_surface':[0,.565,-.9],'curtain_position':[-2.9,0,4.0],'curtain_yaw':0}]
dependencies = []
for family,filename in [('crew_rest','AST-CRW-001.glb'),('crew_rest','AST-CRW-002.glb'),('crew_personal','AST-CRW-003.glb'),('crew_personal','AST-CRW-004.glb')]:
    p=ROOT/'BlenderCatalogue/assets'/family/'exports'/filename
    dependencies.append({'path':str(p.relative_to(ROOT)), 'sha256':sha(p),'copy_required':False})
spec={'schema':1,'catalogue_id':'AST-CRW-G3-001','family':'group3_crew_service_20261009','coordinate_system':'Canonical Godot metres; floor-local Y=0, entry +X','allocation_dimensions_xz':[12,9.5],'ceiling_underside_m':3.2,'shell_floor_exported':False,'parts':parts,'beds':beds,'storage':[{'position':[-5.2,0,-2.0],'yaw':0},{'position':[-5.2,0,2.0],'yaw':math.pi}],'fixtures':fixtures,'dependencies':dependencies,'capacity_state':'Two physical dry-support positions; zero registered berths or occupants. Species allocation remains open.','interaction_dependencies':['Existing residential_suite.gd doors only','Existing static_contact_cache.gd contacts','Existing receiving_source_lights.gd and lighting_budget.gd'],'door_proposals':[{'role':'entry','position':[5.92,0,0],'yaw':math.pi/2,'width_m':2.8,'height_m':2.8},{'role':'wash_privacy','position':[3.5,0,-1.57],'yaw':0,'width_m':1.4,'height_m':2.55}],'unfinished':['All six-species body/pose fit','Live fixture and curtain/storage controls','Wet and waste operation','Main-scene visual, floor, collision and door acceptance']}
(HERE/'source/CREW_BANK_HOME.json').write_text(json.dumps(spec,indent=2)+'\n')

records=json.loads((GAME/'data/reference/D03_crew_envelopes.json').read_text())['records']
spatial=json.loads((GAME/'data/spatial_layout.json').read_text())
compiled=json.loads((GAME/'data/generated/structural_meshes.json').read_text())
floor_union=unary_union([Polygon(t) for r in compiled['regions'] if r['deck']=='D03' for t in r['triangles']])
instances=[];floor_proposals=[];porches=[]
for index,r in enumerate(records):
    x=sum(r['x'])/2;z=sum(r['z'])/2
    yaw=math.pi if x in [-72,100] else 0
    candidate=f'C{index+1:03d}'
    confirmed=118<=index+1<=125 or 168<=index+1<=175
    q={'allocation_key':f'D03_crew_atlas_drawing_{r["drawing_index"]}','source_drawing_index':r['drawing_index'],'position':[x,12,z],'yaw':yaw,'source_envelope':{'x':r['x'],'z':r['z']},'proposed_retained_room_id':candidate,'identity_join_status':'exact_labelled_atlas_detail' if confirmed else 'inferred_sequence_needs_root_review','physical_rest_places':0 if index==35 else 2,'registered_berth_keys':None,'assigned_people':None,'template':'AST-CRW-G3-001','default_scene_adopted':False}
    if index==35:q['hold']='Proposed C036 retains room identity with zero rests only after existing singleton key is bound to installed shared home. No migration applied.'
    instances.append(q)
    floor_proposals.append(box(r['x'][0],r['z'][0],r['x'][1],r['z'][1]))
    sign=-1 if yaw else 1
    door=x+sign*6; hall=math.copysign(86,x)
    p=box(min(door,hall),z-1.8,max(door,hall),z+1.8);porches.append(p)

route=json.loads((GAME/'data/architecture/packages/crew_living/CONNECTOR_AND_DETOUR_REVIEW.json').read_text())
routes=[Polygon(p['boundary'],p['holes'])for p in route['staff_route_union_polygons']]
all_requested=unary_union(floor_proposals+[unary_union(porches+routes).buffer(.14,join_style=2)])
missing=all_requested.difference(floor_union)
def polygons(g):
    return [{'boundary':list(p.exterior.coords)[:-1],'holes':[list(r.coords)[:-1]for r in p.interiors]} for p in shapely.get_parts(g) if p.area>1e-7]
pins={str(p.relative_to(ROOT)):sha(p) for p in [GAME/'data/reference/D03_crew_envelopes.json',GAME/'data/reference/historical_atlas.pdf',GAME/'docs/master_source/MASTER_CURRENT_APPLICATION.json',GAME/'docs/master_source/MASTER_FULL_CONTENT_INDEX.json',GAME/'data/spatial_layout.json',GAME/'data/generated/structural_meshes.json',GAME/'data/architecture/SHARED_CREW_HOME.json',GAME/'scripts/shared_crew_home.gd',GAME/'assets/models/crew_home/SharedCrewHome.glb',GAME/'data/architecture/packages/crew_living/CONNECTOR_AND_DETOUR_REVIEW.json']}
batch={'schema':1,'scope':'Source construction proposal, not a room/population registry','source_pins':pins,'instances':instances,'preserved_shared_home':{'identity':'D03_employee_cabin0','physical_rest_places':2,'modified':False,'proposed_colleague_source_room':'C036','existing_keys_recovered':False,'migration_applied':False},'physical_rest_proposal':{'ordinary_bank':398,'installed_shared_home':2,'total':400,'registered_new_keys':0},'identity_gate':'16 exact labelled joins,184 proposed order joins. Concrete original berth/person keys absent. Do not create or renumber them from this source.','floor_proposal':{'floor_y':12,'thickness':.24,'requested_area_m2':all_requested.area,'missing_only_area_m2':missing.area,'existing_floor_overlap_retained_m2':all_requested.intersection(floor_union).area,'polygons':polygons(missing),'no_exported_floor':True},'porches':polygons(unary_union(porches)),'route_polygons':polygons(unary_union(routes)),'dependencies':dependencies,'unfinished':['Root review of proposed184 ID joins and C036 binding','Missing-only compiled floors and main-scene registration','Door/porch/screen receiving and contacts','Service risers and clinical clean/soiled joins','Species-specific rest fit without invented demographic quotas','Final visual, wet-operation and persistent occupancy acceptance']}
(HERE/'source/CREW_BANK_PLACEMENTS_PROPOSAL.json').write_text(json.dumps(batch,indent=2)+'\n')
print(json.dumps({'parts':len(parts),'homes':len(instances),'physical_rests_proposed':398,'exact_labelled_id_joins':16,'missing_floor_m2':missing.area,'shell_exported_floor':False}))
