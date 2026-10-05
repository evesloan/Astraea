import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/workspace/shared/astraea-catalogue-continuation-20261002/assets/d17_house_platform/source/AST-RES-005.blend')
for o in bpy.context.scene.objects:
 if o.type=='MESH' and not ('Royalty' in o.name or 'Footing' in o.name):o.hide_render=True
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=16;sc.cycles.use_denoising=False
sc.render.resolution_x=600;sc.render.resolution_y=900;sc.render.resolution_percentage=100
sc.world=bpy.data.worlds.new('DiagnosticWorld');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.15,.18,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.7
bpy.ops.object.camera_add(location=(165,-2,65));cam=bpy.context.object;cam.rotation_euler=(Vector((108,-40,50))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=114;sc.camera=cam
bpy.ops.object.light_add(type='AREA',location=(135,-15,85));lamp=bpy.context.object;lamp.data.energy=100000;lamp.data.shape='DISK';lamp.data.size=50;lamp.rotation_euler=(Vector((108,-40,50))-lamp.location).to_track_quat('-Z','Y').to_euler()
sc.render.image_settings.file_format='PNG';sc.render.filepath='/workspace/scratch/375c2e438292/royalty_aft_cross_source_review.png';bpy.ops.render.render(write_still=True)
