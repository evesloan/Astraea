from pathlib import Path
import json,hashlib
from shapely.geometry import Polygon,LineString,box
from shapely.ops import unary_union
W=Path(__file__).resolve().parent;R=W.parents[2]
T=R/'Game/source_derivatives/group4_completion_20261011'
plan=json.loads((W/'RECEIVING_PLAN.json').read_text())
routes={
 'FORWARD':[[5.6,-448.6],[5.6,-446],[0,-446],[0,-444]],
 'AFT':[[5.6,415.4],[5.6,417.5],[0,417.5],[0,420]],
 'FORE_MIDSHIP':[[-11.2,-225.6],[-10,-228],[-5,-228],[0,-230],[0,-251],[0,-253]],
 'AFT_MIDSHIP':[[5.6,228],[5.6,226.5],[3.2,226.5],[0,230],[0,258],[0,260]],
 'CENTRAL':[[-5.6,-68.8],[-5.6,-78],[0,-78],[0,-81]]}
files={'FORWARD':'FORWARD_PUBLIC_CORE.json','AFT':'AFT_PUBLIC_CORE.json','FORE_MIDSHIP':'FORE_MIDSHIP_PUBLIC_CORE.json','AFT_MIDSHIP':'AFT_MIDSHIP_PUBLIC_CORE.json','CENTRAL':'PRIMARY_ATRIUM_CORE.json'}
fixture=json.loads((T/'CANDIDATE_FLOOR_FIXTURE.json').read_text())
floor=unary_union([Polygon(t) for q in fixture for t in q['triangles']])
floor=unary_union([floor]+[Polygon(t) for q in plan['stations'] for t in q.get('floor_triangles_xz',[])])
f=R/'BlenderCatalogue/assets/group4_tram_connections_20261009/north_receiving_006/NORTH_RECEIVING_INTERFACE.json'
n=json.loads(f.read_text())
for rect in [[-13.6,-265.5,-7.8,-252],[-13.6,-252,-4,-225.2],[-13.6,-225.2,-13.4,-221.2],[-9,-225.2,-4,-221.2]]:floor=floor.union(box(*rect))
rows=[];pins={}
for st in plan['stations']:
 label=st['label'];p=R/'Game/data/architecture'/files[label];d=json.loads(p.read_text())
 pins[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
 model=d.get('enclosure_file','AST-CIR-005.glb');mp=R/'Game/assets/models'/model
 pins[str(mp.relative_to(R))]=hashlib.sha256(mp.read_bytes()).hexdigest()
 route=routes[label];corridor=LineString(route).buffer(.36,cap_style=1,join_style=1)
 missing=corridor.difference(floor).area
 assert missing<1e-6,(label,missing)
 rows.append(dict(station=label,retained_core_id=d.get('id','primary_atrium_core'),
   core_contract=files[label],core_origin=d.get('origin',[0,0,-100]),core_model=model,
   core_model_sha256=pins[str(mp.relative_to(R))],core_lift=d['lift'],
   protected_core_gate=d['lift']['gate_origin_xz'],lower_route_xz=route,
   lower_route_y=52.5,supported_capsule_radius_m=.36,supported_length_m=LineString(route).length,
   missing_floor_area_m2=missing,route_status='SUPPORTED_FLOOR_PROPOSAL_REQUIRES_LIVE_LOCAL_CHECK',
   sidewall_aperture_added=False,existing_public_lift_stops_unchanged=True))
ledger=json.loads((R/'Game/data/programme_ledger.json').read_text());index=[]
for q in ledger['destinations']:
 z=sum(q['historical_envelope']['z'])/2 if q.get('historical_envelope') else None
 st=min(plan['stations'],key=lambda s:abs(s['catchment_z']-z)) if z is not None else None
 index.append(dict(programme_key=q['programme_key'],name=q['name'],
    retained_historical_room_id=q.get('historical_room_id'),id_recovered_or_created=False,
    deck=q['historical_deck'],catchment_proposal=st['label'] if st else None,
    core_transfer_contract=files[st['label']] if st else None,
    installed_owner=q.get('current_geometry_owner'),
    terminal_destination_branch_status='EXISTING_OWNER_INTERFACE_REQUIRES_EXACT_LIVE_BINDING',
    gate='Preserve original destination entry; no new room, arrival relocation or shared registry edit'))
assert len(index)==161 and len({q['programme_key'] for q in index})==161
contract=dict(schema='astraea.group4.destination_transfer.v1',active=False,whole_group_complete=False,
 five_core_transfers=rows,destinations=index,source_pins=pins,
 exterior_theater_gate='Theater external entries/backstage and gallery lift remain Group8/shared-owner interfaces; no closed east Cinema5 aperture opened',
 residential_gate='Retain Group1 house/court/lift approaches. Core indexing does not build or accept their terminal branches',
 crew_service_gate='Retain Group3 service network and original physical cart/stock. No source station is a stock provider',
 limits='Supported floor proposal plus explicit ownership index; does not establish all161 reachable destinations or guest routing')
(W/'DESTINATION_CONNECTION_CONTRACT.json').write_text(json.dumps(contract,indent=2)+'\n')
(T/'TRANSFER_TEST_FIXTURE.json').write_text(json.dumps(contract,indent=2)+'\n')
print('TRANSFER_CONTRACT',len(rows),'supported core approaches;',len(index),'unchanged programme keys')
