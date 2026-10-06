"""Read-only planning checks; writes only this package's report. No engine/source authoring."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
read=lambda p:json.loads((ROOT/p).read_text())
spec=read('data/architecture/packages/engineering/SECONDARY_FUSION_SECTION_SPEC.json');layout=read('data/whole_ship_layout.json');spatial=read('data/spatial_layout.json');compiled=read('data/generated/structural_meshes.json');hull=read('data/hull_envelope.json')['plan_xz_m']
def clip(poly,r):
 for axis,edge,keep in [(0,r[0],1),(0,r[1],-1),(1,r[2],1),(1,r[3],-1)]:
  result=[]
  if not poly:return []
  for a,b in zip(poly,poly[1:]+poly[:1]):
   ia=(a[axis]-edge)*keep>=-1e-10;ib=(b[axis]-edge)*keep>=-1e-10
   if ia:result.append(a)
   if ia!=ib:
    t=(edge-a[axis])/(b[axis]-a[axis]);result.append([a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])])
  poly=result
 return poly
def area(poly):return abs(sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(poly,poly[1:]+poly[:1])))/2 if poly else 0
def overlap(poly,r):return area(clip(poly,r))
def rectpoly(r):return [[r[0],r[2]],[r[1],r[2]],[r[1],r[3]],[r[0],r[3]]]
def squares(p):
 rs=[]
 for a,b in zip(p,p[1:]):
  if a[0]==b[0]:rs.append([a[0]-1.8,a[0]+1.8,min(a[1],b[1]),max(a[1],b[1])])
  else:assert a[1]==b[1];rs.append([min(a[0],b[0]),max(a[0],b[0]),a[1]-1.8,a[1]+1.8])
 rs += [[x-1.8,x+1.8,z-1.8,z+1.8]for x,z in p] # all ends/corners explicit3.6m squares
 return rs
def cells(rs):
 xs=sorted(set(v for r in rs for v in r[:2]));zs=sorted(set(v for r in rs for v in r[2:]));out=[]
 for a,b in zip(xs,xs[1:]):
  for c,d in zip(zs,zs[1:]):
   x=(a+b)/2;z=(c+d)/2
   if any(r[0]<=x<=r[1] and r[2]<=z<=r[3]for r in rs):out.append([a,b,c,d])
 return out
routes={k:v for k,v in spec['proposed_service_route_centerlines'].items()if isinstance(v,list)}
routes['revised_secondary_to_lower_staff']=[[-57,-500],[-20,-500],[-20,-535],[20,-535],[20,-500],[57,-500],[57,-432],[54,-432]]
routes['revised_power_end_around']=[[57,290],[57,500],[7.2,500],[7.2,532.5],[-7.2,532.5],[-7.2,500],[-57,500],[-57,216],[-54,216]]
reports=[]
for name,p in routes.items():
 cs=cells(squares(p));result={'route':name,'centerline_xz':p,'footprint_and_turning_squares':squares(p),'union_plan_area_m2':round(sum((r[1]-r[0])*(r[3]-r[2])for r in cs),4)}
 result['outside_plan_hull_m2']=round(sum((r[1]-r[0])*(r[3]-r[2])-overlap(hull,r)for r in cs),4)
 result['compiled_floor_intersections']=[]
 for a in compiled['regions']:
  if a.get('deck')!='D02':continue
  ar=sum(overlap(t,r)for t in a['triangles']for r in cs)
  if ar>1e-5:result['compiled_floor_intersections'].append({'id':a['id'],'area_m2':round(ar,4),'classification':'retained_staff_tee'if 'staff' in a['id'] else 'public_or_other_floor_requires_separation'})
 result['void_intersections']=[]
 for a in spatial['voids']:
  if 'D02' not in a.get('decks',[]):continue
  ar=sum(overlap(a['boundary'],r)for r in cs)
  if ar>1e-5:result['void_intersections'].append({'id':a['id'],'area_m2':round(ar,4)})
 result['reservations']=[]
 for group in ['longitudinal_vertical_core_reservations','staff_riser_reservations']:
  for a in layout[group]:
   x=a.get('lobby_x',a.get('x'));z=a.get('lobby_z',a.get('z'))
   if x is None or z is None:continue
   ar=sum(overlap(rectpoly([*x,*z]),r)for r in cs)
   if ar>1e-5:result['reservations'].append({'id':a['id'],'group':group,'lobby_intersection_m2':round(ar,4)})
 result['programme_intersections']=[]
 for a in layout['programmes']:
  if a['deck']!='D02':continue
  ar=sum(overlap(rectpoly([*a['allocation_x'],*a['allocation_z']]),r)for r in cs)
  if ar>1e-5:result['programme_intersections'].append({'id':a['programme_key'],'area_m2':round(ar,4),'note':'terminal turns must be trimmed at programme boundary and handed to programme floor owner'})
 reports.append(result)
inputs=['data/spatial_layout.json','data/generated/structural_meshes.json','data/whole_ship_layout.json','data/hull_envelope.json']
report={'scope':'Exact polygon clipping of disjoint candidate route/3.6m corner-and-terminal-square union against compiledD02 triangles, applicable spatialvoids, core/riser lobby polygons, programme polygons and planhull','algorithm':'Axis-aligned cells form non-overlapping union; Sutherland-Hodgman polygon-to-rectangle clipping and shoelace area; no packages/engine jobs','inputs_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()for p in inputs},'results':reports,'limits':['No constructed enclosed service route','No per-height hullsection acceptance','Terminal squares at existing programmes require ownership trimming','Compiledfloor contacts do not certify wall/door clearances']}
(OUT/'DETAILED_SERVICE_ROUTE_FIT.json').write_text(json.dumps(report,indent=2)+'\n')
for r in reports:print(r['route'], 'hull',r['outside_plan_hull_m2'],'floor',r['compiled_floor_intersections'],'void',r['void_intersections'],'res',r['reservations'],'programme',r['programme_intersections'])
