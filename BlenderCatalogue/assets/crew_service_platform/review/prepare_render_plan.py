"""Pure render setup; never runs a renderer or changes frozen source/export."""
from pathlib import Path
import json,hashlib
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
R=Path(__file__).resolve().parents[1];C=R.parents[1];G=C.parent/'astraea-godot-production-20261003';contract=json.loads((R/'source/section_contract.json').read_text());support=json.loads((R/'source/SUPPORT_OWNERSHIP_PROPOSAL.json').read_text());layout=json.loads((G/'data/spatial_layout.json').read_text());review=json.loads((R/'PARENT_SOURCE_REVIEW.json').read_text())
assert hashlib.sha256((R/'source/SUPPORT_OWNERSHIP_PROPOSAL.json').read_bytes()).hexdigest()==review['support_proposal_sha256']
def geom(p):return Polygon(p['boundary'],p.get('holes',[]))
retained=unary_union([geom(p) for p in layout['regions'] if p.get('deck')=='D03']);floor=retained.union(unary_union([geom(p) for p in contract['compiler_preview_floor_polygons']])).union(unary_union([geom(p) for p in support['exact_additional_compiler_support_polygons']]))
triangles=[list(t.exterior.coords)[:3] for t in constrained_delaunay_triangles(floor).geoms if floor.covers(t)];assert abs(sum(Polygon(t).area for t in triangles)-floor.area)<1e-6
cameras=[dict(name='01_port_bypass_turn',eye_xyz=[-103,13.65,-40.5],target_xyz=[-95,13.55,-40],purpose='normal-eye5x5m turn into3.6m clear screened cross-detour; full outside framing and supported task fittings'),dict(name='02_crew_care_receiving',eye_xyz=[-57,13.65,421.5],target_xyz=[-44,13.55,422],purpose='normal-eye care receiving branch in screened reception/consultation gap; unfinishedD05 transfer is not shown as built')]
clear=unary_union([geom(p) for p in contract['source_clear_polygons']])
for camera in cameras:
 x,y,z=camera['eye_xyz'];assert floor.covers(Point(x,z)) and clear.covers(Point(x,z));camera['eye_height_above_floor_m']=y-12;camera['supported_under_approved_source_proposal']=True;camera['eye_within_clear_source_route']=True
# All geometry remains visible; floors are new ephemeral preview nodes only.
D=dict(label='SOURCE ONLY / APPROVED SUPPORT PREVIEW / NO RUNTIME ADOPTION',floor_y=12,preview_only=True,never_save_blend=True,never_export=True,floor_triangle_xz=triangles,floor_union_area_m2=floor.area,floor_provenance='retainedD03 compiler polygons + exact unchanged reviewed route difference + parent-approved2010.2348m2 support addition',cameras=cameras,render=dict(engine='CYCLES',device='CPU',samples=32,resolution=[800,500],threads=2),lens_mm=25,source_lens_offset_y_m=.015,fixtures='actual166 exported source datum empties; body/support provenance validated',frozen_inputs={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/'source/AST-STF-010.blend',R/'exports/AST-STF-010.glb',R/'source/section_contract.json',R/'source/geometry_parts.json',R/'source/SUPPORT_OWNERSHIP_PROPOSAL.json']})
(R/'review/RENDER_PLAN.json').write_text(json.dumps(D,indent=2)+'\n');print(json.dumps(dict(preview_floor_triangles=len(triangles),cameras=cameras,frozen_inputs=D['frozen_inputs']),indent=2))
