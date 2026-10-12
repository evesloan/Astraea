"""Corrected real-source assembly. Preserve immutable source bytes and all other poses."""
import bpy,pathlib,json,hashlib,math
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[3];P=pathlib.Path(__file__).resolve().parent
contract=json.loads((ROOT/'Game/data/group2_meal_arrangement/CHAIR_POSE_SUCCESSOR.json').read_text());corrections={r['name']:r for r in contract['rows']}
meal=ROOT/'BlenderCatalogue/assets/group2_family_meal_20261012/source/FAMILY_MEAL_FITTINGS_r001.blend';bpy.ops.wm.open_mainfile(filepath=str(meal));scene=bpy.context.scene
source=ROOT/'Game/assets/models/FAMILY_TERRACE_ARCHITECTURE_lift_r003.glb';source_sha=hashlib.sha256(source.read_bytes()).hexdigest();before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(source));architecture=set(bpy.data.objects)-before;poses={o:o.matrix_world.copy()for o in architecture if o.type=='MESH'}
receiving=json.loads((ROOT/'Game/data/architecture/FAMILY_TERRACE_RECEIVING.json').read_text());placed=[]
for item in receiving['retained_asset_instances']:
 if not item['name'].startswith('D16_'):continue
 definition=receiving['retained_asset_definitions'][item['catalogue_id']];src=ROOT/'Game/assets/models'/definition['model_file'];assert hashlib.sha256(src.read_bytes()).hexdigest()==definition['sha256']
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(src));objects=set(bpy.data.objects)-before
 group=bpy.data.objects.new(item['name'],None);scene.collection.objects.link(group)
 for obj in objects:
  if obj.parent not in objects:obj.parent=group
 yaw=corrections[item['name']]['corrected_yaw_degrees']if item['name']in corrections else item['yaw']
 group.rotation_euler.z=math.radians(yaw);p=item['world_xyz'];group.location=Vector((p[0],-p[2],p[1]));group.scale=Vector((item['scale'],)*3)
 placed.append({'name':item['name'],'yaw':yaw,'world_xyz':p,'intentionally_corrected':item['name']in corrections})
assert sum(v['intentionally_corrected']for v in placed)==12
def point(a):return Vector((a[0],-a[2],a[1]))
camera_data=bpy.data.cameras.new('FamilyMealInwardSourceWide');camera=bpy.data.objects.new(camera_data.name,camera_data);scene.collection.objects.link(camera)
camera.location=point([75.7,99.15,353.1]);target=point([79.5,98.45,348.1]);camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.lens=22;scene.camera=camera
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
s=scene.display.shading;s.light='STUDIO';s.color_type='MATERIAL';s.show_shadows=True;s.shadow_intensity=.15;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD'
if scene.world is None:scene.world=bpy.data.worlds.new('ReviewWorld')
scene.world.color=(.35,.35,.35);scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast';scene.view_settings.exposure=1
native=P/'source/FAMILY_MEAL_INWARD_ARRANGEMENT_r001.blend';native.parent.mkdir(parents=True,exist_ok=True);assert not native.exists();bpy.ops.wm.save_as_mainfile(filepath=str(native))
out=P/'evidence/FAMILY_MEAL_INWARD_SOURCE_WIDE001.png';out.parent.mkdir(exist_ok=True);assert not out.exists();scene.render.filepath=str(out);bpy.ops.render.render(write_still=True)
for o,pose in poses.items():assert all(abs(a-b)<.0001for ar,br in zip(pose,o.matrix_world)for a,b in zip(ar,br))
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_sha
(P/'evidence/SOURCE_CONTEXT001.json').write_text(json.dumps({'pass':True,'actual_retained_receiver_source':str(source.relative_to(ROOT)),'receiver_sha256':source_sha,'retained_architecture_meshes_unchanged':len(poses),'intentional_chair_rotations':12,'D16_retained_asset_instances':placed,'retained_architecture_removed_or_hidden':0,'source_native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'image_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'camera_world_xyz':[75.7,99.15,353.1],'ordinary_eye_height_m':1.65,'lens_mm':22,'production_adoption_or_final_art_accepted':False},indent=2)+'\n')
print('PASS corrected12 retained chair instances inward; other source architecture/poses retained')
