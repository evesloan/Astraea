from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
B=lambda p:(p[0],-p[2],p[1])
native=W/'StarAtlasD17StandardPortal.blend'
old=R/'BlenderCatalogue/assets/star_atlas_upper_commons_20261009/source/StarAtlasUpperCommons.blend'
pins={str(p.relative_to(R)):sha(p)for p in [native,old]}
bpy.ops.wm.open_mainfile(filepath=str(native))
with bpy.data.libraries.load(str(old),link=False)as(a,b):
    b.objects=[n for n in a.objects if n!='SA_D17_SouthWall_0']
for o in b.objects:
    if o:bpy.context.collection.objects.link(o)
scene=bpy.context.scene;scene.render.engine='CYCLES'
scene.cycles.samples=12;scene.cycles.use_denoising=False
scene.render.threads_mode='FIXED';scene.render.threads=3
scene.render.resolution_x=960;scene.render.resolution_y=640
scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX'
scene.world=bpy.data.worlds.new('SourceReviewWorld');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.28,.3,.34,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.65
for p in [(-65,105,11.5),(-65,105,15.5),(-70,106,13),(-62,103,14.5)]:
    bpy.ops.object.light_add(type='AREA',location=B(p))
    bpy.context.object.data.energy=250;bpy.context.object.data.size=2.5
images=[]
for name,p,target,lens in [
    ('SOURCE_INNER_THRESHOLD.png',(-65,103.6,11.0),(-65,103.25,14.13),23),
    ('SOURCE_OUTER_SUPPORT_HOLD.png',(-65,100.5,18),(-65,102.3,14.13),30),
    ('SOURCE_WALL_CONTEXT.png',(-75,105,19),(-65,103.5,14.13),25),
]:
    bpy.ops.object.camera_add(location=B(p));camera=bpy.context.object
    camera.data.lens=lens
    camera.rotation_euler=(Vector(B(target))-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.camera=camera;scene.render.filepath=str(W/name)
    bpy.ops.render.render(write_still=True);images.append(name)
for p,h in pins.items():assert sha(R/p)==h
(W/'SOURCE_VIEW_RUN.json').write_text(json.dumps({'status':'PASS','images':images,'source_only':True,'unsaved_context':True,'native_pins_unchanged':pins,'diagnostic_fill_lighting':True,'original_wall_replaced_in_unsaved_review_only':True,'final_graphical_acceptance':False},indent=2)+'\n')
