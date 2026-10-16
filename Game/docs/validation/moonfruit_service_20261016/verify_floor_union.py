import json,pathlib
from shapely.geometry import Polygon
from shapely.ops import unary_union
R=pathlib.Path('/workspace/Astraea');D=R/'BlenderCatalogue/assets/moonfruit_service_20261016';p=json.load(open(D/'NATIVE_PLAN.json'));polys=[];sources=[]
for f in ['data/generated/structural_meshes.json','data/generated/received_structural_meshes.json','data/architecture/REMAINING_BATCH_FLOORS.json']:
 d=json.load(open(R/'Game'/f))
 for r in d.get('regions',[]):
  if abs(float(r['floor_y'])-61)<.0001:
   for tri in r['triangles']:polys.append(Polygon(tri))
   sources.append(r['id'])
for f in (R/'BlenderCatalogue/assets').glob('*/NATIVE_PLAN.json'):
 if f.parent==D:continue
 d=json.load(open(f))
 if d.get('floor_y')==61 and 'floor_rectangles'in d:
  for a,b,c,e in d['floor_rectangles']:polys.append(Polygon([(a,c),(b,c),(b,e),(a,e)]))
  sources.append(str(f.relative_to(R)))
new=Polygon(p['floor_outline_xz']);overlap=new.intersection(unary_union(polys)).area
assert overlap<1e-9,overlap
r=dict(status='PASS_NEW_FLOOR_UNION',new_floor_m2=new.area,existing_floor_overlap_m2=overlap,existing_sources=sources)
(D/'FLOOR_UNION_VERIFICATION.json').write_text(json.dumps(r,indent=2)+'\n');print(new.area,overlap)
