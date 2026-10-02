"""Read actual geometry for specified contact/void samples; no actor/physics fit."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch05'
def load(p):
 bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False);geo={}
 for o in bpy.context.scene.objects:
  if o.type not in ['MESH','CURVE']:continue
  ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles();v=[o.matrix_world@x.co for x in m.vertices];fs=[tuple(t.vertices) for t in m.loop_triangles];geo[o.name]=BVHTree.FromPolygons(v,fs,all_triangles=True);ev.to_mesh_clear()
 return geo

def ray(geo,start,direction=(0,0,-1),names=None,dist=10):
 hits=[]
 for n,g in geo.items():
  if names is not None and n not in names:continue
  co,no,idx,d=g.ray_cast(Vector(start),Vector(direction),dist)
  if co is not None:hits.append({'part':n,'position_m':list(co),'normal':list(no),'distance_m':d})
 return sorted(hits,key=lambda h:h['distance_m'])
def nearest(geo,p):
 hits=[]
 for n,g in geo.items():
  co,no,idx,d=g.find_nearest(Vector(p));hits.append({'part':n,'distance_m':d,'signed_nearest_distance_m':(Vector(p)-co).dot(no)})
 return sorted(hits,key=lambda h:h['distance_m'])[:3]
rows=[]
for f,id in [('aquatic_lounge','AST-AQU-001'),('aquatic_lounge','AST-AQU-002'),('aquatic_edges','AST-AQU-005'),('aquatic_float','AST-AQU-006')]:
 base=ROOT/'assets'/f;p=next(base.rglob(id+'.blend'));geo=load(p);r={'asset':id,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'scope':'Finite geometric samples on actual evaluated source. No swept body/actor, universal fit, reach, accessibility, structural load, fluid or physics acceptance.'}
 if id in ['AST-AQU-001','AST-AQU-002']:
  sam=[(0,-.1,.2),(-.7,-.1,.5),(.7,-.1,.5)] if id.endswith('001') else [(0,0,.2)]
  r['open_underside_and_approach_samples']=[{'point_m':p,'nearest_surfaces':nearest(geo,p)} for p in sam]
 if id=='AST-AQU-005':
  r['center_route_tread_samples']=[{'x_m':0,'y_m':y,'downward_hits':ray(geo,(0,y,1.2))[:1]} for y in [-.3,.16,.48,.8,1.22]]
  r['above_tread_route_samples']=[{'point_m':[0,y,z+.15],'nearest_surfaces':nearest(geo,(0,y,z+.15))} for y,z in [(-.3,0),(.16,-.18),(.48,-.36),(.8,-.54),(1.22,-.72)]]
  rails=[o for o in bpy.context.scene.objects if 'continuous_return_handrail' in o.name]
  r['rail_parts_found']=[o.name for o in rails]
  # Bounding extents on the two separate handrails establish their inner transverse corridor only.
  inner=[]
  for o in rails:
   ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();xs=[(o.matrix_world@v.co).x for v in m.vertices];inner.append(max(xs) if sum(xs)<0 else min(xs));ev.to_mesh_clear()
  r['transverse_inner_rail_gap_m']=max(inner)-min(inner) if len(inner)==2 else None
 if id=='AST-AQU-006':
  r['seat_membrane_contacts']=[{'xy_m':[x,-.06],'downward_hits':ray(geo,(x,-.06,.3),names=['recessed_tensioned_seat_membrane_with_drain_aperture'])[:1]} for x in [-.12,0,.12]]
  r['well_center_above_seat_sample']={'point_m':[0,-.06,.10],'nearest_surfaces':nearest(geo,(0,-.06,.1))}
  j=json.loads((base/(id+'.manifest.json')).read_text());r['grip_gap_samples']=[]
  for grip in j['design_proposals']['grips']:
   x,y,z=grip['center_m'];h=ray(geo,(x,y,z),names=[grip['side']+'_arched_continuous_grip'])
   hull=ray(geo,(x,y,z-.023-.001),names=['continuous_oval_hull_with_raised_back_cradle'])
   r['grip_gap_samples'].append({'side':grip['side'],'grip_downward_exit':h[:1],'hull_below':hull[:1],'clear_vertical_gap_m':hull[0]['distance_m']+.001 if hull else None})
 rows.append(r)
(OUT/'independent_use_spaces.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2))
