"""Actual unchanged Supreme with the new private kits/receivers; source review only."""
import bpy,bmesh,pathlib,json,hashlib
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[3];P=pathlib.Path(__file__).resolve().parent
original=pathlib.Path('/workspace/group2-native-originals/sections/787_supreme/787_supreme.blend')
contract=json.loads((ROOT/'Game/data/group2_completion/contracts/787.json').read_text())
assert hashlib.sha256(original.read_bytes()).hexdigest()==contract['native_sha256']
bpy.ops.wm.open_mainfile(filepath=str(original));scene=bpy.context.scene
original_meshes={o.name for o in scene.objects if o.type=='MESH'}
original_poses={n:bpy.data.objects[n].matrix_world.copy()for n in original_meshes}
def append(path,prefix):
 with bpy.data.libraries.load(str(path),link=False)as(a,b):b.objects=[n for n in a.objects if n.startswith(prefix)]
 for obj in b.objects:scene.collection.objects.link(obj)
append(ROOT/'BlenderCatalogue/assets/group2_private_vertical_20261011/source/PRIVATE_VERTICAL_KITS_r002.blend','G2V_787_')
append(ROOT/'BlenderCatalogue/assets/group2_private_vertical_20261011/source/CONVERSATION_RECEIVERS_r001.blend','G2R_787_')
pit=next(r for r in json.loads((ROOT/'Game/data/group2_pit_perimeters/PLAN_r003.json').read_text())['suites']if r['source_index']==787)
for suffix in pit['previous_receiver']['deactivate_only']:
 o=bpy.data.objects['G2R_787_'+suffix];bpy.data.objects.remove(o,do_unlink=True)
poses={n:bpy.data.objects[n].matrix_world.copy()for n in pit['furniture_pose_patch']['exact_mesh_names']}
def depth(name):
 o=bpy.data.objects[name];d=0
 while o.parent is not None:d+=1;o=o.parent
 return d
for name in sorted(poses,key=depth):
 pose=poses[name]
 d=pit['furniture_pose_patch']['per_mesh_world_delta'].get(name,[0,.45,0]);pose.translation+=Vector((d[0],-d[2],d[1]));bpy.data.objects[name].matrix_world=pose
bpy.context.view_layer.update()
for name,old_pose in original_poses.items():
 expected=old_pose.copy()
 if name in poses:
  d=pit['furniture_pose_patch']['per_mesh_world_delta'].get(name,[0,.45,0]);expected.translation+=Vector((d[0],-d[2],d[1]))
 assert max(abs(a-b)for ar,br in zip(expected,bpy.data.objects[name].matrix_world)for a,b in zip(ar,br))<.0001,name
append(P/'source/PIT_PERIMETERS_r003.blend','G2P_787_')
append(ROOT/'BlenderCatalogue/assets/group2_completion_20261011/source/FLOOR_INTERFACE_r001.blend','GROUP2_787_upper')
row=next(r for r in json.loads((ROOT/'Game/data/group2_private_vertical/INTERFACES.json').read_text())['suites']if r['source_index']==787)['lower_successor']
vertices=[];faces=[];lookup={}
def vertex(p,h):
 q=(p[0],-p[1],h)
 if q not in lookup:lookup[q]=len(vertices);vertices.append(q)
 return lookup[q]
for triangle in row['triangles']:
 faces.append(tuple(vertex(p,102)for p in triangle));faces.append(tuple(vertex(p,101.76)for p in reversed(triangle)))
for ring in [row['boundary']]+row['holes']:
 for i,a in enumerate(ring):
  b=ring[(i+1)%len(ring)];faces.append((vertex(a,101.76),vertex(b,101.76),vertex(b,102),vertex(a,102)))
mesh=bpy.data.meshes.new('SupremeLowerPrivatePitFloor_Interface');mesh.from_pydata(vertices,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);bm.to_mesh(mesh);bm.free()
floor=bpy.data.objects.new(mesh.name,mesh);scene.collection.objects.link(floor)
material=bpy.data.materials.new('SourceFloorReview');material.diffuse_color=(.29,.32,.34,1);mesh.materials.append(material)
camera_data=bpy.data.cameras.new('Group2_Private_Construction_Wide');camera=bpy.data.objects.new(camera_data.name,camera_data);scene.collection.objects.link(camera)
def source(a):return Vector((a[0],-a[2],a[1]))
camera.location=source([-111.35,104.1,35.35]);target=source([-103.5,103.1,29.6]);camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.lens=20;scene.camera=camera
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
shade=scene.display.shading;shade.light='STUDIO';shade.studiolight_rotate_z=.3;shade.color_type='MATERIAL';shade.show_shadows=True;shade.shadow_intensity=.15;shade.show_cavity=True;shade.cavity_type='BOTH';shade.background_type='WORLD';scene.world.color=(.35,.35,.35)
scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast';scene.view_settings.exposure=1
out=P/'evidence/COMPLETE_PIT_WIDE002.png';assert not out.exists();scene.render.filepath=str(out);bpy.ops.render.render(write_still=True)
assert original_meshes.issubset({o.name for o in scene.objects if o.type=='MESH'})
assert hashlib.sha256(original.read_bytes()).hexdigest()==contract['native_sha256']
(P/'evidence/SOURCE_CONTEXT_RECEIPT002.json').write_text(json.dumps({'pass':True,'image':str(out.relative_to(ROOT)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'real_source_geometry':True,'original_source_meshes_retained':len(original_meshes),'original_source_meshes_removed':0,'original_native_sha256':contract['native_sha256'],'camera_world_xyz':[-111.35,104.1,35.35],'ordinary_eye_height_m':1.65,'lens_mm':20,'review':'Actual native source plus declared furniture pose patch, full pit terraces, retained rear ramp and held private cabin; neutral Workbench colors','accepted_game_photometry_or_final_art':False,'original_native_modified':False},indent=2)+'\n')
print('PASS wide actual-source private construction context')
