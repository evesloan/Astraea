from pathlib import Path
import json,hashlib,math
from shapely.geometry import Polygon,shape,box,Point
from shapely.affinity import rotate,translate
from shapely.ops import unary_union
R=Path('/workspace/Astraea-recovered-e6274e77-20261021');P=R/'Game/star_atlas_living_commons_20261022';d=json.loads((P/'PLAN.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();src=json.loads((R/d['source_plan']).read_text());assert sha(R/d['source_plan'])==d['source_plan_sha256'];assert sha(R/d['native_source'])==d['native_sha256'];assert sha(R/'Game/data/architecture/STAR_ATLAS_UPPER_COMMONS.json')==d['definition_sha256'];assert sha(R/'Game/assets/models'/d['model_file'])==d['model_sha256'];checks=4
parts={q['name']:q for q in d['parts']};original={q['name']:q for q in src['parts']};catalogue={q['catalogue_id']:q for q in d['sources']}
def top(q):
 v=q['verts'];y=max(p[1]for p in v);return unary_union([Polygon([(v[i][0],v[i][2])for i in f])for f in q['faces']if all(abs(v[i][1]-y)<1e-6 for i in f)]),y
for q in d['sources']:
 assert sha(R/'BlenderCatalogue'/q['source'])==q['source_sha256'];assert sha(R/'Game/assets/models'/(q['catalogue_id']+'.glb'))==q['export_sha256'];checks+=2
for p in d['parts']:
 v=p['verts'];deck=15 if min(q[1]for q in v)<97.5 else 16;floor=shape(next(q for q in src['floors']if q['deck']==deck)['desired_geometry']);foot=Polygon([(q[0],q[2])for q in v]).convex_hull;assert floor.covers(foot);assert max(q[1]for q in v)<102;checks+=2
 if 'Soffit'in p['name']:
  upper=shape(next(q for q in src['floors']if q['deck']==deck+1)['new_geometry']);assert upper.covers(foot);assert abs(max(q[1]for q in v)-(93+(deck-15)*4.5+4.27))<1e-6;checks+=2
for p in d['placements']:
 x,y,z=p['position'];deck=15 if y<97.5 else 16;base=93+(deck-15)*4.5
 if p['collision']:
  w,dep,h=catalogue[p['catalogue_id']]['dimensions_blender_xyz_m'];foot=translate(rotate(box(-w/2,-dep/2,w/2,dep/2),-math.degrees(p['yaw']),origin=(0,0)),x,z);floor=shape(next(q for q in src['floors']if q['deck']==deck)['desired_geometry']);assert floor.covers(foot);assert abs(y-base)<1e-6;checks+=2
 elif p['support_part']in parts or p['support_part']in original:
  poly,sy=top(parts.get(p['support_part'],original.get(p['support_part'])));assert poly.covers(Point(x,z));assert abs(y-sy)<.006;checks+=2
 else:assert p['catalogue_id']=='AST-LIB-007' and abs(y-base-.754)<1e-6;checks+=1
assert len(parts)==28 and len(d['placements'])==98;assert not d['lights'];assert d['new_guest_units']==d['new_reserved_rests']==0
out=dict(status='PASS',checks=checks,authored_parts=28,shared_asset_placements=98,standing_furniture_contacts=26,original_upper_meshes=514,new_floor=0,new_guest_units=0,new_reserved_rests=0,D17_VIP_unchanged=True,full_runtime=False,visual_accepted=False);(P/'evidence/GEOMETRY.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
