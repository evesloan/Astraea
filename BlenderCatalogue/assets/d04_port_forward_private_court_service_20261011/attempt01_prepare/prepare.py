from pathlib import Path
import json,hashlib,copy
from shapely.geometry import box
R=Path(__file__).resolve().parents[3];W=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ns={'__file__':str(W/'prepare.py')}
s=(R/'BlenderCatalogue/assets/d04_port_forward_homes_second_20261010/prepare.py').read_text()
exec(s[:s.index('from shapely import affinity')],ns)
parts=ns['parts'];cube=ns['cube'];prism=ns['prism'];pins={};homes={};audit=[]
for n in ['first','second','third','fourth','fifth']:
 p=R/f'BlenderCatalogue/assets/d04_port_forward_homes_{n}_20261010/RUNTIME_PLAN.json';d=json.load(open(p));homes[n]=d
 native=next(a['native']for a in d['native_export_records']if a['export']==d['structure']['model_file'])
 for f in [p,R/'Game/data/architecture'/f'D04_PORT_FORWARD_HOMES_{n.upper()}.json',R/'Game/assets/models'/d['structure']['model_file'],p.parent/native]:
  if f.exists():pins[str(f.relative_to(R))]=sha(f)
 for c in d['courts']:
  if c['side']=='commons':continue
  ps=[q for q in d['commons_parts']if '_'+c['side']+'_'in q['name']]
  floor=next(q for q in ps if q['name'].endswith('_Floor'))
  screen=next(q for q in ps if q['name'].endswith('_PrivacyScreen'))
  plants=[q for q in ps if '_Planter_'in q['name']]
  width=max(v[0]for v in floor['verts'])-min(v[0]for v in floor['verts'])
  aisle=(min(min(v[0]for v in q['verts'])for q in plants)-min(v[0]for v in floor['verts'])) if c['side']=='east' else (max(v[0]for v in floor['verts'])-max(max(v[0]for v in q['verts'])for q in plants))
  audit.append({'group':n,'side':c['side'],'court_width_m':width,'best_continuous_aisle_before_home_wall_m':aisle,'sealed_end_names':[q['name']for q in ps if '_End_'in q['name']],'permission_and_service_route_accepted':False})
old=R/'BlenderCatalogue/assets/d04_port_forward_receiving_20261010/PLAN.json';receiving=json.load(open(old));pins[str(old.relative_to(R))]=sha(old)
for f in ['Game/assets/models/D04_PORT_FORWARD_RECEIVING_r001.glb','Game/scripts/player.gd','Game/scripts/ship.gd','Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json','Game/docs/master_source/MASTER_CURRENT_APPLICATION.json','BlenderCatalogue/references/landings/staff_corridor_services.png']:
 pins[f]=sha(R/f)
pre=[]
for n,ends in [('first',[1,0]),('second',[1,0]),('third',[1])]:
 d=homes[n]
 for end in ends:
  q=next(q for q in d['commons_parts']if '_east_End_'+str(end)==q['name'][q['name'].index('_east'):]);pre.append({'group':n,'model_file':d['structure']['model_file'],'preimage':copy.deepcopy(q),'opening_x':[-28.7,-27.5],'opening_y':[16.5,19.2]})
for q in receiving['parts']:
 if q['name']in ['D04PF_UpperGuard_14','D04PF_UpperGuard_14_Base','D04PF_UpperGuard_14_Cap']:pre.append({'group':'public_receiving','model_file':'D04_PORT_FORWARD_RECEIVING_r001.glb','preimage':copy.deepcopy(q),'opening_x':[-28.8,-27.3],'opening_y':[16.5,19.2]})
assert len(pre)==8
for row in pre:
 q=row['preimage'];lo=[min(v[i]for v in q['verts'])for i in range(3)];hi=[max(v[i]for v in q['verts'])for i in range(3)];x,X=row['opening_x'];Y=row['opening_y'][1]
 cube('D04PCS_'+q['name']+'_Left',lo,[x,hi[1],hi[2]],role=q['role'],category='contained_successor')
 cube('D04PCS_'+q['name']+'_Right',[X,lo[1],lo[2]],hi,role=q['role'],category='contained_successor')
 if hi[1]>Y:cube('D04PCS_'+q['name']+'_Head',[x,Y,lo[2]],[X,hi[1],hi[2]],role=q['role'],category='contained_successor')
successors=copy.deepcopy(parts);parts.clear()
bridges=[]
for i,(z,Z)in enumerate([(-408.4,-406.9),(-423.2,-423.0),(-438.0,-437.8)]):
 cube('D04PCS_LinkFloor_'+str(i),[-28.8,16.26,z],[-27.3,16.5,Z],role='warm_stone',category='link_floor')
 cube('D04PCS_LinkRoof_'+str(i),[-28.8,20.46,z],[-27.3,20.66,Z],role='ivory_enamel',category='link_roof')
 for j,x in enumerate([-28.65,-27.45]):cube('D04PCS_LinkBearer_%s_%s'%(i,j),[x-.075,16.10,z-.35],[x+.075,16.26,Z+.35],category='link_bearer')
 bridges.append({'index':i,'bounds':[[-28.8,16.26,z],[-27.3,16.5,Z]],'clear_worker_center_x':-28.1,'new_floor_m2':1.5*(Z-z),'short_span_m':Z-z,'engineering_accepted':False})
 for side,(x,X)in enumerate([(-28.8,-28.68),(-27.42,-27.3)]):cube('D04PCS_LinkEdge_%s_%s'%(i,side),[x,16.5,z],[X,17.65,Z],role='ivory_enamel',category='edge_guard')
fixed=copy.deepcopy(parts);parts.clear();gates=[]
for i,(z,angle)in enumerate([(-408.4,90),(-423.1,-90),(-437.9,-90)]):
 name='D04PCS_OpaqueGate_'+str(i);cube(name,[-28.7,16.5,z-.09],[-27.5,19.2,z+.09],role='ivory_enamel',category='candidate_gate')
 for j,y in enumerate([16.75,18.95]):prism('D04PCS_Hinge_%s_%s'%(i,j),box(-28.735,z-.055,-28.665,z+.055).buffer(.015,quad_segs=2),y-.10,y+.10,category='candidate_gate_hardware')
 prism('D04PCS_Handle_'+str(i),box(-27.74,z-.16,-27.68,z-.105).buffer(.025,quad_segs=2),17.48,17.72,category='candidate_gate_hardware')
 gates.append({'name':name,'members':[name,'D04PCS_Hinge_%s_0'%i,'D04PCS_Hinge_%s_1'%i,'D04PCS_Handle_'+str(i)],'pivot':[-28.7,16.5,z],'candidate_open_degrees':angle,'closed_default':True,'ordinary_interaction_and_permission_accepted':False})
gateparts=copy.deepcopy(parts)
result={'schema':'astraea.d04.private_court_service_candidate.v1','base_commit':'2ec3e95d432ebcf97b08fc6817b061c6e9d46b97','stage':'native_candidate','production_active':False,'new_units':0,'new_rests':0,'source_pins':pins,'court_audit':audit,'preimages':pre,'successor_parts':successors,'parts':fixed+gateparts,'fixed_parts':fixed,'gate_parts':gateparts,'gates':gates,'bridges':bridges,'new_floor_m2':sum(b['new_floor_m2']for b in bridges),'all_twenty_allocations_unchanged':homes['first']['all_twenty_allocations_unchanged'],'worker_route':[[-28.1,16.5,z]for z in [-405.6,-407.7,-409.4,-415.6,-421.6,-424.3,-430.6,-436.3,-439.2,-441.8,-444.1]],'limits':['Native candidate, not installed in ship.gd; existing gates/guards/home privacy remain unchanged in production','Entrance meets public cross-street, not a dedicated staff or clean/used route','West narrow second court cannot take ordinary worker passage without redesign; all western/northern approaches unfinished','Three east court groups/six outlooks only; no guest entry/window/plant source modification','Normal gate controls, dynamic sweep guard, service permission/occupancy/save remain pending','No loaded-cart, guest-body, maintenance task, primary-load, final ordinary-game/CRT/hardware acceptance']}
assert not(W/'PLAN.json').exists();(W/'PLAN.json').write_text(json.dumps(result,indent=2)+'\n');print('COURT_CANDIDATE_PLAN',len(fixed),len(successors),len(gateparts),len(pins),result['new_floor_m2'])
