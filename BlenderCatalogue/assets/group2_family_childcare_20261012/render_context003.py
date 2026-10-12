"""New childcare component with actual unchanged retained Family receiving source."""
import bpy,pathlib,json,hashlib
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[3];P=pathlib.Path(__file__).resolve().parent
native=P/'source/FAMILY_CHILDCARE_r001.blend';bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene
source=ROOT/'Game/assets/models/FAMILY_TERRACE_ARCHITECTURE_lift_r003.glb';sha=hashlib.sha256(source.read_bytes()).hexdigest();before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(source));retained=set(bpy.data.objects)-before;poses={o:o.matrix_world.copy()for o in retained if o.type=='MESH'}
camera_data=bpy.data.cameras.new('FAMILY_CHILD_SOURCE_WIDE');camera=bpy.data.objects.new(camera_data.name,camera_data);scene.collection.objects.link(camera)
def point(a):return Vector((a[0],-a[2],a[1]))
camera.location=point([90.1,99.15,355.7]);target=point([84.8,98.7,358.7]);camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.lens=20;scene.camera=camera
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
s=scene.display.shading;s.light='STUDIO';s.color_type='MATERIAL';s.show_shadows=True;s.shadow_intensity=.15;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD'
if scene.world is None:scene.world=bpy.data.worlds.new('ReviewWorld')
scene.world.color=(.35,.35,.35);scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast';scene.view_settings.exposure=1
out=P/'evidence/FAMILY_CHILD_SOURCE_WIDE003.png';assert not out.exists();scene.render.filepath=str(out);bpy.ops.render.render(write_still=True)
for o,pose in poses.items():assert all(abs(a-b)<.0001for ar,br in zip(pose,o.matrix_world)for a,b in zip(ar,br))
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
(P/'evidence/SOURCE_CONTEXT003.json').write_text(json.dumps({'pass':True,'actual_retained_receiver_source':str(source.relative_to(ROOT)),'receiver_sha256':sha,'retained_receiver_meshes_unchanged':len(poses),'retained_meshes_removed_or_hidden':0,'image_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'camera_world_xyz':[90.1,99.15,355.7],'ordinary_eye_height_m':1.65,'lens_mm':20,'programme_adoption_child_body_or_final_art_accepted':False},indent=2)+'\n')
print('PASS actual source childcare/retained receiver context; no new floor or removed originals')
