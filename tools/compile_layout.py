"""Compile explicitly authored structural polygons; never generate room programmes.
Requires Shapely2.1.2. Output is runtime-independent cached mesh data.
"""
from pathlib import Path
import json,hashlib,math
import shapely
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
root=Path(__file__).resolve().parents[1]
source=root/'data/spatial_layout.json';layout=json.loads(source.read_text())
contract=json.loads((root/'data/design_contract.json').read_text())
elevations={x['deck_id']:x['floor_elevation_m'] for x in contract['deck_datums']}
shapes={}
for item in layout['regions']:
    shape=Polygon(item['boundary'],item.get('holes',[]));assert shape.is_valid,item['id']
    for void in layout['voids']:
        if item['deck'] in void['decks']:shape=shape.difference(Polygon(void['boundary']))
    shapes[item['id']]=shape
outputs=[];owned={};checks=[]
for item in layout['regions']:
    shape=shapes[item['id']]
    for other in layout['regions']:
        if other['deck']==item['deck'] and other.get('priority',0)>item.get('priority',0):shape=shape.difference(shapes[other['id']])
    assert shape.is_valid,item['id'];owned[item['id']]=shape
    if item.get('provided_by_asset'):continue
    triangles=shapely.constrained_delaunay_triangles(shape)
    total=sum(t.area for t in triangles.geoms)
    assert abs(total-shape.area)<1e-7*max(1,shape.area),(item['id'],total,shape.area)
    for t in triangles.geoms:assert shape.covers(t)
    rings=[]
    for component in shapely.get_parts(shape):
        if component.geom_type!='Polygon':continue
        p=orient(component,sign=1.0)
        rings.append([list(c) for c in p.exterior.coords[:-1]])
        rings.extend([[list(c) for c in ring.coords[:-1]] for ring in p.interiors])
    outputs.append({'id':item['id'],'deck':item['deck'],'floor_y':elevations[item['deck']]+item.get('offset_y',0),'thickness':item.get('thickness',.24),'triangles':[[list(c) for c in t.exterior.coords[:3]] for t in triangles.geoms],'rings':rings,'structural_area_m2':shape.area,'status':item['status']})
for i,a in enumerate(layout['regions']):
    for b in layout['regions'][i+1:]:
        if a['deck']==b['deck']:assert owned[a['id']].intersection(owned[b['id']]).area<1e-7,(a['id'],b['id'])
checks={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'shapely':shapely.__version__,'geos':shapely.geos_version_string,'regions':len(outputs),'triangles':sum(len(x['triangles']) for x in outputs),'polygon_validity':True,'triangle_area_conservation':True,'no_triangles_cross_voids':True,'no_coplanar_region_overlap':True,'scope':'Structural geometry only; not finished rooms, route acceptance, or capacity acceptance'}
(root/'data/generated/structural_meshes.json').write_text(json.dumps({'source_checks':checks,'regions':outputs},separators=(',',':'))+'\n')
(root/'docs/LAYOUT_COMPILE_CHECKS.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks))
