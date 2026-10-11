from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'RUNTIME_PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda a:(a[0],-a[2],a[1]);files=[W/'D04StaffCourtApproachSealed_r002.blend',W/'D04CourtGateClearance_r002.blend',R/'BlenderCatalogue/assets/lower_staff_network/source/AST-STF-009.blend']
for n in ['first','second','third']:
 d=R/f'BlenderCatalogue/assets/d04_port_forward_homes_{n}_20261010';p=json.load(open(d/'RUNTIME_PLAN.json'));files.append(d/next(a['native']for a in p['native_export_records']if a['export']==p['structure']['model_file']))
 for room in p['rooms']:
  if room['court_side']=='east':files.append(d/f'D04Home_{room["source_index"]}.blend')
pins={str(f.relative_to(R)):sha(f)for f in files};bpy.ops.wm.read_factory_settings(use_empty=True)
for f in files:
 with bpy.data.libraries.load(str(f),link=False)as(a,b):b.objects=a.objects
 for o in b.objects:
  if o:
   bpy.context.collection.objects.link(o)
   if o.get('category','')=='stair_walk_surface' or (f.name.startswith('D04Home_')and o.get('category','')in ['floor','frame','truss_brace']):o.hide_render=True
old=json.load(open(R/'BlenderCatalogue/assets/d04_port_forward_private_court_service_20261011/RUNTIME_PLAN.json'))
for row in old['preimages']:
 ob=bpy.data.objects.get(row['preimage']['name'])
 if ob:ob.hide_render=True
floor=next(r for r in json.load(open(R/'Game/data/generated/structural_meshes.json'))['regions']if r['id']=='D03_protected_crew_cover');v=[];faces=[]
for t in floor['triangles']:
 i=len(v);v.extend([B([x,12,z])for x,z in t]);faces.append([i,i+1,i+2])
me=bpy.data.meshes.new('ExistingD03CoverFloorDisplay');me.from_pydata(v,[],faces);me.update();ob=bpy.data.objects.new('ExistingD03CoverFloorDisplay',me);bpy.context.collection.objects.link(ob);mat=bpy.data.materials.new('ExistingCover');mat.diffuse_color=(.22,.26,.3,1);me.materials.append(mat)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=800;s.render.resolution_y=600;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.world=bpy.data.worlds.new('DiagnosticSourceFill');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.3,.34,.4,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
for at in [[-51,13.5,-448.5],[-42,13.5,-448.5],[-34,13.5,-448.5],[-28.1,20,-408.8],[-28.1,20,-422.3],[-28.1,19.8,-446.5]]:
 bpy.ops.object.light_add(type='AREA',location=B(at));bpy.context.object.data.energy=160;bpy.context.object.data.size=2
def view(name,at,target):
 bpy.ops.object.camera_add(location=B(at));o=bpy.context.object;o.data.lens=19;o.rotation_euler=(Vector(B(target))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/name);bpy.ops.render.render(write_still=True)
view('SOURCE_SEPARATE_STAFF_LANES.png',[-52.5,13.65,-447],[-34,13.2,-447.2])
view('SOURCE_STAIR_SEALED_COURT_JOIN.png',[-31,18.1,-449.5],[-28.25,17.9,-445.3])
view('SOURCE_REVISED_GATE_CLOSED.png',[-28.1,18.1,-420.7],[-28.1,17.9,-422.9])
g=P['gates'][1];pivot=Vector(B(g['pivot']));T=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(g['candidate_open_degrees']),4,'Z')@Matrix.Translation(-pivot)
for name in g['members']:bpy.data.objects[name].matrix_world=T@bpy.data.objects[name].matrix_world
view('SOURCE_REVISED_GATE_OPEN.png',[-28.1,18.1,-420.7],[-28.1,17.9,-423.7])
for f,h in pins.items():assert sha(R/f)==h,f
(W/'SOURCE_VIEW_RUN.json').write_text(json.dumps({'status':'PASS','native_pins_unchanged':pins,'images':['SOURCE_SEPARATE_STAFF_LANES.png','SOURCE_STAIR_SEALED_COURT_JOIN.png','SOURCE_REVISED_GATE_CLOSED.png','SOURCE_REVISED_GATE_OPEN.png'],'diagnostic_fill':True,'original_floor_display_only':True,'production_active':False,'ordinary_game_CRT_hardware_accepted':False},indent=2)+'\n')
