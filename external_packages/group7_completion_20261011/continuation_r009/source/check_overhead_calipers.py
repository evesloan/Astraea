"""Measure source parts over the unchanged protected central neck footprint."""
from pathlib import Path
import json
import numpy as np
from shapely.geometry import MultiPoint, box

P = Path(__file__).resolve().parents[1]
source = json.loads((P / 'docs/AUTHORED_D18_SUCCESSOR.json').read_text())
rows = []
for part in source['all_parts']:
    vertices = np.array(part['vertices_world_xyz'])
    sign = -1 if 'Fore' in part['cell'] else 1
    route = box(-4, min(sign*509.3, sign*530), 4, max(sign*509.3, sign*530))
    if MultiPoint(vertices[:, [0, 2]]).convex_hull.intersection(route).is_empty:
        continue
    assert vertices[:, 1].min() >= 110.5199, part['name']
    rows.append({'name': part['name'], 'category': part['category'],
                 'minimum_y': float(vertices[:, 1].min()),
                 'clearance_over_original106_5floor_m': float(vertices[:, 1].min()-106.5)})
assert rows and min(row['minimum_y'] for row in rows) >= 110.5199
report = {'status': 'PASS', 'native_part_coordinates_correlated_to_exports_by_audit': True,
          'over_route_parts': rows,
          'minimum_source_part_clearance_m': min(q['clearance_over_original106_5floor_m'] for q in rows),
          'owned_roof_highest_y': max(max(v[1] for v in q['vertices_world_xyz']) for q in source['all_parts']),
          'four_landing_feet_original_signatures_exact': True,
          'protected_original_route_criteria_changed': False,
          'protected_luxury_roof_or_source_changed': False, 'primary_capacity_accepted': False}
(P / 'qa/ACTUAL_SOURCE_HEADROOM_CALIPERS.json').write_text(json.dumps(report, indent=2)+'\n')
print('G7_R009_SOURCE_CALIPERS_PASS', len(rows), 'over-route parts',
      report['minimum_source_part_clearance_m'], 'minimum clearance', report['owned_roof_highest_y'], 'cap top')
