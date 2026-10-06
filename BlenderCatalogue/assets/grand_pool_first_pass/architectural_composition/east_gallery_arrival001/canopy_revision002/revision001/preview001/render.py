"""Bounded source-composition preview only. Original sources are read-only.
No Game edit/import, model export, source overwrite or final-art acceptance.
"""
from pathlib import Path
import bpy,math,json,hashlib,sys,time
from mathutils import Vector,Matrix
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
PKG=CAT/'assets/grand_pool_first_pass';NEW=PKG/'comfort_greenery';OUT=HERE/'output'
assert not OUT.exists(),'Preserve previous preview';OUT.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def B(p):return Vector((p[0],-p[2],p[1]))
inputs={};counts={};comfort=[];architecture=[]
preview_pins=json.loads((HERE/'PREVIEW_PINS.json').read_text())
for pinned_path,digest in preview_pins['sha256'].items():
 assert sha(pinned_path)==digest,pinned_path
def pin(p):inputs[str(p)]=sha(p)
def append(path,label,floors=False,placement=None,group=None,yaw=0):
 pin(path);print('APPEND_SOURCE',label,flush=True)
 col=bpy.data.collections.new(label);bpy.context.scene.collection.children.link(col)
 with bpy.data.libraries.load(str(path),link=False) as (src,dst):dst.objects=list(src.objects)
 obs=[o for o in dst.objects if o and o.type in {'MESH','EMPTY'}]
 loaded=set(obs)
 for o in obs:col.objects.link(o)
 bpy.context.view_layer.update()
 for o in obs:
  original=o.name
  hidden=bool(o.hide_render or o.get('export_excluded') or original.startswith('REFERENCE_'))
  if label=='candidate_east_arrival' and o.get('programme_instance'):
   hidden=bool(o.hide_render) # Retained instances are excluded only from architectural exports.
  if floors and original.startswith('PREVIEW_ONLY_D') and o.type=='MESH' and not 'Door' in original:hidden=False
  o.hide_render=hidden
  if o.type=='MESH' and not hidden:o.hide_set(False)
  o.name=label+'__'+original
 if placement is not None:
  roots=[o for o in obs if o.parent not in loaded]
  for o in roots:o.matrix_world=Matrix.Translation(B(placement))@Matrix.Rotation(yaw,4,'Z')@o.matrix_world
 bpy.context.view_layer.update();counts[label]=sum(o.type=='MESH' and not o.hide_render for o in obs)
 if group is not None:group.extend(o for o in obs if o.type=='MESH' and not o.hide_render)
 return obs
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=16;scene.cycles.use_denoising=False
scene.cycles.max_bounces=4;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=2;scene.cycles.transmission_bounces=2
scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=960;scene.render.resolution_y=540;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.film_transparent=False
scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
scene.world=bpy.data.worlds.new('SOURCE_PREVIEW_NEUTRAL_WORLD');scene.world.use_nodes=True;bg=scene.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.32,.38,.44,1);bg.inputs['Strength'].default_value=.16
# Bounded real shell context for the east-facing bay camera. The opposite
# west programme lies behind this view and is not reconstructed for this study.
append(CAT/'assets/grand_pool_orchard_section/source/AST-AQU-016.blend','retained_architecture',floors=True)
append(PKG/'finish_envelope/source/grand_pool_finish_envelope.blend','retained_finish')
append(PKG/'architectural_composition/revisions/blockin002/source/AST-AQU-016_pool_roof_composition.blend','retained_roof_hierarchy')
candidate=HERE.parent/'source001/source/AST-AQU-016_east_gallery_canopy_r02.blend'
assert sha(candidate)=='7dfce55242a651af80b59199217424470ed8d951ecb81eee68ac83539ea5fe14'
append(candidate,'candidate_east_arrival')
planpath=HERE/'LIGHT_PROPOSAL.json';pin(planpath);proposal=json.loads(planpath.read_text())
assert proposal['status']=='PASS_SOURCE_PREVIEW_OPTICAL_PLAN'
oldcontract=CAT/'assets/grand_pool_orchard_section/source/connected_contract.json'
finishcontract=PKG/'finish_envelope/source/finish_contract.json'
pin(oldcontract);pin(finishcontract)
fixtures=[]
for row in json.loads(oldcontract.read_text())['fixtures']:
 fixtures.append({'name':row['name'],'position':row['position_xyz'],'direction':row['direction'],'power_watts':700*row['suggested_energy'],'angle':row['suggested_spot_angle_degrees'],'source':'retained_fixture'})
for row in json.loads(finishcontract.read_text())['fixtures']:
 display='Display' in row['name'] or 'display' in row['name']
 fixtures.append({'name':row['name'],'position':row['position_xyz'],'direction':row['direction_xyz'],'power_watts':(35 if display else 850)*row['suggested_energy'],'angle':row['suggested_spot_angle_degrees'],'source':'retained_finish_fixture'})
for row in proposal['fixtures']:
 fixtures.append({'name':row['name'],'position':row['position_xyz'],'direction':row['direction_xyz'],'power_watts':row['source_preview_power_watts'],'angle':row['half_angle_degrees'],'shadow_soft_size_m':row.get('preview_shadow_soft_size_m',.02),'source':'new_actual_housed_source_reserve_provisional'})
for r in fixtures:
 light=bpy.data.lights.new('SOURCE_STUDY_'+r['name'],'SPOT');light.energy=r['power_watts'];light.color=(1,.86,.68);light.spot_size=math.radians(2*r['angle']);light.spot_blend=.55;light.shadow_soft_size=r.get('shadow_soft_size_m',.20)
 ob=bpy.data.objects.new(light.name,light);scene.collection.objects.link(ob);ob.location=B(r['position']);ob.rotation_euler=B(r['direction']).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('SOURCE_REVIEW_CAMERA');camd.type='PERSP';camd.sensor_fit='VERTICAL';camd.sensor_height=32;camd.lens=camd.sensor_height/(2*math.tan(math.radians(72)/2));camd.clip_start=.02;camd.clip_end=1600
cam=bpy.data.objects.new(camd.name,camd);scene.collection.objects.link(cam);scene.camera=cam
view=proposal['view'];cam.location=B(view['eye_xyz']);cam.rotation_euler=(B(view['target_xyz'])-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(OUT/'upper_gallery_canopy_corrected_source_study.png');bpy.context.view_layer.update();started=time.monotonic();bpy.ops.render.render(write_still=True)
for path,digest in inputs.items():assert sha(path)==digest,path
for path,digest in preview_pins['sha256'].items():assert sha(path)==digest,path
report={'status':'SOURCE_LIGHT_STUDY_READY_FOR_PIXEL_REVIEW','candidate_installed':False,'source_unchanged':True,'inputs':inputs,'view':view,'fixtures':fixtures,'new_fixture_native_energy_accepted':False,'shared_renderer_changed':False,'source_preview_mapping':'Existing source-study700W times provisional energy; this is not a Godot brightness equivalence. Neutral world fill, lens/materials and shared source selection are unchanged.','context':'Exact retained shell/floor preview, finish envelope and roof composition; opposite programme outside this east-facing camera is omitted.','seconds':time.monotonic()-started,'image_sha256':sha(OUT/'upper_gallery_canopy_corrected_source_study.png'),'limitations':['Source composition only','Native receiver brightness and natural8-source selection pending','Normal in-game presentation pending','No export or production installation']}
(OUT/'REPORT.json').write_text(json.dumps(report,indent=2)+'\n');print('SOURCE_LIGHT_STUDY_READY',flush=True)
