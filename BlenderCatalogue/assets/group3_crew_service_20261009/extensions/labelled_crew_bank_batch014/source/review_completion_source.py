"""Wide real native source views; temporary cameras only, no exported-source modification."""
from pathlib import Path
import bpy,json,math,sys
from mathutils import Vector,Matrix
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4];PRE=HERE.parent/'d03_remaining_receivers_batch013'
DOOR_ONLY='door_context_only'in sys.argv
def gv(p):return Vector((p[0],-p[2],p[1]))
def setup():
 s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH'
 s.render.resolution_x=1680;s.render.resolution_y=1050;s.render.resolution_percentage=100
 s.render.image_settings.file_format='PNG';s.render.film_transparent=False
 s.display.shading.light='STUDIO';s.display.shading.studiolight_rotate_z=.45
 s.display.shading.color_type='TEXTURE';s.display.shading.show_shadows=False
 s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH'
 s.display.shading.curvature_ridge_factor=1.1;s.display.shading.curvature_valley_factor=.65
 s.display.shading.show_specular_highlight=True;s.display.shading.background_type='WORLD'
 s.world.color=(.18,.2,.23);s.view_settings.view_transform='Standard'
 s.view_settings.look='None';s.view_settings.exposure=1.35;s.view_settings.gamma=1
def camera(eye,target,lens=24,ortho=None):
 d=bpy.data.cameras.new('QA_WideSourceCamera');o=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(o)
 o.location=gv(eye);o.rotation_euler=(gv(target)-o.location).to_track_quat('-Z','Y').to_euler()
 d.lens=lens;d.clip_start=.05;d.clip_end=1000
 if ortho:d.type='ORTHO';d.ortho_scale=ortho
 bpy.context.scene.camera=o
def import_pose(path,position=(0,0,0),yaw=0,opened=False):
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(path));new=set(bpy.context.scene.objects)-before
 pose=Matrix.Translation(gv(position))@Matrix.Rotation(yaw,4,'Z')
 for o in new:
  if o.parent not in new:o.matrix_world=pose@o.matrix_world
 if opened:
  for o in new:
   if 'HINGE_LEFT'in o.name:o.rotation_mode='XYZ';o.rotation_euler.z+=math.pi/2
   if 'HINGE_RIGHT'in o.name:o.rotation_mode='XYZ';o.rotation_euler.z-=math.pi/2
 bpy.context.view_layer.update()
 return new
def render(folder,name):
 bpy.context.scene.render.filepath=str(folder/'qa'/name);bpy.ops.render.render(write_still=True)
def bank():
 bpy.ops.wm.open_mainfile(filepath=str(HERE/'source/AST-CRW-G3-002.blend'));setup()
 import_pose(HERE/'exports/AST-STF-G3-028.glb');import_pose(HERE/'exports/AST-STF-G3-029.glb')
 # Original supports remain in the source view wherever they meet this package.
 support=json.load(open(HERE/'source/LABELLED_BANK_CONTRACT.json'))['protected_D04_support_columns']
 for q in support:
  a=q['bounds'];bpy.ops.mesh.primitive_cube_add(size=1,location=gv([(a[0]+a[1])/2,(a[2]+a[3])/2,(a[4]+a[5])/2]))
  o=bpy.context.object;o.name='RETAINED_D04_CONTEXT_'+q['name'];o.dimensions=(a[1]-a[0],a[5]-a[4],a[3]-a[2])
  o.color=(.4,.45,.48,1)
 # Unscaled actual source doors, same hinge angles as the tested controller.
 contract=json.load(open(HERE/'source/LABELLED_BANK_CONTRACT.json'))
 for q in contract['service_doors']:import_pose(ROOT/'BlenderCatalogue/assets/staff_threshold/exports/AST-STF-008.glb',q['position'],q['yaw'],q['name']=='C125EntryGate')
 camera((77.6,13.62,-52.6),(69.8,13.05,-52.1),22)
 for o in bpy.context.scene.objects:
  if o.name.startswith('C125__Rest')and'__Curtain__'in o.name:o.hide_render=True
 if not DOOR_ONLY:render(HERE,'CREW_C125_WIDE_INTERIOR.png')
 for o in bpy.context.scene.objects:
  if o.name.startswith('C125__Rest')and'__Curtain__'in o.name:o.hide_render=False
 camera((85,13.65,-52.0),(75,13.3,-52),24)
 render(HERE,'CREW_BANK_CONTEXT_DOOR.png')
 # Roof hidden transiently for a whole sixteen-allocation spatial review.
 for o in bpy.context.scene.objects:
  if o.type=='MESH'and('overhead_'in o.name or 'CollarHead'in o.name):o.hide_render=True
 camera((141,102,-139),(86,12,-94),24,132)
 if not DOOR_ONLY:render(HERE,'CREW_SIXTEEN_ALLOCATION_CONTEXT.png')
def training():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);setup()
 import_pose(ROOT/'BlenderCatalogue/assets/crew_batch_receiving_preparation_20261008/incoming/D03_directory_05.glb')
 for f in ['AST-STF-G3-022.glb','AST-STF-G3-026.glb','AST-STF-G3-027.glb']:import_pose(PRE/'exports'/f)
 import_pose(ROOT/'BlenderCatalogue/assets/staff_threshold/exports/AST-STF-008.glb',(-99.4,12,0),math.pi/2,True)
 camera((-103,13.6,0),(-90,13.3,0),20)
 render(PRE,'TRAINING_RECEIVER_WIDE_SOURCE.png')
bank();training()
(HERE/'qa/SOURCE_VIEW_METHOD.json').write_text(json.dumps(dict(
 renderer='Blender 4.3.2 Workbench, original packed textures, neutral diagnostic studio illumination',
 photos=['CREW_C125_WIDE_INTERIOR.png','CREW_BANK_CONTEXT_DOOR.png','CREW_SIXTEEN_ALLOCATION_CONTEXT.png','../d03_remaining_receivers_batch013/qa/TRAINING_RECEIVER_WIDE_SOURCE.png'],
 real_native_geometry=True,concept_generation=False,source_files_saved_or_modified=False,
 context_supports='Exact retained D04 source AABBs, neutral diagnostic material.',
 transient_roof_hidden_only_in_sixteen_allocation_overview=True,
 transient_C125_curtains_hidden_only_in_interior_rest_review=True,
 final_game_CRT_target_hardware_or_species_visual_acceptance=False),indent=2)+'\n')
