from pathlib import Path
import json,math,hashlib
G=Path('/workspace/astraea-protected-integration-20261012/Game');D=Path('/workspace/astraea-integration-cutoff-20261013/fore404_receiving_preparation_20261015');D.mkdir(exist_ok=True);p=G/'data/generated/structural_meshes.json';regions=json.loads(p.read_text())['regions'];out=[]
def nearest_seg(p,a,b):
 dx=b[0]-a[0];dy=b[1]-a[1];q=((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)if dx or dy else 0;q=max(0,min(1,q));return[a[0]+q*dx,a[1]+q*dy]
for point in[[-60.5,-404],[60.5,-404]]:
 rows=[]
 for r in regions:
  if abs(float(r['floor_y'])-52.5)>.00001:continue
  closest=None
  for t in r['triangles']:
   cross=lambda a,b,c:(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);sign=[cross(t[i],t[(i+1)%3],point)for i in range(3)]
   if min(sign)>=0 or max(sign)<=0:near=point
   else:near=min((nearest_seg(point,t[i],t[(i+1)%3])for i in range(3)),key=lambda q:math.dist(point,q))
   v=(math.dist(point,near),near)
   if closest is None or v[0]<closest[0]:closest=v
  if closest:rows.append({'floor_region':r['id'],'distance_m':closest[0],'nearest_source_point_xz':closest[1]})
 out.append({'source_socket_xyz':[point[0],52.5,point[1]],'nearest_compiled_source_floor_regions':sorted(rows,key=lambda r:r['distance_m'])[:8]})
report={'status':'READONLY_COMPILED_SOURCE_FLOOR_PREPARATION_NOT_RUNTIME_RECEIVER_ACCEPTANCE','source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_regions':303,'owned_shopping_floor_and_all_runtime_neighbor_geometry_not_evaluated_here':True,'sockets':out,'new_construction_or_target_ids_created':False};(D/'NEAREST_CANONICAL_SOURCE_FLOOR_PREPARATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(out,indent=2))
