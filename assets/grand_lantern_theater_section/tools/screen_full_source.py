"""Pure footprint/height/contact checks, standard library, package-only outputs."""
import sys,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
import build_geometry as geo
places=json.load(open(R/'contracts/place_instances.json'))['places']
surfaces=json.load(open(R/'contracts/surface_manifest.json'))['surfaces']
original=json.load(open('/workspace/shared/astraea-godot-production-20261003/data/architecture/packages/theater/CHAIR_FOOTPRINT_SCREENING.json'))
objects=json.load(open(R/'source/geometry.json'))['objects']
def chair(s):
 x,y,z=s['position'];a=s['orientation_yaw_radians'];c,t=math.cos(a),math.sin(a)
 return [[x+u*c+v*t,z-u*t+v*c] for u,v in [(-.344,-.325),(.344,-.325),(.344,.460),(-.344,.460)]]
def bounds(p):return [min(x[0] for x in p),min(x[1] for x in p),max(x[0] for x in p),max(x[1] for x in p)]
def intersects(a,b):return a[0]<b[2]+1e-8 and b[0]<a[2]+1e-8 and a[1]<b[3]+1e-8 and b[1]<a[3]+1e-8
def sat(a,b):
 for q in [a,b]:
  for p,r in zip(q,q[1:]+q[:1]):
   ax,az=r[1]-p[1],p[0]-r[0];aa=[v[0]*ax+v[1]*az for v in a];bb=[v[0]*ax+v[1]*az for v in b]
   if min(max(aa),max(bb))-max(min(aa),min(bb))<=1e-8:return False
 return True
ps=[chair(s) for s in places];bs=[bounds(p) for p in ps]
chair_pairs=[];comparisons=0
for i,a in enumerate(ps):
 for j in range(i+1,len(ps)):
  if places[i]['tier']!=places[j]['tier']:continue
  comparisons+=1
  if intersects(bs[i],bs[j]) and sat(a,ps[j]):chair_pairs.append([places[i]['id'],places[j]['id']])
aisle_contacts=[]
for s,p in zip(places,ps):
 for q in original['aisle_reservations']:
  if s['tier']==q['tier'] and sat(p,q['boundary']):aisle_contacts.append(dict(place=s['id'],aisle=q['id']))
# Level terrace tops, not a continuous rake: exact entire conservative chair rectangle must be covered at sameY.
level_parts=[]
for f in surfaces:
 for p in f['parts']:
  if p['top_y'] is not None:level_parts.append((f['deck'],p['top_y'],p['boundary_xz'],bounds(p['boundary_xz'])))
for p in geo.stalls_polys:level_parts.append(('D11',p['top_y'],p['boundary_xz'],bounds(p['boundary_xz'])))
# D11 replaceable places require compiler support, explicitly conditional rather than claim source mesh.
d11_compiler=geo.rect([-117,-263,-35,-116]);failures=[];conditional=[]
for s,p,b in zip(places,ps,bs):
 deck={'stalls':'D11','first_gallery':'D12','crown_gallery':'D13'}[s['tier']];y=s['position'][1]
 if deck=='D11' and s['kind']=='rear_transfer_replaceable_place':conditional.append(s['id']);continue
 uncovered=[p]
 for d,h,q,qb in level_parts:
  if d!=deck or abs(h-y)>1e-6 or not intersects(b,qb):continue
  uncovered=[piece for u in uncovered for piece in geo.subtract_convex(u,q)]
  if not uncovered:break
 missing=sum(geo.area(u) for u in uncovered)
 if missing>1e-7:failures.append(dict(place=s['id'],unsupported_area_m2=missing,required_top_y=y))
# Contacts against physical walls/piers/caps/shaft: same tier vertical chair range is required.
static=[]
for o in objects:
 if o['role'] in ['preview_only','walkable_authored','stair_flight'] or o['name'].startswith(('D11_theater_stalls_rake','D12_theater_gallery','D13_theater_gallery')):continue
 vs=o['vertices_world'];a=[min(v[k] for v in vs) for k in range(3)];b=[max(v[k] for v in vs) for k in range(3)]
 q=[[v[0],v[2]] for v in vs[:len(vs)//2]]
 if len(q)<3 or geo.area(q)<1e-8:q=geo.rect([a[0],a[2],b[0],b[2]])
 static.append((o['name'],a,b,q))
contacts=[]; resolved_taper=[]
for s,p,pb in zip(places,ps,bs):
 y=s['position'][1]
 for n,a,b,q in static:
  if a[1]>=y+1.1-1e-8 or b[1]<=y+1e-8:continue
  if not intersects(pb,[a[0],a[2],b[0],b[2]]):continue
  if n=='west_acoustic_tapered_return':
   sl=8.9/4.5;nn=math.hypot(1,sl)
   margin=min((x+117.65-sl*(y+1.1-87))/nn-.12 for x,z in p)
   resolved_taper.append(dict(place=s['id'],normal_clearance_to_actual_inner_liner_plane=margin))
   if margin>0:continue
  if sat(p,q):contacts.append(dict(place=s['id'],structure=n,method='exact convex footprint with conservative height interval'))
# Source-plane shell margin, including new boundaries (no pressure-hull authoring).
s=8.9/4.5;normal=math.hypot(1,s);shell=[];minimum=(1e9,None)
for o in objects:
 if o['role']=='preview_only':continue
 for x,y,z in o['vertices_world']:
  m=min(x+118.5-.8,(x+118.5-s*(y-87.5))/normal-.8)
  if m<minimum[0]:minimum=(m,dict(object=o['name'],point=[x,y,z]))
  if m < -1e-7:shell.append(dict(object=o['name'],point=[x,y,z],margin=m))
report=dict(status='Pure_source_checks_not_engine_acceptance',chair_count=2200,same_tier_comparisons=comparisons,chair_pair_overlaps=chair_pairs,chair_existing_aisle_contacts=aisle_contacts,whole_chair_level_tread_support_failures=failures,D11_compiler_conditional_places=conditional,source_static_chair_contacts=contacts,resolved_taper_AABB_candidates=resolved_taper,shell_plane_failures=shell,minimum_static_normal_margin=minimum,limits=['Conservative closed full-chair rectangle proves level support; moving pan/feet detailed mounts/species remain gated','D11 compiler flat support must exist and be partitioned','Source static AABB contact candidates require exact mesh review if nonempty','No guard certification, evacuation, loaded-cart or runtime credit'])
(R/'qa/full_source_screen.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:(len(v) if isinstance(v,list) else v) for k,v in report.items()},indent=2))
