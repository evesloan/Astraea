from pathlib import Path
import bpy,json,math,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];N=json.loads((W/'NATIVE_EXPORT_CHECK.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1]);native=W/N['native'];before=sha(native);bpy.ops.wm.open_mainfile(filepath=str(native))
bpy.ops.import_scene.gltf(filepath=str(R/'Game/assets/models/AST-RES-TIDAL_D13_service_receiving_r001.glb'))
P=json.loads((R/'Game/data/architecture/TIDAL_D13_SERVICE_RECEIVING.json').read_text())
mat=bpy.data.materials.new('UNSAVED_ExistingRuntimeStaffFloor');mat.diffuse_color=(.22,.24,.26,1)
for region in P['floor_regions']:
 vertices=[];faces=[]
 for tri in region['triangles']:
  k=len(vertices);vertices.extend(B((x,84,z))for x,z in tri);faces.append((k,k+1,k+2))
 mesh=bpy.data.meshes.new('UNSAVED_EXISTING_FLOOR_'+region['id']);mesh.from_pydata(vertices,[],faces);mesh.materials.append(mat);ob=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(ob)
# Unsaved source-review illumination at the existing retained fixture markers.
for i in P['fixtures']:
 data=bpy.data.lights.new('UNSAVED_EXISTING_FIXTURE_'+i['name'],'POINT');data.energy=120;data.color=i['color'];ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);ob.location=B(i['position'])
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=4;scene.render.resolution_x=960;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
bpy.ops.object.camera_add();camera=bpy.context.object;camera.data.lens=22;scene.camera=camera
camera.location=B((-62,85.65,-495.5));camera.rotation_euler=(Vector(B((-59.7,84.9,-490)))-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(W/'SOURCE_D13_LOCAL_FITTINGS.png');bpy.ops.render.render(write_still=True)
# Native-only overview exposes all three receiving fittings and empty parking, without touching the source.
for o in bpy.data.objects:
 if o.type=='MESH' and not any(o.name.startswith(a)for a in ['D13_Clean','D13_Closed','D13_Parking','D13_PhysicalLabel','UNSAVED_EXISTING_FLOOR']):o.hide_render=True
bpy.ops.object.light_add(type='AREA',location=B((-64,90,-490)));fill=bpy.context.object;fill.data.energy=1200;fill.data.size=8;fill.rotation_euler=(Vector(B((-59.7,85,-490)))-fill.location).to_track_quat('-Z','Y').to_euler()
camera.location=B((-65.4,88.4,-493.9));camera.rotation_euler=(Vector(B((-60.4,84.8,-489.7)))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=28;scene.render.filepath=str(W/'SOURCE_D13_FITTINGS_OVERVIEW.png');bpy.ops.render.render(write_still=True)
assert sha(native)==before;assert sha(W/N['export'])==N['export_sha256'];print('PASS: unsaved source context views; exact native/export unchanged')
