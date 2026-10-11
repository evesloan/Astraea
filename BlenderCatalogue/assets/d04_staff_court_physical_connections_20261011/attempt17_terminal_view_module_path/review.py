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

from mathutils import Matrix
from immutable_revision import require_new
names=['SOURCE_TERMINAL_ROOM_r001.png','SOURCE_TERMINAL_WELL_r001.png','SOURCE_TERMINAL_DETAIL_r001.png']
require_new([W/n for n in names]);proof=json.load(open(W/'SOURCE_VIEW_TERMINAL_RECEIPT_r001.json'));assert proof['status']=='PASS';reach=proof['results'][1]
input_plan_sha256=sha(W/'RUNTIME_PLAN.json');s.cycles.samples=16;s.cycles.use_denoising=True
for gate in P['gates']:
 pivot=Vector(B(gate['pivot']));T=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(gate['candidate_open_degrees']),4,'Z')@Matrix.Translation(-pivot)
 for name in gate['members']:ob=bpy.data.objects[name];ob.matrix_world=T@ob.matrix_world
for name in [P['reach_tool']['model'],P['reach_tool']['angled_terminal']['model']]:
 f=R/'Game/assets/models'/name;pins[str(f.relative_to(R))]=sha(f);bpy.ops.import_scene.gltf(filepath=str(f))
C=Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))
for row in reach['native_part_poses']:
 x,y,z=row['basis'];o=row['origin'];M=Matrix(((x[0],y[0],z[0],o[0]),(x[1],y[1],z[1],o[1]),(x[2],y[2],z[2],o[2]),(0,0,0,1)));bpy.data.objects[row['name']].matrix_world=C@M@C.inverted()
for at,power in [([-57.5,19.2,-429.2],900),([-59.3,19.2,-429.7],1100),([-59.3,18.8,-430.5],500)]:
 bpy.ops.object.light_add(type='AREA',location=B(at));bpy.context.object.data.energy=power;bpy.context.object.data.size=1.2
images=[]
def view(name,at,target,lens):
 bpy.ops.object.camera_add(location=B(at));ob=bpy.context.object;ob.data.lens=lens;ob.rotation_euler=(Vector(B(target))-ob.location).to_track_quat('-Z','Y').to_euler();s.camera=ob;s.render.filepath=str(W/name);bpy.ops.render.render(write_still=True);images.append(name)
view(names[0],[-57.35,18.1,-429.25],reach['shaft_end'],28)
view(names[1],[-59.58,18.6,-429.55],[-59.02,17.85,-429.9],24)
view(names[2],[-58.98,18.25,-430.85],[-59.05,17.72,-430.35],45)
for f,h in pins.items():assert sha(R/f)==h,f
assert sha(W/'RUNTIME_PLAN.json')==input_plan_sha256
(W/'SOURCE_TERMINAL_VIEW_RUN_r001.json').write_text(json.dumps({'status':'PASS_CAPTURE_ONLY','images':{n:sha(W/n)for n in images},'input_runtime_plan_sha256':input_plan_sha256,'source_model_pins_unchanged':pins,'native_contact_pose':reach,'diagnostic_fill_only':True,'production_visual_acceptance':False},indent=2)+'\n')
