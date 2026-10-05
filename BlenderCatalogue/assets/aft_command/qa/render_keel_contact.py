"""Close source-only view of the existing keel and new pier contact; does not save source."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'source/AST-CMD-002.blend'))
with bpy.data.libraries.load(str(C/'assets/lower_hull_body/source/AST-HUL-001.blend'),link=False) as (src,dst):dst.objects=[name for name in src.objects if name=='HUL_KeelPan']
for ob in dst.objects:
 if ob:bpy.context.collection.objects.link(ob);ob.name='QA_ONLY_existing_'+ob.name
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=840;scene.render.resolution_y=525;scene.render.resolution_percentage=100;scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.3,.36,.42,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.7
light=bpy.data.lights.new('QA_ONLY_contact_key','AREA');light.energy=1000;light.size=5;ob=bpy.data.objects.new(light.name,light);bpy.context.collection.objects.link(ob);ob.location=(-32,-89,5)
cam=bpy.data.cameras.new('QA_contact');ob=bpy.data.objects.new(cam.name,cam);bpy.context.collection.objects.link(ob);ob.location=(-39,-91,1.3);ob.rotation_euler=(Vector((-35.5,-86,-2.7))-ob.location).to_track_quat('-Z','Y').to_euler();cam.lens=32;cam.clip_end=1500;scene.camera=ob;scene.render.filepath=str(R/'qa/source_pier_keel_contact.png');bpy.ops.render.render(write_still=True)
(R/'qa/keel_contact_preview_receipt.json').write_text(json.dumps({'new_source_sha256':hashlib.sha256((R/'source/AST-CMD-002.blend').read_bytes()).hexdigest(),'existing_keel_source_sha256':hashlib.sha256((C/'assets/lower_hull_body/source/AST-HUL-001.blend').read_bytes()).hexdigest(),'image':'source_pier_keel_contact.png','scope':'Source-only port pier foot meets the actual existing keel-pan model; diagnostic light/context are not saved or exported','keel_and_pier_contact_y':-3.2},indent=2)+'\n')
