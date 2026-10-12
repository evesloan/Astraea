"""Wide real native source views; temporary cameras only, no exported-source modification."""
from pathlib import Path
import bpy,json,math,sys
from mathutils import Vector,Matrix
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4];PRE=HERE
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

import bmesh,hashlib
pins={str(f.relative_to(HERE)):hashlib.sha256(f.read_bytes()).hexdigest()for f in (HERE/'exports').glob('*.glb')}
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);setup()
for f in sorted((HERE/'exports').glob('*.glb')):import_pose(f)
# Temporary source cutaway of one real level; no file or exported data is saved.
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data=o.data.copy();bm=bmesh.new();bm.from_mesh(o.data)
 inv=o.matrix_world.inverted();normal=(o.matrix_world.to_3x3().transposed()@Vector((0,0,1))).normalized()
 for z,clear in [(20.76,True),(25.35,False)]:
  bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=inv@Vector((0,0,z)),plane_no=normal,clear_inner=clear,clear_outer=not clear,dist=.000001)
 bm.to_mesh(o.data);bm.free()
 if not o.data.polygons:o.hide_render=True
 # Overhead plates and fixture hangers remain visible in interior review;
 # only the survey overview hides roof category plates.
 if o.get('category')in['overhead','shaft_roof']or str(o.name).startswith('overhead_'):o.hide_render=True
camera((78,78,-544),(40.8,21,-489.97),24,78)
render(HERE,'FORE_CLINICAL_BAYS_WIDE_SOURCE.png')
for f,h in pins.items():assert hashlib.sha256((HERE/f).read_bytes()).hexdigest()==h
(HERE/'qa/SOURCE_VIEW_METHOD.json').write_text(json.dumps(dict(renderer='Blender 4.3.2 Workbench, original packed textures, neutral diagnostic studio light',photos=['FORE_CLINICAL_BAYS_WIDE_SOURCE.png'],real_native_geometry=True,concept_generation=False,transient_D05_cutaway_and_roof_hiding=True,source_or_export_files_saved_or_modified=False,final_game_CRT_hardware_or_species_visual_acceptance=False),indent=2)+'\n')
