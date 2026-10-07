"""One inward source eye; do not fabricate an exterior receiving view."""
from pathlib import Path
import bpy,json,math,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'outputs/source_r001/SA_r001__family__shelf_spine__L';OUT=R/'outputs/eye_r001';assert not OUT.exists();OUT.mkdir()
bpy.ops.wm.open_mainfile(filepath=str(D/'assembly.blend'));bpy.context.view_layer.update();scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False;scene.render.resolution_x=1080;scene.render.resolution_y=800;scene.render.resolution_percentage=100
fixtures=[]
for o in list(scene.objects):
 if o.type!='EMPTY'or not o.name.startswith('DATUM_')or'light'not in o.name:continue
 pt=o.matrix_world.translation.copy();assert pt.z>1.4;data=bpy.data.lights.new(o.name+'_source','POINT');data.energy=90 if 'atlas_bed'in o.name else 130 if 'atlas_write'in o.name else 170;data.shadow_soft_size=.10
 light=bpy.data.objects.new(o.name+'_source',data);scene.collection.objects.link(light);light.location=pt;fixtures.append({'datum':o.name,'actual_light_xyz':list(light.location),'evaluated_marker_xyz':list(pt),'elevation_pass':pt.z>1.4})
world=bpy.data.worlds.new('NeutralSourceAmbient');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.17,.18,1);world.node_tree.nodes['Background'].inputs[1].default_value=.18;scene.world=world
camd=bpy.data.cameras.new('StarAtlasInwardEye');cam=bpy.data.objects.new('StarAtlasInwardEye',camd);scene.collection.objects.link(cam);cam.location=(.08,12.40,1.64);target=Vector((0,5.45,1.38));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camd.lens=21;scene.camera=cam;scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'star_atlas_family_library_inward_eye.png');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'source_eye.blend'));bpy.ops.render.render(write_still=True)
(OUT/'RENDER_RECEIPT.json').write_text(json.dumps({'source':str(D/'assembly.blend'),'source_sha256':hashlib.sha256((D/'assembly.blend').read_bytes()).hexdigest(),'camera_xyz':list(cam.location),'target_xyz':list(target),'image':'star_atlas_family_library_inward_eye.png','image_sha256':hashlib.sha256((OUT/'star_atlas_family_library_inward_eye.png').read_bytes()).hexdigest(),'samples':24,'denoise':False,'threads':2,'fixtures':fixtures,'scope':'Actual inward source room eye; no receiving view or runtime art/privacy acceptance; source directional glass remains untested in runtime'},indent=2)+'\n');print('STAR_ATLAS_INWARD_EYE_COMPLETE',len(fixtures),flush=True)
