from pathlib import Path
import bpy,json,hashlib,subprocess
from mathutils import Vector
D=Path(__file__).resolve().parent;S=D.parent;R=Path('/workspace/astraea-protected-integration-20261012');G=R/'Game';commit=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD']).decode().strip();assert commit=='328b706e4b8c58916284f5895b828b56d060789f';assert bpy.app.version[:3]==(4,3,2)
native=R/'BlenderCatalogue/assets/theater_secondary_receiving_20261015/THEATER_SECONDARY_APPROACHES_r002.blend';assert hashlib.sha256(native.read_bytes()).hexdigest()==json.loads((S/'NATIVE_VERIFICATION.json').read_text())['native_sha256'];bpy.ops.wm.open_mainfile(filepath=str(native));bpy.context.preferences.filepaths.save_version=0
# Import only the exact retained static theater and closed-motion source,then retain bounded neighboring context.
owned=set(bpy.data.objects);source_pins={}
for file in['AST-CUL-005_static_003.glb','AST-CUL-005_moving_003.glb']:
 p=G/'assets/models'/file;source_pins[file]=hashlib.sha256(p.read_bytes()).hexdigest();before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(p))
 for o in set(bpy.data.objects)-before:
  if o.type!='MESH':continue
  vs=[o.matrix_world@Vector(v)for v in o.bound_box];xs=[v.x for v in vs];ys=[-v.y for v in vs];zs=[v.z for v in vs]
  if max(xs)<-37 or min(xs)>-2 or max(ys)<-178 or min(ys)>-165 or max(zs)<69 or min(zs)>89:o.hide_render=True
for o in bpy.data.objects:
 if o.type in['LIGHT','CAMERA']:o.hide_render=True
for m in bpy.data.materials:
 if not m.use_nodes:continue
 node=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if node:m.diffuse_color=tuple(node.inputs['Base Color'].default_value[:3])+(float(node.inputs['Alpha'].default_value),)
 for n in m.node_tree.nodes:
  if n.type=='TEX_IMAGE'and n.image:m.node_tree.nodes.active=n;break
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1280;scene.render.resolution_y=800;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False;scene.world.color=(.32,.34,.38)
sh=scene.display.shading;sh.light='STUDIO';sh.studiolight_rotate_z=.35;sh.color_type='TEXTURE';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.curvature_ridge_factor=1.25;sh.curvature_valley_factor=1.0;sh.background_type='WORLD';sh.show_specular_highlight=True;scene.display.render_aa='8';scene.view_settings.view_transform='Standard'
def B(p):return Vector((p[0],-p[2],p[1]))
rows=[]
for name,at,target,lens in [('INSTALLED_D12_SECONDARY_APPROACH_WIDE001',[-5,79.75,-171.7],[-28,79.5,-171.7],20),('INSTALLED_THREE_THEATER_APPROACHES_WIDE001',[-2,87.5,-153],[-22,77.2,-171.7],28)]:
 data=bpy.data.cameras.new(name);data.lens=lens;obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.location=B(at);obj.rotation_euler=(B(target)-obj.location).to_track_quat('-Z','Y').to_euler();scene.camera=obj;obj.hide_render=False;path=D/(name+'.png');scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);rows.append({'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'camera_godot':at,'target_godot':target})
report={'status':'BOUNDED_ACTUAL_INSTALLED_SOURCE_VIEWS','installed_commit':commit,'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'original_context_sources':source_pins,'images':rows,'renderer':'Blender4.3.2 Workbench neutral studio;source textures where supported','scope':'Exact installed three secondary approach native models and retained neighboring static/closed-motion theater sources at authored poses;bounded context only,not whole-ship capture','not_claimed':['Godot rendering','CRT image','runtime illumination','target hardware orwhole ship final visual acceptance'],'source_files_changed':False};(D/'PROGRESS_PICTURE_RECEIPT.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS_BOUNDED_INSTALLED_THEATER_PICTURES')
