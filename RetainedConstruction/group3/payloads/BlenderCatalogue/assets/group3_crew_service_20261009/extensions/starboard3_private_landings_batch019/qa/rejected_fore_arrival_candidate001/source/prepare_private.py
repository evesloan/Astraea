"""Exact starboard3 reservation fit with private, owner-authorized arrivals."""
from pathlib import Path
import json,hashlib,copy,math
import shapely
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4];PAIR=HERE.parent/'remaining_riser_sources_batch017'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
write=lambda f,q:f.write_text(json.dumps(q,indent=2)+'\n')
for line in (PAIR/'SHA256SUMS.txt').read_text().splitlines():h,f=line.split('  ',1);assert sha(PAIR/f)==h,f
layout=json.load(open(ROOT/'Game/data/whole_ship_layout.json'));reservation=next(q for q in layout['staff_riser_reservations']if q['id']=='starboard_service_riser_3')
assert reservation['lobby_z']==[-91.8,-80.2]
survey=json.load(open(HERE/'qa/INHERITED_ACTUAL_MAIN_SURVEY.json'));row=next(q for q in survey['rows']if q['reservation_id']==reservation['id'])
assert not row['shaft_blockers']and not row['above_floor_lobby_contacts']
paths=[PAIR/'source/starboard_service_riser_5.json',PAIR/'source/AFT_PAIR_CONTRACT.json',PAIR/'SHA256SUMS.txt',HERE/'qa/INHERITED_ACTUAL_MAIN_SURVEY.json',ROOT/'Game/data/whole_ship_layout.json',ROOT/'Game/data/spatial_layout.json',ROOT/'Game/data/generated/structural_meshes.json',ROOT/'Game/data/generated/received_structural_meshes.json',ROOT/'Game/scripts/commons_lift.gd',ROOT/'Game/scripts/service_door.gd',ROOT/'Game/assets/models/AST-CIR-003_seventeen_stop.glb',ROOT/'Game/assets/models/AST-DOR-003.glb',ROOT/'Game/assets/models/AST-STF-008.glb']
pins={str(f.relative_to(ROOT)):sha(f)for f in paths}
base=dict(schema=1,family='group3_crew_service_20261009',source_pins=pins,automatic_runtime_adoption=False,authoritative_identity_map=None,registered_berths_added=0)
pair=json.load(open(PAIR/'source/AFT_PAIR_CONTRACT.json'));site=next(q for q in pair['sites']if q['reservation_id']=='starboard_service_riser_5');old=json.load(open(PAIR/'source/starboard_service_riser_5.json'));parts=[];diffs=[]
def shape(q):
 if'boundary'in q:return Polygon(q['boundary'],q['holes'])
 a=q['aabb'];return box(a[0],a[4],a[1],a[5])
def yr(q):return q['y']if'y'in q else q['aabb'][2:4]
def prism(out,name,g,lo,hi,role,category,cell):
 for i,p in enumerate(shapely.get_parts(g)):
  if p.geom_type!='Polygon'or p.area<1e-10:continue
  out.append(dict(name=name+'_'+str(i),boundary=list(p.exterior.coords)[:-1],holes=[list(r.coords)[:-1]for r in p.interiors],triangles=[list(t.exterior.coords)[:3]for t in shapely.constrained_delaunay_triangles(p).geoms],y=[lo,hi],role=role,category=category,batch_cell=cell))
for src in old['parts']:
 q=copy.deepcopy(src);q['name']=q['name'].replace('SA5_','S3_')
 if 'aabb'in q:q['aabb'][4]-=576;q['aabb'][5]-=576
 else:
  q['boundary']=[[a,b-576]for a,b in q['boundary']];q['holes']=[[[a,b-576]for a,b in r]for r in q['holes']];q['triangles']=[[[a,b-576]for a,b in t]for t in q['triangles']]
 before=copy.deepcopy(q)
 if 'aabb'in q:
  a=q['aabb']
  if 'LobbyFore'in q['name']:
   a[4]+=.2;a[5]+=.2
   if 'Lintel'in q['name']:a[2]+=.022
  if 'LobbyAft'in q['name']:a[4]-=.2;a[5]-=.2
  if 'LobbyWestScreen'in q['name']:a[4]+=.2;a[5]-=.2
  if 'LobbyRoof'in q['name']:a[4]+=.2;a[5]-=.2
 if q!=before:diffs.append(dict(name=q['name'],shifted_preimage=before,fitted_successor=q))
 parts.append(q)
fixtures=[dict(q,name=q['name'].replace('starboard_service_riser_5','starboard_service_riser_3'),position=[q['position'][0],q['position'][1],q['position'][2]-576])for q in old['fixtures']]
write(HERE/'source/STARBOARD3_FITTED_SOURCE.json',dict(base,catalogue_id='AST-STF-G3-044',parts=parts,fixtures=fixtures,reservation=reservation,source_fit_deltas=diffs,no_departure_from_exact_reservation=True))
checks=[];floors=[];lobby=box(18.8,-91.8,23.18,-80.2)
compiled=json.load(open(ROOT/'Game/data/generated/structural_meshes.json'))['regions']+json.load(open(ROOT/'Game/data/generated/received_structural_meshes.json'))['regions']
for row in site['floor_checks']:
 deck=row['deck'];y=row['floor_y'];actual=unary_union([Polygon(t)for q in compiled if q['deck']==deck for t in q['triangles']]);sill=next(q for q in parts if q['name'].endswith('LandingSill_'+deck));missing=lobby.difference(actual).difference(shape(sill))
 prism(floors,'S3MissingOnlyFloor_'+deck,missing,y-.24,y,'staff_floor','floor',deck)
 checks.append(dict(deck=deck,floor_y=y,new_floor_m2=missing.area,original_compiled_floor_borrowed_m2=lobby.intersection(actual).area))
write(HERE/'source/STARBOARD3_MISSING_FLOORS.json',dict(base,catalogue_id='AST-STF-G3-045',parts=floors,fixtures=[],floor_proposal_only=True,original_compiled_fore_apron_floors_preserved=True))
doors=[dict(name='private_arrival_'+q['deck'],deck=q['deck'],position=[21,q['floor_y'],-91.62],yaw=math.pi,persistent_id=None,owner_authorization_required=True)for q in checks]
receivers=[]
for q in doors:
 y=q['position'][1]
 for name,g,lo,hi in [('SideLeft',box(19.2,-91.8,19.62,-91.44),y,y+3.2),('SideRight',box(22.38,-91.8,22.8,-91.44),y,y+3.2),('Head',box(19.62,-91.8,22.38,-91.44),y+2.82,y+3.2)]:
  levels=sorted({lo,hi,*[v for p in parts for v in yr(p)if lo<v<hi]})
  for a,b in zip(levels,levels[1:]):
   fixed=unary_union([shape(p)for p in parts if yr(p)[0]<b and yr(p)[1]>a]);prism(receivers,q['name']+name+'_'+str(a),g.difference(fixed),a,b,'staff_white_paint','door_receiver',q['deck'])
write(HERE/'source/STARBOARD3_PRIVATE_RECEIVERS.json',dict(base,catalogue_id='AST-STF-G3-047',parts=receivers,fixtures=[],door_bindings=doors))
contacts=[]
for q in site['source_sill_remainder_contacts']:
 q=copy.deepcopy(q);q['name']=q['name'].replace('starboard_service_riser_5','starboard_service_riser_3');q['aabb'][4]-=576;q['aabb'][5]-=576;contacts.append(q)
contract=dict(base,parent_handoff_commit='d8702f138047fa8da947b799184686962c01b9f5',reservation=reservation,reservation_id=reservation['id'],controller_binding=site['controller_binding'],lift_root_position=[25,0,-86],lift_root_yaw=0,source_sill_remainder_contacts=contacts,door_bindings=doors,fixtures=fixtures,floor_checks=checks,new_floor_m2=sum(q['new_floor_m2']for q in checks),persistent_identity_map=None,owner_authorization_predicate_required=True,inside_egress_does_not_require_external_permission=True,original_D01_shared_circuit_D04_routes_or_compiled_floors_modified=False,no_D18_stop_or_new_berths=True,all_district_arrival_connections_or_egress_engineering_or_species_or_final_acceptance=False)
write(HERE/'source/PRIVATE_LANDING_CONTRACT.json',contract)
print(json.dumps(dict(landings=17,private_arrival_doors=17,new_floor_m2=contract['new_floor_m2'],fixture_profiles=17,fitted_source_changes=len(diffs))))
