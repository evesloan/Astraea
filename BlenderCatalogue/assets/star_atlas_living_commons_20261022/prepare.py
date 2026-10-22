from pathlib import Path
import json,hashlib,math,shutil,struct
from shapely.geometry import Polygon,Point,box as rect,shape
from shapely.affinity import scale as scale_poly,rotate,translate
from shapely import constrained_delaunay_triangles
from shapely.ops import unary_union
R=Path('/workspace/Astraea-recovered-e6274e77-20261021');P=R/'Game/star_atlas_living_commons_20261022';N=R/'BlenderCatalogue/assets/star_atlas_living_commons_20261022';P.mkdir(exist_ok=True);N.mkdir(exist_ok=True);(P/'runtime').mkdir(exist_ok=True);(P/'evidence').mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=R/'BlenderCatalogue/assets/star_atlas_upper_commons_20261009/PLAN.json';d=json.loads(source.read_text());definition=R/'Game/data/architecture/STAR_ATLAS_UPPER_COMMONS.json';D=json.loads(definition.read_text());assert sha(source)==D['plan_sha256'];assert sha(R/'Game/assets/models'/D['model_file'])==D['model_sha256'];assert shutil.disk_usage(R).free>400000000
helper=(R/'BlenderCatalogue/assets/family_court_completion_20261022/prepare_r004.py').read_text();exec(helper[helper.index('def top('):helper.index('for row,soil')]);parts=[];placements=[];contacts=[]
cat=json.loads((R/'BlenderCatalogue/catalogue_manifest.json').read_text())['assets'];catalogue={q['catalogue_id']:q for q in cat}
materials=json.loads((R/'Game/family_reading_garden_20261022/PLAN.json').read_text())['materials']
def place(name,id,p,yaw=0,scale=1,support=None,collision=True):
 placements.append(dict(name=name,catalogue_id=id,position=p,yaw=yaw,scale=scale,receiving_bed='D'+str(15 if p[1]<97.5 else 16),support_part=support,collision=collision))
for deck,y in [(15,93),(16,97.5)]:
 floor=shape(next(q for q in d['floors']if q['deck']==deck)['desired_geometry']);owner='D15_retained_structural_cover' if deck==15 else 'SA_D16_MissingOnlyFloor'
 for ti,x in enumerate([-78,-69]):
  place(f'D{deck}_SharedStudy_{ti}','AST-LIB-STUDY-01',[x,y,-9],support=owner)
  for side,z,yaw in [(0,-10.35,0),(1,-7.65,math.pi)]:
   for ci,dx in enumerate([-.62,.62]):place(f'D{deck}_StudyChair_{ti}_{side}_{ci}','AST-FUR-002',[x+dx,y,z],yaw,support=owner)
  place(f'D{deck}_OpenFolio_{ti}','AST-LIB-007',[x,y+.754,-9],.15 if ti==0 else -.2,support=f'D{deck}_SharedStudy_{ti}',collision=False)
  # Thin grounded trim defines the activity area without a raised floor or threshold.
  outline=rect(x-2.2,-11.3,x+2.2,-6.7);assert floor.covers(outline)
  extrude(outline.difference(outline.buffer(-.045)),y+.001,y+.004,f'D{deck}_StudyInlay_{ti}','champagne_metal',owner)
  # Coffered profiles bear into the actual next-floor underside at y+4.26.
  for k,z in enumerate([-11.6,-9,-6.4]):box(f'D{deck}_StudySoffit_{ti}_{k}',[x,y+4.15,z],[5.4,.24,.22],'warm_walnut',f'SA_D{deck+1}_MissingOnlyFloor')
 for bi,z in enumerate([5,9] if deck==15 else [-5,-9]):place(f'D{deck}_WindowBench_{bi}','AST-FUR-001',[-93,y,z],-math.pi/2,support=owner)
 place(f'D{deck}_WindowTable','AST-FUR-003',[-93,y,7 if deck==15 else -7],0,support=owner)
 for bi,x in enumerate([-93,-88]):
  garden_z=12 if deck==15 else -12;poly=scale_poly(Point(x,garden_z).buffer(1,quad_segs=16),1.3,.65);assert floor.covers(poly)
  extrude(poly,y,y+.52,f'D{deck}_Garden_{bi}_Plinth','warm_stone',owner)
  soil=poly.buffer(-.12);extrude(soil,y+.5,y+.54,f'D{deck}_Garden_{bi}_Soil','botanical_soil',owner);extrude(poly.difference(soil),y+.5,y+.62,f'D{deck}_Garden_{bi}_Rim','ivory_enamel',owner)
  for k in range(9):
   px=x+.86*(k-4)/4;pz=garden_z+.18*math.sin(k*2.4)
   place(f'D{deck}_Garden_{bi}_Plant{k}',['AST-BOT-002','AST-BOT-008','AST-BOT-009'][k%3],[px,y+.535,pz],k*2.4,.8,support=f'D{deck}_Garden_{bi}_Soil',collision=False)
 # Fit content onto existing reading shelves; no replacement shelf or alcove geometry.
 for q in d['parts']:
  if not q['name'].startswith(f'SA_D{deck}_AlcoveShelf_') or not q['name'].endswith(('0.85','1.55')):continue
  poly,sy=top(q);c=poly.centroid;rad=math.atan2(c.y-(-8 if deck==15 else 8),c.x+91);yaw=-rad-math.pi/2
  place(q['name']+'_Collection','AST-LIB-006',[c.x,sy,c.y],yaw,.72,support=q['name'],collision=False)
 # Exclude current source solids (including stair/guards) from all new standing furniture.
 for p in placements:
  if p['position'][1]!=y or not p['collision']:continue
  a=catalogue[p['catalogue_id']];w,dep,h=a['dimensions_blender_xyz_m'];foot=rect(-w/2,-dep/2,w/2,dep/2);foot=translate(rotate(foot,-math.degrees(p['yaw']),origin=(0,0)),p['position'][0],p['position'][2]);assert floor.covers(foot),p['name']
  for q in d['parts']:
   v=q['verts'];lo=min(vv[1]for vv in v);hi=max(vv[1]for vv in v)
   if hi<=y+.005 or lo>=y+h or q['category'] in ['floor','ceiling','fixture']:continue
   obstacle=Polygon([(vv[0],vv[2])for vv in v]).convex_hull
   assert foot.intersection(obstacle).area<1e-6,(p['name'],q['name'])
  contacts.append(dict(name=p['name'],floor_owner=owner,footprint_area=foot.area))
ids=set(q['catalogue_id']for q in placements);sources=[q.copy()for q in cat if q['catalogue_id']in ids]
for q in sources:
 b=(R/'Game/assets/models'/f"{q['catalogue_id']}.glb").read_bytes();g=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]]);q['runtime_mesh_count']=sum('mesh'in n for n in g['nodes']);assert sha(R/'BlenderCatalogue'/q['source'])==q['source_sha256']
native=next((R/'BlenderCatalogue/assets/star_atlas_upper_commons_20261009/source').glob('*.blend'))
plan=dict(status='UNFINISHED D15-D16 living commons; no D17 VIP changes',source_plan=str(source.relative_to(R)),source_plan_sha256=sha(source),native_source=str(native.relative_to(R)),native_sha256=sha(native),definition_sha256=sha(definition),model_file=D['model_file'],model_sha256=D['model_sha256'],materials=materials,parts=parts,placements=placements,sources=sources,lights=[],contacts=contacts,global_light_budget=8,scope='Four shared-study groups, two window lounges, shelf content, four planted edges and connected soffit profiles across two retained floors',new_guest_units=0,new_reserved_rests=0,original_parts=514,D17_VIP_unchanged=True)
(P/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');shutil.copyfile(__file__,N/'prepare.py');print(dict(parts=len(parts),placements=len(placements),furniture_contacts=len(contacts),families=len(sources),free=shutil.disk_usage(R).free))
