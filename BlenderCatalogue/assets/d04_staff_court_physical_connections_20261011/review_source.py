from pathlib import Path
import json,hashlib,bpy,math,ast
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'RUNTIME_PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1]);pins={}
bpy.ops.wm.read_factory_settings(use_empty=True)
models=['AST-STF-009_pool_market_home_equipment.glb',P['previous_candidate']['structure']['model_file'],P['previous_candidate']['court_candidate_model']['model_file'],P['owned_model']['model_file'],P['patch_model']['model_file']]
for group in ['FIRST','SECOND','THIRD']:
 q=json.load(open(R/f'Game/data/architecture/D04_PORT_FORWARD_HOMES_{group}.json'));models.append(q['structure']['model_file']);models.extend(r['model_file']for r in q['rooms'])
for name in models:
 f=R/'Game/assets/models'/name;pins[str(f.relative_to(R))]=sha(f);bpy.ops.import_scene.gltf(filepath=str(f))
for cut in P['cuts']:
 ob=bpy.data.objects.get(cut['name']);assert ob is not None,cut['name'];ob.hide_render=True
q=json.load(open(R/'Game/data/architecture/D04_PORT_FORWARD_PRIVATE_COURT_SERVICE_CANDIDATE.json'))
for row in q['preimages']:
 ob=bpy.data.objects.get(row['preimage']['name'])
 if ob:ob.hide_render=True
for ob in bpy.data.objects:
 if ob.get('category','')=='stair_walk_surface':ob.hide_render=True
floor=next(r for r in json.load(open(R/'Game/data/generated/structural_meshes.json'))['regions']if r['id']=='D03_protected_crew_cover');vs=[];fs=[]
for t in floor['triangles']:
 i=len(vs);vs.extend([B([x,12,z])for x,z in t]);fs.append([i,i+1,i+2])
me=bpy.data.meshes.new('ExistingD03Floor');me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new('ExistingD03Floor',me);bpy.context.collection.objects.link(ob);mat=bpy.data.materials.new('ExistingD03FloorFinish');mat.diffuse_color=(.22,.26,.3,1);me.materials.append(mat)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=800;s.render.resolution_y=600;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.world=bpy.data.worlds.new('DiagnosticSourceFill');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.3,.34,.4,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
for at in [[-57,14.5,-448],[-51,13.5,-448.5],[-42,13.5,-448.5],[-34,13.5,-448.5],[-28.1,20,-446.5],[-56.8,19,-428.8]]:
 bpy.ops.object.light_add(type='AREA',location=B(at));bpy.context.object.data.energy=160;bpy.context.object.data.size=2
images=[]
def view(name,at,target):
 bpy.ops.object.camera_add(location=B(at));ob=bpy.context.object;ob.data.lens=20;ob.rotation_euler=(Vector(B(target))-ob.location).to_track_quat('-Z','Y').to_euler();s.camera=ob;s.render.filepath=str(W/name);bpy.ops.render.render(write_still=True);images.append(name)
view('SOURCE_STAFF_PORTALS_CLOSED.png',[-57.3,13.65,-449.25],[-55.2,13.25,-448.1])
def open_gate(spec):
 pivot=Vector(B(spec['pivot']));T=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(spec['candidate_open_degrees']),4,'Z')@Matrix.Translation(-pivot)
 for name in spec['members']:ob=bpy.data.objects[name];ob.matrix_world=T@ob.matrix_world
for gate in P['gates']:open_gate(gate)
view('SOURCE_STAFF_PORTALS_OPEN.png',[-57.3,13.65,-447],[-52.5,13,-447])
view('SOURCE_FOURTH_COURT_THRESHOLD.png',[-28.1,18.1,-446.8],[-28.1,17.5,-443.5])
proof=json.load(open(W/'SOURCE_VIEW_ENGINE_RECEIPT.json'));reach=next((q for q in proof['maintenance_reach']if q and q['plant']=='D04HC2_west_LeafMass_1_1'),None)
if reach:
 hand=ast.literal_eval(reach['hand']);tip=ast.literal_eval(reach['first_contact']);f=R/'Game/assets/models'/P['reach_tool']['model'];pins[str(f.relative_to(R))]=sha(f);bpy.ops.import_scene.gltf(filepath=str(f));direction=Vector(B(tip))-Vector(B(hand));basis=direction.to_track_quat('-Y','Z').to_matrix().to_4x4();T=Matrix.Translation(Vector(B(hand)))@basis
 for i in range(3):
  ob=bpy.data.objects['D04PC_CareTube_'+str(i)];ob.matrix_world=T@Matrix.Translation(Vector((0,-i*reach['joint_slide'],0)))@ob.matrix_world
 bpy.ops.object.light_add(type='AREA',location=B([hand[0]+.25,19,hand[2]]));bpy.context.object.data.energy=400;bpy.context.object.data.size=1.5
 bpy.ops.object.light_add(type='AREA',location=B([-59.2,19,tip[2]]));bpy.context.object.data.energy=300;bpy.context.object.data.size=1
 view('SOURCE_LIGHTWELL_REACH_ONLY.png',[hand[0]+.5,hand[1]+.35,hand[2]],tip)
for f,h in pins.items():assert sha(R/f)==h,f
(W/'SOURCE_VIEW_RUN.json').write_text(json.dumps({'status':'PASS','images':images,'model_pins_unchanged':pins,'diagnostic_fill':True,'production_active':False,'reach_source':reach},indent=2)+'\n')
