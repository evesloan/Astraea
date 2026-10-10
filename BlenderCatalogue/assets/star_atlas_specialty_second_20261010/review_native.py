from pathlib import Path
import bpy,json
from mathutils import Vector
W=Path(__file__).resolve().parent;B=lambda p:(p[0],-p[2],p[1]);images=[]
for idx,z in [(461,-56.8),(467,56.8),(485,-64.2),(491,64.2)]:
 bpy.ops.wm.open_mainfile(filepath=str(W/f'StarAtlasSpecialty_{idx}.blend'));scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=3;scene.render.resolution_x=960;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
 scene.world=bpy.data.worlds.new('DiagnosticSourceWorld');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.2,.22,.24,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.45
 for p in [(-78,95.7,z-1.5),(-73,95.7,z+.4)]:
  bpy.ops.object.light_add(type='AREA',location=B(p));bpy.context.object.data.energy=120;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=3
 bpy.ops.object.camera_add(location=B((-79.4,94.65,z-1.0)));camera=bpy.context.object;camera.data.lens=16;camera.rotation_euler=(Vector(B((-72.3,94.1,z+.1)))-camera.location).to_track_quat('-Z','Y').to_euler();scene.camera=camera;name=f'SOURCE_INTERIOR_{idx}.png';scene.render.filepath=str(W/name);bpy.ops.render.render(write_still=True);images.append(name)
(W/'SOURCE_VIEW_RUN.json').write_text(json.dumps({'status':'PASS','images':images,'source_only':True,'diagnostic_fill_lighting':True,'unsaved_source_views':True},indent=2)+'\n')
