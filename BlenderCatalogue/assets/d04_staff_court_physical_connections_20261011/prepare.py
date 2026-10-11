from pathlib import Path
import json,hashlib,copy,numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
W=Path(__file__).resolve().parent;R=W.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=R/'BlenderCatalogue/assets/d04_private_court_controls_and_staff_approach_20261011'
old=json.load(open(prior/'RUNTIME_PLAN.json'));pins=dict(old['source_pins'])
for f in prior.rglob('*'):
 if f.is_file():pins[str(f.relative_to(R))]=sha(f)
reader=R/'BlenderCatalogue/assets/forward_staff_shaft_interfaces_20261010/source_geometry.py';ns={'__file__':str(reader)};exec(reader.read_text(),ns);T=ns['triangles']
helpers=R/'BlenderCatalogue/assets/d04_port_forward_homes_second_20261010/prepare.py';ns2={'__file__':str(helpers)};s=helpers.read_text();exec(s[:s.index('from shapely import affinity')],ns2);parts=ns2['parts'];cube=ns2['cube'];prism=ns2['prism']
staff_model='AST-STF-009_pool_market_home_equipment.glb';staff_names=['HOME_BATCH_007_ASTRAEA_staff_bluegrey_paint','HOME_BATCH_174_ASTRAEA_staff_white_paint','HOME_BATCH_124_ASTRAEA_staff_rubber']
cuts=[]
def cut(model,name,volumes,kind):
 triangles=dict(T(model))[name];verts=triangles.reshape(-1,3);bounds=[verts.min(0).tolist(),verts.max(0).tolist()]
 cuts.append({'source_model':model,'name':name,'source_triangles_sha256':hashlib.sha256(triangles.tobytes()).hexdigest(),'source_triangle_count':len(triangles),'bounds':bounds,'volumes':volumes,'kind':kind})
 pins['Game/assets/models/'+model]=sha(R/'Game/assets/models'/model)
volumes=[{'min':[-55.4,12,z0],'max':[-55.19,14.7,z1]}for z0,z1 in[(-449.86,-448.07),(-447.93,-446.14)]]
for n in staff_names:cut(staff_model,n,volumes,'staff_wall')
court=json.load(open(R/'Game/data/architecture/D04_PORT_FORWARD_HOMES_THIRD.json'))
cut(court['structure']['model_file'],'D04HC3_east_End_0',[{'min':[-28.7,16.5,-445.30],'max':[-27.5,19.2,-445.10]}],'court_end')
homes=json.load(open(R/'Game/data/architecture/D04_PORT_FORWARD_HOMES_SECOND.json'))
hatch_ranges={928:[(-429.55,-428.3),(-425.45,-424.05)],952:[(-436.65,-435.4),(-433,-431.75)]}
for room in homes['rooms']:
 if room['source_index']in hatch_ranges:
  idx=room['source_index'];cut(room['model_file'],f'D04H{idx}_GardenDado',[{'min':[-58.951,16.5,a],'max':[-58.769,17.65,b]}for a,b in hatch_ranges[idx]],'home_low_hatch')
for i,z in [(0,[-450,-449.86]),(2,[-446.14,-446])]:cut(old['structure']['model_file'],f'D04SA_ServiceLaneScreen_{i}',[{'min':[-35.7,12,z[0]-.001],'max':[-32.99,13.151,z[1]+.001]}],'owned_bay_entry')
gates=[]
def fitting(name,lo,hi,pivot,angle,private,normal):
 before=len(parts);cube(name+'_Leaf',lo,hi,role='ivory_enamel',category='moving_leaf')
 # Two face handles keep normal controls reachable after the leaf rotates.
 if abs(hi[0]-lo[0])<.1:
  for side,x in [('Home',hi[0]),('Outer',lo[0]-.055)]:cube(name+'_Handle_'+side,[x,lo[1]+.64,hi[2]-.25],[x+.055,lo[1]+.82,hi[2]-.09],category='moving_handle')
  ctl=[hi[0]+.07,lo[1]+min(1.35,(hi[1]-lo[1])-.12),hi[2]-.025]
  cube(name+'_Control',[hi[0]+.015,ctl[1]-.1,hi[2]-.035],[hi[0]+.075,ctl[1]+.1,hi[2]],category='fixed_control')
 else:
  for side,z in [('North',hi[2]),('South',lo[2]-.055)]:cube(name+'_Handle_'+side,[hi[0]-.25,lo[1]+1.1,z],[hi[0]-.09,lo[1]+1.3,z+.055],category='moving_handle')
  ctl=[hi[0]-.015,lo[1]+1.35,lo[2]-.085]
  cube(name+'_Control',[hi[0]-.1,ctl[1]-.1,lo[2]-.09],[hi[0]+.04,ctl[1]+.1,lo[2]-.025],category='fixed_control')
 members=[p['name']for p in parts[before:]if p['category'].startswith('moving')];controls=[p['name']for p in parts[before:]if p['category']=='fixed_control']
 gates.append({'name':name,'id':name,'pivot':pivot,'candidate_open_degrees':angle,'requires_visit':private,'private_side_normal':normal,'closed_center':[(a+b)/2 for a,b in zip(lo,hi)],'leaf_min':lo,'leaf_max':hi,'members':members,'control_members':controls,'control_at':ctl})
for purpose,z0,z1 in [('Used',-449.86,-448.07),('Clean',-447.93,-446.14)]:
 fitting('D04PC_Staff'+purpose,[-55.16,12.02,z0+.02],[-55.10,14.68,z1-.02],[-55.10,12,z0+.02],90,False,[1,0,0])
 for j,(a,b)in enumerate([(z0,z0+.02),(z1-.02,z1)]):cube('D04PC_Staff'+purpose+'_Jamb_'+str(j),[-55.2,12,a],[-55.10,14.7,b],category='fixed_control_frame')
 gates[-1]['control_members']+=['D04PC_Staff'+purpose+'_Jamb_1'];gates[-1]['control_at']=[-55.09,13.35,z1-.012]
fitting('D04PC_CourtSouth',[-28.68,16.52,-445.37],[-27.52,19.18,-445.31],[-28.68,16.5,-445.37],90,True,[0,0,1])
for i,(x,X)in enumerate([(-28.7,-28.68),(-27.52,-27.5)]):cube('D04PC_CourtSouth_Jamb_'+str(i),[x,16.5,-445.4],[X,19.2,-445.11],category='fixed_control_frame')
gates[-1]['control_members'].append('D04PC_CourtSouth_Jamb_1')
for idx,ranges in hatch_ranges.items():
 for j,(a,b)in enumerate(ranges):
  name=f'D04PC_Hatch_{idx}_{j}';fitting(name,[-58.76,16.52,a+.02],[-58.70,17.63,b-.02],[-58.70,16.5,a+.02],90,True,[1,0,0])
  for k,(z,Z)in enumerate([(a,a+.02),(b-.02,b)]):cube(name+'_Jamb_'+str(k),[-58.95,16.5,z],[-58.70,17.65,Z],role='warm_walnut',category='fixed_control_frame')
  gates[-1]['control_members'].append(name+'_Jamb_1');gates[-1]['control_at']=[-58.69,17.48,b-.012];gates[-1]['home_index']=idx
  gates[-1]['service_opening_z']=[a,b]
# Physical local destinations on the retained cover floor, outside both lanes.
for i,x in enumerate([-35.3,-34.3]):
 poly=box(x-.27,-451.3,x+.27,-450.7).buffer(.045,quad_segs=3)
 prism(f'D04PC_ClosedUsed_{i}_Body',poly,12,12.68,role='warm_walnut',category='closed_used_container')
 prism(f'D04PC_ClosedUsed_{i}_Lid',poly.buffer(.012),12.68,12.74,role='ivory_enamel',category='closed_used_container')
 for side,X in enumerate([x-.30,x+.27]):cube(f'D04PC_ClosedUsed_{i}_Handle_{side}',[X,12.48,-451.08],[X+.03,12.6,-450.92],category='closed_used_container')
cube('D04PC_CleanTrayShelf',[-35.5,12.78,-445.15],[-33.8,12.9,-444.65],role='warm_walnut',category='clean_supply_support')
for i,x in enumerate([-35.4,-33.9]):cube('D04PC_CleanShelfPier_'+str(i),[x-.06,12,-445.08],[x+.06,12.78,-444.72],category='clean_supply_support')
cube('D04PC_CleanTrayDeck',[-35.3,12.9,-445.05],[-34,12.94,-444.75],role='ivory_enamel',category='clean_tray')
for i,(a,b)in enumerate([([-35.3,12.94,-445.05],[-34,13.04,-445.02]),([-35.3,12.94,-444.78],[-34,13.04,-444.75]),([-35.3,12.94,-445.02],[-35.27,13.04,-444.78]),([-34.03,12.94,-445.02],[-34,13.04,-444.78])]):cube('D04PC_CleanTrayRim_'+str(i),a,b,category='clean_tray')
cover=next(a for a in json.load(open(R/'Game/data/generated/structural_meshes.json'))['regions']if a['id']=='D03_protected_crew_cover');poly=unary_union([Polygon(t)for t in cover['triangles']]);assert poly.covers(box(-36,-451.6,-33,-444.4))
for f in ['Game/scripts/physics_tether.gd','Game/scripts/cleaning_bottle.gd','Game/scripts/ship.gd','Game/data/generated/structural_meshes.json','Game/data/architecture/D04_PORT_FORWARD_HOMES_SECOND.json','Game/data/architecture/D04_PORT_FORWARD_HOMES_THIRD.json','BlenderCatalogue/references/landings/staff_corridor_services.png']:
 pins[f]=sha(R/f)
for f,h in pins.items():assert sha(R/f)==h,f
plan={'schema':'astraea.d04.physical_connections.v1','base_commit':'b1b31697f4b75ca696511c681bf6cbec52ae70c0','production_active':False,'source_pins':pins,'cuts':cuts,'parts':parts,'gates':gates,'previous_candidate':old,'zero_new_floor':True,'homes':20,'rests':25,'staff_zinc_center_post_preserved':True,'maintenance_person_access':False,'operational_provider_available':False,'clean_bay_approach':[-34.4,12,-445.7],'used_bay_approach':[-34.4,12,-450.35],'limits':['Candidate exact physical connections; live consent/vacancy/dispatch/save absent: all private controls remain closed in production.','Physical local clean/closed-used destinations on unchanged floor; full commons transfer network/traffic/cart vertical held.','Reach-only low service hatches retain fixed upper glass and every original planter/plant; no person access or biology/task-completion credit.','Other west/north courts, full commons/engineering/species/final normal-game/CRT/hardware remain unfinished.']}
(W/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');(W/'PREIMAGE_SUPPORT.json').write_text(json.dumps({'status':'PASS','exact_cut_preimages':len(cuts),'staff_modified_batches':3,'untouched_zinc_post':'HOME_BATCH_238_ASTRAEA_staff_zinc','new_floor_m2':0,'existing_bay_floor':'D03_protected_crew_cover','source_pins':len(pins)},indent=2)+'\n');print('PHYSICAL_PLAN',len(parts),len(cuts),len(pins))
