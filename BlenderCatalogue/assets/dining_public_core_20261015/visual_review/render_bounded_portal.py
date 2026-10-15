from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
D=Path(__file__).resolve().parent;G=Path('/workspace/astraea-protected-integration-20261012/Game');r=json.loads((D/'NATIVE_VERIFICATION.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();native=D/'native/FORWARD_D10_DINING_PUBLIC_BRANCHES_r001.blend';assert sha(native)==r['native_sha256'];bpy.ops.wm.open_mainfile(filepath=str(native));made=set(bpy.data.objects);src=G/'assets/models'/r['source_file'];assert sha(src)==r['source_sha256'];bpy.ops.import_scene.gltf(filepath=str(src));selected={x['source_name']for x in r['walls']}
for o in set(bpy.data.objects)-made:
 if o.type!='MESH':continue
 ps=[o.matrix_world@Vector(v)for v in o.bound_box];lo=Vector(tuple(min(p[i]for p in ps)for i in range(3)));hi=Vector(tuple(max(p[i]for p in ps)for i in range(3)))
 o.hide_render=o.name in selected or hi.z<60.5 or lo.z>65 or hi.x< -10 or lo.x>10 or -lo.y< -5 or -hi.y>5
for mat in bpy.data.materials:
 if not mat.use_nodes:continue
 node=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if node:mat.diffuse_color=tuple(node.inputs['Base Color'].default_value[:3])+(float(node.inputs['Alpha'].default_value),)
 for n in mat.node_tree.nodes:
  if n.type=='TEX_IMAGE'and n.image:mat.node_tree.nodes.active=n;break
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1200;scene.render.resolution_y=800;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.world.color=(.32,.34,.38);sh=scene.display.shading;sh.light='STUDIO';sh.color_type='TEXTURE';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';scene.display.render_aa='8';scene.view_settings.view_transform='Standard';B=lambda p:Vector((p[0],-p[2],p[1]));data=bpy.data.cameras.new('D10PublicPortal');data.lens=27;camera=bpy.data.objects.new('D10PublicPortal',data);scene.collection.objects.link(camera);camera.location=B((-15,63,0));camera.rotation_euler=(B((0,62.8,0))-camera.location).to_track_quat('-Z','Y').to_euler();scene.camera=camera;out=D/'visual_review';out.mkdir(exist_ok=True);file=out/'D10_PUBLIC_CORE_PORTAL_NATIVE_REVIEW.png';scene.render.filepath=str(file);bpy.ops.render.render(write_still=True);(out/'RECEIPT.json').write_text(json.dumps({'status':'BOUNDED_NATIVE_PORTAL_SOURCE_REVIEW','file':str(file),'sha256':sha(file),'native_sha256':sha(native),'retained_source_sha256':sha(src),'scope':'Exact native fourwall successors andbounded retained enclosure context atD10;local coordinates beforeunchanged coreorigin translation. Neutral BlenderWorkbench,notGodot/CRT illumination orfinalvisual acceptance.','source_bytes_changed':False},indent=2)+'\n');print('PASS_BOUNDED_DINING_PORTAL_VIEW')
