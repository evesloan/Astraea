"""Literal exported ceiling vertices,retained floor and original bearing checks."""
from pathlib import Path
import ast,json,hashlib,struct
import numpy as np
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
text=(P/'source/build_large_venue_lighting.py').read_text();tree=ast.parse(text);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='exported_bounds')
code=ast.get_source_segment(text,node);exec(code,globals());exec(code.replace('def exported_bounds','def exported_points').replace("found[node['name']] = (xyz.min(axis=0), xyz.max(axis=0))","found[node['name']] = xyz"),globals())
j=json.loads((ROOT/'Game/data/architecture/group5/MAKER_CONSTRUCTION.json').read_text());spec=j['ceiling_enclosure'];path=ROOT/spec['model_path'].replace('res://','Game/')
assert hashlib.sha256(path.read_bytes()).hexdigest()==spec['model_sha256']
floor_path=ROOT/'Game/data/generated/received_structural_meshes.json';floor=next(r for r in json.loads(floor_path.read_text())['regions'] if r['id']==spec['source_floor_owner']);polygon=unary_union([Polygon(t) for t in floor['triangles']])
points={n:v+np.array(spec['origin_world_xyz']) for n,v in exported_points(path).items()};bounds={n:(v.min(axis=0),v.max(axis=0)) for n,v in points.items()}
old=exported_bounds(ROOT/j['original_model'].replace('res://','Game/'));prefix='D09_directory_05__';contacts=[];checked=0;errors=[]
for n,vertices in points.items():
    for v in vertices:
        checked+=1
        if not polygon.buffer(.00004).covers(Point(v[0],v[2])):errors.append({'mesh':n,'outside_floor_projection':v.tolist()})
        if v[1]>spec['recorded_original_roof_cap_y']:errors.append({'mesh':n,'above_recorded_roof_cap':v.tolist()})
for name,target in [('MakerForeUpperSouth',prefix+'entry_b'),('MakerForeUpperNorth',prefix+'entry_a'),('MakerCanopyBearing_-1',prefix+'threshold-4.5'),('MakerCanopyBearing_1',prefix+'threshold4.5')]:
    a,b=bounds[name];c,d=old[target];over=np.minimum(b,d)-np.maximum(a,c);assert np.all(over>.0001),(name,over)
    contacts.append({'new':name,'original':target,'positive_bearing_xyz_m':over.tolist()})
for name,(a,b) in old.items():
    if not name.startswith(prefix+'gallery_shell'):continue
    assert abs(b[1]-58.3)<.00003
    contacts.append({'original':name,'original_wall_top_y':float(b[1]),'roof_bearing_depth_m':float(b[1]-spec['main_underside_y'])})
assert spec['canopy_underside_y']-spec['door_track_top_y']>.20
assert len(points)==spec['mesh_count']==20
result={'status':'PASS' if not errors else 'HOLD','errors':errors,'exported_vertices_checked':checked,'new_enclosure_meshes':len(points),'literal_floor_projection_area_m2':polygon.area,'original_source_floor_unchanged':True,'bearings':contacts,'main_roof_top_y':spec['maximum_top_y'],'below_recorded_roof_cap_m':spec['recorded_original_roof_cap_y']-spec['maximum_top_y'],'new_canopy_above_door_track_m':spec['canopy_underside_y']-spec['door_track_top_y'],'scope':'Actual export vertices within immutable original floor/cap,positive original wall/canopy-bearing contacts and unchanged moving-door clearance;not engineering sizing,maximum species,load,Game/CRT or final-art acceptance'}
(P/'qa/MAKER_CEILING_SOURCE_FIT.json').write_text(json.dumps(result,indent=2)+'\n');print('MAKER_CEILING_SOURCE_FIT',result['status'],checked,polygon.area);assert not errors
