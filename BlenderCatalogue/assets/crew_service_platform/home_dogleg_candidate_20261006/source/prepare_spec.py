"""Pure authored home approach specification. No Blender, import or shared write."""
from pathlib import Path
import json,hashlib,math,sys
ROOT=Path(__file__).resolve().parents[1];C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');G=Path('/workspace/shared/astraea-godot-production-20261003')
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,x):(ROOT/'source'/name).write_text(json.dumps(x,indent=2)+'\n')
full=read(C/'catalogue_manifest.json');found={}
def scan(v):
 if isinstance(v,dict):
  if v.get('catalogue_id')in['AST-STF-008','AST-STF-010']:found[v['catalogue_id']]=v
  for x in v.values():scan(x)
 elif isinstance(v,list):
  for x in v:scan(x)
scan(full);assert found['AST-STF-008']['family']=='staff_threshold'and found['AST-STF-010']['family']=='crew_service_platform'
parts=read(C/'assets/crew_service_platform/source/geometry_parts.json');home_names=read(Path('/workspace/scratch/375c2e438292/crew-service-next-scope-20261006/HOME_INTERFACE_RECORDS.json'))['home_part_names'];home=[p for p in parts if p['name']in home_names];assert len(home)==85
pins={}
for p in [C/'catalogue_manifest.json',C/'assets/crew_service_platform/source/AST-STF-010.blend',C/'assets/crew_service_platform/source/geometry_parts.json',C/'assets/grand_pool_orchard_section/source/AST-STF-009_pool_market.blend',C/'assets/grand_pool_orchard_section/exports/AST-STF-009_pool_market.glb',C/'assets/lower_staff_network/source/geometry_parts.json',C/'assets/staff_threshold/source/build_service_door.py',C/'materials/staff/manifest.json',G/'data/spatial_layout.json',G/'data/generated/structural_meshes.json']:
 pins[str(p)]=sha(p)
for p in(C/'materials/staff').glob('*.png'):pins[str(p)]=sha(p)
assert pins[str(C/'assets/crew_service_platform/source/AST-STF-010.blend')]=='4bbc808742d7f09ca23c35f6f61ff7824c9b1f54d0f02fb360292049086913c9'
assert pins[str(C/'assets/grand_pool_orchard_section/source/AST-STF-009_pool_market.blend')]=='8e5e89ffc98e2dab8ac54a3266632d00ecfc1be8a1de5670b41e0726650ea5c6'
# Retained four-part wall opening: split only the authored source solids.
old=read(C/'assets/lower_staff_network/source/geometry_parts.json')['boxes'];names=['STF_D03_Wall_00_13_00_'+x for x in ['Wainscot','Enamel','CartBumper','PanelJoint']];opening=[]
for name in names:
 p=next(x for x in old if x['name']==name);x0,x1,y0,y1,z0,z1=p['world_aabb'];replacements=[]
 for a,b in[(z0,min(z1,-433.8)),(max(z0,-430.2),z1)]:
  if b>a:replacements.append([x0,x1,y0,y1,a,b])
 a,b=max(z0,-433.8),min(z1,-430.2)
 if b>a and y1>14.65:replacements.append([x0,x1,max(y0,14.65),y1,a,b])
 opening.append({'original_name':name,'original_aabb':p['world_aabb'],'role':p['role'],'replacement_boxes':replacements})
assert sum(len(p['replacement_boxes'])for p in opening)==8
new=[]
def prism(name,profile,depth,role,parent='STATIC'):
 new.append({'name':name,'shape':'door_prism','profile_x_y':profile,'depth_z':depth,'role':role,'parent':parent,'collision_contract':'static_surface'if parent=='STATIC'else'kinematic_source_part'})
def box(name,bounds,role,parent='STATIC',collision='static_surface'):
 new.append({'name':name,'shape':'world_box','world_aabb':bounds,'role':role,'parent':parent,'collision_contract':collision})
prism('HOME_Jamb_Left',[[-1.94,0],[-1.8,0],[-1.8,2.65],[-1.75,2.72],[-1.88,2.82],[-1.94,2.70]],[-.18,.18],'staff_bluegrey_paint')
prism('HOME_Jamb_Right',[[1.8,0],[1.94,0],[1.94,2.70],[1.88,2.82],[1.75,2.72],[1.8,2.65]],[-.18,.18],'staff_bluegrey_paint')
prism('HOME_Header',[[-1.94,2.70],[-1.8,2.65],[-1.75,2.72],[1.75,2.72],[1.8,2.65],[1.94,2.70],[1.94,2.86],[-1.94,2.86]],[-.18,.18],'staff_bluegrey_paint')
for side,sign in [('LEFT',1),('RIGHT',-1)]:
 lo,hi=(.01,1.74)if sign==1 else(-1.74,-.01);parent='HOME_HINGE_'+side
 prism('HOME_Leaf_'+side,[[lo,.025],[hi,.025],[hi,2.615],[lo,2.615]],[-.035,.035],'staff_white_paint',parent)
 prism('HOME_Kick_'+side,[[lo+.06,.12],[hi-.06,.12],[hi-.06,.48],[lo+.06,.48]],[.036,.043],'staff_zinc',parent)
 h=hi-.19 if sign==1 else lo+.19
 prism('HOME_Push_'+side,[[h-.065,.98],[h+.065,.98],[h+.065,1.40],[h-.065,1.40]],[.042,.066],'staff_rubber',parent)
 prism('HOME_Identifier_'+side,[[lo+.18,1.73],[hi-.18,1.73],[hi-.18,1.91],[lo+.18,1.91]],[.036,.039],'staff_label',parent)
 if side=='LEFT':prism('HOME_Meeting_Seal',[[1.73,.03],[1.77,.03],[1.77,2.61],[1.73,2.61]],[-.043,-.035],'staff_rubber',parent)
# Front-side stop strips cover the side clearance without entering the rear swing.
for side,a,b in[('LEFT',-1.805,-1.73),('RIGHT',1.73,1.805)]:
 prism('HOME_Stop_'+side,[[a,.025],[b,.025],[b,2.615],[a,2.615]],[.038,.06],'staff_rubber')
prism('HOME_Stop_Top',[[-1.805,2.612],[1.805,2.612],[1.805,2.658],[-1.805,2.658]],[.038,.06],'staff_rubber')
# Two exact retained task housings, translated only; new emitter markers sit15mm
# below the real lower opal face, rather than inside opaque source material.
fixture_donor=[p for p in parts if p['name'].startswith('CRW_Task_0_0_')];assert len(fixture_donor)==4
fixtures=[]
for i,(x,z)in enumerate([(-45.2,-431.4),(-45.2,-424.8)]):
 fixtures.append({'name':f'HOME_TASK_{i+1}','donor_part_names':[p['name']for p in fixture_donor],'translation_godot_xyz':[x+57,0,z+210],'emitter_xyz':[x,15.0,z],'direction_xyz':[0,-1,0],'source_lowest_y':15.015,'source_cap_underside_y':15.2,'runtime_light_accepted':False})
# Backed wayfinding and recessed maintenance detail, outside the lower clear lane.
box('HOME_Header_Plate',[-48.137,-48.12,14.9,15.13,-433.5,-430.5],'staff_label')
box('HOME_Junction_Box',[-50.15,-49.85,14.84,15.2,-433.79,-433.53],'staff_zinc')
box('HOME_Maintenance_Panel',[-47.031,-47.022,13.2,14.0,-428.8,-428.1],'staff_zinc')
# Explicit supported overhead service route and short fixture feeds. Round meshes
# are generated later from these measured centre lines; no empty decorative wires.
utilities=[{'name':'HOME_Service_Trunk','points_xyz':[[-50,15.13,-433.65],[-46.65,15.13,-433.65],[-46.65,15.13,-423.65],[-39.5,15.13,-423.65]],'radius_m':.018,'role':'staff_zinc'}]
for i,f in enumerate(fixtures):
 x,y,z=f['emitter_xyz'];utilities.append({'name':f'HOME_Fixture_Feed_{i+1}','points_xyz':[[-46.65,15.146,z],[x-.5,15.146,z],[x-.5,15.14,z]],'radius_m':.008,'role':'staff_rubber'})
labels=[{'name':'HOME_Header_Text','text':'CREW LIVING / QUIET APPROACH','position_xyz':[-48.139,15.015,-432],'normal_xyz':[-1,0,0],'width_m':2.8,'height_m':.12,'backing':'HOME_Header_Plate'},{'name':'HOME_Service_Directions','text':'DEPOT / SERVICE\nRETURN TO STREET','position_xyz':[-47.019,13.62,-428.45],'normal_xyz':[1,0,0],'width_m':.60,'height_m':.042,'backing':'HOME_Maintenance_Panel'}]
labels.extend([{'name':'HOME_Leaf_Text_Left','text':'CREW LIVING','position_xyz':[.875,1.82,.042],'normal_xyz':[0,0,1],'width_m':1.20,'height_m':.085,'backing':'HOME_Identifier_LEFT','parent':'HOME_HINGE_LEFT'},{'name':'HOME_Leaf_Text_Right','text':'QUIET PLEASE','position_xyz':[-.875,1.82,.042],'normal_xyz':[0,0,1],'width_m':1.20,'height_m':.085,'backing':'HOME_Identifier_RIGHT','parent':'HOME_HINGE_RIGHT'}])
spec={'schema':1,'status':'PURE_AUTHORED_CANDIDATE_NOT_BUILT','derivative_id':'AST-STF-010_home_dogleg','preserved_source_family':'AST-STF-010','new_catalogue_design_count':0,'new_floor_owner_count':0,'floor_y':12,'preserve_floor_owners':['D03_protected_crew_cover','D03_port_forward_staff_floor_0','D03_secondary_engineering_cap'],'retained_home_parts':home,'retained_home_part_count':85,'door':{'derived_family':'AST-STF-008','root_xyz':[-48.06,12,-432],'yaw_radians':-math.pi/2,'clear_reservation_width_m':3.6,'clear_reservation_height_m':2.65,'hinge_local_x':[-1.75,1.75],'leaf_angle_interval_degrees':[0,90],'functional_owner':'Unchanged service_door.gd state/interact/pause/motion. Local source-fitting initialization and actual sweep bounds only.','persistent_id_proposal':'D03_home_service_entry_001','original_door_not_scaled':True},'new_parts':new,'fixtures':fixtures,'utility_paths':utilities,'labels':labels,'wall_opening':opening,'route_xz':[[-57,-432],[-51,-432],[-45.2,-432],[-45.2,-424.8],[-41,-424.8]],'cart_policy':'Park in retained6m receiving vestibule; no loaded cart enters the3.6m dogleg','privacy':'Opaque dogleg plus proposed staff door; no occupied home, acoustic or pressure certification','first_pass_accepted':False,'runtime_adopted':False,'source_build_or_render_run':False}
save('HOME_SPEC.json',spec);save('INPUT_PINS.json',pins);print(json.dumps({'retained_home_parts':85,'door_and_static_new_parts':len(new),'translated_fixture_parts':8,'utility_paths':len(utilities),'wall_parts_replaced':4,'replacement_wall_parts':8,'new_floor_owners':0,'status':'Pure specification only'},indent=2))
