from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
D=Path(__file__).resolve().parent;G=Path('/workspace/astraea-protected-integration-20261012/Game');r=json.loads((D/'NATIVE_VERIFICATION.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();native=D/'native/THEATER_BACKSTAGE_RECEIVING_r001.blend';assert sha(native)==r['native_sha256'];bpy.ops.wm.open_mainfile(filepath=str(native));B=lambda p:Vector((p[0],-p[2],p[1]));source_pins={};owned=set(bpy.data.objects)
for o in bpy.data.collections['BACKSTAGE_RECEIVING_R001'].objects:
 if o.name=='Backstage_PositiveHeaderTieCanopy'or o.name.startswith('Backstage_CanopyEdge'):o.hide_render=True
for file,origin in[('AST-CUL-005_static_003.glb',(0,0,0)),('AST-CUL-005_moving_003.glb',(0,0,0)),('AST-CIR-005_fore_midship_cinema2_d11.glb',(0,0,-272))]:
 path=G/'assets/models'/file;source_pins[file]=sha(path);before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path))
 for o in set(bpy.data.objects)-before:
  if o.type!='MESH':continue
  o.parent=None;o.location+=B(origin);ps=[o.matrix_world@Vector(v)for v in o.bound_box];lo=Vector(tuple(min(p[i]for p in ps)for i in range(3)));hi=Vector(tuple(max(p[i]for p in ps)for i in range(3)));o.hide_render=hi.x< -37 or lo.x>9 or hi.z<69 or lo.z>76 or lo.z<69.2 or -lo.y< -263 or -hi.y> -242
# Actual retained floor triangles,not a new reference plane.
floors=json.loads((G/'data/generated/structural_meshes.json').read_text());mat=bpy.data.materials['warm_stone']
for row in floors['regions']:
 if row['id']not in['D11_theater_flat_00','D11_fore_route','D11_fore_midship_public_core_floor']:continue
 vs=[B((p[0],row['floor_y'],p[1]))for tri in row['triangles']for p in tri];mesh=bpy.data.meshes.new(row['id']);mesh.from_pydata(vs,[],[tuple(range(i,i+3))for i in range(0,len(vs),3)]);mesh.materials.append(mat);mesh.update();o=bpy.data.objects.new(row['id'],mesh);bpy.context.scene.collection.objects.link(o)
for mat in bpy.data.materials:
 if not mat.use_nodes:continue
 node=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if node:mat.diffuse_color=tuple(node.inputs['Base Color'].default_value[:3])+(float(node.inputs['Alpha'].default_value),)
 for n in mat.node_tree.nodes:
  if n.type=='TEX_IMAGE'and n.image:mat.node_tree.nodes.active=n;break
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1280;scene.render.resolution_y=850;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.world.color=(.32,.34,.38);sh=scene.display.shading;sh.light='STUDIO';sh.color_type='TEXTURE';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';scene.display.render_aa='8';scene.view_settings.view_transform='Standard';data=bpy.data.cameras.new('BackstageReview');data.type='ORTHO';data.ortho_scale=48;camera=bpy.data.objects.new('BackstageReview',data);scene.collection.objects.link(camera);camera.location=B((8,95,-226));camera.rotation_euler=(B((-18,70,-253))-camera.location).to_track_quat('-Z','Y').to_euler();scene.camera=camera;out=D/'visual_review';out.mkdir(exist_ok=True);file=out/'BACKSTAGE_RECEIVING_R001_NATIVE_CUTAWAY.png';scene.render.filepath=str(file);bpy.ops.render.render(write_still=True);(out/'RECEIPT.json').write_text(json.dumps({'status':'BOUNDED_NEW_NATIVE_CUTAWAY_WITH_RETAINED_CONTEXT','file':file.name,'sha256':sha(file),'native_sha256':sha(native),'original_context_sources':source_pins,'scope':'Exact new receiver withcanopy/edgecaps hidden;retained theater/closed staff door andper-deck core elements,plusactualthree compiled floor regions. Tall multideck context andsource furniture omitted. Neutral Blender Workbench,notGodot/CRT,operating lighting orfinal-art acceptance.','source_files_changed':False},indent=2)+'\n');assert sha(native)==r['native_sha256'];print('PASS_BOUNDED_BACKSTAGE_REVIEW')
