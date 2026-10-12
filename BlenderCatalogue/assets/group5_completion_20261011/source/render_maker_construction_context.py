"""Real current maker source counterpart with posed source-review door and new fittings."""
from pathlib import Path
import bpy,json,hashlib,numpy as np
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
j=json.loads((ROOT/'Game/data/architecture/group5/MAKER_CONSTRUCTION.json').read_text())
native=ROOT/j['current_editable_counterpart'];before=hashlib.sha256(native.read_bytes()).hexdigest();assert before==j['counterpart_sha256']
bpy.ops.wm.open_mainfile(filepath=str(native))
for o in list(bpy.context.scene.objects):
    if o.type in ['CAMERA','LIGHT']:bpy.data.objects.remove(o,do_unlink=True)
def append(path,transform):
    with bpy.data.libraries.load(str(path),link=False) as (src,dst):dst.objects=src.objects
    for o in dst.objects:
        if o:bpy.context.scene.collection.objects.link(o)
    for o in dst.objects:
        if o and o.parent is None:o.matrix_world=transform@o.matrix_world
    return [o for o in dst.objects if o]
def source(a):return Vector((a[0],-a[2],a[1]))
append(ROOT/j['foyer_source']['native'],Matrix.Translation(source(j['foyer_source']['origin_world_xyz'])))
if j.get('ceiling_enclosure'):append(ROOT/j['ceiling_enclosure']['native'],Matrix.Translation(source(j['ceiling_enclosure']['origin_world_xyz'])))
d=j['door'];matrix=Matrix.Translation(source(d['world_xyz']))@Matrix.Rotation(d['rotation_y'],4,'Z')
objects=append(ROOT/j['door_component']['native'],matrix)
for o in objects:
    if 'opening_displacement_x' in o:o.location.x=float(o['opening_displacement_x'])
for control in d['controls']:
    transform=matrix@Matrix.Translation(source(control['local_xyz']))@Matrix.Rotation(control['rotation_y'],4,'Z')
    append(P/'source/retail_door_control_r001.blend',transform)
floor_path=ROOT/'Game/data/generated/received_structural_meshes.json';floors=[r for r in json.loads(floor_path.read_text())['regions'] if r['id'].startswith('D09_directory_05_')]
verts=[];faces=[]
for row in floors:
    for tri in row['triangles']:
        start=len(verts);verts.extend([(x,-z,52.5) for x,z in tri]);faces.append((start,start+1,start+2))
mesh=bpy.data.meshes.new('LiteralRetainedMakerFloor');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new('LiteralRetainedMakerFloor',mesh);bpy.context.scene.collection.objects.link(o)
mat=bpy.data.materials.new('NeutralRetainedFloor');mat.diffuse_color=(.35,.32,.29,1);mesh.materials.append(mat)
for mat in bpy.data.materials:
    if not mat.use_nodes:continue
    bs=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if not bs:continue
    base=bs.inputs['Base Color'];texture=next((l.from_node.image for l in base.links if l.from_node.type=='TEX_IMAGE' and l.from_node.image),None)
    mat.diffuse_color=tuple(np.array(texture.pixels[:]).reshape(-1,4).mean(axis=0)) if texture else base.default_value
eye_world=[-54.1,54.4,0];target_world=[-74,54.2,0];eye=source(eye_world);target=source(target_world)
cam=bpy.data.objects.new('MakerFoyerReview',bpy.data.cameras.new('MakerFoyerReview'));bpy.context.scene.collection.objects.link(cam);cam.location=eye;cam.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();cam.data.lens=18
scene=bpy.context.scene;scene.camera=cam;scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD'
world=bpy.data.worlds.new('NeutralMakerContext');world.color=(.32,.37,.41);scene.world=world;scene.view_settings.view_transform='AgX';scene.view_settings.exposure=1.1
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(P/'qa/SOURCE_MAKER_FOYER_OPEN003.png');bpy.ops.render.render(write_still=True)
assert hashlib.sha256(native.read_bytes()).hexdigest()==before
(P/'qa/SOURCE_MAKER_FOYER_VIEW003.json').write_text(json.dumps({'image':'SOURCE_MAKER_FOYER_OPEN003.png','eye_world_xyz':eye_world,'target_world_xyz':target_world,'actual_current_counterpart_native_sha256':before,'original_native_unchanged':True,'original_current_model_sha256':j['original_model_sha256'],'new_fixture_native_sha256':j['foyer_source']['native_sha256'],'retained_floor_source_sha256':hashlib.sha256(floor_path.read_bytes()).hexdigest(),'source_review_door':'explicitly posed fully open;production default remains closed','scope':'Actual current source geometry and separately saved fittings with literal retained floor;neutral Workbench/mean palette only,no rendered Game,texture/glass/lighting,child/species,CRT/hardware or final-art acceptance;original correction-native still unrecovered'},indent=2)+'\n')
