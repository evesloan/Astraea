"""Explicit diagnostic floor and exact retained-cell cross-section checks."""
from pathlib import Path
import json, math, sys
sys.path.insert(0,'/workspace/shared/astraea_python_deps')
import shapely
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
HERE=Path(__file__).resolve().parents[1];ROOT=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4')
FIRST=ROOT/'BlenderCatalogue/assets/group3_crew_service_20261009'
branch=json.loads((HERE/'source/D03_PORT2_BRANCH.json').read_text());patch=json.loads((HERE/'source/D03_SPINE_RECEIVER_PATCH.json').read_text())
original=json.loads((ROOT/patch['predecessor']['geometry_parts_path']).read_text())['boxes']
original=[q for q in original if q['name']in patch['original_semantic_parts_in_these_batches']]
sections=[]
for y in [12.31,12.8,13.5,14.79,14.81,15.1,15.21]:
    for role in patch['runtime_batch_name_by_role']:
        before=unary_union([box(q['world_aabb'][0],q['world_aabb'][4],q['world_aabb'][1],q['world_aabb'][5])for q in original if q['role']==role and q['world_aabb'][2]<y<q['world_aabb'][3]])
        after=unary_union([box(q['aabb'][0],q['aabb'][4],q['aabb'][1],q['aabb'][5])for q in patch['parts']if q['role']==role and q['aabb'][2]<y<q['aabb'][3]])
        expected=before.difference(box(-55.345,-294.8,-55.2,-291.2)) if y<14.8 else before
        error=after.symmetric_difference(expected).area
        sections.append({'world_y':y,'material_role':role,'cross_section_symmetric_error_m2':error,'pass':error<1e-8})
assert all(q['pass']for q in sections)
compiled=json.loads((ROOT/'Game/data/generated/structural_meshes.json').read_text())
actual=unary_union([Polygon(t)for q in compiled['regions']if q['deck']=='D03'for t in q['triangles']])
riser=json.loads((FIRST/'extensions/port2_clinical_batch006/source/PORT_SECOND_STAFF_RISER.json').read_text());landing=next(q for q in riser['floor_proposals']if q['deck']=='D03')
held=unary_union([Polygon(q['boundary'],q['holes'])for q in branch['floor_proposal']['polygons']+landing['missing_floor_polygons']])
floor=actual.union(held)
points=[[-21,12,-286],[-21,12,-289],[-21,12,-291],[-31,12,-293],[-41,12,-293],[-51,12,-293],[-55,12,-293],[-57,12,-293],[-57,12,-295],[-57,12,-291],[-57,12,-218],[-55,12,-216],[-53.5,12,-216]]
checks=[]
for p in points:
    footprint=Point(p[0],p[2]).buffer(.28);outside=footprint.difference(floor).area
    checks.append({'floor_point':p,'outside_actual_or_explicit_proposed_support_m2':outside,'actual_compiled_supported':footprint.difference(actual).area<1e-8,'pass':outside<1e-8})
assert all(q['pass']for q in checks)
local=floor.intersection(box(-60,-301,-18,-212));triangles=[]
for q in shapely.get_parts(local):
    if q.geom_type=='Polygon':triangles.extend([list(t.exterior.coords)[:3]for t in shapely.constrained_delaunay_triangles(q).geoms])
(HERE/'qa/REVIEW_SUPPORT_AND_PATCH.json').write_text(json.dumps({'status':'PASS','retained_cell_role_cross_sections':sections,'bounded_floor_footprints':checks,'diagnostic_floor_triangles':triangles,'floor_y':12,'general_floor_exported_or_installed':False,'scope':'Twenty-eight exact old/new material-height source cross-sections plus thirteen stationary footprint witnesses. Actual and explicitly proposed floors remain distinct.'},indent=2)+'\n')
print(json.dumps({'status':'PASS','patch_cross_sections':len(sections),'floor_footprints':len(checks),'actual_compiled_supported':sum(q['actual_compiled_supported']for q in checks),'diagnostic_triangles':len(triangles)}))
