"""Bounded source-composition preview only. Original sources are read-only.
No Game edit/import, model export, source overwrite or final-art acceptance.
"""
from pathlib import Path
import bpy,math,json,hashlib,sys,time
from mathutils import Vector,Matrix
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
PKG=CAT/'assets/grand_pool_first_pass';NEW=PKG/'comfort_greenery';OUT=HERE/'source_preview001'
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
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32;scene.cycles.use_denoising=False
scene.cycles.max_bounces=4;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=2;scene.cycles.transmission_bounces=2
scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=960;scene.render.resolution_y=540;scene.render.resolution_percentage=100
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
 if not row['name'].endswith('_basal'): continue # Installed full crowns supersede the middle instances.
 path=NEW/'greenery/candidate_v001/source'/row['model_file'].replace('.glb','.blend');append(path,'new_pocket_'+row['name'],placement=row['position_xyz'],yaw=row['yaw_radians'],group=architecture)
# Exact installed full-crown and feature-hardware sources. No GLB re-import.
featurepath=Path('/workspace/shared/astraea-godot-production-20261003/data/architecture/GRAND_POOL_FEATURE_LAYERS_RUNTIME.json');pin(featurepath);features=json.loads(featurepath.read_text())
feature_root=ARCH/'feature_layers_next'
for row in features['plants']:
 path=feature_root/'planting/full_mass001/candidate_v001/source'/(row['asset']+'.blend')
 assert sha(path)==features['models'][row['asset']]['source_sha256']
 append(path,'installed_full_'+row['name'],placement=row['position_xyz'],yaw=row['yaw_radians'])
hardware=feature_root/'lighting/crosswash002/source_candidate001/source/AST-AQU-016_pool_feature_lighting.blend'
assert sha(hardware)==features['models']['AST-AQU-016_pool_feature_lighting']['source_sha256']
append(hardware,'installed_feature_hardware')
# Only the new candidate is appended; previous assemblies remain read-only context.
candidate=HERE/'source/AST-AQU-016_east_gallery_composed.blend'
build_receipt=HERE/'qa/BUILD_RECEIPT.json';pin(build_receipt);build=json.loads(build_receipt.read_text())
assert sha(candidate)==build['source_sha256']
append(candidate,'candidate_east_arrival')
# Preview illumination comes only from actual old/new fixture reservations.
oldcontract=CAT/'assets/grand_pool_orchard_section/source/connected_contract.json';newcontract=PKG/'finish_envelope/source/finish_contract.json';pin(oldcontract);pin(newcontract)
fixtures=[]
for row in json.loads(oldcontract.read_text())['fixtures']:
 fixtures.append({'name':row['name'],'position':row['position_xyz'],'direction':row['direction'],'power_watts':700*row['suggested_energy'],'angle':row['suggested_spot_angle_degrees'],'source':'retained_fixture'})
for row in json.loads(newcontract.read_text())['fixtures']:
 is_display='Display' in row['name'] or 'display' in row['name']
 fixtures.append({'name':row['name'],'position':row['position_xyz'],'direction':row['direction_xyz'],'power_watts':(35 if is_display else 850)*row['suggested_energy'],'angle':row['suggested_spot_angle_degrees'],'source':'authored_fixture_reservation'})
for row in features['fixtures']:
 fixtures.append({'name':row['name'],'position':row['marker_local_position_xyz'],'direction':row['direction_xyz'],'power_watts':700*row['energy'],'angle':row['spot_angle_degrees'],'source':'installed_source_backed_feature_fixture'})
for r in fixtures:
 ld=bpy.data.lights.new('PREVIEW_'+r['name'],'SPOT');ld.energy=r['power_watts'];ld.color=(1,.86,.68);ld.spot_size=math.radians(2*r['angle']);ld.spot_blend=.55;ld.shadow_soft_size=.20
 ob=bpy.data.objects.new(ld.name,ld);scene.collection.objects.link(ob);ob.location=B(r['position']);ob.rotation_euler=B(r['direction']).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('SOURCE_REVIEW_CAMERA');camd.type='PERSP';camd.sensor_fit='VERTICAL';camd.sensor_height=32;camd.lens=camd.sensor_height/(2*math.tan(math.radians(72)/2));camd.clip_start=.02;camd.clip_end=1600
cam=bpy.data.objects.new('SOURCE_REVIEW_CAMERA',camd);scene.collection.objects.link(cam);scene.camera=cam
views=[
 {'name':'retained_long_view','eye':[-20.5,47.8499,-405.0],'target':[-20.5,48.1499,-415.0],'basis':'Same standing eye and upward pitch as the current installed long-pool view'},
 {'name':'upper_gallery_approach','eye':[-14.0,54.15,-455.8],'target':[-9.65,54.65,-449.5],'basis':'Ordinary 1.65m standing eye on the retained D09 apron, looking into the new supported rest bay'}
]
report={
 'status':'SOURCE_COMPOSITION_RUNNING','inputs':inputs,
 'source_renderer':'Blender Cycles CPU, 2 threads, 32 samples, no denoiser, 960x540',
 'lighting_scope':'Actual original, finish and installed feature-fixture origins with the recorded source-preview watt mapping and neutral world fill. New east-bay fixture reserves are not powered in this study. This is not Godot eight-source selection or light acceptance.',
 'fixtures':fixtures,
 'context':'Retained section, actual retained floor preview, 51 furnishings, 48 stock additions, checked comfort/envelope/sign sources and installed architectural/full-crown/feature-light source equivalents.',
 'candidate':'One new independently reopened east lift profile and upper gallery source assembly with retained plants, housed media and directional signs.',
 'light_angle_semantics':'Godot spot angle is angular radius; Blender full cone is twice that value.',
 'incomplete':['Native import/adoption','Native local light selection and energy','Actual-world player/cart/support checks','Final architectural and first-pass visual acceptance'],
 'renders':[]
}
for view in views:
 cam.location=B(view['eye']);cam.rotation_euler=(B(view['target'])-cam.location).to_track_quat('-Z','Y').to_euler()
 bpy.context.view_layer.update();filename=view['name']+'_source_study.png';scene.render.filepath=str(OUT/filename);start=time.monotonic();bpy.ops.render.render(write_still=True)
 report['renders'].append({'file':filename,'sha256':sha(OUT/filename),'view':view,'seconds':time.monotonic()-start,'acceptance':False})
 (OUT/'PREVIEW_REPORT.json').write_text(json.dumps(report,indent=2)+'\n');print('EAST_SOURCE_PREVIEW_READY',filename,flush=True)
for path,h in inputs.items():assert sha(path)==h,'Input changed during preview'
report['status']='SOURCE_PREVIEWS_COMPLETE_REQUIRING_ACTUAL_PIXEL_REVIEW';report['all_source_inputs_unchanged']=True;(OUT/'PREVIEW_REPORT.json').write_text(json.dumps(report,indent=2)+'\n');print('SOURCE_ARCHITECTURAL_PREVIEW_DONE_NO_EXPORT_NO_GAME_WRITE')
