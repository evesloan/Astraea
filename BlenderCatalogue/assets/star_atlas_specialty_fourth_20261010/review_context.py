from pathlib import Path
import bpy,json
from mathutils import Vector
W=Path(__file__).resolve().parent;B=lambda p:(p[0],-p[2],p[1]);records=[]
for kind in ['aquatic_rest_pair','shared_street']:
 bpy.ops.wm.open_mainfile(filepath=str(W/'StarAtlasSpecialty_545.blend'));scene=bpy.context.scene
 if kind=='shared_street':
  for filename in ['StarAtlasSpecialty_557.blend','StarAtlasSpecialtyFourthReceiving.blend']:
   with bpy.data.libraries.load(str(W/filename),link=False)as(src,dst):dst.objects=src.objects
   for o in dst.objects:
    if o:
     bpy.context.collection.objects.link(o)
     if o.get('persistent_structural_contact_only',False):o.hide_render=True
 scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=3;scene.render.resolution_x=960;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.world=bpy.data.worlds.new('DiagnosticContext');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[1].default_value=.45
 for p in [(-92.5,95.7,-86.4),(-84,96,-86.4)]:
  bpy.ops.object.light_add(type='AREA',location=B(p));bpy.context.object.data.energy=150;bpy.context.object.data.size=3
 at,target,lens=((-92.55,94.8,-86.4),(-95.55,93.65,-86.4),14)if kind=='aquatic_rest_pair'else((-84,94.65,-80.5),(-84,94.4,-88),14)
 bpy.ops.object.camera_add(location=B(at));camera=bpy.context.object;camera.data.lens=lens;camera.rotation_euler=(Vector(B(target))-camera.location).to_track_quat('-Z','Y').to_euler();scene.camera=camera;name='SOURCE_CONTEXT_'+kind+'.png';scene.render.filepath=str(W/name);bpy.ops.render.render(write_still=True);records.append(name)
(W/'SOURCE_CONTEXT_RUN.json').write_text(json.dumps({'status':'PASS','images':records,'unsaved_native_context':True,'actual_source_receiving_and_opposite_room':True,'diagnostic_lighting':True},indent=2)+'\n')
