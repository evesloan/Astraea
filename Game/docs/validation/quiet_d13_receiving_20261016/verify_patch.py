from pathlib import Path
import json,math
from collections import defaultdict,Counter
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
D=Path('/workspace/Astraea/BlenderCatalogue/assets/quiet_d13_staff_receiving_20261016');data=json.loads((D/'PATCH_TRIANGLES.json').read_text());out=[]
for row in data:
 groups={k:defaultdict(list)for k in ['before','after']};planes=defaultdict(list);unaltered={side:Counter()for side in groups}
 for side in groups:
  for tri in row[side]:
   v=[q['p'] for q in tri];ranges=[max(q[i]for q in v)-min(q[i]for q in v)for i in range(3)];axis=min(range(3),key=lambda i:ranges[i]);
   if ranges[axis]>=.0001:
    unaltered[side][tuple(sorted(tuple(q['p']+q['uv'])for q in tri))]+=1;continue
   axes=[i for i in range(3)if i!=axis];plane=sum(q[axis]for q in v)/3;near=[x for x in planes[axis] if abs(x-plane)<.0001]
   if near:plane=min(near,key=lambda x:abs(x-plane))
   elif side=='before':planes[axis].append(plane)
   else:raise AssertionError(('new source plane',row['name'],axis,plane))
   poly=Polygon([(q[axes[0]],q[axes[1]])for q in v]);groups[side][(axis,plane)].append(poly)
 assert unaltered["before"]==unaltered["after"]
 total=0
 for key,polys in groups['before'].items():
  axis,plane=key;axes=[i for i in range(3)if i!=axis];old=unary_union(polys);expected=old
  for cut in [{'min':row['cut_min'],'max':row['cut_max']}]+row.get('additional_cuts',[]):
   if cut['min'][axis]<plane<cut['max'][axis]:expected=expected.difference(box(cut['min'][axes[0]],cut['min'][axes[1]],cut['max'][axes[0]],cut['max'][axes[1]]))
  actual=unary_union(groups['after'].get(key,[]));err=expected.symmetric_difference(actual).area;assert err<.0002,(row['name'],key,err);total+=err
 assert not(set(groups['after'])-set(groups['before']))
 out.append({'name':row['name'],'planes':len(groups['before']),'surface_difference_m2':total,'unaltered_nonaxial_triangles':sum(unaltered['before'].values()),'old_triangles':len(row['before']),'new_triangles':len(row['after'])})
(D/'PATCH_VERIFICATION.json').write_text(json.dumps({'status':'PASS_INDEPENDENT_SHAPELY_SURFACE_SUBTRACTION','rows':out,'scope':'Exact axis-aligned source surface subtraction; no route/engineering acceptance'},indent=2)+'\n');print(out)
