from pathlib import Path
import bpy,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
def tri_box(tri,lo,hi):
    c=(lo+hi)*.5;h=(hi-lo)*.5;p=[v-c for v in tri]
    edges=[p[1]-p[0],p[2]-p[1],p[0]-p[2]]
    unit=[Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1))]
    axes=unit+[edges[0].cross(edges[1])]+[e.cross(a) for e in edges for a in unit]
    for a in axes:
        if a.length_squared<1e-16:continue
        r=sum(abs(a[i])*h[i] for i in range(3));values=[a.dot(v) for v in p]
        if min(values)>=r-1e-6 or max(values)<=-r+1e-6:return False
    return True

manifest=json.loads((R/'qa/SOURCE_MANIFEST_009.json').read_text())
reservations={
'existing_waiting_3p6':[(.01,-1.8,.05),(14,1.8,2.4)],
'existing_admission_3p6':[(15.2,-15.8,.05),(18.8,1.8,2.4)],
'new_admission_3p6':[(15.2,1.8,.05),(18.8,19.8,2.4)],
'clinical_cross_3p6':[(-13.8,10.2,.05),(18.8,13.8,2.4)],
'existing_core_entry_3p6':[(18.8,-15.8,.05),(20,-12.2,2.4)]}
for room in manifest['rooms']:
 cx=room['module_center_source_x'];front=room['front_source_y'];a=room['orientation_z'];pts=[]
 for u,v in [(-.8,.25),(2.8,.25),(2.8,3.85),(-.8,3.85)]:pts.append((cx+math.cos(a)*u-math.sin(a)*v,front+math.sin(a)*u+math.cos(a)*v))
 reservations[room['programme_child']+'_source_manoeuvre']=[(min(p[0]for p in pts),min(p[1]for p in pts),.05),(max(p[0]for p in pts),max(p[1]for p in pts),2.4)]
hits={name:[]for name in reservations};deps=bpy.context.evaluated_depsgraph_get()
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 ev=ob.evaluated_get(deps);me=ev.to_mesh();verts=[ev.matrix_world@v.co for v in me.vertices]
 if not verts:ev.to_mesh_clear();continue
 lo=Vector(tuple(min(v[i]for v in verts)for i in range(3)));hi=Vector(tuple(max(v[i]for v in verts)for i in range(3)));me.calc_loop_triangles()
 for name,(a,b)in reservations.items():
  low,high=Vector(a),Vector(b)
  if any(hi[i]<=low[i]+1e-6 or lo[i]>=high[i]-1e-6 for i in range(3)):continue
  n=sum(tri_box([verts[j]for j in t.vertices],low,high)for t in me.loop_triangles)
  if n:hits[name].append({'part':ob.name,'triangle_hits':n})
 ev.to_mesh_clear()
result={'status':'SOURCE_ROUTE_AND_ROOM_SCREEN_PASS'if all(not v for v in hits.values())else'SOURCE_ROUTE_OR_ROOM_SCREEN_FAILED','source_sha256':manifest['source_sha256'],'reservations':reservations,'hits':hits,'scope':'Conservative evaluated source triangle/empty-prism screen. Door sweeps, player/cart travel, robots/species and clinical operation are separate.'}
(R/'qa/LOADED_SOURCE_FIT_009.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],{k:len(v)for k,v in hits.items()},flush=True)
