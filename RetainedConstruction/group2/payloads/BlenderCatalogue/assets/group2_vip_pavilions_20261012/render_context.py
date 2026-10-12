"""Real native wet-kit view; unplaced source construction, no shared roof omitted."""
import bpy,hashlib,json,pathlib
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[3];P=pathlib.Path(__file__).resolve().parent
native=P/'source/VIP_WET_KITS_r003.blend';before=hashlib.sha256(native.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene
for collection in bpy.data.collections:
 if collection.name.startswith('G2VIP_QUIET_'):collection.hide_render=True
meshes={o.name for o in scene.objects if o.type=='MESH'and o.name.startswith('G2VIP_TIDAL_')}
camera_data=bpy.data.cameras.new('VIP_Real_Source_Kit_Wide');camera=bpy.data.objects.new(camera_data.name,camera_data);scene.collection.objects.link(camera)
def point(a):return Vector((a[0],-a[2],a[1]))
camera.location=point([-13.1,3.15,-8.45]);target=point([6.7,2.7,-9.25]);camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.lens=20;scene.camera=camera
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
shade=scene.display.shading;shade.light='STUDIO';shade.studiolight_rotate_z=.3;shade.color_type='MATERIAL';shade.show_shadows=True;shade.shadow_intensity=.15;shade.show_cavity=True;shade.cavity_type='BOTH';shade.background_type='WORLD'
if scene.world is None:scene.world=bpy.data.worlds.new('SourceReviewWorld')
scene.world.color=(.35,.35,.35);scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast';scene.view_settings.exposure=1
out=P/'evidence/VIP_WET_SOURCE_WIDE001.png';assert not out.exists();scene.render.filepath=str(out);bpy.ops.render.render(write_still=True)
assert meshes.issubset({o.name for o in scene.objects if o.type=='MESH'})and hashlib.sha256(native.read_bytes()).hexdigest()==before
(P/'evidence/SOURCE_CONTEXT001.json').write_text(json.dumps({'pass':True,'real_native_source':True,'source_sha256':before,'source_meshes_retained':len(meshes),'source_meshes_removed':0,
 'image_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'lens_mm':20,'ordinary_eye_above_terrace_m':1.65,'camera_local_xyz':[-13.1,3.15,-8.45],
 'image':'evidence/VIP_WET_SOURCE_WIDE001.png','scope':'Unplaced Tidal construction kit; Quiet alternative retained separately; this is not an installed shared commons',
 'shared_receiving_roof_removed':False,'shared_placement_final_art_photometry_accepted':False},indent=2)+'\n')
print('PASS actual native source kit contextual review')
