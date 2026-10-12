"""Actual retained native/export furnishings and new source doors;no native save."""
from pathlib import Path
import bpy,json,hashlib,numpy as np,math
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
j=json.loads((ROOT/'Game/data/architecture/group5/LIVING_GIFTS_DOORS.json').read_text());native=ROOT/j['original_native'];before=hashlib.sha256(native.read_bytes()).hexdigest();assert before==j['original_native_sha256']
bpy.ops.wm.open_mainfile(filepath=str(native))
for o in list(bpy.context.scene.objects):
    if o.type in ['CAMERA','LIGHT']:bpy.data.objects.remove(o,do_unlink=True)
# Move original local source architecture to its literal retained world pose.
for o in bpy.context.scene.objects:
    if o.parent is None:o.matrix_world=Matrix.Translation((46,-230.4,52.5))@o.matrix_world
def point(v):return Vector((v[0],-v[2],v[1]))
inputs={}
def glb(name,at,yaw=0):
    path=ROOT/'Game/assets/models'/name;inputs[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest();before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(path));objects=set(bpy.context.scene.objects)-before;transform=Matrix.Translation(point(at))@Matrix.Rotation(yaw,4,'Z')
    for o in objects:
        if o.parent not in objects:o.matrix_world=transform@o.matrix_world
    bpy.context.view_layer.update();return objects
display=glb('AST-RTL-001.glb',[53,52.5,232.7],-math.pi/2)
glb('AST-RTL-003.glb',[48.9,52.5,239.6])
for i,(file,at) in enumerate([('AST-BOT-001.glb',[48.3,52.865,232.4]),('AST-BOT-009.glb',[47.1,53.015,240]),('AST-BOT-009.glb',[47.1,53.315,241.15]),('AST-BOT-003.glb',[47.25,53.115,233.1])]):glb(file,at,i*.42)
for i,name in enumerate(['MAIN_DISPLAY_LEFT_PATCH_CONTACT','MAIN_DISPLAY_RIGHT_PATCH_CONTACT','LEFT_SHELF_PATCH_CONTACT','RIGHT_SHELF_PATCH_CONTACT']):
    marker=next(o for o in display if o.name==name);at=marker.matrix_world.translation+Matrix.Rotation(-math.pi/2,4,'Z')@Vector((0,-.07,0));world=[at.x,at.z,-at.y];pots=glb('AST-BOT-012_low.glb' if i in [0,3] else 'AST-BOT-012.glb',world,-math.pi/2);soil=next(o for o in pots if o.name.startswith('DATUM_soil_surface'));at=soil.matrix_world.translation;glb('AST-BOT-003.glb',[at.x,at.z,-at.y],-math.pi/2)
def append(path,matrix):
    with bpy.data.libraries.load(str(path),link=False) as (src,dst):dst.objects=src.objects
    for o in dst.objects:
        if o:bpy.context.scene.collection.objects.link(o)
    for o in dst.objects:
        if o and o.parent is None:o.matrix_world=matrix@o.matrix_world
    return [o for o in dst.objects if o]
for row in j['doors']:
    matrix=Matrix.Translation(point(row['world_xyz']))@Matrix.Rotation(row['rotation_y'],4,'Z');objects=append(ROOT/row['native'],matrix)
    if row['mode']=='public':
        for o in objects:
            if 'opening_displacement_x' in o:o.location.x=float(o['opening_displacement_x'])
    for control in row['controls']:append(P/'source/retail_door_control_r001.blend',matrix@Matrix.Translation(point(control['local_xyz']))@Matrix.Rotation(control['rotation_y'],4,'Z'))
floor_path=ROOT/'Game/data/generated/structural_meshes.json';floor=next(r for r in json.loads(floor_path.read_text())['regions'] if r['id']=='D09_living_gifts_floor');verts=[];faces=[]
for tri in floor['triangles']:
    start=len(verts);verts.extend([(x,-z,52.5) for x,z in tri]);faces.append((start,start+1,start+2))
mesh=bpy.data.meshes.new('LiteralRetainedLivingFloor');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new('LiteralRetainedLivingFloor',mesh);bpy.context.scene.collection.objects.link(o);m=bpy.data.materials.new('NeutralRetainedFloor');m.diffuse_color=(.33,.31,.27,1);mesh.materials.append(m)
glb('AST-STR-001.glb',[50,52.5,244])
for material in bpy.data.materials:
    if not material.use_nodes:continue
    bs=next((n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if not bs:continue
    base=bs.inputs['Base Color'];texture=next((l.from_node.image for l in base.links if l.from_node.type=='TEX_IMAGE' and l.from_node.image),None);material.diffuse_color=tuple(np.array(texture.pixels[:]).reshape(-1,4).mean(axis=0)) if texture else base.default_value
eye_world=[44.5,54.45,236.1];target_world=[51,54.2,236.1];eye=point(eye_world);target=point(target_world)
cam=bpy.data.objects.new('LivingGiftContext',bpy.data.cameras.new('LivingGiftContext'));bpy.context.scene.collection.objects.link(cam);cam.location=eye;cam.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();cam.data.lens=19
scene=bpy.context.scene;scene.camera=cam;scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD';world=bpy.data.worlds.new('NeutralLivingContext');world.color=(.32,.37,.41);scene.world=world;scene.view_settings.view_transform='AgX';scene.view_settings.exposure=1.4
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(P/'qa/SOURCE_LIVING_PUBLIC_OPEN001.png');bpy.ops.render.render(write_still=True)
assert hashlib.sha256(native.read_bytes()).hexdigest()==before
(P/'qa/SOURCE_LIVING_PUBLIC_VIEW001.json').write_text(json.dumps({'image':'SOURCE_LIVING_PUBLIC_OPEN001.png','eye_world_xyz':eye_world,'target_world_xyz':target_world,'original_native_sha256':before,'original_unchanged':True,'actual_furnishing_model_pins':inputs,'new_door_model_pins':{r['model_path']:r['model_sha256'] for r in j['doors']},'retained_floor_source_sha256':hashlib.sha256(floor_path.read_bytes()).hexdigest(),'source_review_pose':'Public posed open,service candidate closed;production public defaults closed andservice candidate remains unapplied pending Group6 adoption','scope':'Actual source native plus retained runtime-export furnishing geometry,literal floor andunchanged aquatic column;neutral Workbench mean palette,no full texture/glass/actual lighting,Game/CRT/hardware/final-art acceptance'},indent=2)+'\n')
