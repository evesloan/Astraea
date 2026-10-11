from pathlib import Path
import bpy,json,hashlib,sys,math
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'RUNTIME_PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1]);files=[W/'D04CommonsCartDocks_r001.blend',R/'BlenderCatalogue/assets/d04_port_forward_commons_service_20261010/D04CommonsServiceActivity.blend',R/'BlenderCatalogue'/P['original_cart_source']['source']];pins={str(p.relative_to(R)):sha(p)for p in files};bpy.ops.wm.open_mainfile(filepath=str(files[0]))
with bpy.data.libraries.load(str(files[1]),link=False)as(a,b):b.objects=a.objects
for o in b.objects:
 if o:bpy.context.collection.objects.link(o)
sys.path.insert(0,str(R/'Game/tools'));from validate_production_glb import preview_only
with bpy.data.libraries.load(str(files[2]),link=False)as(a,b):b.objects=a.objects
obs=[o for o in b.objects if o]
for o in obs:bpy.context.collection.objects.link(o)
bpy.context.view_layer.update();worlds={o:o.matrix_world.copy()for o in obs};root=bpy.data.objects.new('DiagnosticOriginalCart',None);bpy.context.collection.objects.link(root)
for o in obs:
 if o.type not in ['MESH','EMPTY']or preview_only(o.name,{k:o.get(k,False)for k in ['preview_only','presentation_only','exclude_from_production']}):bpy.data.objects.remove(o,do_unlink=True);continue
 o.parent=root;o.matrix_world=worlds[o]
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.exposure=-1.5;s.world=bpy.data.worlds.new('ScopedDockDiagnostic');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.27,.32,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
for at in [[-77.3,20.04,-358.4],[-72.3,20.04,-358.4]]:
 bpy.ops.object.light_add(type='AREA',location=B(at));bpy.context.object.data.energy=240;bpy.context.object.data.size=2
images=[]
for dock in P['docks']:
 name='SOURCE_'+dock['name']+'_DOCK.png';assert not(W/name).exists();root.matrix_world=Matrix.Translation(Vector(B(dock['position'])))@Matrix.Rotation(math.pi,4,'Z');bpy.context.view_layer.update();at=[dock['position'][0]+1.4,18.15,-360.3];target=[dock['position'][0],17.2,-358.4];bpy.ops.object.camera_add(location=B(at));o=bpy.context.object;o.data.lens=23;o.rotation_euler=(Vector(B(target))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/name);bpy.ops.render.render(write_still=True);images.append(name)
for f,h in pins.items():assert sha(R/f)==h,f
(W/'SOURCE_VIEW_RUN.json').write_text(json.dumps({'status':'PASS','images':images,'native_pins_unchanged':pins,'one_original_cart_source_posed_for_diagnostic_only':True,'actual_dynamic_loaded_gate_separate':True,'diagnostic_fill':True,'final_graphics_accepted':False},indent=2)+'\n')
