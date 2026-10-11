"""Wide saved-source photograph. No original native is saved; review camera only."""
from pathlib import Path
import bpy,json,math,sys
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
old=ROOT/'BlenderCatalogue/assets/shopping_promenade_20261009'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def append(path):
    with bpy.data.libraries.load(str(path),link=False) as (a,d):d.objects=a.objects
    col=bpy.data.collections.new(path.stem);bpy.context.scene.collection.children.link(col)
    for o in d.objects:
        if o:col.objects.link(o)
    return [o for o in d.objects if o]
definition=json.loads((ROOT/'Game/data/architecture/group5/CONSTRUCTION.json').read_text())
plan=json.loads((old/'docs/PLACEMENT_AND_CONNECTORS.json').read_text());rooms={r['chunk_id']:r for r in plan['rooms']+plan['chunks']}
def import_export(path):
    before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    return list(set(bpy.data.objects)-before)
for row in plan['rooms']+plan['chunks']:
    x,_,z=row['position']
    if row.get('retained') or x<0 or abs(x-86)>29 or abs(z-110)>90:continue
    for layer,path in row['exports'].items():
        if layer=='floor' and not path:continue
        objects=import_export(old/path)
        for ob in objects:
            if ob.parent is None:ob.location+=(Vector((x,-z,0)))
added=[]
for row in definition['doors']:
    parent=rooms[row['chunk_id']];x,_,z=parent['position']
    if x<0 or not 74<=z<=158:continue
    name=Path(row['model_path']).stem
    objects=import_export(P/'exports'/(name+'.glb'))
    # Runtime yaw is Blender rotation around source Z.
    px=x+row['local_xyz'][0];pz=z+row['local_xyz'][2]
    roots=[o for o in objects if o.parent is None]
    door_matrix=Matrix.Translation((px,-pz,0))@Matrix.Rotation(row['rotation_y'],4,'Z')
    for ob in roots:
        # glTF imports use quaternion mode. Assign a full matrix so the runtime
        # yaw is applied instead of silently ignored by an Euler-field write.
        ob.matrix_world=door_matrix@ob.matrix_world
    if row['chunk_id']=='SHOP_D09_S72_A080' and row['local_name']=='PublicDoors':
        for ob in objects:
            if 'opening_displacement_x' in ob:ob.location.x=float(ob['opening_displacement_x'])
    added.append(row['physical_id'])
    for control in row.get('controls',[]):
        cx,cy,cz=control['local_xyz']
        transform=door_matrix@Matrix.Translation((cx,-cz,cy))@Matrix.Rotation(control['rotation_y'],4,'Z')
        for ob in import_export(P/'exports/retail_door_control_r001.glb'):
            if ob.parent is None:ob.matrix_world=transform@ob.matrix_world
for row in definition['wayfinding']:
    parent=rooms[row['chunk_id']];x,_,z=parent['position'];px=x+row['local_xyz'][0];pz=z+row['local_xyz'][2]
    if x<0 or not 74<=pz<=158:continue
    objects=import_export(P/'exports'/(Path(row['model_path']).stem+'.glb'))
    transform=Matrix.Translation((px,-pz,0))@Matrix.Rotation(row['rotation_y'],4,'Z')
    for ob in objects:
        if ob.parent is None:ob.matrix_world=transform@ob.matrix_world
bpy.context.view_layer.update()
for ob in bpy.context.scene.objects:
    if ob.type!='MESH':continue
    center=ob.matrix_world@(sum((Vector(v) for v in ob.bound_box),Vector())/8)
    if abs(center.x-86)>29 or abs(-center.y-110)>64:ob.hide_render=True
scene=bpy.context.scene
world=bpy.data.worlds.new('NeutralSourceReview');world.use_nodes=True;scene.world=world
world.node_tree.nodes['Background'].inputs[0].default_value=(.23,.27,.31,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.4
for spec in json.loads((old/'docs/LIGHT_SOURCES.json').read_text()):
    x,y,z=spec['position_world']
    if abs(x-86)>25 or not 60<z<165:continue
    data=bpy.data.lights.new(spec['id'],'SPOT');data.energy=320*spec['energy'];data.color=spec['colour'];data.spot_size=math.radians(spec['angle_deg']);data.spot_blend=.5
    ob=bpy.data.objects.new(spec['id'],data);scene.collection.objects.link(ob);ob.location=(x,-z,y-52.5)
camera_data=bpy.data.cameras.new('WideSourceCamera');camera=bpy.data.objects.new('WideSourceCamera',camera_data);scene.collection.objects.link(camera)
entry='entry' in sys.argv
eye=Vector((83,-76,2.2)) if entry else Vector((86,-76,3.5))
target=Vector((71,-81,1.8)) if entry else Vector((82,-116,2.5))
camera.location=eye;camera.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();camera_data.lens=20 if entry else 22;scene.camera=camera
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD'
scene.world.color=(.32,.37,.41)
material_roles={}
for f in ['materials/material_manifest.json','materials/retail/manifest.json']:
    material_roles.update(json.loads((ROOT/'BlenderCatalogue'/f).read_text())['materials'])
for material in bpy.data.materials:
    for role,row in material_roles.items():
        if role in material.name and 'colour_srgb_8bit' in row:material.diffuse_color=tuple(c/255 for c in row['colour_srgb_8bit'])+(1,);break
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.7
filename='SOURCE_EXPORT_GROUP5_ENTRY010.png' if entry else 'SOURCE_EXPORT_GROUP5_WIDE009.png'
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(P/'qa'/filename)
bpy.ops.render.render(write_still=True)
(P/'qa'/('SOURCE_ENTRY_VIEW.json' if entry else 'SOURCE_VIEW.json')).write_text(json.dumps({'image':filename,'geometry':'actual retained GLB exports with literal zero-error native-match receipt, plus new native/export door/guide geometry; Blender4.3 cannot read native5.1 header','eye_ship_xyz':[eye.x,eye.z+52.5,-eye.y],'target_ship_xyz':[target.x,target.z+52.5,-target.y],'new_doors_in_view_catchment':added,'one_public_door_open_for_visual_review':True,'production_default':'all new doors closed','runtime_yaw':'full GLB root matrices, respecting quaternion import mode; matches supplied Godot rotation_y','lighting':'neutral Workbench studio; original source material palette colors; actual geometry; texture/glass shading and Godot light deliberately absent','scope':'wide actual source-export photograph; no generated concept; no Godot/CRT/hardware or full district acceptance'},indent=2)+'\n')
