from pathlib import Path
import json,hashlib
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[3];P=R/'Game/quiet_court_finish_20261022';d=json.loads((R/'BlenderCatalogue/assets/quiet_lift_receiving_20261009/LIFT_GEOMETRY_PLAN.json').read_text());parts={x['name']:x for x in d['parts']};bounds=json.loads((P/'evidence/RUNTIME_BOUNDS.json').read_text());checks=[]
for row in bounds['placements']:
 part=parts[row['bed']];v=part['verts'];y=max(x[1]for x in v);shape=unary_union([Polygon([(v[i][0],v[i][2])for i in f])for f in part['faces']if all(abs(v[i][1]-y)<1e-5 for i in f)]);lo=row['min'];hi=row['max'];okay=shape.buffer(.002).covers(box(lo[0],lo[2],hi[0],hi[2]));checks.append(dict(name=row['name'],complete_bounds_inside_actual_bed_polygon=okay))
failed=[x for x in checks if not x['complete_bounds_inside_actual_bed_polygon']];out=dict(status='FAIL'if failed else'PASS',checks=checks,scope='Actual packed runtime bounds against actual retained top-face polygons, including clipped inner bed. No assumption that AABB is a valid soil footprint.');(P/'evidence/FOOTPRINTS.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(checks),'failures',failed[:8]);assert not failed
