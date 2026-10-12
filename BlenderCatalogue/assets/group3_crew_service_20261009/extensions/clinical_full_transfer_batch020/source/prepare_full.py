"""Full retained clinical streets and source-bound controlled crossings."""
from pathlib import Path
import json,hashlib,copy,math
import shapely
from shapely.geometry import Polygon,box,Point
from shapely.ops import unary_union
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4];EXT=HERE.parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
write=lambda f,q:f.write_text(json.dumps(q,indent=2)+'\n')
paths=[EXT/'clinical_streets_batch002/source/CLINICAL_STREETS.json',EXT/'clinical_streets_batch002/SHA256SUMS.txt',EXT/'port2_clinical_physical_batch016/source/BOUNDED_CLINICAL_STREETS.json',EXT/'port2_clinical_physical_batch016/source/PORT2_MISSING_ONLY_FLOORS.json',EXT/'port2_clinical_physical_batch016/source/PHYSICAL_CONTRACT.json',EXT/'fore_starboard_clinical_batch018/source/FORE_HEADER_AND_BAYS.json',EXT/'fore_starboard_clinical_batch018/source/FORE_MISSING_ONLY_FLOORS.json',EXT/'fore_starboard_clinical_batch018/source/FORE_PHYSICAL_CONTRACT.json',ROOT/'Game/data/generated/structural_meshes.json',ROOT/'Game/data/generated/received_structural_meshes.json',ROOT/'Game/scripts/service_door.gd',ROOT/'Game/scripts/group3_port2_clinical_20261011/crossing_supervisor.gd',ROOT/'Game/scripts/lift_button.gd',HERE/'qa/ACTUAL_MAIN_EXISTING_SCREEN.json',ROOT/'Game/data/architecture/REMAINING_BATCH_FLOORS.json',ROOT/'Game/data/architecture/REMAINING_BATCH_SECTIONS.json',HERE/'qa/ACTUAL_ALL_SOURCE_RETURN_STANCES.json',HERE/'qa/ALL_ORIGINAL_D05_LOADED_GATE_FIT.json',ROOT/'Game/data/architecture/received_sections.json',ROOT/'Game/scripts/received_room_residency.gd',ROOT/'Game/scripts/remaining_batch_receiving.gd']
for folder in ['clinical_streets_batch002','port2_clinical_physical_batch016','fore_starboard_clinical_batch018']:
 for line in (EXT/folder/'SHA256SUMS.txt').read_text().splitlines():h,f=line.split('  ',1);assert sha(EXT/folder/f)==h,f
old=json.load(open(paths[0]));p2=json.load(open(paths[2]));fore=json.load(open(paths[5]));survey=json.load(open(HERE/'qa/ACTUAL_MAIN_EXISTING_SCREEN.json'))
pins={str(f.relative_to(ROOT)):sha(f)for f in paths}
base=dict(schema=1,family='group3_crew_service_20261009',material_contract='retained_lower_staff_network',source_pins=pins,automatic_runtime_adoption=False,authoritative_identity_map=None,registered_berths_added=0)
for i in range(7,11):assert not any(q['catalogue_id']==f'AST-MED-G3-{i:03d}'for q in json.load(open(ROOT/'BlenderCatalogue/catalogue_manifest.json'))['assets'])
holds=[dict(name='RetainedRoyaltyPierFore',bounds_xz=[106.3,26,110,32],witness=[108,21,29],source_contact=survey['rows'][3]['existing_static_blockers'][0]['existing_static_contact']),dict(name='RetainedRoyaltyPierAft',bounds_xz=[106.3,48,110,54],witness=[108,21,51],source_contact=survey['rows'][3]['existing_static_blockers'][1]['existing_static_contact'])]
holds.append(dict(name='GrandPoolMedicalDirectory01JunctionInterface',bounds_xz=[-61.2,-406.2,-52.8,-397.8],witness=[-57,21,-406],source_contact='GrandPoolOrchardSection_WIP/GrandPoolConnectedArchitecture/AST-AQU-016/GPM_CELL_-4_-21_2_ASTRAEA_warm_stone_concave_static_surface'))
held=unary_union([box(*q['bounds_xz'])for q in holds]);p2area=box(-63.1,-312,-53,-278);forearea=box(54.9,-482,63.1,-470)
def shape(q):
 if'boundary'in q:return Polygon(q['boundary'],q['holes'])
 a=q['aabb'];return box(a[0],a[4],a[1],a[5])
def yr(q):return q['y']if'y'in q else q['aabb'][2:4]
def prism(out,name,g,lo,hi,role,category,cell):
 lo=round(lo,6);hi=round(hi,6)
 if hi-lo<.000001:return
 g=shapely.set_precision(g,grid_size=.000001)
 for i,p in enumerate(shapely.get_parts(g)):
  if p.geom_type!='Polygon'or p.area<1e-10:continue
  out.append(dict(name=name+'_'+str(i),boundary=list(p.exterior.coords)[:-1],holes=[list(r.coords)[:-1]for r in p.interiors],triangles=[list(t.exterior.coords)[:3]for t in shapely.constrained_delaunay_triangles(p).geoms],y=[lo,hi],role=role,category=category,batch_cell=cell))
gates=[];crossings=[]
for c in old['controlled_crossings']:
 key=c['programme_key'];r=c['retained_crossing'];row=dict(programme_key=key,clear_buffer_bounds_xz=[r['crossing_clear_rect'][i]for i in[0,2,1,3]],source_outer_bounds_xz=[r['outer_rect'][i]for i in[0,2,1,3]],sealed_return_available=key!='D05_directory_06',gates=[])
 for i,portal in enumerate(r['gated_portals']):
  x,z=portal['center_xz'];q=dict(name=key+'_crossing_'+str(i),programme_key=key,position=[x,21,z],yaw=0 if i<2 else math.pi/2,axis='clean'if i<2 else'sealed_return',persistent_id=None,clear_aperture_m=[3.6,2.4],pocket_m=1.9)
  if key=='D05_directory_02'and i==0:q['position'][2]+=.2;q['source_fit_delta_m']=[0,0,.2]
  gates.append(q);row['gates'].append(q['name'])
 # Both physical requests are on the retained approach wall inside face,
 # outside the inner shared crossing buffer.
 x,z=gates[-4]['position'][0],gates[-4]['position'][2];row['dispatch_buttons']=[dict(name=key+'_clean_dispatch',axis='clean',position=[x-1.755,22.3,z-1.0],persistent_id=None),dict(name=key+'_return_dispatch',axis='sealed_return',position=[x-1.755,22.3,z-2.0],persistent_id=None)]
 crossings.append(row)
proposal_gates=copy.deepcopy(gates);held_crossings=[q for q in crossings if q['programme_key']=='D05_directory_01'];gates=[q for q in gates if q['programme_key']!='D05_directory_01'];crossings=[q for q in crossings if q['programme_key']!='D05_directory_01']
def gate_rect(q,half_x,half_z):
 x,y,z=q['position'];c=math.cos(q['yaw']);s=math.sin(q['yaw'])
 return Polygon([(x+c*a+s*b,z-s*a+c*b)for a,b in [(-half_x,-half_z),(half_x,-half_z),(half_x,half_z),(-half_x,half_z)]])
parts=[]
# Full successor replaces old port2 bounded selection; fore stubs stay owned by
# batch018 and are omitted here. Only new gate frame/pocket receiving cuts follow.
source=[]
for q in old['parts']:
 g=shape(q).difference(p2area).difference(forearea).difference(held)
 if not g.is_empty:source.append((q,g))
for q in p2['parts']:source.append((q,shape(q).difference(held)))
for q,g in source:
 lo,hi=yr(q);levels=sorted({round(v,6)for v in [lo,hi,*[v for v in [23.4,23.552]if lo<v<hi]]})
 for a,b in zip(levels,levels[1:]):
  cut=unary_union([gate_rect(d,3.722,.142)for d in gates])if a<23.552 else Polygon()
  prism(parts,q['name']+'_Complete_'+str(a),g.difference(cut),a,b,q['role'],q['category'],q.get('batch_cell','clinical'))
fore_fixtures=json.load(open(paths[7]))['fixtures'];fore_names={q['name']for q in fore_fixtures}|{q['name']for q in json.load(open(paths[4]))['fixtures']}
fixtures=[q for q in old['fixtures']if q['name']not in fore_names and not held.covers(Point(q['position'][0],q['position'][2]))]
# Two held support spans are open interfaces. Their fixtures are omitted, and
# the associated district06 return dispatch fails closed.
write(HERE/'source/CLINICAL_COMPLETE_ARCHITECTURE.json',dict(base,catalogue_id='AST-MED-G3-007',parts=parts,fixtures=fixtures,held_support_spans=holds,old_port2_bounded_source_replaced=True,fore_stub_source_omitted=True,original_medical_receivers_opened=False))
compiled=json.load(open(paths[8]))['regions']+json.load(open(paths[9]))['regions']+json.load(open(ROOT/'Game/data/architecture/REMAINING_BATCH_FLOORS.json'))['regions'];actual=unary_union([Polygon(t)for q in compiled if q['deck']=='D05'for t in q['triangles']])
old_group=[]
for f in [paths[3],paths[6]]:
 for q in json.load(open(f))['parts']:
  if q['batch_cell']=='D05':old_group.append(shape(q))
old_group=unary_union(old_group);request=unary_union([Polygon(q['boundary'],q['holes'])for q in old['floor_proposal']['polygons']]).difference(held)
request=request.union(unary_union([gate_rect(d,3.722,.142)for d in gates])).difference(held)
missing=request.difference(actual).difference(old_group);floor=[]
prism(floor,'ClinicalCompleteMissingFloor',missing,20.76,21,'staff_floor','floor','D05')
write(HERE/'source/CLINICAL_COMPLETE_MISSING_FLOOR.json',dict(base,catalogue_id='AST-MED-G3-008',parts=floor,fixtures=[],new_floor_m2=missing.area,old_compiled_or_prior_Group3_floor_overlaid=False,primary_structure_acceptance=False))
worker_routes=copy.deepcopy(old['routes'])
for route in worker_routes:
 if route['id']=='soiled_return_port':route['proposed_centerline_xz']=[[-61,-480],[-61,-457],[-61.8,-456],[-61.8,-450],[-61,-449],[-61,-436],[-61.8,-435],[-61.8,-429],[-61,-428],[-61,-74],[-108,-74],[-108,74],[-61,74],[-61,480]]
contract=dict(base,worker_route_overrides=worker_routes,worker_route_override_policy='Two0.8m exterior offsets remain inside the original3.6m used street around retained pool surfaces; original source route and architecture are preserved.',parent_handoff_commit='cc780461aab31747af48afc9c84d2b9ba6968f55',door_bindings=gates,crossings=crossings,held_crossing_interfaces=held_crossings,proposed_gate_bindings=proposal_gates,fixtures=fixtures,routes=old['routes'],terminal_interfaces=old['retained_terminal_interfaces'],held_support_spans=holds,new_floor_m2=missing.area,prior_Group3_floor_exclusion_m2=request.intersection(old_group).area,original_D01_D04_or_medical_room_or_shared_root_modified=False,old_port2_clinical_visual_to_remove='AST-MED-G3-006',fore_clinical_stub_preserved=True,required_prior_physical_packages=['Group3Port2ClinicalPhysical','Group3ForeStarboardClinical'],source_slider_asset='AST-MED-G3-009.glb',static_fittings_asset='AST-MED-G3-010.glb',authoritative_operation_IDs=None,actual_medical_receiver_contact_or_inventory_or_sterility_or_sealed_load_acceptance=False,complete_starboard_return_route_accepted=False,sliding_gate_policy='Existing service-door lifecycle, new dimensioned source fitting only; no engine or generic interaction system',largest_species_loaded_cart_primary_structure_graphical_or_full_group_acceptance=False)
write(HERE/'source/COMPLETE_CLINICAL_CONTRACT.json',contract)
print(json.dumps(dict(parts=len(parts),fixtures=len(fixtures),missing_floor_m2=missing.area,controlled_crossings=len(crossings),source_sliding_gates=len(gates),held_support_spans=len(holds))))
