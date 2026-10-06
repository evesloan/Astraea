"""Pure, read-only reservation screening. Bounds are not solid design geometry."""
from pathlib import Path
import json,hashlib,math
G=Path('/workspace/shared/astraea-godot-production-20261003');S=Path(__file__).resolve().parent
D=json.loads((G/'data/architecture/GRAND_POOL_SECTION_RUNTIME.json').read_text());O=json.loads((G/'data/architecture/GRAND_POOL_FIRST_PASS_RUNTIME.json').read_text());F=json.loads((G/'data/architecture/GRAND_POOL_FINISH_RUNTIME.json').read_text());floor=next(x for x in D['floor_regions']if x['id']=='D08_grand_pool_wet')
boxes=[('wet_fore',[-53.70,46.2,-448.4],[-49.30,52.24,-436.0]),('wet_middle',[-53.70,46.2,-430.2],[-49.30,52.24,-419.0]),('wet_aft',[-53.70,46.2,-412.9],[-49.30,52.24,-400.5]),('focal_end',[-37,46.2,-465.68],[-25,50.85,-461.38])]
def side(a,b,p):return(b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
def floor_has(p):
 for t in floor['triangles']:
  q=[side(t[i],t[(i+1)%3],p)for i in range(3)]
  if min(q)>=-1e-9 or max(q)<=1e-9:return True
 return False
def inside(p,lo,hi):return all(lo[i]<p[i]<hi[i]for i in range(3))
def overlap(lo,hi,a,b):return all(min(hi[i],b[i])-max(lo[i],a[i])>1e-7 for i in range(3))
def bounds(vertices):return [min(v[i]for v in vertices)for i in range(3)],[max(v[i]for v in vertices)for i in range(3)]
reports=[]
for name,lo,hi in boxes:
 missing=[];count=0
 nx=math.ceil((hi[0]-lo[0])/.1);nz=math.ceil((hi[2]-lo[2])/.1)
 for ix in range(nx+1):
  for iz in range(nz+1):
   p=[lo[0]+(hi[0]-lo[0])*ix/nx,lo[2]+(hi[2]-lo[2])*iz/nz];count+=1
   if not floor_has(p):missing.append(p)
 original_mesh_constraints=[]
 for row in D['source_parts']:
  vs=row.get('world_vertices',[])
  if not vs or row.get('export_excluded'):continue
  a,b=bounds(vs)
  if overlap(lo,hi,a,b):original_mesh_constraints.append(row['name'])
 preserved_furniture=[]
 for row in O['placements']+F['placements']:
  if overlap(lo,hi,row['envelope_min_xyz'],row['envelope_max_xyz']):preserved_furniture.append(row['name'])
 rays=[]
 for row in D['fixtures']+F['fixtures']:
  p=row.get('position_xyz')or row.get('position')
  if p and inside(p,lo,hi):rays.append(row['name'])
 approaches=[]
 for row in O['approach_paths']:
  if any(lo[0]-.5<=p[0]<=hi[0]+.5 and lo[2]-.5<=p[2]<=hi[2]+.5 and abs(p[1]-lo[1])<.1 for p in row['points']):approaches.append(row['item'])
 reports.append(dict(name=name,bounds=[lo,hi],existing_wet_floor_samples=count,unsupported_samples=missing,old_source_parts_inside_reservation=original_mesh_constraints,preserved_furnishing_overlaps=preserved_furniture,fixture_origin_reservations=rays,old_approaches_within_half_metre=approaches,scope='Open architectural room reservation; listed retained geometry must be excluded or used as a real named support, never filled through. No mesh/route/light acceptance.'))
result=dict(status='PURE_RESERVATION_SCREEN_ONLY',retained_floor_owner=floor['id'],floor_y=floor['floor_y'],inputs={r:hashlib.sha256((G/r).read_bytes()).hexdigest()for r in ['data/architecture/GRAND_POOL_SECTION_RUNTIME.json','data/architecture/GRAND_POOL_FIRST_PASS_RUNTIME.json','data/architecture/GRAND_POOL_FINISH_RUNTIME.json']},reservations=reports)
(S/'RESERVATION_SCREEN.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(reports,indent=2))
