"""Complete fore staff arrival, clinical branch controls and retained receiving bays."""
from pathlib import Path
import json,hashlib,copy,math
import shapely
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4];FIRST=HERE.parent.parent
PAIR=HERE.parent/'remaining_riser_sources_batch017';SERVICE=HERE.parent/'service_receiving_batch004';CLINIC=HERE.parent/'clinical_streets_batch002'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
write=lambda f,q:f.write_text(json.dumps(q,indent=2)+'\n')
catalogue=json.load(open(ROOT/'BlenderCatalogue/catalogue_manifest.json'))
for i in range(37,44):assert not any(q['catalogue_id']==f'AST-STF-G3-{i:03d}'for q in catalogue['assets'])
for d in [PAIR,SERVICE]:
 for line in(d/'SHA256SUMS.txt').read_text().splitlines():h,f=line.split('  ',1);assert sha(d/f)==h,f
survey=json.load(open(HERE/'qa/ACTUAL_EXISTING_SURVEY.json'))
r=next(q for q in survey['rows']if q['reservation_id']=='starboard_service_riser_1');assert not r['shaft_blockers']and not r['above_floor_lobby_contacts']
old_riser=json.load(open(PAIR/'source/starboard_service_riser_5.json'));pair=json.load(open(PAIR/'source/AFT_PAIR_CONTRACT.json'))
header=json.load(open(SERVICE/'source/HEADER_EQUIPMENT_SUCCESSOR.json'));bays=json.load(open(SERVICE/'source/SERVICE_RECEIVING.json'))
streets=json.load(open(FIRST/'source/CREW_STREETS.json'));clinical=json.load(open(CLINIC/'source/CLINICAL_STREETS.json'))
paths=[PAIR/'source/starboard_service_riser_5.json',PAIR/'source/AFT_PAIR_CONTRACT.json',PAIR/'SHA256SUMS.txt',SERVICE/'source/HEADER_EQUIPMENT_SUCCESSOR.json',SERVICE/'source/SERVICE_RECEIVING.json',SERVICE/'SHA256SUMS.txt',
 FIRST/'source/CREW_STREETS.json',FIRST/'source/STARBOARD_FORWARD_STAFF_RISER.json',CLINIC/'source/CLINICAL_STREETS.json',
 ROOT/'Game/data/generated/structural_meshes.json',ROOT/'Game/data/generated/received_structural_meshes.json',ROOT/'Game/data/whole_ship_layout.json',ROOT/'Game/data/spatial_layout.json',
 ROOT/'Game/data/architecture/HULL_BODY_SECTION_PROPOSAL.json',ROOT/'Game/scripts/commons_lift.gd',ROOT/'Game/scripts/service_door.gd',
 ROOT/'Game/assets/models/AST-CIR-003_seventeen_stop.glb',ROOT/'Game/assets/models/AST-DOR-003.glb',ROOT/'Game/assets/models/AST-STF-008.glb']
paths.append(ROOT/'BlenderCatalogue/assets/crew_service_platform/source/geometry_parts.json')
pins={str(f.relative_to(ROOT)):sha(f)for f in paths}
for q in bays['reused_asset_dependencies']:assert sha(ROOT/q['path'])==q['sha256'];pins[q['path']]=q['sha256']
base=dict(schema=1,family='group3_crew_service_20261009',source_pins=pins,automatic_runtime_adoption=False,authoritative_identity_map=None,registered_berths_added=0)
def shape(q):
 if'boundary'in q:return Polygon(q['boundary'],q['holes'])
 a=q['aabb'];return box(a[0],a[4],a[1],a[5])
def yr(q):return q['y']if'y'in q else q['aabb'][2:4]
def prism(out,name,g,lo,hi,role,cat,cell):
 for i,p in enumerate(shapely.get_parts(g)):
  if p.geom_type!='Polygon'or p.area<1e-10:continue
  out.append(dict(name=name+'_'+str(i),boundary=list(p.exterior.coords)[:-1],holes=[list(r.coords)[:-1]for r in p.interiors],triangles=[list(t.exterior.coords)[:3]for t in shapely.constrained_delaunay_triangles(p).geoms],
   y=[lo,hi],role=role,category=cat,batch_cell=cell))
def shift(q,delta):
 q=copy.deepcopy(q);q['name']=q['name'].replace('SA5_','S1_')
 if'aabb'in q:q['aabb'][4]+=delta;q['aabb'][5]+=delta
 else:
  def point(v):return[v[0],v[1]+delta]
  q['boundary']=[point(v)for v in q['boundary']];q['holes']=[[point(v)for v in ring]for ring in q['holes']];q['triangles']=[[point(v)for v in t]for t in q['triangles']]
 return q
riser_parts=[shift(q,-980)for q in old_riser['parts']]
riser_fixtures=[dict(q,name=q['name'].replace('starboard_service_riser_5','starboard_service_riser_1'),position=[q['position'][0],q['position'][1],q['position'][2]-980])for q in old_riser['fixtures']]
write(HERE/'source/FORE_RISER.json',dict(base,catalogue_id='AST-STF-G3-037',parts=riser_parts,fixtures=riser_fixtures,original_first_starboard_successor_only=True,corrected_original_seventeen_stop_cabin_required=True))
crew_selection=box(18.5,-502.5,60,-475);lobby=box(18.8,-496,23.18,-484);crew=[]
for q in streets['parts']:
 g=shape(q).intersection(crew_selection).difference(lobby)
 if g.is_empty:continue
 prism(crew,q['name']+'_ForeSelected',g,*yr(q),q['role'],q['category'],q['batch_cell'])
crew_lights=[q for q in streets['fixtures']if crew_selection.covers(shapely.Point(q['position'][0],q['position'][2]))and not lobby.covers(shapely.Point(q['position'][0],q['position'][2]))]
fixture_parts=json.load(open(ROOT/'BlenderCatalogue/assets/crew_service_platform/source/geometry_parts.json'))
old_fixture=next(q for q in fixture_parts if q['name']=='CRW_Task_8_0_Housing');oldx=sum(old_fixture['world_aabb'][:2])/2;oldz=sum(old_fixture['world_aabb'][4:])/2
for x,z in [(21,-499),(33,-500),(45,-500),(57,-499),(57,-487),(57,-477.5)]:
 name='ForeCrewTask_'+str(x)+'_'+str(z)
 for suffix in ['Housing','Opal','Hanger0','Hanger1']:
  q=next(q for q in fixture_parts if q['name']=='CRW_Task_8_0_'+suffix);a,b,lo,hi,c,d=q['world_aabb']
  crew.append(dict(name=name+'_'+suffix,aabb=[a+x-oldx,b+x-oldx,lo,hi,c+z-oldz,d+z-oldz],role=q['role'],category='lighting_fixture',batch_cell=name,original_rigid_source_fixture=q['name']))
 crew_lights.append(dict(name=name,position=[x,15.03,z],range_m=8,energy=.9,color=[.78,.88,1]))
write(HERE/'source/CREW_FORE_STREETS.json',dict(base,catalogue_id='AST-STF-G3-038',material_contract='retained_lower_staff_network',parts=crew,fixtures=crew_lights,original_inside_lobby_street_fragments_omitted=True))
gates=[dict(name='crew_arrival',position=[21,12,-496.5],yaw=math.pi,axis=None)]
for name,z,axis in [('clinical_clean',-500,'clean'),('clinical_return',-504,'sealed_return')]:gates.append(dict(name=name,position=[24.2,21,z],yaw=-math.pi/2,axis=axis))
for q in bays['bays']:gates.append(dict(name=q['name']+'_entry',position=q['receiver'],yaw=math.pi if q['front']==-1 else 0,axis=None))
for q in gates:q['persistent_id']=None
def frame(q,pad=.002):
 x,y,z=q['position'];c=math.cos(q['yaw']);s=math.sin(q['yaw']);return Polygon([(x+c*a+s*b,z-s*a+c*b)for a,b in [(-1.38-pad,-.18-pad),(1.38+pad,-.18-pad),(1.38+pad,.18+pad),(-1.38-pad,.18+pad)]])
fore_bays=[]
for q in header['parts']+bays['parts']:
 lo,hi=yr(q);levels=sorted({lo,hi,*[v for v in [23.822]if lo<v<hi]});g=shape(q)
 for a,b in zip(levels,levels[1:]):
  cut=unary_union([frame(d)for d in gates if d['position'][1]==21 and a<23.822])
  prism(fore_bays,q['name']+'_Fitted_'+str(a),g.difference(cut),a,b,q['role'],q['category'],q.get('batch_cell','fore_service'))
write(HERE/'source/FORE_HEADER_AND_BAYS.json',dict(base,catalogue_id='AST-STF-G3-039',material_contract='retained_lower_staff_network',parts=fore_bays,fixtures=header['fixtures']+bays['fixtures'],
 source_gate_frame_cuts_only=True,original_bay_furniture_and_sealed_receivers_preserved=True))
clinical_sel=box(54.9,-482,63.1,-470);clin=[]
for q in clinical['parts']:
 g=shape(q).intersection(clinical_sel)
 if not g.is_empty:prism(clin,q['name']+'_ForeStub',g,*yr(q),q['role'],q['category'],q['batch_cell'])
clin_lights=[q for q in clinical['fixtures']if clinical_sel.covers(shapely.Point(q['position'][0],q['position'][2]))]
# The two exact original fore street mouths are already open to these stubs.
fore_bays+=clin
write(HERE/'source/FORE_HEADER_AND_BAYS.json',dict(base,catalogue_id='AST-STF-G3-039',material_contract='retained_lower_staff_network',parts=fore_bays,fixtures=header['fixtures']+bays['fixtures']+clin_lights,
 source_gate_frame_cuts_only=True,original_bay_furniture_and_sealed_receivers_preserved=True,bounded_clinical_stub_only=True))
receivers=[];fixed=riser_parts+crew+fore_bays
def gate_shape(q,x0,x1,z0,z1):
 x,y,z=q['position'];c=math.cos(q['yaw']);s=math.sin(q['yaw']);return Polygon([(x+c*a+s*b,z-s*a+c*b)for a,b in [(x0,z0),(x1,z0),(x1,z1),(x0,z1)]])
def fill(name,g,lo,hi,role,cell):
 levels=sorted({lo,hi,*[v for q in fixed for v in yr(q)if lo<v<hi]})
 for a,b in zip(levels,levels[1:]):
  solid=unary_union([shape(q)for q in fixed if yr(q)[0]<b and yr(q)[1]>a])
  prism(receivers,name+'_'+str(a),g.difference(solid),a,b,role,'door_receiver',cell)
for q in gates:
 y=q['position'][1];ceiling=y+(3.2 if y==12 else 4.2)
 for lo,hi in [(-1.8,-1.38),(1.38,1.8)]:fill(q['name']+'_Side',gate_shape(q,lo,hi,-.18,.18),y,ceiling,'staff_white_paint',q['name'])
 fill(q['name']+'_Head',gate_shape(q,-1.38,1.38,-.18,.18),y+2.82,ceiling,'staff_white_paint',q['name'])
fill('D05LobbyRoofStepClosure',box(19.06,-496.14,22.94,-496),24.34,25.2,'staff_white_paint','fore_header')
write(HERE/'source/FORE_DOOR_RECEIVERS.json',dict(base,catalogue_id='AST-STF-G3-040',material_contract='retained_lower_staff_network',parts=receivers,fixtures=[],door_bindings=gates))
compiled=json.load(open(ROOT/'Game/data/generated/structural_meshes.json'))['regions']+json.load(open(ROOT/'Game/data/generated/received_structural_meshes.json'))['regions']
floorparts=[];floorchecks=[]
site=next(q for q in pair['sites']if q['reservation_id']=='starboard_service_riser_5')
for row in site['floor_checks']:
 deck=row['deck'];y=row['floor_y'];request=lobby
 if deck=='D03':request=request.union(unary_union([Polygon(q['boundary'],q['holes'])for q in streets['route_shape']+streets['porch_shapes']]).intersection(crew_selection).buffer(.14,join_style=2))
 if deck=='D05':
  request=request.union(unary_union([Polygon(q['boundary'],q['holes'])for q in header['floor_proposal']['polygons']+bays['floor_proposal']['polygons']]))
  request=request.union(unary_union([Polygon(q['boundary'],q['holes'])for q in clinical['floor_proposal']['polygons']]).intersection(clinical_sel))
 actual=unary_union([Polygon(t)for q in compiled if q['deck']==deck for t in q['triangles']])
 sill=next(q for q in riser_parts if q['name'].endswith('Port2_LandingSill_'+deck));missing=request.difference(actual).difference(shape(sill))
 prism(floorparts,'ForeMissingFloor_'+deck,missing,y-.24,y,'staff_floor','floor',deck)
 floorchecks.append(dict(deck=deck,floor_y=y,new_floor_m2=missing.area,old_floor_overlap_m2=missing.intersection(actual).area))
write(HERE/'source/FORE_MISSING_ONLY_FLOORS.json',dict(base,catalogue_id='AST-STF-G3-041',material_contract='retained_lower_staff_network',parts=floorparts,fixtures=[],floor_proposal_only=True))
contacts=[]
for q in site['source_sill_remainder_contacts']:
 q=copy.deepcopy(q);q['name']=q['name'].replace('starboard_service_riser_5','starboard_service_riser_1');q['aabb'][4]-=980;q['aabb'][5]-=980;contacts.append(q)
reuse=[q for q in bays['reused_asset_instances']if q['asset']!='AST-HSK-005']
contract=dict(base,parent_handoff_commit='004d387c2cbc9d693844585ccd3083fd720d62b6',reservation_id='starboard_service_riser_1',controller_binding=site['controller_binding'],
 lift_root_position=[25,0,-490],lift_root_yaw=0,source_sill_remainder_contacts=contacts,door_bindings=gates,
 fixtures=riser_fixtures+crew_lights+header['fixtures']+bays['fixtures']+clin_lights,floor_checks=floorchecks,new_floor_m2=sum(q['new_floor_m2']for q in floorchecks),
 reused_asset_dependencies=bays['reused_asset_dependencies'],reused_asset_instances=reuse,custodial_cart_parking_candidate_only=[q for q in bays['reused_asset_instances']if q['asset']=='AST-HSK-005'],
 original_custodial_cart_identity_or_position_changed=False,duplicate_physics_cart_created=False,
 dispatch_buttons=[dict(name='clean_dispatch',axis='clean',position=[19.15,22.3,-495.815],persistent_id=None),dict(name='return_dispatch',axis='sealed_return',position=[22.87,22.3,-495.815],persistent_id=None)],
 shared_buffer_bounds_xz=header['shared_lift_transfer_buffer']['bounds_xz'],sealed_load_predicate_required=True,
 authoritative_operation_IDs=None,source_400_person_berth_or_C036_mapping_created=False,
 adoption='Replace frozen first-starboard source and original fore header/bays/selected street pieces only in a scoped owner derivative; never overlay originals. Existing ward/source floors and D01/D04/fore-port identities remain unchanged.',
 full_medical_clinical_network_or_stock_or_species_or_primary_engineering_accepted=False)
write(HERE/'source/FORE_PHYSICAL_CONTRACT.json',contract)
write(HERE/'qa/PLAN_CHECKS.json',dict(status='SOURCE_PROPOSAL_PREPARED',landings=17,source_doors=len(gates),bays=3,new_floor_m2=contract['new_floor_m2'],fixture_profiles=len(contract['fixtures']),originals_changed=False,keys_created=False))
print(json.dumps(dict(landings=17,doors=len(gates),bays=3,new_floor_m2=contract['new_floor_m2'],fixture_profiles=len(contract['fixtures']))))
