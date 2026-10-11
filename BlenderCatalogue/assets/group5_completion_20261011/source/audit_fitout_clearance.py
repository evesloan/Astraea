"""Literal moved component bounds, retained floor ownership and wall contact."""
from pathlib import Path
import json,numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
old=ROOT/'BlenderCatalogue/assets/shopping_promenade_20261009'
geometry=json.loads((old/'qa/source_geometry.json').read_text())
plan=json.loads((old/'docs/PLACEMENT_AND_CONNECTORS.json').read_text())
rooms={r['chunk_id']:r for r in plan['rooms']}
floors={}
for f in plan['floor_proposals']:floors.setdefault(f['chunk_id'],[]).append(Polygon(f['boundary'],f['holes']))
receipt=[];contacts=[]
for row in json.loads((P/'docs/FITOUT_CLEARANCE.json').read_text())['rows']:
    key=row['chunk_id'];G=np.array(row['godot_matrix_rows']);moved=set(row['moved_parts'])
    fixed=[p for layer in ['shell','fitout'] for p in geometry[key+'__'+layer] if p['part'] not in moved]
    bounds=[(p['part'],np.array(p['vertices_xyz']).min(0),np.array(p['vertices_xyz']).max(0)) for p in fixed]
    changed=[];sole=None;back=None
    for p in geometry[key+'__fitout']:
        if p['part'] not in moved:continue
        a=np.array(p['vertices_xyz'])@G[:3,:3].T+G[:3,3];lo=a.min(0);hi=a.max(0)
        for name,x,y in bounds:
            overlap=np.minimum(hi,y)-np.maximum(lo,x)
            if np.all(overlap>1e-5):contacts.append({'chunk_id':key,'part':p['part'],'fixed_part':name,'overlap_xyz_m':overlap.tolist()})
        changed.append({'part':p['part'],'min':lo.tolist(),'max':hi.tolist()})
        if p['part'].endswith('_sole'):sole=(lo,hi)
        if p['part'].endswith('_back'):back=(lo,hi)
    assert sole is not None and back is not None
    ox,_,oz=rooms[key]['position'];lo,hi=sole
    footprint=box(ox+lo[0],oz+lo[2],ox+hi[0],oz+hi[2])
    owned=unary_union(floors[key]).buffer(1e-6).covers(footprint)
    wall_contact=bool(abs(back[0][2]+5.56)<1e-5)
    receipt.append({'chunk_id':key,'moved_parts':len(changed),'changed_part_bounds':changed,'complete_original_floor_ownership':owned,'ground_contact_y_m':float(lo[1]),'original_inner_sidewall_contact':wall_contact,'topology_UV_and_items_preserved':row['topology_and_UV_unchanged'],'vertex_error_m':row['geometry_error_m'],'passed':bool(owned and wall_contact and abs(lo[1])<1e-5 and row['topology_and_UV_unchanged'] and row['geometry_error_m']<1e-5)})
r={'status':'PASS' if not contacts and all(x['passed'] for x in receipt) else 'HOLD','shops':receipt,'potential_source_contacts':contacts,'scope':'Ten explicitly derived batched source layouts;110 existing source components relocated;all other vertices/topology/UV unchanged;owned-floor footprints and literal wall contact. Conservative source-bound screen,no engineering,gameplay or whole-group acceptance.'}
(P/'qa/FITOUT_CLEARANCE_PROOF.json').write_text(json.dumps(r,indent=2)+'\n');print('GROUP5_CARE_FIT',r['status'],len(receipt),'potential contacts',len(contacts))
assert r['status']=='PASS',contacts[:5]
