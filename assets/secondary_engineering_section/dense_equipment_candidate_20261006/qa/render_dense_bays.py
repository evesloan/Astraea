"""Actual imported additive export, preserved context, ordinary-eye source diagnostic.
Run only under parent render allocation. No ambient/fill; real visible source markers only.
"""
from pathlib import Path
import bpy,json,math,hashlib,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');assert str(R)=='/workspace/scratch/375c2e438292/engineering-dense-bays'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def cv(p):return Vector((p[0],-p[2],p[1]))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
inputs=[C/'assets/secondary_engineering_section/exports/AST-ENG-008.glb',R.parent/'engineering-essentials/exports/AST-ENG-008_essentials.glb',R/'exports/AST-ENG-008_dense_bays.glb']
for p in inputs:bpy.ops.import_scene.gltf(filepath=str(p))
# This single floor previews the compiler owner, not new production geometry.
bpy.ops.mesh.primitive_plane_add(size=2,location=cv((31,6,-432)));floor=bpy.context.object;floor.name='QA_ONLY_COMPILER_Y6';floor.scale=(23,34,1)
m=bpy.data.materials.new('QA_ONLY_retained_staff_floor');m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.87;t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(C/'materials/staff/staff_floor.png'));t.interpolation='Linear';m.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color']);floor.data.materials.append(m)
for u in floor.data.uv_layers.active.data:u.uv=(u.uv.x*46/.8,u.uv.y*68/.8)
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=24;sc.cycles.use_denoising=False;sc.render.resolution_x=960;sc.render.resolution_y=540;sc.render.resolution_percentage=100;sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0;sc.view_settings.view_transform='Standard';sc.view_settings.look='None';sc.view_settings.exposure=0
settings={'DATUM_control_task':{'position':[26,8.845,-459],'aim':[26,7.4,-462.95],'watts':650,'half_cone_degrees':65},'DATUM_workbay_task':{'position':[27,9.145,-405],'aim':[26.5,7,-401.4],'watts':750,'half_cone_degrees':65},'LIGHT_PROPOSAL_west_rack':{'position':[23,9.005,-406.5],'aim':[20.98,7.36,-405.8],'watts':260,'half_cone_degrees':58},'LIGHT_PROPOSAL_test_rack':{'position':[33.08,8.295,-402.02],'aim':[32.98,7.4,-401.5],'watts':75,'half_cone_degrees':58},'LIGHT_PROPOSAL_north_services':{'position':[24.52,8.66,-408.00],'aim':[24.52,7.31,-408.58],'watts':420,'half_cone_degrees':68},'LIGHT_PROPOSAL_bench_task':{'position':[26.43,7.73,-401.45],'aim':[26.1,7.18,-401.35],'watts':35,'half_cone_degrees':55}}
lights={}
for name,p in settings.items():
 d=bpy.data.lights.new(name+'_SOURCE_DIAGNOSTIC','SPOT');d.energy=p['watts'];d.spot_size=math.radians(p['half_cone_degrees']*2);d.spot_blend=.6;d.shadow_soft_size=.075;o=bpy.data.objects.new(name+'_SOURCE_DIAGNOSTIC',d);sc.collection.objects.link(o);o.location=cv(p['position']);o.rotation_euler=(cv(p['aim'])-o.location).to_track_quat('-Z','Y').to_euler();lights[name]=o
cam=bpy.data.cameras.new('QA_ORDINARY_EYE');o=bpy.data.objects.new('QA_ORDINARY_EYE',cam);sc.collection.objects.link(o);sc.camera=o;cam.sensor_fit='VERTICAL';cam.sensor_height=32;cam.lens=32/(2*math.tan(math.radians(72)/2));cam.clip_start=.05;cam.clip_end=100
views=[{'name':'control_rejected_pose_existing_sources','eye':[30,7.6501565,-457.200012],'yaw':.616,'pitch':-.05,'lights':['DATUM_control_task']},{'name':'workbay_rejected_pose_existing_sources','eye':[30,7.6501565,-405],'yaw':math.pi/2,'pitch':0,'lights':['DATUM_workbay_task']},{'name':'workbay_rejected_pose_fixture_trial','eye':[30,7.6501565,-405],'yaw':math.pi/2,'pitch':0,'lights':['DATUM_workbay_task','LIGHT_PROPOSAL_west_rack','LIGHT_PROPOSAL_test_rack','LIGHT_PROPOSAL_bench_task','LIGHT_PROPOSAL_north_services']},{'name':'control_operating_detail','eye':[26.0,7.65,-461.30],'target':[26,7.44,-462.60],'lights':['DATUM_control_task']},{'name':'workbay_bench_fixture_trial','eye':[26.0,7.65,-403.5],'target':[25.6,7.4,-401.25],'lights':['DATUM_workbay_task','LIGHT_PROPOSAL_west_rack','LIGHT_PROPOSAL_test_rack','LIGHT_PROPOSAL_bench_task','LIGHT_PROPOSAL_north_services']}]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];selected=args or [v['name'] for v in views];done=[]
for v in views:
 if v['name'] not in selected:continue
 for k,l in lights.items():l.hide_render=k not in v['lights']
 eye=v['eye'];o.location=cv(eye)
 if 'target'in v:target=v['target']
 else:
  yaw=v['yaw'];pitch=v['pitch'];direction=[-math.sin(yaw)*math.cos(pitch),math.sin(pitch),-math.cos(yaw)*math.cos(pitch)];target=[eye[i]+direction[i] for i in range(3)]
 o.rotation_euler=(cv(target)-o.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(R/'qa'/('source_'+v['name']+'.png'));bpy.ops.render.render(write_still=True);done.append(v)
manifest={'scope':'Blender imported-source geometry/light diagnostic; no Godot selector, retro processing, runtime watts calibration or final visual acceptance','inputs_sha256':{str(p):sha(p) for p in inputs},'renderer':'Blender Cycles CPU24samples, two threads','resolution':[960,540],'world_strength':0,'unexplained_fill_lights':0,'retained_walls_and_ceilings_hidden':False,'qa_floor_only':'Y6 compiler preview, retained 0.8m staff floor texture; never exported','vertical_fov_degrees':72,'horizontal_fov_degrees':104.504860145,'camera_sensor_fit':'VERTICAL','physical_source_settings':settings,'rendered_views':done,'runtime_selection_reproduced':False,'fixture_trial_runtime_approved':False}
(R/'qa'/('render_manifest_'+('_'.join(selected))+'.json')).write_text(json.dumps(manifest,indent=2)+'\n')
print('DENSE_SOURCE_RENDERS_OK',[v['name'] for v in done])

import resource
print('PROCESS_PEAK_RSS_KIB',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
