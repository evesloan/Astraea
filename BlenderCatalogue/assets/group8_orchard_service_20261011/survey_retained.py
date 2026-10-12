from pathlib import Path
import bpy,json,hashlib
from mathutils import Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];C=R/'BlenderCatalogue'
rows=[]
def inspect(path,label,at,yaw=0):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(str(path),link=False)as(src,dst):dst.objects=src.objects
    for ob in dst.objects:
        if ob:bpy.context.collection.objects.link(ob)
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    pose=Matrix.Translation((at[0],-at[2],at[1]))@Matrix.Rotation(yaw,4,'Z')
    for ob in dst.objects:
        if not ob or ob.type!='MESH':continue
        ev=ob.evaluated_get(dg);me=ev.to_mesh();world=pose@ev.matrix_world
        vs=[world@v.co for v in me.vertices];v=[(q.x,q.z,-q.y)for q in vs]
        rows.append({'name':ob.name,'instance':label,'native':str(path.relative_to(R)),'world_aabb':[min(q[0]for q in v),max(q[0]for q in v),min(q[1]for q in v),max(q[1]for q in v),min(q[2]for q in v),max(q[2]for q in v)],'vertices':len(v),'faces':len(me.polygons)})
        ev.to_mesh_clear()
inspect(C/'assets/orchard_foodhall/source/AST-DIN-008.blend','RetainedArchitecture',[8,61,-250])
for i,z in enumerate([-223.5,-208.5]):inspect(C/'assets/hospitality_serviceware/source/AST-HSP-005.blend','RetainedServiceware'+str(i),[35.5,61,z+2.7],-1.5707963267948966)
(W/'RETAINED_NATIVE_BOUNDS.json').write_text(json.dumps(rows,indent=2)+'\n')
print('RETAINED ORCHARD NATIVE SURVEY',len(rows),'evaluated mesh bounds')
