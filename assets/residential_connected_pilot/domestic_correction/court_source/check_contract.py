"""Read-only geometry-bound checks against final source records and actual compiled receiver triangles."""
import json,math,hashlib,collections
from pathlib import Path
O=Path(__file__).resolve().parent
G=Path('/workspace/shared/astraea-godot-production-20261003')
S=Path('/workspace/scratch/375c2e438292/residential-production-schedule-20261006/ALL_1000_SOURCE_COLOR_CROSSWALK.json')
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def overlap(a0,a1,b0,b1):return min(a1,b1)-max(a0,b0)
def intri(p,t,eps=1e-5):
 a,b,c=t;cross=lambda u,v:u[0]*v[1]-u[1]*v[0];sub=lambda u,v:(u[0]-v[0],u[1]-v[1]);s=[cross(sub(b,a),sub(p,a)),cross(sub(c,b),sub(p,b)),cross(sub(a,c),sub(p,c))];return min(s)>=-eps or max(s)<=eps
parts=read(O/'PARTS.json');rows=parts['objects'];guests=read(S)['records'];programmes=read(G/'data/programme_ledger.json')['destinations'];regions=read(G/'data/generated/structural_meshes.json')['regions'];contacts=read(O/'CONTACTS.json')['contacts'];routes=read(O/'ROUTES.json')['routes']
# A separating AABB proves no triangle can enter the protected plan prism; a hit would need triangle-level follow-up.
guests_hit=[];programmes_hit=[]
for r in rows:
 lo,hi=r['bounds_world_min_xyz'],r['bounds_world_max_xyz']
 for g in guests:
  if overlap(lo[0],hi[0],*g['allocation_x'])>1e-5 and overlap(lo[2],hi[2],*g['allocation_z'])>1e-5:guests_hit.append([r['name'],g['source_envelope_index']])
 for p in programmes:
  if p['historical_deck']not in ['D12','D13','D14','D15','D16','D17']:continue
  e=p['historical_envelope']
  if overlap(lo[0],hi[0],*e['x'])>1e-5 and overlap(lo[2],hi[2],*e['z'])>1e-5:programmes_hit.append([r['name'],p['programme_key']])
byname={r['name']:r for r in rows};byregion={r['id']:r for r in regions};contact_checks=[]
for c in contacts:
 p=c['point_world_xyz'];r=byname[c['a']];lo,hi=r['bounds_world_min_xyz'],r['bounds_world_max_xyz'];inside=all(lo[i]-3e-5<=p[i]<=hi[i]+3e-5 for i in range(3))
 if 'b_existing'in c:
  b=byregion[c['b_existing']];inside_target=any(intri([p[0],p[2]],t)for t in b['triangles']) and b['floor_y']-b['thickness']-3e-5<=p[1]<=b['floor_y']+3e-5
 else:
  b=byname[c['b']];inside_target=all(b['bounds_world_min_xyz'][i]-3e-5<=p[i]<=b['bounds_world_max_xyz'][i]+3e-5 for i in range(3))
 contact_checks.append({'a':c['a'],'b':c.get('b',c.get('b_existing')),'point_world_xyz':p,'inside_source_evaluated_bounds':inside,'inside_receiver_actual_triangle_or_bounds':inside_target,'pass':inside and inside_target})
# Broad-phase route sweeps at 20cm spacing; deliberately conservative, actual bounding boxes incl. curves.
route_checks=[]
for route in routes[:2]:
 hit={};N=0;minhead=1e6
 pts=route['points_world_xyz'];rad=route['design_minimum_clear_width_m']/2
 for a,b in zip(pts,pts[1:]):
  length=math.dist(a,b);steps=max(1,math.ceil(length/.2))
  for j in range(steps+1):
   p=[a[i]+(b[i]-a[i])*j/steps for i in range(3)];N+=1
   for r in rows:
    lo,hi=r['bounds_world_min_xyz'],r['bounds_world_max_xyz']
    # Walking surface is measured separately; overhead elements still count if low.
    if hi[1]<=p[1]+.03:continue
    if lo[1]>=p[1]+2.1:continue
    if lo[0]>=p[0]+rad or hi[0]<=p[0]-rad or lo[2]>=p[2]+rad or hi[2]<=p[2]-rad:continue
    hit[r['name']]=hit.get(r['name'],0)+1
 route_checks.append({'route':route['id'],'samples':N,'probe':'axis-aligned square swept envelope; stated width x 2.1m height; 0.03m floor tolerance','potential_hits':hit,'pass':not hit})
assets=read(O/'ASSET_TRANSFORMS.json');deps=assets['dependencies'];unchanged={p:sha(p)==h for p,h in deps.items()}
result={'status':'Source-only checks; no runtime, structural capacity, species ergonomics or visual acceptance claims','source_bounds_world_xyz':[parts['bounds_world_min_xyz'],parts['bounds_world_max_xyz']],'mesh_and_curve_parts':len(rows),'triangles':parts['evaluated_triangles'],'guest_envelopes_screened':len(guests),'guest_positive_plan_prism_intersections':guests_hit,'D12_D17_programme_positive_plan_prism_intersections':programmes_hit,'court_upper_limit_y':parts['bounds_world_max_xyz'][1],'D15_floor_datum':93,'hypothetical_D15_024_slab_underside':92.76,'spare_below_D15_024_underside':92.76-parts['bounds_world_max_xyz'][1],'lower_limit_y':parts['bounds_world_min_xyz'][1],'D12_spine_datum':78,'contact_checks':contact_checks,'route_checks':route_checks,'dependency_hashes_unchanged':unchanged,'asset_counts':dict(collections.Counter(a['catalogue_id']for a in assets['instances'])),'limitations':['Zero envelope intersections are separating-bound proofs; no exhaustive full-game triangle occupancy survey was executed.','Routes use conservative evaluated-part bounds, no character/cart simulation or door interaction.','Receiver source contacts do not establish anchorage/load capacity. All structural transfer remains a proposed interface.','D11 Cinema2 has no verified current builder in the current script/amenity audit. Its future upper ceiling/interface must remain at or below D12 or be coordinated explicitly. This court adds nothing below Y78.','Source area lights remain only in the editable blend; GLB supports punctual lights, not these area lights.']}
result['overall_scoped_pass']=not guests_hit and not programmes_hit and all(c['pass']for c in contact_checks)and all(c['pass']for c in route_checks)and all(unchanged.values())
(O/'GEOMETRY_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items()if k not in ['dependency_hashes_unchanged','contact_checks','asset_counts']},indent=2))
