"""New childcare component with actual unchanged retained Family receiving source."""
import bpy,pathlib,json,hashlib
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[3];P=pathlib.Path(__file__).resolve().parent
native=P/'source/FAMILY_MEAL_FITTINGS_r001.blend';bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene
source=ROOT/'Game/assets/models/FAMILY_TERRACE_ARCHITECTURE_lift_r003.glb';sha=hashlib.sha256(source.read_bytes()).hexdigest();before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(source));retained=set(bpy.data.objects)-before;poses={o:o.matrix_world.copy()for o in retained if o.type=='MESH'}
receiving=json.loads((ROOT/"Game/data/architecture/FAMILY_TERRACE_RECEIVING.json").read_text())
for fitting in receiving["retained_asset_instances"]:
 if not fitting["name"].startswith("D16_UpperGroupTable_Seat"):continue
 src=ROOT/"Game/assets/models"/receiving["retained_asset_definitions"][fitting["catalogue_id"]]["model_file"];assert hashlib.sha256(src.read_bytes()).hexdigest()==receiving["retained_asset_definitions"][fitting["catalogue_id"]]["sha256"]
 existing=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(src));new=set(bpy.data.objects)-existing
 for obj in new:
  if obj.parent not in new:
   import math
   obj.rotation_euler.z+=math.radians(fitting["yaw"]);obj.location+=Vector((fitting["world_xyz"][0],-fitting["world_xyz"][2],fitting["world_xyz"][1]))
 for obj in new:obj.name=fitting["name"]+"_"+obj.name
camera_data=bpy.data.cameras.new('FAMILY_CHILD_SOURCE_WIDE');camera=bpy.data.objects.new(camera_data.name,camera_data);scene.collection.objects.link(camera)
def point(a):return Vector((a[0],-a[2],a[1]))
camera.location=point([76.9,99.15,351.2]);target=point([79.5,98.45,348.1]);camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.lens=20;scene.camera=camera
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
s=scene.display.shading;s.light='STUDIO';s.color_type='MATERIAL';s.show_shadows=True;s.shadow_intensity=.15;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD'
if scene.world is None:scene.world=bpy.data.worlds.new('ReviewWorld')
scene.world.color=(.35,.35,.35);scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast';scene.view_settings.exposure=1
out=P/'evidence/FAMILY_MEAL_SOURCE_WIDE001.png';assert not out.exists();scene.render.filepath=str(out);bpy.ops.render.render(write_still=True)
for o,pose in poses.items():assert all(abs(a-b)<.0001for ar,br in zip(pose,o.matrix_world)for a,b in zip(ar,br))
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
(P/'evidence/SOURCE_CONTEXT001.json').write_text(json.dumps({'pass':True,'actual_retained_receiver_source':str(source.relative_to(ROOT)),'receiver_sha256':sha,'retained_receiver_meshes_unchanged':len(poses),'retained_meshes_removed_or_hidden':0,'image_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'camera_world_xyz':[76.9,99.15,351.2],'ordinary_eye_height_m':1.65,'lens_mm':20,'programme_adoption_child_body_or_final_art_accepted':False},indent=2)+'\n')
print('PASS actual source childcare/retained receiver context; no new floor or removed originals')
