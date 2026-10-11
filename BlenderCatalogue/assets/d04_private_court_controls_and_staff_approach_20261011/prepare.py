from pathlib import Path
import json,hashlib,copy
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[3];W=Path(__file__).resolve().parent;O=R/'BlenderCatalogue/assets/d04_port_forward_private_court_service_20261011';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();old=json.load(open(O/'RUNTIME_PLAN.json'));pins=dict(old['source_pins'])
for f in O.rglob('*'):
 if f.is_file():pins[str(f.relative_to(R))]=sha(f)
for f in ['Game/scripts/service_door.gd','Game/scripts/guest_entry_door.gd','Game/data/generated/structural_meshes.json','Game/data/spatial_layout.json','Game/assets/models/D04_STAFF_WALL_PORTAL_PATCH_r001.glb','Game/assets/models/AST-CIR-001_H450.glb','BlenderCatalogue/assets/circulation_architecture/source/AST-CIR-001_H450.blend','BlenderCatalogue/assets/group3_crew_service_20261009/source/CREW_BANK_PLACEMENTS_PROPOSAL.json','Game/data/architecture/CREW_HOME_APPROACH_RUNTIME.json']:
 pins[f]=sha(R/f)
ns={'__file__':str(W/'prepare.py')};s=(R/'BlenderCatalogue/assets/d04_port_forward_homes_second_20261010/prepare.py').read_text();exec(s[:s.index('from shapely import affinity')],ns);parts=ns['parts'];cube=ns['cube'];add=ns['add']
cube('D04SA_StaffJunctionGapFloor',[-55.2,11.76,-450],[-54,12,-446],role='warm_stone',category='link_floor')
for i,z in enumerate([-449.65,-446.35]):cube('D04SA_GapBearer_'+str(i),[-55.55,11.6,z-.1],[-53.65,11.76,z+.1],category='link_bearer')
for i,(z,Z)in enumerate([(-450,-449.86),(-448.07,-447.93),(-446.14,-446)]):cube('D04SA_ServiceLaneScreen_'+str(i),[-54,12,z],[-33,13.15,Z],role='ivory_enamel',category='service_lane_screen')
for i,(x,z)in enumerate([(-51,-449.86),(-42,-449.86),(-34,-449.86)]):
 cube('D04SA_WorkBulbHousing_'+str(i),[x-.3,13.15,z-.03],[x+.3,13.27,z+.17],category='light_source');cube('D04SA_WorkBulbLens_'+str(i),[x-.25,13.19,z+.17],[x+.25,13.23,z+.19],role='opal_glow',category='light_source')
cube('D04SA_UpperCourtLanding',[-29.5,16.26,-447.5],[-27,16.5,-445.2],role='warm_stone',category='upper_landing')
for i,(x,z)in enumerate([(-29.3,-447.3),(-27.2,-447.3),(-29.3,-445.4),(-27.2,-445.4)]):cube('D04SA_UpperLandingPier_'+str(i),[x-.09,12,z-.09],[x+.09,16.26,z+.09])
for i,(x,X)in enumerate([(-29.5,-29.38),(-27.12,-27)]):cube('D04SA_UpperEdge_'+str(i),[x,16.5,-447.5],[X,17.65,-445.2],role='ivory_enamel',category='edge_guard')
offset=[31.8,0,-76.7]
base=json.load(open(R/'BlenderCatalogue/assets/d04_port_forward_receiving_20261010/PLAN.json'))
for q in base['parts']:
 if q['category']=='stair_walk_surface':
  q=copy.deepcopy(q);q['name']=q['name'].replace('D04PF_','D04SA_');q['verts']=[[v[i]+offset[i]for i in range(3)]for v in q['verts']];parts.append(q)
cube('D04SA_LowerStairApproach',[-34,11.76,-447.5],[-30.5,12,-445.8],role='warm_stone',category='lower_landing')
regions=json.load(open(R/'Game/data/generated/structural_meshes.json'))['regions'];cover=next(q for q in regions if q['id']=='D03_protected_crew_cover');floor=unary_union([Polygon(r)for r in cover['rings']]);route=box(-54,-450,-33,-446);assert floor.covers(route)
crew=json.load(open(R/'BlenderCatalogue/assets/group3_crew_service_20261009/source/CREW_BANK_PLACEMENTS_PROPOSAL.json'))['instances']
envelope=box(-55.2,-458,-27,-445.2);conflicts=[]
for q in crew:
 e=q['source_envelope'];area=envelope.intersection(box(e['x'][0],e['z'][0],e['x'][1],e['z'][1])).area
 if area>1e-8:conflicts.append(q['allocation_key'])
assert not conflicts
upper=box(-33,-458,-27,-445.2)
for u in old['all_twenty_allocations_unchanged']:assert upper.intersection(box(u['allocation_x'][0],u['allocation_z'][0],u['allocation_x'][1],u['allocation_z'][1])).area<1e-8
plan={'schema':'astraea.d04.staff_approach_and_court_controls.v1','base_commit':'3ff3c85dc172547972ad0738779965f49b6bd0ca','production_active':False,'source_pins':pins,'parts':parts,'stair':{'source':base['stair']['source'],'origin':[-33,12,-447.5],'yaw':0,'model':base['stair']['model'],'rigid_source_not_scaled':True},'source_fittings':[],'gates':old['gates'],'court_candidate_model':old['structure'],'all_twenty_allocations_unchanged':old['all_twenty_allocations_unchanged'],'lanes':[{'purpose':'clean_supply','center_z':-447.0,'x':[-54,-34],'floor_y':12,'existing_floor_owner':'D03_protected_crew_cover'},{'purpose':'closed_used_items','center_z':-449.0,'x':[-54,-34],'floor_y':12,'existing_floor_owner':'D03_protected_crew_cover'}],'new_floor_scope':{'staff_gap_m2':4.8,'upper_landing_m2':5.75,'lower_stair_approach_m2':5.95,'staff_lane_floor_m2':0,'walking_stair_source_landings_not_area_credit':True},'staff_wall_junction_held':{'at':[-55.2,12,-448],'current_source':'D04_STAFF_WALL_PORTAL_PATCH_r001.glb','exact_cut_not_authorized_by_geometry_audit':True,'production_wall_unchanged':True},'court_south_threshold_held':{'name':'D04HC3_east_End_0','at':[-28.1,16.5,-445.2],'production_wall_unchanged':True},'narrow_west_lightwell_solution':{'scope':'Reach-only through home-side service sashes, following retained common-garden sash precedent; no worker floor in0.75m lightwell','held':'Consent/vacancy plus exact pane/planter reach and full moving-contact checks required before authoring/activation','planters_and_home_outlooks_unchanged':True},'limits':['Sealed native approach on existing floor; both wall junctions unchanged until exact preimage/controller gates','Separated screened clean/closed-used horizontal lanes; stair/landing circulation is shared and traffic/carry/cart operation unaccepted','Explicit temporary court visits in tests; no production occupancy/consent provider, guest authorization or persistence invented','Original homes/courts/crew approach/staff source unchanged; lightwell remains reach-only','No full commons, network, maintenance task, primary engineering, ordinary-game/CRT/hardware completion']}
assert not(W/'PLAN.json').exists();(W/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');(W/'PREIMAGE_SUPPORT.json').write_text(json.dumps({'status':'PASS','source_floor_owner':cover['id'],'staff_lane_floor_m2':0,'crew_allocation_conflicts':conflicts,'all20_home_allocation_overlap_m2':0,'junctions_remain_sealed':True,'protected_pins':len(pins)},indent=2)+'\n');print('STAFF_APPROACH_PLAN',len(parts),len(pins))
