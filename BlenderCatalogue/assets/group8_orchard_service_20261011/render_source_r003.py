"""Wide actual native photographs in retained Orchard context, no generated concept."""
from pathlib import Path
import bpy,json,math,hashlib
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];C=R/'BlenderCatalogue'
bpy.ops.wm.open_mainfile(filepath=str(W/'OrchardService_r003.blend'))
def append(path,at,yaw=0):
    with bpy.data.libraries.load(str(path),link=False)as(src,dst):dst.objects=src.objects
    for ob in dst.objects:
        if ob:bpy.context.collection.objects.link(ob)
    bpy.context.view_layer.update();poses={ob:ob.matrix_world.copy()for ob in dst.objects if ob}
    transform=Matrix.Translation((at[0],-at[2],at[1]))@Matrix.Rotation(yaw,4,'Z')
    for ob,matrix in poses.items():ob.parent=None;ob.matrix_world=transform@matrix
append(C/'assets/orchard_foodhall/source/AST-DIN-008.blend',[8,61,-250])
for z in [-223.5,-208.5]:
    append(C/'assets/hospitality_serviceware/source/AST-HSP-005.blend',[35.5,61,z+2.7],-math.pi/2)
    append(C/'assets/hospitality_stations/source/AST-HSP-003.blend',[29.55,61.92,z],-math.pi/2)
# The exact retained compiler floor triangles are context, never saved/exported.
d=json.load(open(R/'Game/data/generated/structural_meshes.json'));vs=[];faces=[]
for region in d['regions']:
    if region['floor_y']!=61:continue
    for triangle in region['triangles']:
        faces.append(tuple(range(len(vs),len(vs)+3)));vs.extend((q[0],-q[1],61)for q in triangle)
me=bpy.data.meshes.new('ExactRetainedD10CompilerTriangles');me.from_pydata(vs,[],faces);me.update();ob=bpy.data.objects.new('ExactRetainedD10CompilerTriangles',me);bpy.context.collection.objects.link(ob)
mat=bpy.data.materials.new('SourceReviewFloor');mat.diffuse_color=(.28,.34,.36,1);me.materials.append(mat)
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.studio_light='paint.sl';scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.1;scene.display.shading.curvature_valley_factor=.8
scene.display.shading.background_type='WORLD';scene.world.color=(.08,.1,.12);scene.view_settings.view_transform='Standard'
scene.render.resolution_x=1800;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
camera=bpy.data.cameras.new('ActualSourceWideCamera');ob=bpy.data.objects.new('ActualSourceWideCamera',camera);bpy.context.collection.objects.link(ob);scene.camera=ob;camera.lens=19
def photo(name,at,target):
    path=W/name;assert not path.exists(),'Preserve earlier photographs'
    ob.location=(at[0],-at[2],at[1]);t=Vector((target[0],-target[2],target[1]));ob.rotation_euler=(t-ob.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
photo('SOURCE_ORCHARD_NORTH_GALLEY_WIDE001.png',[37.35,63.25,-223.5],[32.7,62.25,-223.8])
photo('SOURCE_ORCHARD_SOUTH_GALLEY_WIDE001.png',[37.35,63.25,-208.5],[32.7,62.25,-208.8])
photo('SOURCE_ORCHARD_RECEIVING_WIDE001.png',[50.9,63.1,-235],[53,62.0,-216])
(W/'SOURCE_PHOTO_RECEIPT.json').write_text(json.dumps({'native':'OrchardService_r003.blend','native_sha256':hashlib.sha256((W/'OrchardService_r003.blend').read_bytes()).hexdigest(),'images':['SOURCE_ORCHARD_NORTH_GALLEY_WIDE001.png','SOURCE_ORCHARD_SOUTH_GALLEY_WIDE001.png','SOURCE_ORCHARD_RECEIVING_WIDE001.png'],'actual_original_context':['AST-DIN-008.blend','AST-HSP-005.blend','AST-HSP-003.blend','exact retained D10 compiler floor triangles'],'presentation':'Blender Workbench source material colours,1800x1000; no source saved/changed','limits':['No original texture finish or ordinary Godot light comparison','No CRT/target GPU/gameplay/hygiene/species/engineering/final-art acceptance']},indent=2)+'\n')
