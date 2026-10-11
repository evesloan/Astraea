"""Freshly export spatial material batches from the immutable saved native."""
import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1]
native=P/'source/natives/G7_Completion_r002.blend'
bpy.ops.wm.open_mainfile(filepath=str(native))
source=bpy.context.scene;objects=[ob for ob in source.objects if ob.type=='MESH'and'group7_cell'in ob]
cells=sorted(set(ob['group7_cell']for ob in objects));rows=[]
for cell in cells:
    scene=bpy.data.scenes.new(cell+'_Export');bpy.context.window.scene=scene
    groups={}
    for ob in objects:
        if ob['group7_cell']!=cell:continue
        for si,slot in enumerate(ob.material_slots):
            if slot.material:groups.setdefault((slot.material.name,ob['contact_category']),[]).append((ob,si))
    for (material,category),members in groups.items():
        vs=[];fs=[];uvs=[]
        for ob,si in members:
            offset=len(vs);vs.extend(tuple(ob.matrix_world@q.co)for q in ob.data.vertices)
            for f in ob.data.polygons:
                if f.material_index!=si:continue
                fs.append(tuple(offset+i for i in f.vertices));uvs.append([tuple(ob.data.uv_layers.active.data[k].uv)for k in f.loop_indices])
        me=bpy.data.meshes.new(cell+'_'+material+'_'+category);me.from_pydata(vs,[],fs);me.update();me.materials.append(bpy.data.materials[material]);uv=me.uv_layers.new(name='RetainedSourceUV')
        for f,uvrow in zip(me.polygons,uvs):
            for k,u in zip(f.loop_indices,uvrow):uv.data[k].uv=u
        ob=bpy.data.objects.new(me.name,me);scene.collection.objects.link(ob);ob['contact_category']=category;ob['group7_cell']=cell
    for ob in scene.objects:ob.select_set(True)
    output=P/'exports'/('G7_Completion_'+cell+'.glb')
    bpy.ops.export_scene.gltf(filepath=str(output),export_format='GLB',export_yup=True,export_extras=True,use_active_scene=True,use_selection=True,export_cameras=False,export_lights=False)
    rows.append({'cell':cell,'file':output.name,'path':output.relative_to(P).as_posix(),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'bytes':output.stat().st_size,'mesh_nodes':len(scene.objects),'placement':[0,0,0],'rotation_y':0,'scale':[1,1,1]})
    bpy.context.window.scene=source
    bpy.data.scenes.remove(scene)
(P/'docs/EXPORTS.json').write_text(json.dumps({'native':native.relative_to(P).as_posix(),'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'exports':rows},indent=2)+'\n')
print('GROUP7_FRESH_NATIVE_EXPORTS',len(rows))
