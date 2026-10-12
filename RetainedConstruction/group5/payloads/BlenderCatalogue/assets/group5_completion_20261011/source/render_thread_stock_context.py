"""Clear actual original-source staff-lane context;readonly natives,neutral Workbench."""
from pathlib import Path
import bpy,json,hashlib,numpy as np
from mathutils import Vector
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
j=json.loads((ROOT/'Game/data/architecture/group5/THREAD_STOCK_REPAIR.json').read_text())
original=ROOT/j['original_native'];new=ROOT/j['native']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(original)==j['original_native_sha256'] and sha(new)==j['native_sha256']
bpy.ops.wm.open_mainfile(filepath=str(original))
for o in list(bpy.context.scene.objects):
    if o.type in ['CAMERA','LIGHT']:bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(str(new),link=False) as (src,dst):dst.objects=src.objects
for o in dst.objects:
    if o:bpy.context.scene.collection.objects.link(o)
floor_path=ROOT/'Game/data/generated/structural_meshes.json'
floor=next(r for r in json.loads(floor_path.read_text())['regions'] if r['id']=='D09_thread_shell_floor')
verts=[];faces=[]
for tri in floor['triangles']:
    start=len(verts);verts.extend([(x-8,-z-216,0) for x,z in tri]);faces.append((start,start+1,start+2))
d=bpy.data.meshes.new('LiteralRetainedThreadFloor');d.from_pydata(verts,[],faces);d.update()
o=bpy.data.objects.new('LiteralRetainedThreadFloor',d);bpy.context.scene.collection.objects.link(o)
m=bpy.data.materials.new('NeutralRetainedFloor');m.diffuse_color=(.32,.30,.27,1);d.materials.append(m)
for mat in bpy.data.materials:
    if not mat.use_nodes:continue
    bs=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if not bs:continue
    base=bs.inputs['Base Color'];texture=next((l.from_node.image for l in base.links if l.from_node.type=='TEX_IMAGE' and l.from_node.image),None)
    mat.diffuse_color=tuple(np.array(texture.pixels[:]).reshape(-1,4).mean(axis=0)) if texture else base.default_value
eye_world=(39.4,54.25,-198.1);target_world=(42.08,54.1,-223.5)
def source(p):return Vector((p[0]-8,-p[2]-216,p[1]-52.5))
eye=source(eye_world);target=source(target_world)
camera=bpy.data.objects.new('StaffEntryContext',bpy.data.cameras.new('StaffEntryContext'));bpy.context.scene.collection.objects.link(camera)
camera.location=eye;camera.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();camera.data.lens=20
scene=bpy.context.scene;scene.camera=camera;scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD'
world=bpy.data.worlds.new('NeutralThreadSourceContext');world.color=(.32,.37,.41);scene.world=world
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=1.5;scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(P/'qa/SOURCE_THREAD_STOCK_WIDE003.png')
bpy.ops.render.render(write_still=True)
assert sha(original)==j['original_native_sha256'] and sha(new)==j['native_sha256']
(P/'qa/SOURCE_THREAD_STOCK_VIEW003.json').write_text(json.dumps({'image':'SOURCE_THREAD_STOCK_WIDE003.png','eye_world_xyz':eye_world,'target_world_xyz':target_world,'original_native_sha256':sha(original),'new_native_sha256':sha(new),'floor_source_sha256':sha(floor_path),'originals_unchanged':True,'geometry':'Actual original Thread & Shell native,new saved stock/repair native,literal compiled receiving floor triangles','scope':'Neutral Workbench source context and mean texture palette;not texture/glass/engine-lighting,CRT,hardware,complete species or final-art acceptance'},indent=2)+'\n')
