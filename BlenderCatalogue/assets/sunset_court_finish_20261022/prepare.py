from pathlib import Path
import json,hashlib,math,shutil
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union,triangulate
R=Path('/workspace/Astraea-recovered-e6274e77-20261021');P=R/'Game/sunset_court_finish_20261022';N=R/'BlenderCatalogue/assets/sunset_court_finish_20261022'
P.mkdir(exist_ok=True);N.mkdir(exist_ok=True);(P/'evidence').mkdir(exist_ok=True);(P/'runtime').mkdir(exist_ok=True)
source=next((R/'BlenderCatalogue/assets/residential_hotels').rglob('sunset_conservatory_house/outputs/house_r002/PLAN.json'));d=json.loads(source.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert shutil.disk_usage(R).free>500_000_000
materials={'warm_stone':{'color':[.64,.53,.38,1],'roughness':.73,'metallic':0},'ivory_enamel':{'color':[.82,.77,.64,1],'roughness':.6,'metallic':0},'warm_walnut':{'color':[.27,.13,.055,1],'roughness':.55,'metallic':0},'oatmeal_weave':{'color':[.66,.54,.36,1],'roughness':.92,'metallic':0},'champagne_metal':{'color':[.5,.36,.18,1],'roughness':.36,'metallic':.65},'lens':{'color':[1,.84,.58,1],'roughness':.4,'metallic':0},'botanical_soil':{'color':[.085,.052,.027,1],'roughness':1,'metallic':0}}
parts=[];placements=[];lights=[];checks=[]
def top(row):
 vs=row['verts'];y=max(v[1]for v in vs);polys=[Polygon([(vs[i][0],vs[i][2])for i in f])for f in row['faces']if all(abs(vs[i][1]-y)<1e-6 for i in f)];return unary_union([p for p in polys if p.area>1e-8]),y
def extrude(poly,lo,hi,name,role,owner):
 verts=[];faces=[]
 for g in ([poly] if poly.geom_type=='Polygon'else poly.geoms):
  tris=[t for t in triangulate(g)if g.buffer(1e-8).covers(t)];assert abs(sum(t.area for t in tris)-g.area)<1e-4
  for t in tris:
   coords=list(t.exterior.coords)[:3];base=len(verts);verts.extend([[x,lo,z]for x,z in coords]+[[x,hi,z]for x,z in coords]);faces.extend([[base+i for i in [0,1,2]],[base+i for i in [5,4,3]]])
  from shapely.geometry.polygon import orient
  g=orient(g,sign=1)
  for ring in [g.exterior,*g.interiors]:
   cs=list(ring.coords)
   for (x,z),(xx,zz)in zip(cs,cs[1:]):
    b=len(verts);verts.extend([[x,lo,z],[xx,lo,zz],[xx,hi,zz],[x,hi,z]]);faces.append([b+3,b+2,b+1,b])
 parts.append(dict(name=name,role=role,owner=owner,verts=verts,faces=faces))
def box(name,center,size,role,owner):
 x,y,z=center;sx,sy,sz=size;extrude(Polygon([(x-sx/2,z-sz/2),(x+sx/2,z-sz/2),(x+sx/2,z+sz/2),(x-sx/2,z+sz/2)]),y-sy/2,y+sy/2,name,role,owner)
for row in [x for x in d['parts']if x['category']=='planter']:
 p,y=top(row);extrude(p,y-.01,y+.06,'Coping_'+row['name'],'warm_stone',row['name']);checks.append(dict(owner=row['name'],footprint_area=p.area,positive_contact_m=.01))
existing=d['asset_instances']
for bi,row in enumerate([x for x in d['parts']if x['category']=='soil']):
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
  placements.append(dict(name=f'Understory_{bi:02}_{i:02}',catalogue_id='AST-BOT-008'if (i+bi)%2==0 else'AST-BOT-009',position=[x,y-.005,z],yaw=(i*2.399+bi*.41)%(2*math.pi),scale=scale,receiving_bed=row['name']))
for i,row in enumerate([x for x in d['parts']if x['category']=='ceiling_rib']):
 a,b=row['a'],row['b'];x=(a[0]+b[0])/2;z=a[2];length=abs(a[0]-b[0]);box(f'RibReveal_{i}',[x,105.725,z],[length,.06,.38],'warm_walnut',row['name']);box(f'CanopyHousing_{i}',[x,105.62,z],[.65,.18,1.2],'champagne_metal',row['name']);box(f'CanopyLens_{i}',[x,105.525,z],[.52,.05,1.05],'lens',row['name']);lights.append(dict(name=f'SunsetCanopy_{i}',position=[x,105.44,z],energy=1.1,range=30,color=[1,.93,.8]))
plantplan=json.loads((R/'Game/quiet_court_finish_20261022/PLAN_R003.json').read_text())
plan=dict(status='UNFINISHED source successor; no final design or full-runtime acceptance',source_plan=str(source.relative_to(R)),source_plan_sha256=sha(source),native_source='BlenderCatalogue/assets/sunset_lift_receiving_20261009/source/architecture_lift_fit.blend',materials=materials,parts=parts,placements=placements,sources=plantplan['sources'],lights=lights,bed_contacts=checks,unchanged_original_instances=len(existing),global_light_budget=8,minimum_trim_clearance_above_D17_m=3.695)
plan['native_sha256']=sha(R/plan['native_source']);(P/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');shutil.copyfile(__file__,N/'prepare.py');print(json.dumps(dict(parts=len(parts),plants=len(placements),beds=len(checks),lights=len(lights),bytes=(P/'PLAN.json').stat().st_size)))
