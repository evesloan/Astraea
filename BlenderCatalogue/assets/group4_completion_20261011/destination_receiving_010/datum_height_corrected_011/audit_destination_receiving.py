"""Exact bounded floor-component audit, not collision or travel acceptance."""
from pathlib import Path
import hashlib,json,collections
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
W=Path(__file__).resolve().parent;R=next(p for p in W.parents if (p/"Game").is_dir())
pins={}
def read(p):
 data=(R/p).read_bytes();pins[p]=hashlib.sha256(data).hexdigest();return json.loads(data)
contract=read('BlenderCatalogue/assets/group4_completion_20261011/DESTINATION_CONNECTION_CONTRACT.json')
sections=read('Game/data/architecture/received_sections.json')['sections'];bykey={s['programme_key']:s for s in sections}
floorfiles=['Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json','Game/data/architecture/SALON_RECEIVING_FLOORS_CANDIDATE.json','Game/data/architecture/STILLROOM_RECEIVING_FLOORS_CANDIDATE.json','Game/data/architecture/CINEMA5_RECEIVING_FLOORS_CANDIDATE.json']
datums={d['deck_id']:d['floor_elevation_m'] for d in read('Game/data/design_contract.json')['deck_datums']}
regions=[];floor_by_level=collections.defaultdict(list)
for file in floorfiles:
 for region in read(file)['regions']:
  assert all(len(t)==3 and Polygon(t).is_valid and Polygon(t).area>1e-9 for t in region['triangles']),region['id']
  shape=unary_union([Polygon(t) for t in region['triangles']]);assert shape.is_valid
  item={'owner_id':region['id'],'deck':region['deck'],'floor_y':region['floor_y'],'input':file,'shape':shape}
  regions.append(item);floor_by_level[(item['deck'],round(float(item['floor_y']),6))].append(shape)
assert len({r['owner_id'] for r in regions})==len(regions)
unions={level:unary_union(polys) for level,polys in floor_by_level.items()}
clear={deck:shape.buffer(-.36,join_style=2) for deck,shape in unions.items()}
def components(shape):return list(shape.geoms) if hasattr(shape,'geoms') else [shape]
cores={}
for row in contract['five_core_transfers']:
 c=read('Game/data/architecture/'+row['core_contract']);cores[row['station']]=c
rows=[]
for original in contract['destinations']:
 row={k:original[k] for k in ['programme_key','name','retained_historical_room_id','deck','catchment_proposal','core_transfer_contract','installed_owner']}
 row.update(id_recovered_or_created=False,whole_route_accepted=False)
 s=bykey.get(row['programme_key'])
 if s:
  point=s['portal_xyz'];row.update(portal_source='received_sections.json exact source contract',portal_xyz=point,original_floor_owner_ids=s.get('floor_owner_ids',[]),source_export_file=s['model_file'],source_export_sha256=s['source_sha256'])
  assert hashlib.sha256((R/'Game/assets/models'/s['model_file']).read_bytes()).hexdigest()==s['source_sha256']
  p=Point(point[0],point[2]);deck=row['deck'];level=(deck,round(float(point[1]),6));u=unions[level];corridor=clear[level]
  core=cores[row['catchment_proposal']];gate=core['lift']['gate_origin_xz']
  anchor=[gate[0]-1.2,float(point[1]),gate[1]];a=Point(anchor[0],anchor[2])
  row['geometric_core_floor_anchor_xyz']=anchor
  row['portal_point_supported_by_audited_compiled_floor']=u.buffer(1e-5).covers(p)
  row['portal_capsule_radius036_floor_clear']=corridor.buffer(1e-5).covers(p)
  row['core_anchor_capsule_radius036_floor_clear']=corridor.buffer(1e-5).covers(a)
  common=next((part for part in components(corridor) if part.buffer(1e-5).covers(a) and part.buffer(1e-5).covers(p)),None)
  row['shared_radius036_floor_component']=common is not None
  row['portal_compiled_floor_owners']=[r['owner_id'] for r in regions if r['deck']==deck and abs(r['floor_y']-point[1])<1e-6 and r['shape'].buffer(1e-5).covers(p)]
  row['status']='FLOOR_COMPONENT_CONTINUOUS_COLLISION_OPERATION_OPEN' if common is not None else 'FLOOR_COMPONENT_HOLD_REQUIRES_EXACT_OWNER_REVIEW'
  row['boundary']='Floor polygons only; excludes walls, pillars, furniture, doors, step transitions, native-only floors, cart/body envelopes and live vertical transport. No path or travel acceptance inferred.'
 else:
  row.update(status='NO_PRECISE_PORTAL_IN_AUDITED_RECEIVED_SET',portal_xyz=None,boundary='Historical allocation/catchment is not a current doorway. Resolve actual receiver with its source owner; no missing geometry or room ID inferred.')
 rows.append(row)
assert len(rows)==161 and len({r['programme_key'] for r in rows})==161
theater=read('Game/data/architecture/THEATER_D11_MAIN_ENTRY023.json')
theater_interface={'programme_keys':['D11_directory_01','D12_directory_11','D13_directory_01'],'D11_existing_exterior_call_stance':theater['controls'][1]['stance_native'],'D11_existing_exterior_call_target':theater['controls'][1]['target_native'],'D11_floor_owner':theater['controls'][1]['expected_floor_owner'],'source_pin':pins['Game/data/architecture/THEATER_D11_MAIN_ENTRY023.json'],'Group4_exterior_route_owner':True,'Group8_interior_receiver_owner':True,'shared_geometry_modified':False,'next_gate':'Obtain Group8 current entry/gallery/backstage receiving contract. Source023 baseline entry alone does not define adopted D12/D13/secondary routes. Preserve the closed east Cinema5 aperture.'}
summary=dict(collections.Counter(r['status'] for r in rows))
out={'schema':'astraea.group4.destination_receiving_audit.height_corrected.v2','based_on_group4_checkpoint':'99736e00b24803fed0b61dca997866fe6fc9ab18','baseline_main':'affc5c807087ff87da29f3642c2d6e418241b896','programme_count':161,'exact_received_portal_count':len(sections),'compiled_floor_owner_count':len(regions),'canonical_datum_floor_owners':sum(abs(r['floor_y']-datums[r['deck']])<1e-6 for r in regions),'non_datum_regions_excluded_from_canonical_component':[{'owner_id':r['owner_id'],'deck':r['deck'],'actual_floor_y':r['floor_y'],'canonical_floor_y':datums[r['deck']]} for r in regions if abs(r['floor_y']-datums[r['deck']])>=1e-6],'height_matching_tolerance_m':1e-6,'prior_audit_status':'HOLD_REJECTED_HEIGHT_PROJECTION; prior010 remains immutable, never accepted as travel evidence','summary':summary,'capsule_radius_reference_m':.36,'seam_query_tolerance_m':1e-5,'floor_triangle_inputs_are_actual_selected_compilations':True,'scope':'Read-only floor-component screening and exact receiving backlog. It does not prove traversability or accept159 destinations. Actual two terminal input tests remain separately scoped.','source_pins_sha256':pins,'theater_exterior_interface':theater_interface,'rows':rows,'physical_construction_added':False,'whole_group_accepted':False,'shared_registry_or_source_modified':False}
(W/'DESTINATION_RECEIVING_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n')
print('GROUP4 RECEIVING AUDIT',len(rows),'stable programmes;',len(regions),'actual compiled floor owners;',summary)
for row in rows:
 if row['status']=='FLOOR_COMPONENT_HOLD_REQUIRES_EXACT_OWNER_REVIEW':print('HOLD',row['programme_key'],row['portal_xyz'],'core',row['geometric_core_floor_anchor_xyz'],'portal_floor',row['portal_point_supported_by_audited_compiled_floor'],'r036',row['portal_capsule_radius036_floor_clear'])
