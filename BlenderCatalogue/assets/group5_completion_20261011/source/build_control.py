"""Small physical two-sided retail door control, seated on literal retained wall faces."""
from pathlib import Path
import bpy,bmesh,importlib.util,json,hashlib
P=Path(__file__).resolve().parents[1];CAT=P.parents[1]
spec=importlib.util.spec_from_file_location('retail_palette',CAT/'standards/retail_materials.py')
pal=importlib.util.module_from_spec(spec);spec.loader.exec_module(pal);M=pal.materials()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
F=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def box(name,low,high,role):
    verts=[(x,-z,y) for x,y,z in [(low[0],low[1],low[2]),(high[0],low[1],low[2]),(high[0],high[1],low[2]),(low[0],high[1],low[2]),(low[0],low[1],high[2]),(high[0],low[1],high[2]),(high[0],high[1],high[2]),(low[0],high[1],high[2])]]
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],F);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    me.materials.append(M[role]);uv=me.uv_layers.new(name='metric_material_uv')
    for face in me.polygons:
        axes=[a for a in range(3) if a!=max(range(3),key=lambda a:abs(face.normal[a]))]
        for li in face.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]],co[axes[1]])
    o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o)
box('Control_SeatedBack',(-.08,-.16,0),(.08,.16,.025),'ivory_enamel')
box('Control_OrangeReveal',(-.066,-.146,.025),(.066,.146,.042),'retail_terracotta_enamel')
box('Control_BrassButton',(-.040,-.060,.042),(.040,.060,.055),'champagne_metal')
for y in [-.12,.12]:box('Control_Fixing_'+str(y),(-.016,y-.01,.042),(.016,y+.01,.05),'champagne_metal')
native=P/'source/retail_door_control_r001.blend';out=P/'exports/retail_door_control_r001.glb'
bpy.ops.wm.save_as_mainfile(filepath=str(native))
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_texcoords=True,export_materials='EXPORT')
(P/'docs/CONTROL_COMPONENT.json').write_text(json.dumps({'native':str(native.relative_to(P)),'export':str(out.relative_to(P)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'dimensions':[.16,.32,.055],'mount':'source-local Z=0 against retained wall face; normal +Z','interaction':'existing door ancestor dispatch through fixed contact; no new controller'},indent=2)+'\n')
