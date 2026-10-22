from pathlib import Path
import json,hashlib,math,shutil,struct
from shapely.geometry import Polygon,Point,box as rect,shape
from shapely import constrained_delaunay_triangles
from shapely.ops import unary_union
R=Path('/workspace/Astraea-recovered-e6274e77-20261021');P=R/'Game/family_enclosure_finish_20261022';N=R/'BlenderCatalogue/assets/family_enclosure_finish_20261022'
P.mkdir(exist_ok=True);N.mkdir(exist_ok=True);(P/'runtime').mkdir(exist_ok=True);(P/'evidence').mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();old=json.loads((R/'Game/family_reading_garden_20261022/PLAN.json').read_text());d=json.loads((R/old['source_plan']).read_text());assert sha(R/old['source_plan'])==old['source_plan_sha256'];assert shutil.disk_usage(R).free>500000000
helper=(R/'BlenderCatalogue/assets/family_court_completion_20261022/prepare_r004.py').read_text();exec(helper[helper.index('def top('):helper.index('for row,soil')]);parts=[];placements=[];lights=[]
materials={**old['materials'],'arch_limestone':{'color':[.79,.71,.57,1],'roughness':.8,'metallic':0},'recess_plaster':{'color':[.58,.46,.31,1],'roughness':.94,'metallic':0},'reveal_walnut':{'color':[.22,.095,.035,1],'roughness':.58,'metallic':0}}
# Extrude a YZ silhouette inward from the existing wall. Rotation preserves winding.
def wallpoly(poly,front,back,name,role,owner):
 extrude(poly,front,back,name,role,owner)
 for v in parts[-1]['verts']:v[:]=[v[1],v[2],v[0]] # old plane(u=z,v=y), extrusion=x; even permutation
for bi,(z0,z1) in enumerate([(261,293),(293,325)]):
 owner='FT_CourtEnclosure_1_3_0';center=(z0+z1)/2
 outer=[(z0,84),(z0,94)]+[(center-16*math.cos(math.pi*j/48),94+7.7*math.sin(math.pi*j/48))for j in range(49)]+[(z1,84)]
 inner=[(z0+.75,84),(z0+.75,94)]+[(center-15.25*math.cos(math.pi*j/48),94+6.9*math.sin(math.pi*j/48))for j in range(49)]+[(z1-.75,84)]
 shell=Polygon(outer).buffer(0);opening=Polygon(inner).buffer(0);profile=shell.difference(opening);assert profile.area>0
 wallpoly(profile,98.82,99.94,f'GrandArch_{bi}','arch_limestone',owner)
 # A secondary dark reveal makes the entire large arch read as depth, not a flat drawn outline.
 reveal=opening.difference(opening.buffer(-.24));wallpoly(reveal,99.18,99.94,f'ArchShadowReveal_{bi}','reveal_walnut',owner)
 wallpoly(opening.buffer(-.25),99.86,99.94,f'RecessField_{bi}','recess_plaster',owner)
 # Continuous low dado follows the existing wall; no new circulation surface.
 box(f'Dado_{bi}',[99.7,85.1,center],[.46,2.2,30.5],'warm_stone','FT_CourtEnclosure_1_0_0')
 # Articulated arch keystone and collector align with the retained wall crown.
 box(f'ArchCrown_{bi}',[99.1,101.45,center],[1.6,.5,1.5],'ivory_enamel',owner)
 # Wall-mounted down-wash: visible receiver testing remains with the existing budget.
 box(f'WallwashArm_{bi}',[98.1,100.9,center],[3.65,.14,.18],'champagne_metal',owner)
 box(f'WallwashHousing_{bi}',[96.35,100.85,center],[.55,.32,.8],'warm_walnut',owner)
 box(f'WallwashLens_{bi}',[96.35,100.66,center],[.4,.08,.62],'lens',owner)
 lights.append(dict(name=f'FamilyArchWash_{bi}',kind='spot',position=[96.35,100.58,center],target=[99.7,94.8,center],receiver=[99.78,94.8,center],energy=3.2,range=25,angle=68,color=[1,.91,.75]))
for pi,z in enumerate([261,293,325]):
 owner=f'FT_CourtPier_{pi}_99.52_0';assert any(q['name']==owner for q in d['parts'])
 # Three continuous profiled pilasters bind the large arches to actual retained piers.
 box(f'PierBacking_{pi}',[99.25,92.85,z],[1.35,17.7,1.4],'arch_limestone',owner)
 box(f'PierFlute_{pi}',[98.52,93.2,z],[.2,17.0,.42],'warm_walnut',owner)
 # Two substantial attached planted bowls per pier, above standing headroom; never decks.
 for ti,y in enumerate([88.3,94.0]):
  poly=Point(98.75,z).buffer(1,quad_segs=16)
  from shapely.affinity import scale
  poly=scale(poly,1.05,2.65);poly=poly.intersection(rect(97.7,z-3,99.94,z+3))
  extrude(poly,y,y+.55,f'PierGarden_{pi}_{ti}_Bowl','warm_stone',owner)
  soil=poly.buffer(-.14);extrude(soil,y+.53,y+.57,f'PierGarden_{pi}_{ti}_Soil','botanical_soil',owner)
  rim=poly.difference(soil);extrude(rim,y+.52,y+.68,f'PierGarden_{pi}_{ti}_Rim','ivory_enamel',owner)
  box(f'PierGarden_{pi}_{ti}_Bracket',[99.2,y-.18,z],[1.4,.45,.65],'champagne_metal',owner)
  for j in range(13):
   px=98.75+.42*math.sin(j*2.399);pz=z+1.96*(j-6)/6
   assert soil.covers(Point(px,pz))
   placements.append(dict(name=f'PierPlant_{pi}_{ti}_{j}',catalogue_id=['AST-BOT-002','AST-BOT-008','AST-BOT-009'][j%3],position=[px,y+.565,pz],scale=.95 if j%3==0 else .85,yaw=j*2.399,receiving_bed=owner,support_part=f'PierGarden_{pi}_{ti}_Soil'))
 # Crown lies above the clerestory band; capped/connected to the original roof underside106.02.
 for k,(x,width,y,height,role) in enumerate([(99.22,1.45,105.93,.22,'arch_limestone'),(98.73,.28,105.77,.18,'warm_walnut'),(99.45,1.1,106.0,.06,'ivory_enamel')]):
  box(f'CeilingEdge_{pi}_{k}',[x,y,z+0 if pi==2 else z+8],[width,height,16 if pi<2 else 1.4],role,'FT_PrincipalOpaqueCover_0')
# Continuous ceiling-edge infill between profiles; stops before the retained upper gathering destination.
for i,z in enumerate([285,317]):
 box(f'CeilingEdgeLink_{i}',[99.22,105.93,z],[1.45,.22,16],'arch_limestone','FT_PrincipalOpaqueCover_0')
cat=json.loads((R/'BlenderCatalogue/catalogue_manifest.json').read_text())['assets'];sources=[q for q in cat if q['catalogue_id']in set(p['catalogue_id']for p in placements)]
for q in sources:
 b=(R/'Game/assets/models'/f"{q['catalogue_id']}.glb").read_bytes();g=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]]);q['runtime_mesh_count']=sum('mesh'in n for n in g['nodes'])
plan={**old,'parts':parts,'placements':placements,'sources':sources,'materials':materials,'lights':lights,'relocations':[],'scope':'Two32m full-height wall arches, three retained-pier compositions, six elevated planted bowls, profiled roof-edge connection; additive interior treatment only','reading_garden_parent_sha256':sha(R/'Game/family_reading_garden_20261022/adapter.gd'),'status':'UNFINISHED enclosure finish; source integration subject to focused checks','global_light_budget':8,'clerestory_clear_band_y':[102,105.68]}
(P/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');shutil.copyfile(__file__,N/'prepare.py');print(json.dumps({'parts':len(parts),'plants':len(placements),'lights':len(lights),'free':shutil.disk_usage(R).free}))
