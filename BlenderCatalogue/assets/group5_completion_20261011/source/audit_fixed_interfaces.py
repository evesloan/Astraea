"""Literal original wall contacts for controls/brackets; protected street/sign footprints."""
from pathlib import Path
import json,numpy as np,math
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
def read(p):return json.loads((ROOT/p).read_text())
d=read('Game/data/architecture/group5/CONSTRUCTION.json')
old=read('BlenderCatalogue/assets/shopping_promenade_20261009/docs/PLACEMENT_AND_CONNECTORS.json')
geometry=read('BlenderCatalogue/assets/shopping_promenade_20261009/qa/source_geometry.json')
rows={r['chunk_id']:r for r in old['rooms']+old['chunks']}
contacts=[];brackets=[];signs=[];potential=[]
for row in d['doors']:
    s=1 if row['rotation_y']<0 else -1
    rotation=np.array([[0,0,-s],[0,1,0],[s,0,0]],dtype=float)
    origin=np.array(row['local_xyz'])
    sources=[]
    for part in geometry[row['chunk_id']+'__shell']:
        name=part['part'];a=np.array(part['vertices_xyz']);sources.append((name,a.min(axis=0),a.max(axis=0)))
    for c in row['controls']:
        point=origin+rotation@np.array(c['local_xyz'])
        matches=[]
        for name,lo,hi in sources:
            is_wall=any(n in name for n in ['entry_nested_jamb','__front_pier_','stock_privacy_','__rear_'])
            plane=abs(point[0]-lo[0])<1e-5 or abs(point[0]-hi[0])<1e-5
            contained=lo[1]+.16<point[1]<hi[1]-.16 and lo[2]+.08<point[2]<hi[2]-.08
            if is_wall and plane and contained:matches.append(name)
        contacts.append({'door':row['physical_id'],'control':c['id'],'source_base_xyz':point.tolist(),'original_mount_faces':matches,'passed':len(matches)==1})
    if row['local_name']=='PublicDoors':
        for x in [-1.925,1.925]:
            point=origin+rotation@np.array([x,3.8225,.17])
            matches=[name for name,lo,hi in sources if 'entry_nested_jamb' in name and (abs(point[0]-lo[0])<1e-5 or abs(point[0]-hi[0])<1e-5) and lo[1]<point[1]<hi[1] and lo[2]<point[2]<hi[2]]
            brackets.append({'door':row['physical_id'],'original_jamb_contacts':matches,'passed':len(matches)==1})
regions=read('Game/data/spatial_layout.json')['regions']
guard=unary_union([Polygon(r['boundary'],r.get('holes',[])) for r in regions if r['id']=='D09_R070_and_connected_approach'])
floors={}
for r in old['floor_proposals']:floors.setdefault(r['chunk_id'],[]).append(Polygon(r['boundary'],r['holes']))
for spec in d['wayfinding']:
    row=rows[spec['chunk_id']];x=row['position'][0]+spec['local_xyz'][0];z=row['position'][2]+spec['local_xyz'][2]
    footprint=box(x-.65,z-.15,x+.65,z+.15)
    a,b=row['clear_through_x'];street=box(a,row['bounds_xz'][1][0],b,row['bounds_xz'][1][1])
    owns=unary_union(floors[row['chunk_id']]).buffer(1e-6).covers(footprint)
    signs.append({'id':spec['id'],'floor_owned':owns,'protected_route_overlap_m2':footprint.intersection(street).area,'R070_overlap_m2':footprint.intersection(guard).area,'passed':owns and footprint.intersection(street).area<1e-7 and footprint.intersection(guard).area<1e-7})
receipt={'status':'PASS' if all(r['passed'] for r in contacts+brackets+signs) else 'HOLD','control_mount_contacts':contacts,'original_jamb_bracket_contacts':brackets,'wayfinding_floor_route_proof':signs,'scope':'594 actual source face contacts,198 bracket contacts and18 protected floor/route footprints; source wall parts are retained rectangular native solids. This is no primary load capacity or final visual acceptance.'}
(P/'qa/FIXED_INTERFACE_PROOF.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('GROUP5_FIXED_INTERFACES',receipt['status'],len(contacts),len(brackets),len(signs))
if receipt['status']!='PASS':print([r for r in contacts+brackets+signs if not r['passed']][:10])
