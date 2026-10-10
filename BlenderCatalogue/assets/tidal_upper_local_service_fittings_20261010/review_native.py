from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.loads((W/'FITTINGS_PLAN.json').read_text());N=json.loads((W/'NATIVE_EXPORT_CHECK.json').read_text());B=lambda p:(p[0],-p[2],p[1]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(W/N['native']);bpy.ops.wm.open_mainfile(filepath=str(W/N['native']))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=4;scene.render.resolution_x=960;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';bpy.ops.object.camera_add();camera=bpy.context.object;camera.data.lens=22;scene.camera=camera
native_meshes=[o for o in bpy.data.objects if o.type=='MESH'];images=[]
for deck in P['decks']:
 d=deck['deck'];y=deck['floor_y'];definition=json.loads((R/f'Game/data/architecture/TIDAL_D{d}_SERVICE_RECEIVING.json').read_text());old=set(bpy.data.objects)
 bpy.ops.import_scene.gltf(filepath=str(R/'Game/assets/models'/definition['corridor_file']))
 mat=bpy.data.materials.new(f'UNSAVED_D{d}_ExistingRuntimeFloor');mat.diffuse_color=(.22,.24,.26,1)
 for region in definition.get('floor_regions',definition.get('approach_floor_regions',[])):
  vertices=[];faces=[]
  for tri in region['triangles']:
   k=len(vertices);vertices.extend(B((x,y,z))for x,z in tri);faces.append((k,k+1,k+2))
  mesh=bpy.data.meshes.new('UNSAVED_'+region['id']);mesh.from_pydata(vertices,[],faces);mesh.materials.append(mat);ob=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(ob)
 for f in definition['fixtures']:
  position=f.get('position')
  if position is None:continue
  data=bpy.data.lights.new('UNSAVED_EXISTING_FIXTURE_'+f.get('name',f.get('marker','light')),'POINT');data.energy=120;data.color=f['color'];ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);ob.location=B(position)
 # Diagnostic fill is not a runtime lighting proposal; fixtures retain their current runtime settings.
 bpy.ops.object.light_add(type='AREA',location=B((-61,y+3,-490)));light=bpy.context.object;light.data.energy=120;light.data.size=3
 for o in native_meshes:o.hide_render=not o.name.startswith(f'D{d}_')
 camera.location=B((-62,y+1.65,-495.5));camera.rotation_euler=(Vector(B((-59.7,y+.9,-490)))-camera.location).to_track_quat('-Z','Y').to_euler();name=f'SOURCE_D{d}_LOCAL_FITTINGS.png';scene.render.filepath=str(W/name);bpy.ops.render.render(write_still=True);images.append(name)
 for o in set(bpy.data.objects)-old:bpy.data.objects.remove(o,do_unlink=True)
assert sha(W/N['native'])==before and sha(W/N['export'])==N['export_sha256']
(W/'SOURCE_VIEW_RUN.json').write_text(json.dumps({'status':'PASS','images':images,'source_only':True,'native_export_unchanged':True,'diagnostic_fill_runtime_unmodified':True},indent=2)+'\n');print('PASS: four unsaved deck-specific source context views')
