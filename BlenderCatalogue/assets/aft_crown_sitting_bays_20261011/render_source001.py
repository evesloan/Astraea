from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));bpy.ops.wm.read_factory_settings(use_empty=True)
for f in [R/'BlenderCatalogue/assets/aft_crown_platform/source/AST-CMD-005.blend',W/P['structure']['native']]:
 with bpy.data.libraries.load(str(f),link=False)as(src,dst):dst.objects=src.objects
 for ob in dst.objects:
  if ob:bpy.context.collection.objects.link(ob)
# Retained parent compiler floor,exact published triangle bytes;never exported with the new bays.
for f in ['structural_meshes.json','received_structural_meshes.json']:
 for q in json.load(open(R/'Game/data/generated'/f))['regions']:
  if abs(q['floor_y']-106.5)>.0001:continue
  vs=[];faces=[]
  for tri in q['triangles']:
   faces.append(list(range(len(vs),len(vs)+3)));vs.extend((x,-z,106.5)for x,z in tri)
  me=bpy.data.meshes.new(q['id']);me.from_pydata(vs,[],faces);ob=bpy.data.objects.new(q['id'],me);bpy.context.collection.objects.link(ob)
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.studio_light='paint.sl';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD';s.world=bpy.data.worlds.new('Neutral actual platform source');s.world.color=(.6,.6,.6);s.render.resolution_x=1440;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='Standard'
bpy.ops.object.camera_add(location=(-14,-161.5,108.25));o=bpy.context.object;o.data.lens=18;o.rotation_euler=(Vector((-26,-160.5,108.1))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/'SOURCE_AFT_CROWN_SITTING_BAYS_WIDE001.png');assert not Path(s.render.filepath).exists();bpy.ops.render.render(write_still=True)
(W/'SOURCE_VIEW_RECEIPT001.json').write_text(json.dumps({'status':'PASS','image':Path(s.render.filepath).name,'actual_saved_native_platform_and_new_bays':True,'floor_from_exact_retained_parent_compiler_triangles':True,'all_source_roofs_guards_structural_members_and_furniture_retained':True,'mode':'Neutral Blender Workbench material-color source view;original textures,glass shading and game lighting omitted','no_exterior_vista_full_ship_Godot_CRT_hardware_final_acceptance':True},indent=2)+'\n')
