from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
D=Path(__file__).parent;G=Path('/workspace/astraea-protected-integration-20261012/Game');N=D/'native/VESPER_SERVICE_RECEIVER_r001.blend';pin=hashlib.sha256(N.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(N));bpy.data.collections['VESPER_SERVICE_RECEIVING_RUNTIME_R001'].hide_render=True;col=bpy.data.collections['VESPER_SERVICE_RECEIVING_AUTHORING_R001'];col.hide_render=False
for o in col.objects:
 if 'SourceJoinedRoof'in o.name:o.hide_render=True
B=lambda p:Vector((p[0],-p[2],p[1]))
for file,origin in [('AST-DIN-003.glb',(48.6,61,233)),('AST-DIN-004.glb',(21,61,182))]:
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(G/'assets/models'/file))
 for o in set(bpy.data.objects)-before:
  if o.parent is None:o.location+=B(origin)
  if 'Ceiling'in o.name:o.hide_render=True
records=json.loads((G/'data/generated/structural_meshes.json').read_text())['regions']
for row in records:
 if row['id']not in ['D10_vesper_floor','D10_aft_route']:continue
 vs=[];fs=[]
 for tri in row['triangles']:
  fs.append(tuple(range(len(vs),len(vs)+3)));vs.extend([tuple(B((x,row['floor_y'],z)))for x,z in tri])
 mesh=bpy.data.meshes.new(row['id']);mesh.from_pydata(vs,[],fs);mesh.update();o=bpy.data.objects.new(row['id'],mesh);bpy.context.collection.objects.link(o)
 mat=bpy.data.materials.new(row['id']+'_review');mat.diffuse_color=(.55,.52,.45,1);mesh.materials.append(mat)
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1152;scene.render.resolution_y=864;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.world=scene.world or bpy.data.worlds.new('ReviewWorld');scene.world.color=(.3,.33,.36);sh=scene.display.shading;sh.light='STUDIO';sh.color_type='TEXTURE';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';scene.display.render_aa='8';scene.view_settings.view_transform='Standard';data=bpy.data.cameras.new('VesperPhysicalReview');data.type='ORTHO';data.ortho_scale=106;cam=bpy.data.objects.new('VesperPhysicalReview',data);scene.collection.objects.link(cam);cam.location=B((108,117,270));cam.rotation_euler=(B((35,62,202))-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam;out=D/'visual_review';out.mkdir(exist_ok=True);path=out/'VESPER_RECEIVING_NATIVE_REVIEW.png';scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);assert hashlib.sha256(N.read_bytes()).hexdigest()==pin;(out/'RECEIPT.json').write_text(json.dumps({'status':'LOCAL_NATIVE_CUTAWAY_REVIEW_PENDING','native_sha256':pin,'image_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'scope':'New receiving architecture plus two exact original Vesper architectural models at retained transforms. Cutaway roof/ceiling; exact two compiled floor owners shown; room furniture and wider whole-ship context omitted. Workbench, no Game/CRT/final art admission.','user_delivery_requested':False},indent=2)+'\n');print('PASS_NATIVE_REVIEW_RENDER')
