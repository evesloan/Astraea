"""Compile additive authored receiving floors through the existing slab format.
Does not allocate rooms, alter the original compiled owners, or claim traversal.
"""
from pathlib import Path
import json,hashlib,math
import shapely
from shapely.geometry import Polygon,box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

def compile_received(root,source):
    root=Path(root)
    base_path=root/'data/generated/structural_meshes.json'
    base=json.loads(base_path.read_text())
    contract=json.loads((root/'data/design_contract.json').read_text())
    datums={r['deck_id']:r['floor_elevation_m'] for r in contract['deck_datums']}
    layout=json.loads((root/'data/spatial_layout.json').read_text())
    programmes={r['programme_key']:r for r in json.loads((root/'data/whole_ship_layout.json').read_text())['programmes']}
    old=[(r,unary_union([Polygon(t) for t in r['triangles']])) for r in base['regions']]
    outputs=[];new_shapes=[];ids={r['id'] for r in base['regions']}
    for item in source['regions']:
        assert item['id'] not in ids;ids.add(item['id'])
        programme=programmes[item['programme_key']];deck=programme['deck'];y=datums[deck]
        shape=Polygon(item['boundary'],item.get('holes',[]));assert shape.is_valid and shape.area>0
        envelope=box(programme['allocation_x'][0],programme['allocation_z'][0],programme['allocation_x'][1],programme['allocation_z'][1])
        if item['kind']=='authored_room_floor':assert envelope.buffer(1e-7).covers(shape)
        else:assert item['kind']=='explicit_connection' and item.get('connection_to') in {r['id'] for r in base['regions']}
        for void in layout['voids']:
            if deck in void['decks']:assert shape.intersection(Polygon(void['boundary'])).area<1e-7
        for row,prior in old+new_shapes:
            area=shape.intersection(prior).area
            if abs(row['floor_y']-y)<1e-6:assert area<1e-7,(item['id'],row['id'],'coplanar_overlap')
            elif area>1e-7:assert min(y,row['floor_y'])-max(y-.24,row['floor_y']-row['thickness'])<1e-6
        triangles=[list(t.exterior.coords)[:3] for t in shapely.constrained_delaunay_triangles(shape).geoms]
        assert abs(sum(Polygon(t).area for t in triangles)-shape.area)<1e-7*max(1,shape.area)
        chunks=[];x0,z0,x1,z1=shape.bounds
        for x in range(math.floor(x0/8),math.ceil(x1/8)):
            for z in range(math.floor(z0/8),math.ceil(z1/8)):
                piece=shape.intersection(box(x*8,z*8,(x+1)*8,(z+1)*8))
                if piece.area>1e-8:chunks.append({'id':f'cell_{x}_{z}','triangles':[list(t.exterior.coords)[:3] for t in shapely.constrained_delaunay_triangles(piece).geoms]})
        normalized=orient(shape,sign=1)
        row={'id':item['id'],'deck':deck,'floor_y':y,'thickness':.24,'triangles':triangles,'rings':[list(normalized.exterior.coords)[:-1]]+[list(r.coords)[:-1] for r in normalized.interiors],'structural_area_m2':shape.area,'render_chunks':chunks,'status':'received_section_structural_candidate','material_role':item.get('material_role','guest_floor')}
        outputs.append(row);new_shapes.append((row,shape))
    return {'source_checks':{'baseline_structural_sha256':hashlib.sha256(base_path.read_bytes()).hexdigest(),'baseline_owner_count':len(old),'new_owner_count':len(outputs),'no_coplanar_overlap':True,'voids_preserved':True,'slab_volumes_disjoint':True,'scope':'Additive authored geometry; operational and visual acceptance separate'},'regions':outputs}

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    source=json.loads((root/'data/architecture/received_section_floors.json').read_text())
    result=compile_received(root,source)
    (root/'data/generated/received_structural_meshes.json').write_text(json.dumps(result,separators=(',',':'))+'\n')
    print(json.dumps(result['source_checks']))
