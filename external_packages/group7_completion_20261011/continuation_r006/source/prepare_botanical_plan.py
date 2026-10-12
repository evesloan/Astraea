"""Four composed principal terrace edges on exact immutable floor receivers."""
from pathlib import Path
import json, gzip, hashlib, math
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

P = Path(__file__).resolve().parents[1]
C = P.parent
R = C.parents[1]
(P / 'docs').mkdir(exist_ok=True)
(P / 'qa').mkdir(exist_ok=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
census = json.loads(gzip.decompress((C / 'qa/RETAINED_RUNTIME_CENSUS.json.gz').read_bytes()))['meshes']
census = [q for q in census if 'All18DeckStructuralDatums_NOT_FINISHED_ARCHITECTURE' not in q['path'] and 'CompiledStructuralFloors_NotFinishedRooms' not in q['path']]
floor_files = ['Game/data/generated/structural_meshes.json', 'Game/data/generated/received_structural_meshes.json']
floors = [q for f in floor_files for q in json.loads((R / f).read_text())['regions']]
rows = [
    ('D06', 27., -1, 'Canopy Terrace arrival garden', [(-10., 6.8), (10., 6.8)], ['AST-BOT-001', 'AST-BOT-007']),
    ('D09', 52.5, 1, 'Craft and flowering garden', [(-10., 6.8), (0., 6.2), (10., 6.8)], ['AST-BOT-001', 'AST-BOT-009']),
    ('D12', 78., -1, 'Quiet sky reading garden', [(-8.7, 10.), (8.7, 10.)], ['AST-BOT-007', 'AST-BOT-001']),
    ('D16', 97.5, 1, 'Family sky garden', [(-11., 5.5), (-3.65, 5.3), (3.65, 5.3), (11., 5.5)], ['AST-BOT-001', 'AST-BOT-007']),
]
terraces, plants, lights, seat_bays, tables = [], [], [], [], []
for deck, y, side, purpose, islands, palette in rows:
    x = side * 44
    union = unary_union([Polygon(t) for f in floors if abs(f['floor_y'] - y) < .0001 for t in f['triangles']])
    reserve = box(min(side * 42.1, side * 45.5), -14.4, max(side * 42.1, side * 45.5), 14.4)
    assert reserve.difference(union).area < 1e-7, deck
    candidates = [q['path'] for q in census if q['maximum'][1] > y + .04 and q['minimum'][1] < y + 3.55 and q['maximum'][0] > reserve.bounds[0] and q['minimum'][0] < reserve.bounds[2] and q['maximum'][2] > reserve.bounds[1] and q['minimum'][2] < reserve.bounds[3]]
    assert not candidates, (deck, candidates)
    receiving = [f['id'] for f in floors if abs(f['floor_y'] - y) < .0001 and any(Polygon(t).intersection(reserve).area > 1e-7 for t in f['triangles'])]
    contour_rows = []
    for i, (z, length) in enumerate(islands):
        contour = []
        for j in range(32):
            a = j * math.tau / 32
            # A quiet asymmetric sweep, not a repeated rectangular planter.
            v = 1.32 * math.cos(a) * (1 + .065 * math.sin(2 * a + i))
            u = length / 2 * math.sin(a)
            contour.append([x + side * v, z + u])
        poly = Polygon(contour)
        assert poly.is_valid and poly.difference(reserve).area < 1e-7
        soil = poly.buffer(-.16)
        soil_y = y + (.39 if deck != 'D09' else .46)
        contour_rows.append({'id': f'G7C6_{deck}_Island_{i}', 'outer_xz': contour,
                             'soil_xz': list(soil.exterior.coords)[:-1], 'soil_y': soil_y,
                             'floor_y': y, 'length_m': length, 'center': [x, y, z]})
        canopy_file = palette[i % len(palette)]
        # Canopy, understory and groundcover follow the island's long curve.
        if canopy_file in ['AST-BOT-001', 'AST-BOT-007']:
            plants.append({'id': f'G7C6_{deck}_Canopy_{i}', 'file': canopy_file + '.glb',
                           'position': [x + side * .1, soil_y, z], 'yaw': side * (.25 + i * .65),
                           'scale': [1, 1, 1], 'layer': 'canopy', 'island': contour_rows[-1]['id']})
        else:
            # Flower-bank island gets a canopy at its far end, retaining a low middle.
            plants.append({'id': f'G7C6_{deck}_Canopy_{i}', 'file': 'AST-BOT-001.glb',
                           'position': [x + side * .1, soil_y, z + 1.25], 'yaw': .9,
                           'scale': [1, 1, 1], 'layer': 'canopy', 'island': contour_rows[-1]['id']})
        for k, offset in enumerate([-length * .3, -length * .16, length * .16, length * .3]):
            plants.append({'id': f'G7C6_{deck}_Shrub_{i}_{k}',
                           'file': ('AST-BOT-009' if deck == 'D09' and k % 2 == 0 else 'AST-BOT-002') + '.glb',
                           'position': [x + side * (.38 if k % 2 else -.32), soil_y, z + offset],
                           'yaw': (i * .55 + k * 1.1) * side, 'scale': [1, 1, 1],
                           'layer': 'shrub', 'island': contour_rows[-1]['id']})
        for k, offset in enumerate([-length * .32, -length * .22, -.65, .65, length * .22, length * .32]):
            plants.append({'id': f'G7C6_{deck}_Groundcover_{i}_{k}', 'file': 'AST-BOT-003.glb',
                           'position': [x + side * (.78 if k % 2 else -.68), soil_y, z + offset],
                           'yaw': i + k * .8, 'scale': [1, 1, 1], 'layer': 'groundcover',
                           'island': contour_rows[-1]['id']})
        seat_bays.append({'id': f'G7C6_{deck}_SeatBay_{i}', 'floor_y': y,
                          'side': side, 'center_z': z, 'length_m': length,
                          'integrated_island': contour_rows[-1]['id']})
    # Clear centre arrival remains open on D06. Other decks receive a low shared table.
    if deck != 'D06':
        gap = -5.0 if deck == 'D09' else 0.0
        tables.append({'id': f'G7C6_{deck}_GardenTable', 'position': [side * 42.72, y, gap],
                       'radius_m': .48 if deck != 'D16' else .42, 'height_m': .66 if deck != 'D16' else .55})
    for i, z in enumerate([-11.8, 11.8]):
        lights.append({'id': f'G7C6_{deck}_GardenSource_{i}', 'position': [side * 42.18, y + 3.23, z],
                       'direction': [0, -1, 0], 'range': 10, 'energy': 1.1, 'angle': 62,
                       'color': [1, .94, .82], 'source_hardware': f'G7C6_{deck}_Lantern_{i}',
                       'post_position': [side * 45.12, y, z]})
    terraces.append({'id': f'G7C6_{deck}_ComposedEdge', 'deck': deck, 'floor_y': y, 'side': side,
                     'purpose': purpose, 'extent_m': 28.8, 'reserved_xz': list(reserve.exterior.coords)[:-1],
                     'existing_floor_receivers': receiving, 'new_floor': False,
                     'islands': contour_rows, 'normal_walk_bypass': [[side * 40.9, y, -15.5], [side * 40.9, y, 15.5]],
                     'd06_arrival_gap_z': [-6.6, 6.6] if deck == 'D06' else None,
                     'preserved_source_candidates': candidates})
pins = {f: sha(R / f) for f in floor_files + ['Game/scripts/atrium_garden.gd', 'Game/scripts/canopy_terrace.gd', 'Game/scripts/garden_overlook.gd', 'Game/assets/models/AST-GAR-001.glb', 'Game/assets/models/AST-GAR-004.glb', 'Game/assets/models/AST-GAR-005.glb', 'Game/assets/models/AST-BOT-011.glb']}
for row in plants:
    name = 'Game/assets/models/' + row['file']
    pins[name] = sha(R / name)
plan = {'schema': 'astraea.group7.botanical-sequence.v1', 'status': 'SOURCE_PLANNED_RUNTIME_AND_VISUAL_ACCEPTANCE_PENDING',
        'terraces': terraces, 'plants': plants, 'seat_bays': seat_bays, 'tables': tables,
        'lights': lights, 'source_pins': pins, 'original_plants_or_architecture_overwritten': False,
        'new_room_ids': 0, 'capacity_delta': 0, 'species_cart_horticulture_capacity_accepted': False,
        'intent': 'Four distinct principal terrace edges with three rigid original planting scales, shaped inhabited pockets and clear sightline/arrival gaps. Lower two-tree island, guards, portals, tram/lifts, all original courts and fifteen gallery rooms remain retained.'}
(P / 'docs/BOTANICAL_PLAN.json').write_text(json.dumps(plan, indent=2) + '\n')
print('G7_R006_BOTANICAL_PLAN', len(terraces), 'edges', len(plants), 'rigid source bindings', len(seat_bays), 'seat bays', len(lights), 'fixture sources')
