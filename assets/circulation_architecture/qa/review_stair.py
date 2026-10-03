from pathlib import Path
import bpy,json
from mathutils import Vector
root=Path(__file__).resolve().parents[1];m=json.loads((root/'AST-CIR-001.manifest.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(root/'exports/AST-CIR-001.glb'))
tri=0
for ob in bpy.context.scene.objects:
 if ob.type=='MESH':ob.data.calc_loop_triangles();tri+=len(ob.data.loop_triangles)
assert tri==m['triangles']
assert (bpy.data.objects['DATUM_UPPER'].location-Vector((4.75,0,8.5))).length<1e-5
assert (bpy.data.objects['DATUM_LOWER'].location-Vector((1.25,0,0))).length<1e-5
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=4
scene.render.resolution_x=960;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.world.color=(.16,.16,.16)
bpy.ops.object.camera_add(location=(19,-17,16));cam=bpy.context.object;cam.rotation_euler=(Vector((3,4.5,4))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=18;scene.camera=cam
for name,loc,power,size in [('Key',(1,-3,16),2200,9),('Fill',(12,10,12),1800,8)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.size=size;o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((3,4.5,4))-o.location).to_track_quat('-Z','Y').to_euler()
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(root/'qa/import_review.png');scene.view_settings.view_transform='AgX';bpy.ops.render.render(write_still=True)
(root/'qa/roundtrip.json').write_text(json.dumps({'triangles_match':tri,'lower_and_upper_datums_match':True,'status':'Component source roundtrip only; visual review and complete railing collision acceptance separate'},indent=2)+'\n')
