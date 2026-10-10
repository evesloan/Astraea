from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;N=json.load(open(W/'NATIVE_EXPORT_CHECK.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();native=W/'AST-CIR-003_ten_stop.blend';bpy.ops.wm.open_mainfile(filepath=str(native))
for o in bpy.context.scene.objects:
 if o.type=='MESH'and('Roof'in o.name):o.hide_render=True
mat=bpy.data.materials.new('UNSAVED_ControlDatum');mat.diffuse_color=(.1,.7,.85,1)
for i in range(10):
 marker=bpy.data.objects['DATUM_floor_button_'+str(i)];bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=.045,location=marker.location);bpy.context.object.data.materials.append(mat)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=640;s.render.resolution_y=480;s.render.resolution_percentage=100;s.world.color=(.08,.08,.08)
bpy.ops.object.camera_add(location=(-.5,.45,2.1));c=bpy.context.object;c.data.type='ORTHO';c.data.ortho_scale=2.1;c.rotation_euler=(Vector((1.8,1.02,1.50))-c.location).to_track_quat('-Z','Y').to_euler();s.camera=c
bpy.ops.object.light_add(type='AREA',location=(-.5,.7,2.6));l=bpy.context.object;l.data.energy=250;l.data.size=2;l.rotation_euler=(Vector((1.8,1.02,1.5))-l.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=str(W/'SOURCE_TEN_STOP_PANEL.png');bpy.ops.render.render(write_still=True);assert sha(native)==N['native_sha256'];assert sha(W/'AST-CIR-003_ten_stop.glb')==N['export_sha256']
(W/'SOURCE_VIEW_RUN.json').write_text(json.dumps({'status':'rendered_for_review','native_and_export_unchanged':True,'view':'SOURCE_TEN_STOP_PANEL.png','unsaved_diagnostic_controls':'Ten datum spheres; runtime lift_button.gd supplies interactive button geometry','native_roof_hidden':True,'production_runtime_visual_acceptance':False},indent=2)+'\n')
