"""Small diagnostic floor composite and local support witnesses, never runtime."""
from pathlib import Path
import json, hashlib, sys
sys.path.insert(0, '/workspace/shared/astraea_python_deps')
import shapely
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parents[1]
ROOT = Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4')
FIRST = ROOT / 'BlenderCatalogue/assets/group3_crew_service_20261009'
riser = json.loads((HERE / 'source/PORT_SECOND_STAFF_RISER.json').read_text())
header = json.loads((HERE / 'source/PORT2_CLINICAL_HEADER.json').read_text())
clinical = json.loads((FIRST / 'extensions/clinical_streets_batch002/source/CLINICAL_STREETS.json').read_text())
compiled = json.loads((ROOT / 'Game/data/generated/structural_meshes.json').read_text())

def polys(rows):
    return unary_union([Polygon(q['boundary'], q.get('holes', [])) for q in rows])

existing = unary_union([Polygon(t) for q in compiled['regions'] if q['deck'] == 'D05' for t in q['triangles']])
reserved = polys(clinical['floor_proposal']['polygons']).union(polys(header['floor_proposal']['polygons']))
reserved = reserved.union(polys(next(q for q in riser['floor_proposals'] if q['deck'] == 'D05')['missing_floor_polygons']))
support = existing.union(reserved)
points = [(-21,-286),(-22.45,-283),(-21,-289),(-21,-291),(-33,-293),(-45,-293),(-55,-293),(-57,-293),(-33,-297),(-45,-297),(-54.6,-297),(-57,-297),(-59,-297),(-61,-297),(-57,-300),(-57,-295),(-57,-291)]
checks = []
for x,z in points:
    footprint = Point(x,z).buffer(.28)
    checks.append({'floor_point':[x,21,z], 'outside_existing_or_explicit_proposed_support_m2':footprint.difference(support).area, 'actual_compiled_supported': footprint.difference(existing).area < 1e-8, 'pass': footprint.difference(support).area < 1e-8})
assert all(q['pass'] for q in checks)
local = support.intersection(box(-64,-303,-18,-275))
triangles = []
for p in shapely.get_parts(local):
    if p.geom_type == 'Polygon':
        triangles.extend([list(t.exterior.coords)[:3] for t in shapely.constrained_delaunay_triangles(p).geoms])
report = {'status':'PASS', 'source_only_support_witnesses':checks, 'diagnostic_floor_triangles':triangles, 'diagnostic_floor_y':21, 'floor_general_exported_or_installed':False, 'scope':'Bounded D05 radius 0.28 stationary floor footprints against actual compiled floor plus explicitly held source floor proposals. No bearing structure or actual-main floor acceptance.'}
(HERE/'qa/REVIEW_SUPPORT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':'PASS','source_floor_support_witnesses':len(checks),'actual_compiled_supported':sum(q['actual_compiled_supported'] for q in checks),'diagnostic_triangles':len(triangles)}))
