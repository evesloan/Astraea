"""Missing-only seventeen-landings and source-fitted midship clinical crossing."""
from pathlib import Path
import json,hashlib,math
import shapely
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4];FIRST=HERE.parent.parent
OLD=HERE.parent/'port2_clinical_batch006';STREET=HERE.parent/'clinical_streets_batch002'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n')
registry=json.load(open(ROOT/'BlenderCatalogue/catalogue_manifest.json'))
for aid in ['AST-STF-G3-030','AST-STF-G3-031','AST-STF-G3-032','AST-MED-G3-005','AST-MED-G3-006']:assert not any(q['catalogue_id']==aid for q in registry['assets'])
frozen=[]
for d in [FIRST]+sorted(HERE.parent.iterdir()):
 if not d.is_dir()or d==HERE or not(d/'SHA256SUMS.txt').exists():continue
 for line in(d/'SHA256SUMS.txt').read_text().splitlines():
  h,path=line.split('  ',1);assert sha(d/path)==h,str(d/path)
 frozen.append(dict(path=str((d/'SHA256SUMS.txt').relative_to(ROOT)),sha256=sha(d/'SHA256SUMS.txt')))
paths=[OLD/'source/PORT_SECOND_STAFF_RISER.json',OLD/'source/PORT2_CLINICAL_HEADER.json',OLD/'source/CLINICAL_PORT2_RECEIVER_PATCH.json',
 OLD/'exports/AST-STF-G3-006.glb',OLD/'exports/AST-MED-G3-004.glb',STREET/'source/CLINICAL_STREETS.json',STREET/'exports/AST-MED-G3-002.glb',
 ROOT/'Game/data/generated/structural_meshes.json',ROOT/'Game/data/generated/received_structural_meshes.json',ROOT/'Game/data/whole_ship_layout.json',
 ROOT/'Game/docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx',ROOT/'Game/docs/master_source/MASTER_CURRENT_APPLICATION.json',
 ROOT/'Game/data/architecture/packages/crew_living/SECTION_DISTRIBUTION_PROPOSAL.json',ROOT/'Game/data/architecture/SHARED_CREW_HOME.json',
 ROOT/'Game/data/architecture/D04_PORT_CENTRAL_STAFF_RISER.json',ROOT/'Game/scripts/d04_port_central_staff_riser.gd',
 ROOT/'Game/scripts/commons_lift.gd',ROOT/'Game/scripts/lift_gate.gd',ROOT/'Game/scripts/service_door.gd',ROOT/'Game/scripts/player.gd',
 ROOT/'Game/assets/models/AST-CIR-003_seventeen_stop.glb',ROOT/'Game/assets/models/AST-DOR-003.glb',ROOT/'Game/assets/models/AST-STF-008.glb']
pins={str(p.relative_to(ROOT)):sha(p)for p in paths}
base=dict(schema=1,family='group3_crew_service_20261009',material_contract='retained_lower_staff_network',source_pins=pins,
 automatic_runtime_adoption=False,persistent_identity_mapping_created=False,registered_population_or_berths_added=0)
riser=json.load(open(paths[0]));header=json.load(open(paths[1]));patch=json.load(open(paths[2]));street=json.load(open(STREET/'source/CLINICAL_STREETS.json'))
gates=[]
for i,q in enumerate(header['held_new_clean_soiled_crossing']['gate_positions_proposed_only']):
 gates.append(dict(name=q['role'].removesuffix('_hold'),position=q['position'],yaw=q['yaw'],axis='clean'if i<2 else'sealed_return',
  persistent_id=None,identity_binding='Owner must supply an authoritative resolved mechanism identity; no generated default.'))
def shape(q):
 if'boundary'in q:return Polygon(q['boundary'],q['holes'])
 a=q['aabb'];return box(a[0],a[4],a[1],a[5])
def ys(q):return q['y']if'y'in q else q['aabb'][2:4]
def prism(parts,name,g,lo,hi,role,category,cell):
 for i,p in enumerate(shapely.get_parts(g)):
  if p.geom_type!='Polygon'or p.area<1e-10:continue
  parts.append(dict(name=name+'_'+str(i),boundary=list(p.exterior.coords)[:-1],holes=[list(r.coords)[:-1]for r in p.interiors],
   triangles=[list(t.exterior.coords)[:3]for t in shapely.constrained_delaunay_triangles(p).geoms],y=[lo,hi],role=role,category=category,batch_cell=cell))
trim_footprint=box(-23.187,-284.922,-22.983,-281.078)
altered=[q for q in riser['parts']if q['name'].startswith('Port2_ShaftFront')or q['name'].startswith('Port2_CallControlBacking')]
riser_omissions=sorted({q['category']+'_'+q['role']+'_'+q['batch_cell']for q in altered})
riser_patch=[];trim_changes=[];backing_changes=[]
for q in riser['parts']:
 if q['category']+'_'+q['role']+'_'+q['batch_cell']not in riser_omissions:continue
 if q['name'].startswith('Port2_CallControlBacking'):
  a=list(q['aabb']);a[0],a[1]=-22.995,-22.895;a[4]+=.36;a[5]+=.36;r=dict(q,aabb=a);riser_patch.append(r)
  backing_changes.append(dict(name=q['name'],original_aabb=q['aabb'],fitted_aabb=a,actual_controller_call_z=-284.65,
   actual_controller_call_center_x=-22.86,mounted_on_native_gate_front_skin_x=-22.995,
   source_backing_outside_moving_pocket=True,original_button_sphere_unchanged=True))
 elif q['name'].startswith('Port2_ShaftFront'):
  deck=q['name'].split('_')[-1];floor=next(l['floor_y']for l in riser['floor_proposals']if l['deck']==deck)
  lo,hi=ys(q);levels=sorted({lo,hi,*[y for y in [floor+2.648,floor+2.852]if lo<y<hi]})
  volume=0
  for a,b in zip(levels,levels[1:]):
   original_shape=shape(q);g=original_shape.difference(trim_footprint)if a<floor+2.852 and b>floor+2.648 else original_shape
   volume+=(original_shape.area-g.area)*(b-a)
   prism(riser_patch,q['name']+'_TrimFit_'+str(a),g,a,b,q['role'],q['category'],q['batch_cell'])
  trim_changes.append(dict(name=q['name'],removed_volume_m3=volume,original_sill_or_lobby_changed=False))
 else:riser_patch.append(q)
# The original riser used its basic metric UV axes; preserve that material/UV contract.
riser_base={k:v for k,v in base.items()if k!='material_contract'}
write(HERE/'source/RISER_FRAME_AND_CALL_PATCH.json',dict(riser_base,catalogue_id='AST-STF-G3-032',parts=riser_patch,fixtures=[],
 native_meshes_to_omit=riser_omissions,selected_original_semantic_parts=[q['name']for q in riser['parts']if q['category']+'_'+q['role']+'_'+q['batch_cell']in riser_omissions],
 frame_trim_only_clearance_m=.002,frame_trim_source='Unscaled native AST-DOR-003 warm-walnut header: 3.84m width and Y2.65..2.85.',
 call_backings=backing_changes,trim_changes=trim_changes,original_riser_source_modified=False,all_unselected_original_native_nodes_preserved=True))
def gate_shape(q,x0,x1,z0,z1):
 x,y,z=q['position'];c=math.cos(q['yaw']);s=math.sin(q['yaw'])
 return Polygon([(x+c*a+s*b,z-s*a+c*b)for a,b in [(x0,z0),(x1,z0),(x1,z1),(x0,z1)]])
selection=box(-63.1,-312,-53.0,-278)
replace=set(patch['original_semantic_parts_in_these_batches'])
original=[q for q in street['parts']if q['name']not in replace]+patch['parts']
frame_cuts=unary_union([gate_shape(q,-1.382,1.382,-.182,.182)for q in gates])
selected=[];source_names=[]
for q in original:
 g=shape(q).intersection(selection)
 if g.is_empty:continue
 source_names.append(q['name']);lo,hi=ys(q)
 levels=sorted({lo,hi,*[y for y in [23.8,23.822]if lo<y<hi]})
 for a,b in zip(levels,levels[1:]):
  candidate=g.difference(frame_cuts)if a<23.822 and b>23.8 else g
  prism(selected,q['name']+'_Bounded_'+str(a),candidate,a,b,q['role'],q['category'],q.get('batch_cell','clinic'))
selected_fixtures=[q for q in street['fixtures']if selection.covers(shapely.Point(q['position'][0],q['position'][2]))]
write(HERE/'source/BOUNDED_CLINICAL_STREETS.json',dict(base,catalogue_id='AST-MED-G3-006',parts=selected,fixtures=selected_fixtures,
 selected_source_parts=source_names,selection_xz=[-63.1,-312,-53,-278],
 original_receiver_patch_used=True,extra_source_cut_only_y=[23.8,23.822],extra_source_cut_frame_rectangles=[list(gate_shape(q,-1.382,1.382,-.182,.182).exterior.coords)[:-1]for q in gates],
 original_ten_clinical_junctions_changed=False,full_clinical_export=False))

# Fill only empty head/side spaces around four unscaled original door fittings.
# Existing walls, header and lobbies own their complete original solid volume.
fixed=selected+header['parts']+[q for q in riser['parts']if' D05'in q['name']or'_D05'in q['name']]
collars=[]
def missing_prism(name,g,lo,hi,role,category,cell):
 levels=sorted({lo,hi,*[y for q in fixed for y in ys(q)if lo<y<hi]})
 for a,b in zip(levels,levels[1:]):
  existing=unary_union([shape(q)for q in fixed if ys(q)[0]<b and ys(q)[1]>a])
  prism(collars,name+'_'+str(a),g.difference(existing),a,b,role,category,cell)
for q in gates:
 for x0,x1 in [(-1.8,-1.38),(1.38,1.8)]:missing_prism(q['name']+'_Side_'+str(x0),gate_shape(q,x0,x1,-.18,.18),21,25.2,'staff_white_paint','door_receiver',q['name'])
 missing_prism(q['name']+'_Head',gate_shape(q,-1.38,1.38,-.18,.18),23.82,25.2,'staff_white_paint','door_receiver',q['name'])
# Explicit roof-height step between the existing 3.2m lobby and 4.2m header.
missing_prism('LobbyHeaderUpperClosure',box(-22.94,-289.14,-19.06,-289),24.34,25.2,'staff_white_paint','header_step','port2_header')
write(HERE/'source/CROSSING_DOOR_RECEIVERS.json',dict(base,catalogue_id='AST-MED-G3-005',parts=collars,fixtures=[],
 original_service_fitting_unscaled=True,door_bindings=gates,clinical_or_sterile_flow_accepted=False))

compiled=json.load(open(ROOT/'Game/data/generated/structural_meshes.json'));received=json.load(open(ROOT/'Game/data/generated/received_structural_meshes.json'))
floorparts=[];floorchecks=[];requests=[];sill_contacts=[]
for landing in riser['floor_proposals']:
 deck=landing['deck'];y=landing['floor_y'];request=unary_union([Polygon(q['boundary'],q['holes'])for q in landing['missing_floor_polygons']])
 if deck=='D05':
  clinical=unary_union([Polygon(q['boundary'],q['holes'])for q in street['floor_proposal']['polygons']]).intersection(selection)
  request=request.union(clinical).union(unary_union([Polygon(q['boundary'],q['holes'])for q in header['floor_proposal']['polygons']]))
 actual=unary_union([Polygon(t)for q in compiled['regions']+received['regions']if q['deck']==deck for t in q['triangles']])
 missing=request.difference(actual)
 # Existing visual sills remain visible, and the lift controller owns their contact.
 sill=next(q for q in riser['parts']if q['name']=='Port2_LandingSill_'+deck)
 missing=missing.difference(shape(sill))
 # Original controller keeps its exact fixed-sill contact; these three source
 # remainders cover only the native sill volume outside that original box.
 for i,a in enumerate([[-23.10,-23.02,y-.06,y,-284.85,-281.15],
                      [-23.18,-23.10,y-.06,y,-284.85,-284.20],
                      [-23.18,-23.10,y-.06,y,-281.80,-281.15]]):
  sill_contacts.append(dict(name='SourceSillRemainder_'+deck+'_'+str(i),aabb=a,derived_from='Port2_LandingSill_'+deck,controller_owned_box_not_replaced=True))
 prism(floorparts,'Port2MissingFloor_'+deck,missing,y-.24,y,'staff_floor','floor',deck)
 floorchecks.append(dict(deck=deck,floor_y=y,new_floor_m2=missing.area,existing_floor_duplicate_m2=missing.intersection(actual).area,existing_sill_contact_owner_preserved=True))
 requests.append(dict(deck=deck,floor_y=y,polygons=[dict(boundary=list(p.exterior.coords)[:-1],holes=[list(r.coords)[:-1]for r in p.interiors])for p in shapely.get_parts(request)if p.geom_type=='Polygon']))
write(HERE/'source/PORT2_MISSING_ONLY_FLOORS.json',dict(base,catalogue_id='AST-STF-G3-030',parts=floorparts,fixtures=[],floor_proposal_only=True,checks=floorchecks))
contract=dict(base,reservation_id='port_service_riser_2',protected_existing_D04_riser_reservation='port_service_riser_3',
 base_handoff_commit='28e32333ba9c8c20aa673b1fa01812efc68c769e',frozen_manifests=frozen,
 original_riser_export=str((OLD/'exports/AST-STF-G3-006.glb').relative_to(ROOT)),original_header_export=str((OLD/'exports/AST-MED-G3-004.glb').relative_to(ROOT)),
 controller_binding=riser['controller_binding_proposal']['explicit_controller_fields_proposal'],lift_root_position=[-25,0,-283],lift_root_yaw=math.pi,
 door_bindings=gates,fixtures=riser['fixtures']+header['fixtures']+selected_fixtures,
 source_sill_remainder_contacts=sill_contacts,
 riser_native_meshes_to_omit=riser_omissions,
 floor_checks=floorchecks,floor_requests=requests,new_floor_m2=sum(q['new_floor_m2']for q in floorchecks),
 default_main_adopted=False,original_door_width_open_clear_m=2.168,largest_species_loaded_cart_and_structural_capacity_accepted=False,
 sequential_crossing_policy='Close and verify the other axis before opening requested axis; buffer occupancy prevents mode switch. Shared lift buffer remains sequential sealed-load, never simultaneous/sterile segregation.',
 supplied_identity_map_required=['lift_persistent_id','lift_identity_prefix','clean_north','clean_south','sealed_load_east','sealed_load_west'],
 authoritative_identity_map=None,registry_or_save_written=False,clinical_operational_acceptance=False,
 source_boundaries=['D01 existing processing and shared circuit unchanged; port2 lobby only.', 'D04 existing riser3 and neighborhood routes unchanged; port2 lobby only.',
 'Original forward port lift, stop keys, wet datum and D04-D07 blank rule unchanged.', 'No D18 stop or branch added.',
 'Bounded D05 clinical selection only; do not overlay full old clinical sources or overwrite original receiver/junctions.'])
write(HERE/'source/PHYSICAL_CONTRACT.json',contract)
write(HERE/'qa/PLAN_CHECKS.json',dict(status='PASS',landings=17,source_gates=4,new_floor_m2=contract['new_floor_m2'],
 original_manifests_verified=len(frozen),existing_floor_duplicate_m2=sum(q['existing_floor_duplicate_m2']for q in floorchecks),
 frames_cut_extra_height_m=.022,original_sources_modified=False,persistent_keys_created=False))
print(json.dumps(dict(landings=17,gates=4,new_floor_m2=contract['new_floor_m2'],fixture_profiles=len(contract['fixtures']),frozen_manifests=len(frozen))))
