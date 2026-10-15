from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
D=Path(__file__).resolve().parent;G=Path('/workspace/astraea-protected-integration-20261012/Game');r=json.loads((D/'NATIVE_RECEIVER_VERIFICATION.json').read_text());native=D/'native'/r['native_file'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(native)==r['native_sha256'];bpy.ops.wm.open_mainfile(filepath=str(native));B=lambda p:Vector((p[0],-p[2],p[1]));GV=lambda p:Vector((p.x,p.z,-p.y));next(c for c in bpy.data.collections if c.name.startswith('D10_CONNECTED_SERVICE_RUNTIME_R')).hide_render=True;next(c for c in bpy.data.collections if c.name.startswith('D10_CONNECTED_SERVICE_RECEIVERS_R')).hide_render=False
for o in next(c for c in bpy.data.collections if c.name.startswith('D10_CONNECTED_SERVICE_RECEIVERS_R')).objects:o.hide_render=not o.name.startswith('D10S_01_')or'SourceJoinedRoof'in o.name
source=G/'assets/models/SOL_D10_directory_01_remaining_batch.glb';old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(source))
for o in set(bpy.data.objects)-old:
 if o.type!='MESH':continue
 ps=[GV(o.matrix_world@Vector(v))for v in o.bound_box];o.hide_render=not('service_boundary'in o.name or (max(p.x for p in ps)<-48 and min(p.y for p in ps)<64.5))
floors=json.loads((G/'data/generated/structural_meshes.json').read_text());material=next(m for m in bpy.data.materials if m.name=='ASTRAEA_staff_bluegrey_paint')
for row in floors['regions']:
 if row['id']not in['D10_fore_route','D10_shared_table_reserved_cap']:continue
 vs=[B((p[0],row['floor_y'],p[1]))for tri in row['triangles']for p in tri];mesh=bpy.data.meshes.new(row['id']);mesh.from_pydata(vs,[],[tuple(range(i,i+3))for i in range(0,len(vs),3)]);mesh.materials.append(material);mesh.update();o=bpy.data.objects.new(row['id'],mesh);bpy.context.scene.collection.objects.link(o)
for mat in bpy.data.materials:
 if not mat.use_nodes:continue
 node=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if node:mat.diffuse_color=tuple(node.inputs['Base Color'].default_value[:3])+(float(node.inputs['Alpha'].default_value),)
 for n in mat.node_tree.nodes:
  if n.type=='TEX_IMAGE'and n.image:mat.node_tree.nodes.active=n;break
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1500;scene.render.resolution_y=1050;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.world=scene.world or bpy.data.worlds.new('D10ReviewWorld');scene.world.color=(.32,.34,.38);sh=scene.display.shading;sh.light='STUDIO';sh.color_type='TEXTURE';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';scene.display.render_aa='8';scene.view_settings.view_transform='Standard';data=bpy.data.cameras.new('D10ServiceReview');data.type='ORTHO';camera=bpy.data.objects.new('D10ServiceReview',data);scene.collection.objects.link(camera);scene.camera=camera;out=D/'visual_review';out.mkdir(exist_ok=True);views=[]
for name,eye,target,scale in [('D10_WEST_SERVICE_RECEIVING_WIDE',(-116,128,-500),(-38,62,-442),88),('D10_WEST_FINISHING_GALLEY',(-89,85,-479),(-60,62,-455),23)]:
 data.ortho_scale=scale;camera.location=B(eye);camera.rotation_euler=(B(target)-camera.location).to_track_quat('-Z','Y').to_euler();file=out/(name+'.png');scene.render.filepath=str(file);bpy.ops.render.render(write_still=True);views.append({'file':file.name,'sha256':sha(file)})
assert sha(native)==r['native_sha256'];(out/'RECEIPT.json').write_text(json.dumps({'status':'BOUNDED_NEW_SERVICE_NATIVE_WITH_EXACT_RETAINED_CONTEXT','native_sha256':sha(native),'source_room_sha256':sha(source),'views':views,'scope':'Port forward service receiving and clean finishing bay,withnewroofs removed. Original dining service boundary andnear-wall fittings plusoriginal compiledfloor triangles retained ascontext. New other two sites hidden. Neutral Blender Workbench,notGodot/CRT oroperating lighting,food safety,engineering orfinal-art acceptance.','original_sources_modified':False},indent=2)+'\n');print('PASS_BOUNDED_D10_SERVICE_VISUAL_REVIEW')
