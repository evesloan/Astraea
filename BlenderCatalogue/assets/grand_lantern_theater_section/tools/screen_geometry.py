import json, math
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text())
g=read(R/'source/geometry.json'); sm=read(R/'contracts/surface_manifest.json'); seats=read(R/'contracts/place_instances.json')['places']
def contains(p,x,z):
 inside=False
 for a,b in zip(p,p[1:]+p[:1]):
  if abs((b[0]-a[0])*(z-a[1])-(b[1]-a[1])*(x-a[0]))<1e-7 and min(a[0],b[0])-1e-7<=x<=max(a[0],b[0])+1e-7 and min(a[1],b[1])-1e-7<=z<=max(a[1],b[1])+1e-7:return True
  if (a[1]>z)!=(b[1]>z) and x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0]:inside=not inside
 return inside
support=[]
for s in seats:
 if s['tier']=='stalls':continue
 deck='D12' if s['tier']=='first_gallery' else 'D13'; x,y,z=s['position']
 hits=[p for f in sm['surfaces'] if f['deck']==deck for p in f['parts'] if contains(p['boundary_xz'],x,z)]
 if not any(p['top_y'] is not None and abs(p['top_y']-y)<1e-5 for p in hits):support.append(dict(id=s['id'],position=s['position'],surface_top_y=sorted(set(p['top_y'] for p in hits)),reason='policy return clipping removes source rake support' if hits else 'no named surface at place centre'))
# Geometry-only bounds, not body or collision acceptance
outside=[]
for o in g['objects']:
 for x,y,z in o['vertices_world']:
  if not(-118<=x<=-34 and 69.05<=y<=92 and -265<=z<=-115): outside.append(o['name']);break
report=dict(status='SOURCE_SUPPORT_GATE_OPEN',source_object_count=len(g['objects']),outside_allocation=outside,upper_place_support_failures=support,method='Exact centre point versus named convex top polygons and top elevation. Does not test whole seat bearing, species, runtime or dynamic objects.',engine_or_export_run=False)
(R/'qa/source_support_screen.json').write_text(json.dumps(report,indent=2)+'\n');print('Outside:',len(outside),'Upper place source support failures:',len(support));print(support[:3])
