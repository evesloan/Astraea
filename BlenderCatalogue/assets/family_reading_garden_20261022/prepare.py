from pathlib import Path
import json,hashlib,math,shutil,struct
from shapely.geometry import Polygon,Point,shape,box as rect,LineString
from shapely.affinity import scale as scale_poly
from shapely import constrained_delaunay_triangles
from shapely.ops import unary_union
R=Path('/workspace/Astraea-recovered-e6274e77-20261021');P=R/'Game/family_reading_garden_20261022';N=R/'BlenderCatalogue/assets/family_reading_garden_20261022'
P.mkdir(exist_ok=True);N.mkdir(exist_ok=True);(P/'runtime').mkdir(exist_ok=True);(P/'evidence').mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((R/'Game/family_court_completion_20261022/PLAN_R004.json').read_text());d=json.loads((R/old['source_plan']).read_text());assert sha(R/old['source_plan'])==old['source_plan_sha256'];assert shutil.disk_usage(R).free>500000000
# Reuse proven winding helper without executing the predecessor's authoring loops.
helper=(R/'BlenderCatalogue/assets/family_court_completion_20261022/prepare_r004.py').read_text();exec(helper[helper.index('def top('):helper.index('for row,soil')])
parts=[q for q in old['parts'] if not q['name'].startswith(('WallReveal_','WallInset_'))];placements=[];relocations=[];checks=[]
materials=old['materials'];materials['warm_stone']['color']=[.69,.59,.43,1]
base=next(q for q in d['floor_regions']if q['name']=='FT_PrincipalTerraceCourtBase');floor=shape(base['geometry']);assert base['floor_y']==84
beds=[q for q in d['parts']if q['name']in ['FT_RootedGardenSoil_0_0','FT_RootedGardenSoil_1_0']]
for bi,(zc,benchx) in enumerate([(282,93.1),(319,92.1)]):
 # Two open-ended timber reading shelters: support only on the existing public court.
 # Open west face frames the garden; east through-route stays outside X96.2.
 for side,x in enumerate([benchx-1.35,benchx+1.65]):
  for end,z in enumerate([zc-2.6,zc+2.6]):
   foot=rect(x-.14,z-.14,x+.14,z+.14);assert floor.covers(foot)
   box(f'Alcove{bi}_Post_{side}_{end}',[x,85.52,z],[.28,3.06,.28],'warm_walnut',base['name']);checks.append({'kind':'floor_contact','part':parts[-1]['name'],'owner':base['name'],'overlap_m':.01})
 # Cambered ribs spring from the posts; 2.8m minimum underside, no walkable deck.
 for end,z in enumerate([zc-2.6,zc+2.6]):
  for j in range(12):
   x0=benchx-1.35+3*j/12;x1=x0+.25
   y0=87.0+.42*math.sin(math.pi*j/12);y1=87.0+.42*math.sin(math.pi*(j+1)/12)
   verts=[[x0,y0,z-.12],[x1,y1,z-.12],[x1,y1+.2,z-.12],[x0,y0+.2,z-.12],[x0,y0,z+.12],[x1,y1,z+.12],[x1,y1+.2,z+.12],[x0,y0+.2,z+.12]]
   parts.append(dict(name=f'Alcove{bi}_Arch_{end}_{j}',role='warm_walnut',owner=base['name'],verts=verts,faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[3,7,6,2],[0,4,7,3],[1,2,6,5]]))
 for j in range(11):
  x=benchx-1.35+3*j/10;y=87.22+.42*math.sin(math.pi*j/10)
  box(f'Alcove{bi}_ShadeSlat_{j}',[x,y,zc],[.14,.12,5.46],'ivory_enamel',base['name'])
 # Low side reading ledges do not add seats or intrude on the west/front approach.
 for end,z in enumerate([zc-2.2,zc+2.2]):
  box(f'Alcove{bi}_ReadingPier_{end}',[benchx+.7,84.3,z],[.6,.62,.65],'warm_stone',base['name'])
  box(f'Alcove{bi}_ReadingSurface_{end}',[benchx+.7,84.64,z],[.85,.08,.85],'warm_walnut',base['name'])
 # Six terraced planted islands sit entirely inside the retained soil footprint.
 soil,sy=top(beds[bi]);tiers=[]
 for ti,(dx,dz,rx,rz,height) in enumerate([(-2.8,-7,2.0,2.3,.45),(2.3,6,2.1,2.4,.85),(-1.7,4.1,1.8,2.1,1.3)] if bi==0 else [(-2.0,-4.7,1.6,1.7,.45),(1.7,4.6,1.7,1.8,.85),(-1.4,2.2,1.5,1.6,1.3)]):
  x,z=83+dx,zc+dz;poly=scale_poly(Point(x,z).buffer(1,quad_segs=12),rx,rz);assert soil.covers(poly)
  # Retained tree trunk remains outside new raised soil.
  assert not poly.buffer(.7).covers(Point(83,zc))
  rim=poly.difference(poly.buffer(-.13));extrude(poly,84.49,84.5+height-.1,f'Garden{bi}_Tier{ti}_Base','warm_stone',beds[bi]['name']);extrude(rim,84.5+height-.1,84.5+height+.05,f'Garden{bi}_Tier{ti}_Rim','ivory_enamel',beds[bi]['name']);extrude(poly.buffer(-.13),84.5+height-.12,84.5+height-.04,f'Garden{bi}_Tier{ti}_Soil','botanical_soil',beds[bi]['name']);tiers.append((poly,x,z,rx,rz,84.5+height-.045,ti))
  for j in range(14):
   ang=j*2.399963;r=.24+.48*((j%4)/3);px=x+rx*r*math.cos(ang);pz=z+rz*r*math.sin(ang)
   placements.append(dict(name=f'Garden{bi}_Layer{ti}_{j}',catalogue_id=['AST-BOT-002','AST-BOT-003','AST-BOT-008','AST-BOT-009'][j%4],position=[px,84.5+height-.045,pz],yaw=ang,scale=.9 if j%4!=1 else 1.2,receiving_bed=beds[bi]['name'],support_part=f'Garden{bi}_Tier{ti}_Soil'))
 # Preserve every original plant object; lift only those affected by a new island.
 for row in d['asset_instances']:
  if not row['name'].startswith(f'FT_GardenUnderplant_{bi}_'):continue
  x,y,z=row['world_xyz'];matches=[t for t in tiers if t[0].buffer(.5).covers(Point(x,z))]
  if matches:
   t=matches[0];relocations.append(dict(name=row['name'],source=row,target_position=[t[1]+.4*math.cos(len(relocations)*2.4),t[5],t[2]+.4*math.sin(len(relocations)*2.4)],reason='retain original object above raised soil instead of burying it'))
 # Layered canopy crowns remain in the open principal court, not over room floors.
 for ci,(zoff,scl) in enumerate([(-8,.69),(9,.52)] if bi==0 else [(-6,.57),(7,.46)]):
  x=83.0;z=zc+zoff;assert soil.covers(Point(x,z).buffer(.6));placements.append(dict(name=f'Garden{bi}_Canopy{ci}',catalogue_id='AST-BOT-011',position=[x,84.5,z],yaw=.7+ci*1.8+bi,scale=scl,receiving_bed=beds[bi]['name'],support_part=beds[bi]['name']))
 # Verifiable clear route and seat-front approach, no new solid occupies them below headroom.
 approach=rect(benchx-1.0,zc-1.5,benchx-.5,zc+1.5)
 for q in parts:
  if not q['name'].startswith(f'Alcove{bi}_') or min(v[1]for v in q['verts'])>86.6:continue
  footprint=Polygon([(v[0],v[2])for v in q['verts']]).convex_hull
  assert not footprint.intersects(approach),q['name']
 checks.append({'kind':'seat_approach','bench':f'FT_GardenPauseBench_{bi}','clear_box_xz':list(approach.bounds)})
cat=json.loads((R/'BlenderCatalogue/catalogue_manifest.json').read_text())['assets'];ids=sorted(set(p['catalogue_id']for p in placements));sources=[q for q in cat if q['catalogue_id']in ids]
for q in sources:
 b=(R/'Game/assets/models'/f"{q['catalogue_id']}.glb").read_bytes();g=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]]);q['runtime_mesh_count']=sum('mesh'in n for n in g['nodes']);assert sha(R/'BlenderCatalogue'/q['source'])==q['source_sha256']
plan={**old,'status':'UNFINISHED spatial successor; prior wall-grid candidate unselected','parts':parts,'placements':placements,'sources':sources,'relocations':relocations,'scope':'Two public reading alcoves, six terraced planted islands and four layered canopy trees; original floor/support/wall/clerestory unchanged','checks':checks,'materials':materials,'rejected_grid_parts_removed_from_successor':80,'original_native_revisions_preserved':True}
(P/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');shutil.copyfile(__file__,N/'prepare.py');print(json.dumps({'parts':len(parts),'new_plants':len(placements),'relocated_originals':len(relocations),'floor_checks':len(checks),'sources':len(sources)}))
