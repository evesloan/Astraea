from pathlib import Path
import json,hashlib,sys
sys.path.insert(0,'/workspace/shared/astraea_python_deps')
from shapely.geometry import box,Polygon
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
from shapely.geometry.polygon import orient
r=Path(__file__).resolve().parents[3];g=r/'Game';o=r/'BlenderCatalogue/assets/central_residential_streets_20261009';o.mkdir(exist_ok=True)
sources=[g/'data/generated/structural_meshes.json',g/'data/generated/received_structural_meshes.json'];prior=[x for p in sources for x in json.load(open(p))['regions']];regions=[];checks=[]
for deck,y in [('D13',84),('D14',88.5),('D16',97.5)]:
 existing=unary_union([Polygon(t) for v in prior if abs(v['floor_y']-y)<.001 for t in v['triangles']])
 for side in [-1,1]:
  xmin,xmax=(-86.05,-81.95) if side<0 else (81.95,86.05)
  fore=(-75.2 if side<0 else -67.8) if deck=='D13' else -104.8
  aft=67.8 if deck=='D13' else (104.8 if side<0 else 97.4)
  links=(-86.05,-49.5) if side<0 else (49.5,86.05)
  requested=unary_union([box(xmin,fore,xmax,-30.5),box(xmin,28.5,xmax,aft),box(links[0],-33.5,links[1],-30.5),box(links[0],28.5,links[1],31.5)])
  missing=requested.difference(existing);polys=[missing] if missing.geom_type=='Polygon' else list(missing.geoms)
  name='STAR_ATLAS' if side<0 else 'NIGHT_GARDEN';checks.append({'deck':deck,'house':name,'requested_area':requested.area,'missing_area':missing.area,'pieces':len(polys),'existing_owner_overlap':missing.intersection(existing).area})
  assert missing.intersection(existing).area<1e-7
  for n,pol in enumerate(polys):
   if pol.area<1e-6:continue
   pol=orient(pol,sign=1);tris=[list(t.exterior.coords)[:3] for t in constrained_delaunay_triangles(pol).geoms];rings=[list(pol.exterior.coords)[:-1]]+[list(x.coords)[:-1] for x in pol.interiors]
   assert abs(sum(Polygon(t).area for t in tris)-pol.area)<1e-5
   regions.append({'id':deck+'_'+name+'_MISSING_STREET_'+str(n),'deck':deck,'floor_y':y,'thickness':.24,'triangles':tris,'rings':rings,'structural_area_m2':pol.area,'render_chunks':[],'status':'additive construction WIP; receiving frame, garden and full traversal acceptance unfinished'})
d={'schema':'astraea.central_residential_streets.v1','source_checks':{str(p.relative_to(g)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},'regions':regions,'systems':checks,'preservation':'Missing-only union/difference; no existing floor owner or protected central void replaced. Pilot temporary guard seams open only where new floor connects.','limits':['Receiving structure remains unfinished','Wintergardens and flanking gardens incomplete','Lifts, service, directional privacy and full traversal unaccepted']}
def put(p,s):t=p.with_name(p.name+'.new');t.write_text(s);t.replace(p)
put(g/'data/architecture/CENTRAL_RESIDENTIAL_STREETS.json',json.dumps(d,indent=2)+'\n');put(o/'STREET_PLAN.json',json.dumps(d,indent=2)+'\n')
print(json.dumps({'regions':len(regions),'systems':checks}))
