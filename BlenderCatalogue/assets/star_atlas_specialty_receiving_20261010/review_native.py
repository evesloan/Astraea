from pathlib import Path
import bpy,json
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];B=lambda p:(p[0],-p[2],p[1]);images=[]
for side,sign in [('North',-1),('South',1)]:
 bpy.ops.wm.open_mainfile(filepath=str(W/'StarAtlasSpecialtyStructuralReceiving.blend'));scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=3;scene.render.resolution_x=1100;scene.render.resolution_y=740;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.world=bpy.data.worlds.new('SourceDiagnosticWorld');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[1].default_value=.8
 for o in bpy.context.scene.objects:
  if o.type=='MESH':
   center=sum((o.matrix_world@Vector(v)for v in o.bound_box),Vector())/8;o.hide_render=center.y*sign>0
 # Unsaved first-batch floor/post context; no lower interior or source edits.
 p=json.loads((R/'BlenderCatalogue/assets/star_atlas_specialty_first_20261010/PLAN.json').read_text());mat=bpy.data.materials.new('OriginalD15FloorFrameContext');mat.diffuse_color=(.36,.45,.47,1)
 for room in p['rooms']:
  if sum(room['allocation']['allocation_z'])/2*sign<0:continue
  for part in room['parts']:
   if part['category']not in ['receiving','floor']:continue
   mesh=bpy.data.meshes.new(part['name']);mesh.from_pydata([B(v)for v in part['verts']],[],part['faces']);mesh.materials.append(mat);mesh.update();ob=bpy.data.objects.new(part['name'],mesh);bpy.context.collection.objects.link(ob)
 receiving=json.loads((R/'BlenderCatalogue/assets/star_atlas_specialty_first_20261010/RECEIVING_PLAN.json').read_text())
 for part in receiving['parts']:
  if part['category'] not in ['receiving','floor','cover_edge_tie']:continue
  if sum(v[2]for v in part['verts'])/len(part['verts'])*sign<0:continue
  mesh=bpy.data.meshes.new(part['name']);mesh.from_pydata([B(v)for v in part['verts']],[],part['faces']);mesh.materials.append(mat);mesh.update();ob=bpy.data.objects.new(part['name'],mesh);bpy.context.collection.objects.link(ob)
 bpy.ops.object.light_add(type='AREA',location=B((-75,110,25*sign)));bpy.context.object.data.energy=2000;bpy.context.object.data.size=35
 bpy.ops.object.camera_add(location=B((-106,103,63*sign)));camera=bpy.context.object;camera.data.lens=32;camera.rotation_euler=(Vector(B((-80,89.5,32*sign)))-camera.location).to_track_quat('-Z','Y').to_euler();scene.camera=camera;name=f'SOURCE_RECEIVING_{side.upper()}.png';scene.render.filepath=str(W/name);bpy.ops.render.render(write_still=True);images.append(name)
(W/'SOURCE_VIEW_RUN.json').write_text(json.dumps({'status':'PASS','images':images,'source_only':True,'unsaved_diagnostic_first_batch_context':True,'native_unchanged':True},indent=2)+'\n')
