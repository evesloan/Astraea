from pathlib import Path
import json
from shapely.geometry import Polygon,box,Point,LineString
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
R=Path(__file__).resolve().parents[1];C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');d=json.load(open(R/'data/aquatic_section.json'))
outer=box(8,182,54,250);opening=Polygon(d['openings']['D10']);central=opening.buffer(2,join_style=3).intersection(outer.buffer(-2));middle=central.buffer(1.5,join_style=3).intersection(outer.buffer(-.2));coffers=unary_union([Point(x,z).buffer(1.45,quad_segs=4)for x,z in [(20,186),(50,244),(12,243)]])
relief=Polygon()
mezz=R/'data/architecture/D10_vesper_mezzanine.json'
if mezz.exists():
 v=json.loads(mezz.read_text())['ceiling_relief_xz'];relief=box(v['x'][0],v['z'][0],v['x'][1],v['z'][1])
# Paired raised dining ceiling bays add section depth without reducing headroom.
dining_bays=[]
for name,x0,x1,z1 in [('WestDiningBay',26.8,38.6,192.5),('EastDiningBay',40.0,52.3,195.5)]:
 shape=box(x0+1.1,184.1,x1-1.1,z1-1.1).buffer(1.1,quad_segs=3)
 assert shape.intersection(middle).area<1e-5, 'Dining bay must not cross an existing ceiling tier'
 inner=shape.buffer(-.45,join_style=2)
 dining_bays.append((name,shape,inner))
dining_cuts=unary_union([v[1] for v in dining_bays]) if mezz.exists() else Polygon()
def encode(name,g,lo,hi,role):
 assert g.is_valid
 rings=[]
 for p in ([g]if g.geom_type=='Polygon'else g.geoms):
  rings.append([list(v)for v in p.exterior.coords[:-1]])
  rings.extend([[list(v)for v in h.coords[:-1]]for h in p.interiors])
 tris=constrained_delaunay_triangles(g);assert abs(sum(t.area for t in tris.geoms)-g.area)<1e-6
 return {'name':name,'rings':rings,'triangles':[[list(v)for v in t.exterior.coords[:3]]for t in tris.geoms],'lo':lo,'hi':hi,'role':role}
contract={'id':'aquatic_ceiling','origin_xyz':[8,61,182],'cover_top_y':69.5,'protected_underside_y':69.1,'central_field_basis':'Existing D10 opening expanded2m; no skylight or deck opening','layers':[encode('HighCentralField',central.difference(coffers).difference(relief).difference(dining_cuts),68.85,69.01,'ivory_enamel'),encode('MiddleCove',middle.difference(central).difference(coffers).difference(relief).difference(dining_cuts),68.20,68.36,'ivory_enamel'),encode('PeripheralSoffit',outer.difference(middle).difference(coffers).difference(relief).difference(dining_cuts),67.4,67.56,'ivory_enamel')],'central_edge':[list(v)for v in central.exterior.coords[:-1]],'middle_edge':[list(v)for v in middle.exterior.coords[:-1]],'bearing_centers_xz':[[20,186],[50,244],[12,243]],'bearing_height':8.1,'coffer_radius':1.45,'status':'Authored ceiling composition in progress; support joints and visual review pending'}
if mezz.exists():
 contract['dining_bays']=[]
 for name,outer_bay,inner_bay in dining_bays:
  contract['layers'].append(encode(name,inner_bay,68.0,68.16,'ivory_enamel'))
  contract['dining_bays'].append({'name':name,'outer':list(outer_bay.exterior.coords)[:-1],'inner':list(inner_bay.exterior.coords)[:-1],'base_y':67.4,'crown_y':68.0})
contract['dining_task_mounts']=[]
for x,z in [(29.3,186.8),(40.1,186.8),(34.7,192.6),(45.5,192.6)]:
 height=67.4
 for _,shape,inner in dining_bays:
  if shape.contains(Point(x,z)):height=67.4+.6*min(1,shape.boundary.distance(Point(x,z))/.45)
 contract['dining_task_mounts'].append({'x':x,'z':z,'height':height})
contract['fixture_mounts']=[]
for x,z in [(15,207),(52,207),(20,246),(43,186)]:
 height=68.0 if mezz.exists() and any(inner.contains(Point(x,z)) for _,_,inner in dining_bays) else 67.4
 contract['fixture_mounts'].append({'x':x,'z':z,'height':height})
if not relief.is_empty:
 contract['layers'].append(encode('VesperLiftRelief',relief,68.2,68.36,'ivory_enamel'))
 contract['lift_relief_boundary']=[list(v)for v in relief.exterior.coords[:-1]]
 contract['edge_segments']={}
 for key in ['central_edge','middle_edge']:
  edge=contract[key];segments=[]
  for a,b in zip(edge,edge[1:]+edge[:1]):
   line=LineString([a,b]).difference(relief.buffer(.06))
   for part in ([line]if line.geom_type=='LineString'else getattr(line,'geoms',[])):
    if not part.is_empty:segments.append([list(part.coords[0]),list(part.coords[-1])])
  contract['edge_segments'][key]=segments
p=R/'data/architecture/D08_D10_aquatic_ceiling.json';p.write_text(json.dumps(contract,indent=2)+'\n');r=C/'assets/aquatic_ceiling';(r/'source').mkdir(parents=True,exist_ok=True);(r/'exports').mkdir(exist_ok=True);(r/'source/ceiling_contract.json').write_text(p.read_text());print('ceiling layers',[(v['name'],len(v['triangles']))for v in contract['layers']])
