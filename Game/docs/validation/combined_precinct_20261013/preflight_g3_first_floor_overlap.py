from pathlib import Path
import json,math
C=Path(__file__).parent;G=Path('/workspace/astraea-protected-integration-20261012/Game')
def cross(a,b,c):return(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def area(p):return abs(sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1]for i in range(len(p)))/2)if len(p)>2 else 0.
def box(t):return min(p[0]for p in t),max(p[0]for p in t),min(p[1]for p in t),max(p[1]for p in t)
def overlap(a,b):
 x=box(a);y=box(b)
 if x[1]<=y[0]or y[1]<=x[0]or x[3]<=y[2]or y[3]<=x[2]:return 0.
 clip=list(b)
 if cross(*clip)<0:clip.reverse()
 poly=list(a)
 for i in range(3):
  u,v=clip[i],clip[(i+1)%3];result=[]
  if not poly:break
  s=poly[-1];ds=cross(u,v,s)
  for e in poly:
   de=cross(u,v,e)
   if(de>=-1e-10)!=(ds>=-1e-10):
    f=ds/(ds-de);result.append([s[0]+f*(e[0]-s[0]),s[1]+f*(e[1]-s[1])])
   if de>=-1e-10:result.append(e)
   s,ds=e,de
  poly=result
 return area(poly)
old=[]
for rel in ['data/generated/structural_meshes.json','data/generated/received_structural_meshes.json','data/architecture/REMAINING_BATCH_FLOORS.json']:
 d=json.loads((G/rel).read_text())
 for row in d.get('regions',[]):
  if abs(float(row.get('floor_y',-999))-12)<.001:
   for t in row['triangles']:old.append((str(row['id']),t))
new=[];records=[]
for name in ['MISSING_ONLY_FLOOR_PATCH.json','BANK_MISSING_ONLY_FLOOR.json']:
 d=json.loads((C/'g3_first_floor_preflight'/name).read_text());tris=[t for p in d['parts']for t in p['triangles']];hits=[]
 for i,t in enumerate(tris):
  for owner,base in old+new:
   a=overlap(t,base)
   if a>1e-6:hits.append({'new_triangle':i,'existing_owner':owner,'area_m2':a})
 records.append({'source':name,'triangles':len(tris),'source_area_m2':sum(area(t)for t in tris),'overlaps':hits,'total_overlap_m2':sum(x['area_m2']for x in hits)});new.extend((name,t)for t in tris)
r={'status':'PASS_DECLARED_MISSING_ONLY_FLOORS_AGAINST_CURRENT_COMPILER_RECEIVERS'if all(not x['overlaps']for x in records)else'HOLD_EXACT_SOURCE_FLOOR_OVERLAP','current_D03_floor_triangles':len(old),'source_packages':records,'actual_scene_native_floor_receiving_still_required':True,'new_compiler_records_or_geometry_generated':False};(C/'G3_FIRST_FLOOR_OVERLAP_PREFLIGHT.json').write_text(json.dumps(r,indent=2)+'\n');print('status',r['status'],'current_triangles',len(old));print([(x['source'],x['triangles'],x['source_area_m2'],x['total_overlap_m2'],len(x['overlaps']))for x in records])
