from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'RUNTIME_PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda a:(a[0],-a[2],a[1]);files=[W/'D04PrivateCourtServiceCandidate.blend',R/'BlenderCatalogue/assets/d04_port_forward_receiving_20261010/D04PortForwardReceiving.blend']
for n in ['first','second','third']:
 d=R/f'BlenderCatalogue/assets/d04_port_forward_homes_{n}_20261010';p=json.load(open(d/'RUNTIME_PLAN.json'));files.append(d/next(r['native']for r in p['native_export_records']if r['export']==p['structure']['model_file']))
 for room in p['rooms']:
  if room['court_side']=='east':files.append(d/f'D04Home_{room["source_index"]}.blend')
pins={str(f.relative_to(R)):sha(f)for f in files};bpy.ops.wm.read_factory_settings(use_empty=True)
for f in files:
 with bpy.data.libraries.load(str(f),link=False)as(a,b):b.objects=a.objects
 for o in b.objects:
  if o:
   bpy.context.collection.objects.link(o)
   if f.name.startswith('D04Home_') and o.get('category','')in ['floor','frame','truss_brace']:o.hide_render=True
for r in P['preimages']:bpy.data.objects[r['preimage']['name']].hide_render=True
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=800;s.render.resolution_y=600;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.world=bpy.data.worlds.new('DiagnosticSourceFill');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.3,.34,.4,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.45
for z in [-407,-411,-422,-425]:
 bpy.ops.object.light_add(type='AREA',location=B([-28.1,20,z]));bpy.context.object.data.energy=150;bpy.context.object.data.size=2
def view(name,at,target):
 bpy.ops.object.camera_add(location=B(at));o=bpy.context.object;o.data.lens=19;o.rotation_euler=(Vector(B(target))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/name);bpy.ops.render.render(write_still=True)
view('SOURCE_COURT_ENTRY_CLOSED.png',[-28.1,18.1,-405.6],[-28.1,17.9,-408.4])
for g in P['gates']:
 pivot=Vector(B(g['pivot']));T=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(g['candidate_open_degrees']),4,'Z')@Matrix.Translation(-pivot)
 for name in g['members']:bpy.data.objects[name].matrix_world=T@bpy.data.objects[name].matrix_world
view('SOURCE_COURT_ENTRY_OPEN_CANDIDATE.png',[-28.1,18.1,-407.0],[-28.1,17.9,-412.0])
view('SOURCE_COURT_PAIR_LINK_OPEN_CANDIDATE.png',[-28.1,18.1,-420.2],[-28.1,17.9,-426.0])
for f,h in pins.items():assert sha(R/f)==h,f
(W/'SOURCE_VIEW_RUN.json').write_text(json.dumps({'status':'PASS','native_pins_unchanged':pins,'images':['SOURCE_COURT_ENTRY_CLOSED.png','SOURCE_COURT_ENTRY_OPEN_CANDIDATE.png','SOURCE_COURT_PAIR_LINK_OPEN_CANDIDATE.png'],'diagnostic_fill':True,'source_only':True,'production_active':False,'ordinary_game_CRT_hardware_accepted':False},indent=2)+'\n')
