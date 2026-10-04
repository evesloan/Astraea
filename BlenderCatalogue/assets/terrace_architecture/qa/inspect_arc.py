from pathlib import Path
import bpy, json, math
from mathutils import Vector, Matrix
root=Path(__file__).resolve().parents[1];m=json.loads((root/'AST-ARC-001.manifest.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(root/'exports'/'AST-ARC-001.glb'))
parts=[o for o in bpy.context.scene.objects if o.type=='MESH'];points=[];tri=0
for o in parts:
    o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles);points.extend(o.matrix_world@v.co for v in o.data.vertices)
lo=[min(v[i] for v in points) for i in range(3)];hi=[max(v[i] for v in points) for i in range(3)]
assert tri==m['triangles'];assert max(abs(lo[i]-m['source_bounds']['min'][i]) for i in range(3))<1e-5
assert max(abs(hi[i]-m['source_bounds']['max'][i]) for i in range(3))<1e-5
start=bpy.data.objects['DATUM_START'];end=bpy.data.objects['DATUM_END']
assert (start.location-Vector((0,0,0))).length<1e-6
assert (end.location-Vector((5,10-10*math.cos(math.pi/6),0))).length<1e-5
recipe=Matrix.Translation(end.location)@Matrix.Rotation(math.pi/6,4,'Z')
for o in parts:
    duplicate=o.copy();duplicate.data=o.data;bpy.context.collection.objects.link(duplicate);duplicate.name='JOINED_'+o.name;duplicate.matrix_world=recipe@o.matrix_world
bpy.data.objects['ARC_Post_04'].hide_render=True
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32;scene.cycles.use_denoising=False
scene.render.threads_mode='FIXED';scene.render.threads=4
scene.render.resolution_x=960;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.world.color=(.12,.12,.12)
bpy.ops.object.camera_add(location=(12,-10,10));cam=bpy.context.object;cam.rotation_euler=(Vector((4,3,.2))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=15.0;scene.camera=cam
for name,loc,power,size in [('Key',(1,-3,10),1600,7),('Fill',(9,7,8),1100,6)]:
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
    ob=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((4,3,0))-ob.location).to_track_quat('-Z','Y').to_euler()
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(root/'qa'/'joined_import_review.png')
scene.view_settings.view_transform='AgX'
bpy.ops.render.render(write_still=True)
(root/'qa'/'source_roundtrip.json').write_text(json.dumps({'triangles_match':True,'bounds_match':True,'source_triangles':tri,'start_socket_verified':True,'end_socket_verified':True,'joined_recipe':'end translation plus30degree localZ; omit one duplicate joining post','render':'joined_import_review.png','scope':'Blender GLB roundtrip and two-module component assembly only; Godot movement/room fit and independent visual approval pending'},indent=2)+'\n')
print('ARC_ROUNDTRIP_PASS',tri)
