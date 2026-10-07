"""One actual source-eye context. No render stands in for runtime art acceptance."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'outputs/house_r001';OUT=R/'outputs/eye_r001';OUT.mkdir(exist_ok=True);assert not(OUT/'family_terrace_source_eye.png').exists()
bpy.ops.wm.open_mainfile(filepath=str(D/'house.blend'));scene=bpy.context.scene
cam=bpy.data.cameras.new('FT_ActualCourtEye');o=bpy.data.objects.new('FT_ActualCourtEye',cam);scene.collection.objects.link(o)
eye=(66.7,85.7,332);target=(83,91,369);world=lambda p:Vector((p[0],-p[2],p[1]));o.location=world(eye);o.rotation_euler=(world(target)-o.location).to_track_quat('-Z','Y').to_euler();cam.lens=24;cam.clip_end=600;scene.camera=o
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=20;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=960;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'family_terrace_source_eye.png');scene.view_settings.exposure=1.0
bpy.ops.render.render(write_still=True)
(OUT/'EYE_RECEIPT.json').write_text(json.dumps({'source_house_sha256':hashlib.sha256((D/'house.blend').read_bytes()).hexdigest(),'eye_world_xyz':eye,'target_world_xyz':target,'lens_mm':24,'source_only':True,'runtime_capture':False,'samples':20,'denoising':False,'threads':2,'exposure':1.0,'sha256':hashlib.sha256((OUT/'family_terrace_source_eye.png').read_bytes()).hexdigest(),'scope':'Actual whole-house geometry and authored fixture lights; normal standing1.7m source eye, not native CRT or moving-door/privacy proof.'},indent=2)+'\n');print('FAMILY_TERRACE_SOURCE_EYE_COMPLETE')
