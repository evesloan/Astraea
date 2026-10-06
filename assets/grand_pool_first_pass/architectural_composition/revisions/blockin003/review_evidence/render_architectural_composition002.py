"""Bounded source-composition preview only. Original sources are read-only.
No Game edit/import, model export, source overwrite or final-art acceptance.
"""
from pathlib import Path
import bpy,math,json,hashlib,sys,time
from mathutils import Vector,Matrix
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
PKG=CAT/'assets/grand_pool_first_pass';NEW=PKG/'comfort_greenery';OUT=HERE/'previews_blockin002'
assert not OUT.exists(),'Preserve previous preview';OUT.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def B(p):return Vector((p[0],-p[2],p[1]))
inputs={};counts={};comfort=[];architecture=[]
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
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=48;scene.cycles.use_denoising=False
scene.cycles.max_bounces=4;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=2;scene.cycles.transmission_bounces=2
scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=640;scene.render.resolution_y=360;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.film_transparent=False
scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
scene.world=bpy.data.worlds.new('SOURCE_PREVIEW_NEUTRAL_WORLD');scene.world.use_nodes=True;bg=scene.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.32,.38,.44,1);bg.inputs['Strength'].default_value=.16
append(CAT/'assets/grand_pool_orchard_section/source/AST-AQU-016.blend','retained_architecture',floors=True)
append(PKG/'source/grand_pool_first_pass_editable_corrected.blend','retained_51')
append(PKG/'finish_envelope/source/grand_pool_finish_envelope.blend','source_checked_finish')
append(PKG/'finish_envelope/wayfinding/source/grand_pool_wayfinding.blend','source_checked_wayfinding')
# Reuse exact retained source objects for the previously checked 48 additions.
stockpath=PKG/'finish_envelope/stock/stock_placement_contract.json';pin(stockpath);stock=json.loads(stockpath.read_text());prototypes={}
for ident,row in stock['input_inventory'].items():
 obs=append(CAT/row['source'],'PROTOTYPE_'+ident)
 bpy.context.view_layer.update();prototypes[ident]=[(o,o.matrix_world.copy(),o.hide_render)for o in obs]
 for o,_,_ in prototypes[ident]:o.hide_render=True
stockcol=bpy.data.collections.new('retained_48_source_additions');scene.collection.children.link(stockcol)
for row in stock['placements']:
 transform=Matrix.Translation(B(row['position_xyz']))@Matrix.Rotation(row['yaw_radians'],4,'Z')
 for original,matrix,hidden in prototypes[row['asset']]:
  if original.type!='MESH' or hidden:continue
  ob=original.copy();ob.name='stock_'+row['name']+'__'+original.name;stockcol.objects.link(ob);ob.parent=None;ob.matrix_world=transform@matrix;ob.hide_render=False;ob.hide_set(False)
counts['retained_48_source_additions']=len(stockcol.objects)
greenpath=NEW/'greenery/candidate_v001/qa/SOURCE_QA_all.json';pin(greenpath);green=json.loads(greenpath.read_text());assert green['status']=='PASS_SOURCE_QA_ONLY'
contractpath=NEW/'greenery/greenery_contract.json';pin(contractpath);contract=json.loads(contractpath.read_text());positions={a['name']:a['position_xyz']for a in contract['assets']}
for row in green['sources']:
 path=Path(row['source']);assert sha(path)==row['source_sha256'];append(path,'lush_'+row['name'],placement=positions[row['name']],group=comfort)
media=NEW/'media/source/AST-LIB-010_pool_leisure_displays.blend';assert sha(media)=='63a68558675f6c4f286a87499982c5c05230fe46e5a24c6d2426c879e974a1f2';append(media,'checked_leisure_displays',group=comfort)
ARCH=PKG/'architectural_composition';run=json.loads((ARCH/'qa/SOURCE_JOB_002b.json').read_text());assert run['status']=='BLOCKIN002_REOPEN_RETAINED_AND_NEW_CONTACT_GATES_PASS'
buildpath=ARCH/'revisions/blockin002/qa/BUILD_RECEIPT.json';pin(buildpath);built=json.loads(buildpath.read_text())
for row in built['sources']:
 path=Path(row['source']);assert sha(path)==row['source_sha256'];append(path,'architectural_'+row['group'],group=architecture)
planpath=ARCH/'source_tooling002/BLOCKIN_PLAN_002.json';pin(planpath);newplan=json.loads(planpath.read_text())
for row in newplan['plants']:
 path=NEW/'greenery/candidate_v001/source'/row['model_file'].replace('.glb','.blend');append(path,'new_pocket_'+row['name'],placement=row['position_xyz'],yaw=row['yaw_radians'],group=architecture)
# Preview illumination comes only from actual old/new fixture reservations.
oldcontract=CAT/'assets/grand_pool_orchard_section/source/connected_contract.json';newcontract=PKG/'finish_envelope/source/finish_contract.json';pin(oldcontract);pin(newcontract)
fixtures=[]
for row in json.loads(oldcontract.read_text())['fixtures']:
 fixtures.append({'name':row['name'],'position':row['position_xyz'],'direction':row['direction'],'power_watts':700*row['suggested_energy'],'angle':row['suggested_spot_angle_degrees'],'source':'retained_fixture'})
for row in json.loads(newcontract.read_text())['fixtures']:
 is_display='Display' in row['name'] or 'display' in row['name']
 fixtures.append({'name':row['name'],'position':row['position_xyz'],'direction':row['direction_xyz'],'power_watts':(35 if is_display else 850)*row['suggested_energy'],'angle':row['suggested_spot_angle_degrees'],'source':'authored_fixture_reservation'})
for r in fixtures:
 ld=bpy.data.lights.new('PREVIEW_'+r['name'],'SPOT');ld.energy=r['power_watts'];ld.color=(1,.86,.68);ld.spot_size=math.radians(2*r['angle']);ld.spot_blend=.55;ld.shadow_soft_size=.20
 ob=bpy.data.objects.new(ld.name,ld);scene.collection.objects.link(ob);ob.location=B(r['position']);ob.rotation_euler=B(r['direction']).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('SOURCE_REVIEW_CAMERA');camd.type='PERSP';camd.sensor_fit='VERTICAL';camd.sensor_height=32;camd.lens=camd.sensor_height/(2*math.tan(math.radians(72)/2));camd.clip_start=.02;camd.clip_end=1600
cam=bpy.data.objects.new('SOURCE_REVIEW_CAMERA',camd);scene.collection.objects.link(cam);scene.camera=cam
views=[{'name':'wet_loggia','eye':[-45.9,47.8499,-438.0],'target':[-52,48.4499,-442.2],'basis':'Ordinary1.65mwet-route eye,72degree verticalFOV; new bay framed through retained lounge foreground'}, {'name':'retained_long_view','eye':[-20.5,47.8499,-405.0],'target':[-20.5,48.1499,-415.0],'basis':'Same standing eye and0.03rad upwardpitch as current in-game long-view composition'}]
report={'status':'SOURCE_BLOCKIN_COMPOSITION_RUNNING','inputs':inputs,'source_renderer':'Blender Cycles CPU,2threads,48samples,no denoiser,640x360','lighting_scope':'Same39actual original/checked fixture origins in both versions, recorded source watt mapping and neutral world fill. No new reserved fixture is simulated. This is not Godot eight-source selection or visual acceptance.','fixtures':fixtures,'before_definition':'Installed126programme context represented by the exact saved source assemblies, materials and retained floor preview','after_definition':'Same context plus three geometry-screened architecture source block-ins and12unscaled retained botanical instances; no source is resaved/exported','light_angle_semantics':'Godot angle is angular radius; Blender full cone is twice that value. Corrected without changing any fixture contract, runtime light or watt mapping.','incomplete':['Pier-connected asymmetric market thresholds','New physically housed focal/aft lights','Support/new-new contact graph and final geometry fitting','Actual native-engine adoption/lighting/visual review'],'renders':[]}
for view in views:
 cam.location=B(view['eye']);cam.rotation_euler=(B(view['target'])-cam.location).to_track_quat('-Z','Y').to_euler()
 for enriched in [True,False]:
  for ob in architecture:ob.hide_render=not enriched
  bpy.context.view_layer.update();filename=view['name']+('_architecture_blockin'if enriched else'_current_source_baseline')+'.png';scene.render.filepath=str(OUT/filename);start=time.monotonic();bpy.ops.render.render(write_still=True)
  report['renders'].append({'file':filename,'sha256':sha(OUT/filename),'view':view,'architecture_visible':enriched,'seconds':time.monotonic()-start,'acceptance':False});(OUT/'PREVIEW_REPORT.json').write_text(json.dumps(report,indent=2)+'\n');print('ARCHITECTURE_PREVIEW_READY',filename,flush=True)
for path,h in inputs.items():assert sha(path)==h,'Input changed during preview'
report['status']='SOURCE_PREVIEWS_COMPLETE_REQUIRING_ACTUAL_PIXEL_REVIEW';report['all_source_inputs_unchanged']=True;(OUT/'PREVIEW_REPORT.json').write_text(json.dumps(report,indent=2)+'\n');print('SOURCE_ARCHITECTURAL_PREVIEW_DONE_NO_EXPORT_NO_GAME_WRITE')
