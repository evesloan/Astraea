"""Exact current shopping staff sockets;shared risers remain owner controlled."""
from pathlib import Path
import json,hashlib,ast,struct
import numpy as np
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
parsed=ast.parse((P/'source/build_large_venue_lighting.py').read_text())
fn=next(n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name=='exported_bounds')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'literal_glb_bounds','exec'),globals())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
shopping=ROOT/'Game/data/architecture/SHOPPING_PROMENADE.json';s=json.loads(shopping.read_text())
survey_path=P/'qa/RETAINED_CONNECTION_SURVEY.json';survey=json.loads(survey_path.read_text())
circuits=survey['staff_graph']['connected_components'];assert len(circuits)==4
rows=[]
for row in s['chunks']:
    if not row['chunk_id'].startswith('STAFFLINK_'):continue
    circuit=next(i for i,ids in enumerate(circuits) if row['chunk_id'] in ids)
    models={}
    for layer in ['floor','shell']:
        spec=row['layers'][layer];path=ROOT/'Game'/spec['path'][6:]
        assert sha(path)==spec['sha256']
        shapes=exported_bounds(path);origin=np.array(row['position'])
        bounds={name:[(lo+origin).tolist(),(hi+origin).tolist()] for name,(lo,hi) in shapes.items()}
        models[layer]={'model_path':spec['path'],'sha256':spec['sha256'],'actual_world_mesh_bounds':bounds}
    floor_boxes=list(models['floor']['actual_world_mesh_bounds'].values())
    floor_lo=np.array([b[0] for b in floor_boxes]).min(axis=0);floor_hi=np.array([b[1] for b in floor_boxes]).max(axis=0)
    assert abs(floor_hi[1]-52.5)<.00002
    endpoints=[]
    for endpoint,(x,z) in zip(['inner','outer'],row['points_xz']):
        assert floor_lo[0]-.00002<=x<=floor_hi[0]+.00002 and floor_lo[2]-.00002<=z<=floor_hi[2]+.00002
        endpoints.append({'existing_endpoint_kind':endpoint,'world_xyz':[x,52.5,z],
            'source_floor_lateral_width_m':float(floor_hi[2]-floor_lo[2]),
            'source_boundary':'Existing crosslink endpoint only;not a new shaft,room ID or verified target join'})
    rows.append({'existing_chunk_id':row['chunk_id'],'existing_circuit_index':circuit,'circuit_members':circuits[circuit],
        'endpoints':endpoints,'models':models,'shared_riser_owner':'Group3 and Group1 integration',
        'join_status':'HOLD:no independently verified matching shared-riser receiving footprint/adoption'})
assert len(rows)==8
staff=ROOT/'Game/data/architecture/GRAND_POOL_SECTION_RUNTIME.json';existing=json.loads(staff.read_text())['staff']
contract={'schema':'astraea.group5.staff_riser_interfaces.v1','source_shopping_sha256':sha(shopping),
    'source_survey_sha256':sha(survey_path),'actual_connections_preserved':78,'staff_circuits':4,'existing_crosslinks':8,
    'rows':rows,'existing_forward_staff_source':{'manifest':str(staff.relative_to(ROOT)),'sha256':sha(staff),
        'persistent_lift_id':existing['existing_persistent_lift_id'],'root_xyz':existing['existing_root_xyz'],
        'preserved_D01_D02_D03_D08wet_D09_stops_y':existing['proposed_all_stops_y'],
        'existing_D09_market_route':existing['adopted_route_xz'],
        'source_rules':existing['rules'],'scope':'Existing shared source interface only;do not add D04-D07 stops or claim adjacency to the shopping circuits.'},
    'protected_interfaces':['Group6 GrandPool/Orchard wet/hull and original service screen','Group8 FoodHall/orchard_exchange_lift_001/switchback','Group7 structural bearings/hull','R070 and all84 null joins'],
    'required_owner_delivery':'Hash-pinned matching receiving floor/portal,existing lift/stop identity,source mounting/structural bearing contract,screening and clean/used policies.Then test continuous physical stock routes into the unchanged circuit;source endpoint coordinates alone are not a join.',
    'scoped_delivery':'Read-only source contract;no shared registry/root/shaft/floor edits or duplicate riser construction.',
    'whole_group_accepted':False}
(ROOT/'Game/docs/group5/STAFF_RISER_INTERFACE_CONTRACT.json').write_text(json.dumps(contract,indent=2)+'\n')
print('GROUP5_STAFF_RISER_SOURCE_CONTRACT_PASS',4,8,16)
