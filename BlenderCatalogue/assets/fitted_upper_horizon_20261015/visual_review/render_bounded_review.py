from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
D=Path(__file__).resolve().parent;G=Path('/workspace/astraea-protected-integration-20261012/Game');native=D/'native/FITTED_UPPER_HORIZON_r001.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(native);bpy.ops.wm.open_mainfile(filepath=str(native));B=lambda p:Vector((p[0],-p[2],p[1]));pins={}
for file in ['AFT_CROWN_FOYER_WAITING_EDGES_r001.glb','AFT_CROWN_SITTING_BAYS_r001.glb']:
 path=G/'assets/models'/file;pins[file]=sha(path);bpy.ops.import_scene.gltf(filepath=str(path))
floors=json.loads((G/'data/generated/structural_meshes.json').read_text());floor_ids=[];mat=bpy.data.materials.new('Retained_floor_review');mat.diffuse_color=(.43,.45,.46,1)
for row in floors['regions']:
 if abs(row['floor_y']-106.5)>.001 or not any(k in row['id'] for k in ['upper_horizon','foyer','crown_sitting']):continue
 floor_ids.append(row['id']);vs=[B((p[0],row['floor_y'],p[1]))for tri in row['triangles']for p in tri];mesh=bpy.data.meshes.new(row['id']);mesh.from_pydata(vs,[],[tuple(range(i,i+3))for i in range(0,len(vs),3)]);mesh.materials.append(mat);mesh.update();o=bpy.data.objects.new(row['id'],mesh);bpy.context.scene.collection.objects.link(o)
for mat in bpy.data.materials:
 if not mat.use_nodes:continue
 node=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if node:mat.diffuse_color=tuple(node.inputs['Base Color'].default_value[:3])+(float(node.inputs['Alpha'].default_value),)
 for n in mat.node_tree.nodes:
  if n.type=='TEX_IMAGE'and n.image:mat.node_tree.nodes.active=n;break
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.world.color=(.32,.34,.38);sh=scene.display.shading;sh.light='STUDIO';sh.color_type='TEXTURE';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';scene.display.render_aa='8';scene.view_settings.view_transform='Standard';data=bpy.data.cameras.new('HorizonReview');data.type='ORTHO';data.ortho_scale=64;camera=bpy.data.objects.new('HorizonReview',data);scene.collection.objects.link(camera);camera.location=B((-72,160,109));camera.rotation_euler=(B((-22,107,140))-camera.location).to_track_quat('-Z','Y').to_euler();scene.camera=camera;out=D/'visual_review';out.mkdir(exist_ok=True);file=out/'FITTED_HORIZON_R001_NATIVE_CONTEXT.png';scene.render.filepath=str(file);bpy.ops.render.render(write_still=True);assert sha(native)==before;(out/'RECEIPT.json').write_text(json.dumps({'file':file.name,'sha256':sha(file),'native_sha256':before,'retained_context_pins':pins,'compiled_floor_ids':floor_ids,'scope':'Exact fitted Horizon runtime geometry with original foyer/sitting assets and original floor triangles. Roof, enclosing walls and window shell omitted for visibility. Neutral Blender Workbench; not runtime lighting, CRT, operation or final-art acceptance.','reference_reopened':'Game/docs/visual_checks/upper_horizon_enclosure_20261005/horizon_port_seated_clear_world_capture.png'},indent=2)+'\n');print('PASS_HORIZON_BOUNDED_NATIVE_REVIEW')
