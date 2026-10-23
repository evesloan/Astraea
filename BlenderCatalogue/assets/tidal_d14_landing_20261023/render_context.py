import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[3];G=R/'Game';N=R/'BlenderCatalogue/assets/tidal_d14_landing_20261023';P=G/'tidal_d14_landing_20261023'
bpy.ops.wm.open_mainfile(filepath=str(N/'TidalD14Landing_r001.blend'))
d=json.loads((G/'data/architecture/TIDAL_LIFT_RECEIVING_CANDIDATE.json').read_text());plan=json.loads((P/'PLAN.json').read_text())
def load_model(path):
 old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path));new=set(bpy.data.objects)-old
 return list(new),[o for o in new if o.parent not in new]
arch,roots=load_model(G/'assets/models'/d['model_file'])
for o in arch:o['context_source_only']=True
cache={};count=0
for row in d['retained_asset_instances']:
 if not row['name'].startswith('D14'):continue
 key=row['catalogue_id']
 if key not in cache:
  objects,roots=load_model(G/'assets/models'/d['retained_asset_definitions'][key]['model_file']);collection=bpy.data.collections.new('ContextTemplate_'+key)
  for o in objects:
   for owner in list(o.users_collection):owner.objects.unlink(o)
   collection.objects.link(o)
  cache[key]=collection
 e=bpy.data.objects.new(row['name'],None);e.instance_type='COLLECTION';e.instance_collection=cache[key];bpy.context.scene.collection.objects.link(e)
 p=row['world_xyz'];e.location=(p[0],-p[2],p[1]);e.rotation_euler.z=math.radians(-row['yaw']);e.scale=(row['scale'],)*3;count+=1
for row in plan['lights']:
 data=bpy.data.lights.new(row['name'],'POINT');data.energy=240;data.color=row['color'];data.shadow_soft_size=.18
 o=bpy.data.objects.new(row['name'],data);bpy.context.scene.collection.objects.link(o);p=row['position'];o.location=(p[0],-p[2],p[1])
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=8
s.world=bpy.data.worlds.new('RetainedContextNeutralAmbient');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.25,.29,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
camera=bpy.data.cameras.new('D14LandingContext');o=bpy.data.objects.new('D14LandingContext',camera);s.collection.objects.link(o);o.location=(-79,381,91.5);target=Vector((-87,390,90.15));o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler();camera.lens=23;s.camera=o
s.render.resolution_x=1100;s.render.resolution_y=700;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.exposure=0;s.render.image_settings.file_format='PNG';s.render.filepath=str(P/'evidence/TIDAL_D14_NATIVE_CONTEXT_UNFINISHED.png')
bpy.ops.render.render(write_still=True)
receipt={'status':'native_context_not_runtime_visual_acceptance','native_sha256':hashlib.sha256((N/'TidalD14Landing_r001.blend').read_bytes()).hexdigest(),'original_architecture_sha256':d['source_sha256'],'original_architecture_objects':len(arch),'retained_D14_instances':count,'new_fixture_sources':2,'render_engine':'Blender 4.3.2 Cycles CPU','omitted_context':'Later distant specialty frontages and service receiving are outside this landing crop. Not a full installed-ship render.','lighting_limit':'Cycles watts/neutral ambient are preview settings, not Godot lighting or performance validation.','image_sha256':hashlib.sha256(Path(s.render.filepath).read_bytes()).hexdigest()}
(P/'evidence/NATIVE_VIEW.json').write_text(json.dumps(receipt,indent=2)+'\n');print('TIDAL_CONTEXT',json.dumps(receipt))
