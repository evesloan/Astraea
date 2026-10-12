"""New fittings in the real unchanged source care adjunct; wide normal-height view."""
import bpy,bmesh,json,pathlib,hashlib
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[3];P=pathlib.Path(__file__).resolve().parent
key='port_central_upper_house';original=pathlib.Path('/workspace/group2-native-originals/facilities')/key/'house_adjunct.blend'
c=json.loads((ROOT/f'Game/data/group2_completion/contracts/{key}.json').read_text());assert hashlib.sha256(original.read_bytes()).hexdigest()==c['native_sha256']
bpy.ops.wm.open_mainfile(filepath=str(original));scene=bpy.context.scene
before={o.name:o.matrix_world.copy()for o in scene.objects if o.type=='MESH'}
with bpy.data.libraries.load(str(P/'source/CARE_FITTINGS_r001.blend'),link=False)as(a,b):b.objects=[n for n in a.objects if n.startswith('G2C_'+key+'_')]
for obj in b.objects:scene.collection.objects.link(obj)
floors=json.loads((ROOT/'Game/data/group2_completion/FLOOR_INTERFACE.json').read_text())
row=next(row for row in floors['rows']if row['source_owner']==key)
# The retained proposal floor is review context only, still awaiting supported adoption.
vertices=[];faces=[]
for tri in row['triangles']:
 start=len(vertices);vertices.extend([(q[0],-q[1],102)for q in tri]);faces.append((start,start+1,start+2))
mesh=bpy.data.meshes.new('RetainedFloorProposalReview');mesh.from_pydata(vertices,[],faces);mesh.update();o=bpy.data.objects.new(mesh.name,mesh);scene.collection.objects.link(o)
m=bpy.data.materials.new('ReviewFloor');m.diffuse_color=(.29,.32,.34,1);mesh.materials.append(m)
camera_data=bpy.data.cameras.new('CARE_SOURCE_WIDE');camera=bpy.data.objects.new(camera_data.name,camera_data);scene.collection.objects.link(camera)
def point(a):return Vector((a[0],-a[2],a[1]))
camera.location=point([-83.8,103.65,-20.2]);target=point([-80.8,103.0,-17.4]);camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.lens=20;scene.camera=camera
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
s=scene.display.shading;s.light='STUDIO';s.color_type='MATERIAL';s.show_shadows=True;s.shadow_intensity=.15;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.35,.35,.35)
scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast';scene.view_settings.exposure=1
out=P/'evidence/CARE_ADJUNCT_WIDE001.png';assert not out.exists();scene.render.filepath=str(out);bpy.ops.render.render(write_still=True)
for name,pose in before.items():assert all(abs(a-b)<.0001for ar,br in zip(pose,bpy.data.objects[name].matrix_world)for a,b in zip(ar,br))
assert hashlib.sha256(original.read_bytes()).hexdigest()==c['native_sha256']
(P/'evidence/SOURCE_CONTEXT001.json').write_text(json.dumps({'pass':True,'real_native_source':True,'original_meshes_unchanged':len(before),'image_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'camera_world_xyz':[-83.8,103.65,-20.2],'ordinary_eye_height_m':1.65,'lens_mm':20,'supported_floor_or_game_final_art_accepted':False},indent=2)+'\n')
print('PASS real unchanged adjunct and new source fittings contextual view')
