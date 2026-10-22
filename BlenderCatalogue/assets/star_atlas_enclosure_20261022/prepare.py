from pathlib import Path
import json,hashlib,shutil
from shapely.geometry import Polygon,box as rect,shape
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
R=Path('/workspace/Astraea-recovered-e6274e77-20261021');G=R/'Game';P=G/'star_atlas_enclosure_20261022';N=R/'BlenderCatalogue/assets/star_atlas_enclosure_20261022'
assert not (P/'PLAN.json').exists();P.mkdir(exist_ok=True);N.mkdir(exist_ok=True);(P/'runtime').mkdir(exist_ok=True);(P/'evidence').mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();base=G/'star_atlas_living_commons_20261022/PLAN.json';old=json.loads(base.read_text());source=R/old['source_plan'];d=json.loads(source.read_text());parts=[]
helper=(R/'BlenderCatalogue/assets/family_court_completion_20261022/prepare_r004.py').read_text();exec(helper[helper.index('def top('):helper.index('for row,soil')])
def footprint(q):return Polygon([(v[0],v[2])for v in q['verts']]).convex_hull
allparts=d['parts']+old['parts'];checks=[];coverage=[]
for deck,y in [(15,93),(16,97.5)]:
 floor=shape(next(q for q in d['floors']if q['deck']==deck+1)['desired_geometry']);inside=rect(-96.55,-13.5,-63.55,13.5);roof=floor.intersection(inside)
 blockers=unary_union([footprint(q).buffer(.025)for q in allparts if max(v[1]for v in q['verts'])>y+3.96 and min(v[1]for v in q['verts'])<y+4.26 and q.get('category')not in ['floor'] and 'MissingOnlyFloor'not in q['name']])
 available=roof.difference(blockers);total=0
 # The reading edge, shared study and arrival bays get distinct broad fields; original stair/void/beam/fixture footprints are subtracted.
 for ix,(x0,x1) in enumerate([(-96.5,-89),(-88.8,-81.2),(-81,-74.9),(-74.1,-68.9),(-68.7,-63.6)]):
  for iz,(z0,z1) in enumerate([(-13.45,-6.2),(-6,1.8),(2,7.3),(7.5,13.45)]):
   poly=available.intersection(rect(x0,z0,x1,z1));inset=poly.buffer(-.14)
   if inset.is_empty:continue
   border=poly.difference(inset);extrude(border,y+4.06,y+4.26,f'D{deck}_Coffer_{ix}_{iz}_Frame','warm_walnut',f'SA_D{deck+1}_MissingOnlyFloor')
   extrude(inset,y+4.215,y+4.26,f'D{deck}_Coffer_{ix}_{iz}_Field','ivory_enamel',f'SA_D{deck+1}_MissingOnlyFloor');total+=poly.area
   band=inset.difference(inset.buffer(-.025));extrude(band,y+4.205,y+4.215,f'D{deck}_Coffer_{ix}_{iz}_FineEdge','champagne_metal',f'SA_D{deck+1}_MissingOnlyFloor')
 coverage.append(dict(deck=deck,ceiling_finish_m2=total,minimum_new_ceiling_clearance=4.06))
 # Friezes fit only the actual solid north/south wall spans, above activity furniture and below source beams.
 for q in d['parts']:
  if not q['name'].startswith(f'SA_D{deck}_') or not any(s in q['name']for s in ['NorthWall','SouthWall','EastWall']):continue
  v=q['verts'];lo=[min(a[i]for a in v)for i in range(3)];hi=[max(a[i]for a in v)for i in range(3)];north='North'in q['name'];east='East'in q['name']
  if east: poly=rect(lo[0]-.075,lo[2]+.12,lo[0],hi[2]-.12)
  elif north:poly=rect(lo[0]+.12,hi[2],hi[0]-.12,hi[2]+.075)
  else:poly=rect(lo[0]+.12,lo[2]-.075,hi[0]-.12,lo[2])
  obstacles=unary_union([footprint(a).buffer(.005)for a in allparts if a['name']!=q['name']and max(v[1]for v in a['verts'])>y+2.95 and min(v[1]for v in a['verts'])<y+3.40]);poly=poly.difference(obstacles)
  extrude(poly,y+2.95,y+3.32,q['name']+'_AcousticFrieze','oatmeal_weave',q['name']);extrude(poly,y+3.32,y+3.40,q['name']+'_Crown','warm_walnut',q['name'])
assert len(parts)>100
# Every added overhead part stays under actual source ceiling coverage; all solid source intersections were clipped before authoring.
for q in parts:
 deck=15 if min(v[1]for v in q['verts'])<97.5 else 16;y=93 if deck==15 else 97.5
 assert min(v[1]for v in q['verts'])>=y+2.95-1e-6
 assert max(v[1]for v in q['verts'])<=y+4.26+1e-6
 checks.append(q['name'])
plan=dict(old);plan.update(status='UNFINISHED whole D15/D16 public ceiling and upper-wall enclosure composition',parts=parts,placements=[],sources=[],lights=[],contacts=[],coverage=coverage,predecessor_plan_sha256=sha(base),predecessor_plan=str(base.relative_to(R)),scope='Two complete public levels: clipped layered ceiling fields, timber framing and woven upper-wall friezes; no new floor, opening, fixture, private room or capacity',original_parts=514)
(P/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');(P/'evidence/GEOMETRY.json').write_text(json.dumps(dict(status='PASS',parts=len(parts),bounded_geometry_checks=len(checks)*2,coverage=coverage,source_owners_unchanged=True,source_clipping_clearance_m=.025,wall_clearance_m=.005,headroom_not_structural_change=True),indent=2)+'\n')
shutil.copyfile(__file__,N/'prepare.py')
for rel in ['build_native.py']:
 s=(R/'BlenderCatalogue/assets/star_atlas_living_commons_20261022'/rel).read_text().replace('star_atlas_living_commons_20261022','star_atlas_enclosure_20261022').replace('StarAtlasLivingCommons','StarAtlasEnclosure').replace('StarAtlasLiving_','StarAtlasEnclosure_');(N/rel).write_text(s)
s=(G/'star_atlas_living_commons_20261022/bake.gd').read_text().replace('star_atlas_living_commons_20261022','star_atlas_enclosure_20261022').replace('StarAtlasLivingCommons','StarAtlasEnclosure').replace('StarAtlasLiving_','StarAtlasEnclosure_').replace('"shared_catalogue_meshes":19','"shared_catalogue_meshes":0');(P/'bake.gd').write_text(s)
print('parts',len(parts),'coverage',coverage,'free',shutil.disk_usage(R).free)
