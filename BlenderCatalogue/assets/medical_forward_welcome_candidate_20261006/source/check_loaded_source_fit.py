"""One bounded fit screen on the already reloaded source scene. No engine acceptance."""
import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
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

reservations={
    'admission_longitudinal_3p6':[(15.2,-15.8,.05),(18.8,1.8,2.4)],
    'waiting_central_3p6':[(.01,-1.8,.05),(14.0,1.8,2.4)],
    'core_entry_3p6':[(18.8,-15.8,.05),(20.0,-12.2,2.4)],
}
hits={name:[] for name in reservations};deps=bpy.context.evaluated_depsgraph_get();new_bounds=[];retained_floor=[]
for ob in list(bpy.context.scene.objects):
    if ob.type!='MESH':continue
    ev=ob.evaluated_get(deps);me=ev.to_mesh();verts=[ev.matrix_world@v.co for v in me.vertices]
    if not verts:ev.to_mesh_clear();continue
    low=Vector(tuple(min(v[i] for v in verts) for i in range(3)));high=Vector(tuple(max(v[i] for v in verts) for i in range(3)))
    if ob.get('source_package')=='D05_forward_welcome_candidate':new_bounds.append({'name':ob.name,'min':list(low),'max':list(high)})
    me.calc_loop_triangles()
    for name,(a,b) in reservations.items():
        lo,hi=Vector(a),Vector(b)
        if any(high[i]<=lo[i]+1e-6 or low[i]>=hi[i]-1e-6 for i in range(3)):continue
        count=0
        for tri in me.loop_triangles:
            if tri_box([verts[i] for i in tri.vertices],lo,hi):count+=1
        if count:hits[name].append({'object':ob.name,'triangle_hits':count})
    ev.to_mesh_clear()
report={'scope':'Evaluated Blender triangle vs reserved empty-volume screen only. No capsules, door operation, loaded-cart turns, species fit or runtime acceptance.','reservations_source_xyz':reservations,'hits':hits,'clear':all(not x for x in hits.values()),'new_architecture_bounds':new_bounds,'no_production_floor_objects':not any('floor' in o.name.lower() and 'shoe' not in o.name.lower() and o.type=='MESH' and o.get('source_package')=='D05_forward_welcome_candidate' for o in bpy.context.scene.objects)}
run=Path(bpy.data.filepath).stem.rsplit('_',1)[-1]
(ROOT/'qa'/f'LOADED_SOURCE_FIT_{run}.json').write_text(json.dumps(report,indent=2)+'\n')
print('BOUNDED_SOURCE_FIT',report['clear'],{k:len(v) for k,v in hits.items()},flush=True)
