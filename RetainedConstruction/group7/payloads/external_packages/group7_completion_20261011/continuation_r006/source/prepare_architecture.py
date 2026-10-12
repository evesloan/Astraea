"""Finite shaped planter/seat/light/table parts, with explicit physical categories."""
from pathlib import Path
import json, math
from shapely.geometry import Polygon, box
from shapely import constrained_delaunay_triangles

P = Path(__file__).resolve().parents[1]
plan = json.loads((P / 'docs/BOTANICAL_PLAN.json').read_text())
parts = []

def prism(name, poly, low, high, role, category, cell):
    assert poly.is_valid and poly.area > 1e-6 and high > low
    rings = [list(poly.exterior.coords)[:-1]] + [list(r.coords)[:-1] for r in poly.interiors]
    xy, index = [], {}
    def point(p):
        key = (round(p[0], 7), round(p[1], 7))
        if key not in index:
            index[key] = len(xy)
            xy.append(list(key))
        return index[key]
    loops = [[point(q) for q in ring] for ring in rings]
    tris = [[point(q) for q in list(tri.exterior.coords)[:3]] for tri in constrained_delaunay_triangles(poly).geoms]
    assert abs(sum(Polygon([xy[k] for k in t]).area for t in tris) - poly.area) < 1e-6
    n = len(xy)
    faces = [list(reversed(t)) for t in tris] + [[i + n for i in t] for t in tris]
    for loop in loops:
        for a, b in zip(loop, loop[1:] + loop[:1]):
            faces.append([a, b, b + n, a + n])
    parts.append({'name': name, 'vertices_world_xyz': [[x, y, z] for y in [low, high] for x, z in xy],
                  'faces': faces, 'role': role, 'category': category, 'cell': cell,
                  'volume_m3': poly.area * (high - low), 'footprint_xz': rings})

def disk(x, z, radius, count=16):
    return Polygon([(x + radius * math.cos(i * math.tau / count), z + radius * math.sin(i * math.tau / count)) for i in range(count)])

for terrace in plan['terraces']:
    cell = terrace['id']
    side, y = terrace['side'], terrace['floor_y']
    for island in terrace['islands']:
        name, x, z = island['id'], island['center'][0], island['center'][2]
        outer, soil = Polygon(island['outer_xz']), Polygon(island['soil_xz'])
        prism(name + '_WeightedFoot', outer.buffer(.025, quad_segs=2), y, y + .1, 'metal', 'solid_planter', cell)
        prism(name + '_StonePlinth', outer, y + .1, y + .34, 'stone', 'solid_planter', cell)
        prism(name + '_Soil', soil, y + .34, island['soil_y'], 'soil', 'solid_planter', cell)
        prism(name + '_NestedRim', outer.difference(soil), y + .34, y + .52, 'stone', 'solid_planter', cell)
        prism(name + '_BronzeBelt', outer.buffer(.014, quad_segs=2).difference(outer.buffer(-.025)), y + .145, y + .185, 'metal', 'solid_planter', cell)
        inner_half = box(-1000, z - island['length_m'] * .35, x, z + island['length_m'] * .35) if side == 1 else box(x, z - island['length_m'] * .35, 1000, z + island['length_m'] * .35)
        cap = outer.buffer(.25, quad_segs=2).difference(outer.buffer(-.11)).intersection(inner_half)
        seat_base = outer.buffer(.24, quad_segs=2).difference(outer.buffer(-.02)).intersection(inner_half)
        prism(name + '_SeatBase', seat_base, y + .1, y + .43, 'stone', 'solid_furniture', cell)
        prism(name + '_CurvedSeatCap', cap, y + .43, y + .49, 'wood', 'solid_furniture', cell)
        back = outer.buffer(-.065).difference(outer.buffer(-.16)).intersection(inner_half)
        prism(name + '_SeatBack', back, y + .49, y + (.75 if terrace['deck'] == 'D16' else .86), 'wood', 'solid_furniture', cell)
    for light in [q for q in plan['lights'] if q['id'].startswith('G7C6_' + terrace['deck'])]:
        name = light['source_hardware']
        px, _, z = light['post_position']
        lx = light['position'][0]
        prism(name + '_Foot', disk(px, z, .115), y, y + .13, 'metal', 'solid_fixture', cell)
        prism(name + '_FlutedPost', disk(px, z, .055, 12), y + .13, y + 3.34, 'metal', 'solid_fixture', cell)
        prism(name + '_TopReturn', box(min(px, lx) - .04, z - .04, max(px, lx) + .04, z + .04), y + 3.31, y + 3.39, 'metal', 'solid_fixture', cell)
        prism(name + '_OpenBezel', box(lx - .19, z - .22, lx + .19, z + .22).difference(box(lx - .14, z - .17, lx + .14, z + .17)), y + 3.25, y + 3.35, 'metal', 'solid_fixture', cell)
        prism(name + '_Opal', box(lx - .135, z - .165, lx + .135, z + .165), y + 3.245, y + 3.255, 'opal', 'visual_lens', cell)
    for table in [q for q in plan['tables'] if q['id'].startswith('G7C6_' + terrace['deck'])]:
        x, _, z = table['position']; name = table['id']; h = table['height_m']; r = table['radius_m']
        prism(name + '_Foot', disk(x, z, .26), y, y + .06, 'metal', 'solid_furniture', cell)
        prism(name + '_Stem', disk(x, z, .055, 12), y + .06, y + h - .055, 'metal', 'solid_furniture', cell)
        prism(name + '_Top', disk(x, z, r, 24), y + h - .055, y + h, 'wood', 'solid_furniture', cell)
    assert all(min(v[1] for v in part['vertices_world_xyz']) >= y - 1e-6 and max(v[1] for v in part['vertices_world_xyz']) < y + 3.55 for part in parts if part['cell'] == cell)
(P / 'docs/ARCHITECTURE_PARTS.json').write_text(json.dumps({'parts': parts}, separators=(',', ':')) + '\n')
print('G7_R006_FINITE_ARCHITECTURE', len(parts), 'parts', sum(p['volume_m3'] for p in parts), 'source geometric volume only; capacity held')
