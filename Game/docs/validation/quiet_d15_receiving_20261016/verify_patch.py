from pathlib import Path
import json,math
from collections import defaultdict
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
D=Path('/workspace/Astraea/BlenderCatalogue/assets/quiet_d15_staff_receiving_20261016/r003');data=json.loads((D/'PATCH_TRIANGLES.json').read_text());out=[]
for row in data:
 groups={k:defaultdict(list)for k in ['before','after']};planes=defaultdict(list)
 for side in groups:
  for tri in row[side]:
   v=[q['p'] for q in tri];ranges=[max(q[i]for q in v)-min(q[i]for q in v)for i in range(3)];axis=min(range(3),key=lambda i:ranges[i]);assert ranges[axis]<.0001,(row['name'],ranges)
   axes=[i for i in range(3)if i!=axis];plane=sum(q[axis]for q in v)/3;near=[x for x in planes[axis] if abs(x-plane)<.0001]
   if near:plane=min(near,key=lambda x:abs(x-plane))
   elif side=='before':planes[axis].append(plane)
   else:raise AssertionError(('new source plane',row['name'],axis,plane))
   poly=Polygon([(q[axes[0]],q[axes[1]])for q in v]);groups[side][(axis,plane)].append(poly)
 total=0
 for key,polys in groups['before'].items():
  axis,plane=key;axes=[i for i in range(3)if i!=axis];old=unary_union(polys);expected=old
  if row['cut_min'][axis]<plane<row['cut_max'][axis]:expected=old.difference(box(row['cut_min'][axes[0]],row['cut_min'][axes[1]],row['cut_max'][axes[0]],row['cut_max'][axes[1]]))
  actual=unary_union(groups['after'].get(key,[]));err=expected.symmetric_difference(actual).area;assert err<.0002,(row['name'],key,err);total+=err
 assert not(set(groups['after'])-set(groups['before']))
 out.append({'name':row['name'],'planes':len(groups['before']),'surface_difference_m2':total,'old_triangles':len(row['before']),'new_triangles':len(row['after'])})
(D/'PATCH_VERIFICATION.json').write_text(json.dumps({'status':'PASS_INDEPENDENT_SHAPELY_SURFACE_SUBTRACTION','rows':out,'scope':'Exact axis-aligned source surface subtraction; no route/engineering acceptance'},indent=2)+'\n');print(out)
