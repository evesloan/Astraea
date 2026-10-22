from pathlib import Path
import json,hashlib,math,shutil
from shapely.geometry import Polygon,Point
from shapely import constrained_delaunay_triangles
from shapely.ops import unary_union,triangulate
R=Path('/workspace/Astraea-recovered-e6274e77-20261021');P=R/'Game/family_court_completion_20261022';N=R/'BlenderCatalogue/assets/family_court_completion_20261022'
P.mkdir(exist_ok=True);N.mkdir(exist_ok=True);(P/'evidence').mkdir(exist_ok=True);(P/'runtime').mkdir(exist_ok=True)
source=R/'BlenderCatalogue/assets/family_lift_receiving_20261009/LIFT_GEOMETRY_PLAN.json';d=json.loads(source.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert shutil.disk_usage(R).free>500_000_000
materials={'warm_stone':{'color':[.64,.53,.38,1],'roughness':.73,'metallic':0},'ivory_enamel':{'color':[.82,.77,.64,1],'roughness':.6,'metallic':0},'warm_walnut':{'color':[.27,.13,.055,1],'roughness':.55,'metallic':0},'oatmeal_weave':{'color':[.66,.54,.36,1],'roughness':.92,'metallic':0},'champagne_metal':{'color':[.5,.36,.18,1],'roughness':.36,'metallic':.65},'lens':{'color':[1,.84,.58,1],'roughness':.4,'metallic':0},'botanical_soil':{'color':[.085,.052,.027,1],'roughness':1,'metallic':0}}
parts=[];placements=[];lights=[];checks=[]
def top(row):
 vs=row['verts'];y=max(v[1]for v in vs);polys=[Polygon([(vs[i][0],vs[i][2])for i in f])for f in row['faces']if all(abs(vs[i][1]-y)<1e-6 for i in f)];return unary_union([p for p in polys if p.area>1e-8]),y
def extrude(poly,lo,hi,name,role,owner):
 verts=[];faces=[]
 for g in ([poly] if poly.geom_type=='Polygon'else poly.geoms):
  tris=list(constrained_delaunay_triangles(g).geoms);assert abs(sum(t.area for t in tris)-g.area)<1e-4
  for t in tris:
   coords=list(t.exterior.coords)[:3];coords=coords if t.exterior.is_ccw else list(reversed(coords));base=len(verts);verts.extend([[x,lo,z]for x,z in coords]+[[x,hi,z]for x,z in coords]);faces.extend([[base+i for i in [0,1,2]],[base+i for i in [5,4,3]]])
  from shapely.geometry.polygon import orient
  g=orient(g,sign=1)
  for ring in [g.exterior,*g.interiors]:
   cs=list(ring.coords)
   for (x,z),(xx,zz)in zip(cs,cs[1:]):
    b=len(verts);verts.extend([[x,lo,z],[xx,lo,zz],[xx,hi,zz],[x,hi,z]]);faces.append([b+3,b+2,b+1,b])
 parts.append(dict(name=name,role=role,owner=owner,verts=verts,faces=faces))
def box(name,center,size,role,owner):
 x,y,z=center;sx,sy,sz=size;extrude(Polygon([(x-sx/2,z-sz/2),(x+sx/2,z-sz/2),(x+sx/2,z+sz/2),(x-sx/2,z+sz/2)]),y-sy/2,y+sy/2,name,role,owner)
for row,soil in zip([x for x in d['parts']if x['category']=='planter' and ('RootedGarden' in x['name']) and x['name'].endswith(('_0_0','_1_0'))],[x for x in d['parts']if x['category']=='soil' and ('RootedGarden' in x['name']) and x['name'].endswith(('_0_0','_1_0'))]):
 p,y=top(row);soil_poly,soil_y=top(soil);assert p.covers(soil_poly);p=p.difference(soil_poly);assert p.intersection(soil_poly).area<1e-7
 extrude(soil_poly,y-.005,y+.006,'SoilFinish_'+soil['name'],'botanical_soil',soil['name'])
 extrude(p,y-.01,y+.06,'Coping_'+row['name'],'warm_stone',row['name']);checks.append(dict(owner=row['name'],footprint_area=p.area,positive_contact_m=.01))
existing=d['asset_instances']
for bi,row in enumerate([x for x in d['parts']if x['category']=='soil' and ('RootedGarden' in x['name']) and x['name'].endswith(('_0_0','_1_0'))]):
 p,y=top(row);safe=p.buffer(-(.31 if p.area<4 else .52));assert not safe.is_empty
 target=18 if p.area>200 else (9 if p.area>50 else (3 if p.area>4 else 2))
 # Deterministic staggered clusters, confined to exact soil and clear of retained trunks/furnishings.
 minx,minz,maxx,maxz=safe.bounds;candidates=[]
 for ix in range(1,12):
  for iz in range(1,20):
   x=minx+(maxx-minx)*ix/12;z=minz+(maxz-minz)*iz/20
   if not safe.covers(Point(x,z)):continue
   if any(abs(float(a['world_xyz'][1])-y)<2 and math.hypot(x-a['world_xyz'][0],z-a['world_xyz'][2])<1.5 for a in existing):continue
   candidates.append((x,z))
 selected=[]
 for i in range(target):
  if not candidates:break
  if not selected:pick=min(candidates,key=lambda q:(q[0]-(minx+maxx)/2)**2+(q[1]-(minz+maxz)/2)**2)
  else:pick=max(candidates,key=lambda q:min(math.hypot(q[0]-s[0],q[1]-s[1])for s in selected))
  if selected and min(math.dist(pick,s)for s in selected)<.55:break
  selected.append(pick);candidates.remove(pick)
 for i,(x,z)in enumerate(selected):
  scale=.55 if p.area<4 else (.65 if p.area<10 else .9)
  assert p.covers(Point(x,z).buffer(.55*scale))
  placements.append(dict(name=f'Understory_{bi:02}_{i:02}',catalogue_id='AST-BOT-008'if (i+bi)%2==0 else'AST-BOT-009',position=[x,y+.021,z],yaw=(i*2.399+bi*.41)%(2*math.pi),scale=scale,receiving_bed=row['name']))
for i,row in enumerate([x for x in d['parts']if x['category']=='ceiling_rib' and x['kind']=='beam' and x['a'][2]<350]):
 a,b=row['a'],row['b'];x=(a[0]+b[0])/2;z=a[2];length=abs(a[0]-b[0]);box(f'RibReveal_{i}',[x,105.745,z],[length,.06,.38],'warm_walnut',row['name']);box(f'CanopyHousing_{i}',[x,105.64,z],[.65,.18,1.2],'champagne_metal',row['name']);box(f'CanopyLens_{i}',[x,105.545,z],[.52,.05,1.05],'lens',row['name']);lights.append(dict(name=f'SunsetCanopy_{i}',position=[x,105.46,z],energy=1.1,range=30,color=[1,.93,.8]))
# Deep, floor-independent wall reveals: physically attached to the actual opaque enclosure.
for level,y in enumerate([84,88.5,93,97.5]):
 owner=f'FT_CourtEnclosure_1_{level}_0'
 assert any(q['name']==owner for q in d['parts'])
 for bay,z in enumerate([263,282,301,320,339]):
  box(f'WallReveal_{level}_{bay}_Left',[99.76,y+2.2,z-4.0],[.34,3.7,.18],'warm_walnut',owner)
  box(f'WallReveal_{level}_{bay}_Right',[99.76,y+2.2,z+4.0],[.34,3.7,.18],'warm_walnut',owner)
  box(f'WallReveal_{level}_{bay}_Head',[99.76,y+4.0,z],[.34,.18,8.18],'warm_walnut',owner)
  box(f'WallInset_{level}_{bay}',[99.885,y+2.2,z],[.07,3.5,7.8],'oatmeal_weave',owner)
plantplan=json.loads((R/'Game/quiet_court_finish_20261022/PLAN_R003.json').read_text())
plan=dict(status='UNFINISHED source successor; no final design or full-runtime acceptance',source_plan=str(source.relative_to(R)),source_plan_sha256=sha(source),native_source='BlenderCatalogue/assets/family_lift_receiving_20261009/source/architecture_lift_fit.blend',materials=materials,parts=parts,placements=placements,sources=plantplan['sources'],lights=lights,bed_contacts=checks,unchanged_original_instances=len(existing),global_light_budget=8,minimum_trim_clearance_above_D17_m=3.715,scope='Forward reading gardens Z250..350; preserve original benches and structure',retained_pause_benches=[x for x in existing if x['name'] in ['FT_GardenPauseBench_0','FT_GardenPauseBench_1']])
plan['native_sha256']=sha(R/plan['native_source']);(P/'PLAN_R003.json').write_text(json.dumps(plan,indent=2)+'\n');shutil.copyfile(__file__,N/'prepare_r003.py');print(json.dumps(dict(parts=len(parts),plants=len(placements),beds=len(checks),lights=len(lights),bytes=(P/'PLAN_R003.json').stat().st_size)))
