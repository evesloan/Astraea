"""Eight actual Night Garden source recipes, retaining all recovered bed anchors.
Run only in a coordinated two-thread Blender slot. Never writes Game/Catalogue.
"""
from pathlib import Path
import bpy,bmesh,json,math,hashlib,ast,types,importlib.util,sys
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];W=R.parents[1]
ROOT=W/'residential-batch-neighborhood-20261006/scale_domestic_r011'
CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
args=types.SimpleNamespace(domestic=True);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=ROOT/'source/build_family.py'
for node in ast.parse(base.read_text()).body:
 if isinstance(node,ast.FunctionDef):exec(compile(ast.Module(body=[node],type_ignores=[]),str(base),'exec'),globals())
plan=json.loads((R/'NIGHT_GARDEN_80_PLACEMENT_MAP.json').read_text())
OUT=R/'outputs/source_r004';assert not OUT.exists(),'Preserve prior revisions';OUT.mkdir()
pins=json.loads((R/'qa/INPUT_PINS.json').read_text());assert all(sha(p)==h for p,h in pins.items())
def drop(prefixes):
 for o in list(bpy.context.scene.objects):
  if any(o.name.startswith(p)for p in prefixes):bpy.data.objects.remove(o,do_unlink=True)

def night_shell(cfg):
 cc=dict(cfg);cc.update(historical_class='standard',view_lounge_replan=False,family_sleep_bay_privacy=False)
 ns=author_shell(cc)
 drop(['SUI_LivingCase','SUI_SleepThresholdWing','SUI_ThresholdTimberCap','SUI_SleepingValance','SUI_Writing','SUI_LoungeCarpet','SUI_BedSconce','DATUM_bed_light_','DATUM_bed_table_','DATUM_writing_chair','SUI_AcousticLiving'])
 ex,wall,mesh,datum=[ns[k]for k in ['extrusion','wall','mesh','datum']]
 h=cfg['night_garden_handing'];design=cfg['night_garden_design'];family=cfg['historical_class']=='family'
 def fit(x,y,margin=.085):
  return (max(ns['at'](ns['left'],y)+margin,min(h*x,ns['at'](ns['right'],y)-margin)),y)
 def poly(n,p,lo,hi,role):
  # Insert every perimeter change before fitting an edge, so a long shelf/rug
  # edge follows a concave wall instead of cutting through its inward shoulder.
  pts=[];knots=sorted({v[1]for v in ns['left']+ns['right']})
  for a,b in zip(p,p[1:]+p[:1]):
   ts=[0]+sorted((y-a[1])/(b[1]-a[1])for y in knots if min(a[1],b[1])<y<max(a[1],b[1])) if a[1]!=b[1] else [0]
   for t in ts:pts.append(fit(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t))
  return ex(n,pts,lo,hi,role)
 def line(n,a,b,lo,hi,role,width=.12):return wall(n,fit(*a,width/2+.065),fit(*b,width/2+.065),lo,hi,hi,role,width)
 # Entry is genuinely layered. A short fixed shoulder roots in the wet-room
 # enclosure; the curving canopy stops before the sitting pocket and clear route.
 wall('NG_EntryPrivacyRoot',(-.65,3.92),(-.65,4.32),0,2.28,2.28,'ivory_enamel',.13)
 wall('NG_EntryPrivacyReturn',(-.65,4.32),(-.10,4.48),0,1.58,1.58,'oatmeal_weave',.13)
 wall('NG_EntryTimberTop',(-.65,4.32),(-.10,4.48),1.58,1.64,1.64,'warm_walnut',.17)
 foyer=[(-.62,3.35),(2.48,3.35),(2.45,3.73),(1.83,4.23),(.89,4.39),(-.16,4.30),(-.62,4.05)]
 ex('NG_LayeredArrivalSoffit',foyer,2.67,2.79,'warm_walnut')
 ex('NG_ArrivalSoffitSoftInset',[(x*.96,y)for x,y in foyer],2.64,2.67,'oatmeal_weave')
 ex('NG_ArrivalSoffitBearing',[(-.76,3.40),(-.55,3.40),(-.55,3.92),(-.76,3.92)],2.55,2.70,'warm_walnut')
 # Fixed shallow pocket stores coats/drop objects outside both door travel areas.
 ex('NG_KeyDropShelf',[(1.91,3.23),(2.41,3.23),(2.44,3.46),(1.97,3.61),(1.91,3.48)],.80,.86,'warm_walnut')
 ex('NG_KeyDropShelfBearing',[(2.27,3.26),(2.39,3.26),(2.39,3.41),(2.27,3.41)],0,.80,'ivory_enamel')
 # Sitting and writing are arranged differently, preserving the family third
 # support on its exact recovered side and the same useful central walk/view line.
 if design=='glimpse_parlor':
  rug=[(-3.13,4.24),(-1.24,4.24),(-.42,4.70),(-.40,6.60),(-.80,7.01),(-3.10,7.01)]
  desk=[(-3.26,7.98),(-1.25,7.98),(-1.08,8.17),(-1.27,8.39),(-3.26,8.39)]
  poly('NG_ParlorWritingDesk',desk,.75,.82,'warm_walnut')
  for x in [-3.10,-1.43]:poly('NG_ParlorDeskLeg_'+str(x),[(x-.05,8.04),(x+.05,8.04),(x+.05,8.32),(x-.05,8.32)],0,.75,'champagne_metal')
  # A supported wide writing canopy makes an intimate side room in section.
  canopy=[(-3.36,6.74),(-1.05,6.74),(-.84,7.12),(-.98,8.50),(-3.36,8.50)]
  poly('NG_ParlorReadCanopy',canopy,2.43,2.53,'oatmeal_weave')
  for y in [6.77,8.38]:
   host=ns['at'](ns['left']if h==1 else ns['right'],y)
   wall('NG_ParlorCanopyWallBearer_'+str(y),(host,y),(host+h*.30,y),2.32,2.47,2.47,'warm_walnut',.17)
  shoulder_specs=[(-1,8.70,1.65),(1,8.25,1.92)]
 else:
  rug=[(-3.16,4.17),(-.22,4.17),(-.12,4.80),(-.55,6.48),(-2.74,6.60),(-3.17,6.20)]
  desk=[(-3.28,7.22),(-2.50,7.22),(-2.46,7.40),(-2.50,8.13),(-3.28,8.30)]
  poly('NG_GalleryLongWritingDesk',desk,.75,.82,'warm_walnut')
  for y in [7.30,8.08]:poly('NG_GalleryDeskLeg_'+str(y),[(-3.21,y),(-2.72,y),(-2.72,y+.08),(-3.21,y+.08)],0,.75,'champagne_metal')
  # Two unequal arches frame successive activity zones without lowering the
  # central route or pretending the inherited main curved roof disappeared.
  for k,y in enumerate([6.56,8.48]):
   spans=[(-3.32,2.45),(-2.60,2.64),(-1.38,3.06),(0,3.24),(1.45,2.93),(2.74,2.62),(3.32,2.50)]
   for j,(a,b)in enumerate(zip(spans,spans[1:])):
    q=[(*fit(a[0],y,.065),a[1]),(*fit(b[0],y,.065),b[1]),(*fit(b[0],y+.16,.065),b[1]),(*fit(a[0],y+.16,.065),a[1])]
    mesh(f'NG_GallerySplitArch_{k}_{j}',q+[(x,v,z+.08)for x,v,z in q],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'warm_walnut')
  shoulder_specs=[(-1,8.63,1.93),(1,8.46,1.58)]
 poly('NG_SittingPocketWovenRug',rug,.013,.020,'clay_weave')
 # Purposeful rest threshold: the two exact rear beds are screened from the
 # entrance by staggered shoulders with a central glimpse to the real aperture.
 for i,(side,y,height)in enumerate(shoulder_specs):
  line('NG_RestShoulder_'+str(i),(side*3.32,y),(side*.84,y+.20),0,height,'ivory_enamel',.12)
  line('NG_RestShoulderCap_'+str(i),(side*3.32,y),(side*.84,y+.20),height,height+.07,'warm_walnut',.16)
  line('NG_RestShoulderWoven_'+str(i),(side*3.20,y-.075),(side*1.02,y+.10),.20,height-.20,'oatmeal_weave',.025)
 if family:
  # Third rest is adult-scale, exact position; short longitudinal screen blocks
  # direct central standing sight while its foot approach remains open.
  line('NG_FamilyThirdRestScreen',(1.04,5.82),(1.04,7.53),0,1.53,'oatmeal_weave',.10)
  line('NG_FamilyThirdRestCap',(1.04,5.82),(1.04,7.53),1.53,1.59,'warm_walnut',.13)
  poly('NG_FamilyThirdRestCanopy',[(1.05,5.08),(2.73,5.08),(3.25,7.65),(1.05,7.65)],2.46,2.55,'oatmeal_weave')
 else:
  # Standards use the otherwise empty side bay as a fitted luggage and textile
  # store, rather than counterfeit a third bed or oversized unused niche.
  poly('NG_StandardLuggageBench',[(1.65,5.27),(2.55,5.27),(2.68,6.31),(1.65,6.31)],0,.40,'warm_walnut')
  poly('NG_StandardLuggageCushion',[(1.68,5.30),(2.52,5.30),(2.62,6.27),(1.68,6.27)],.40,.49,'oatmeal_weave')
 # All rooms have usable deep storage at the rear window flank, clear of every
 # recovered support. Access passes behind the beds from the central aisle.
 storage=[(-3.30,11.76),(-2.84,11.76),(-2.84,12.49),(-3.30,12.49)]
 poly('NG_CommonStorageBack',[(-3.30,11.76),(-3.24,11.76),(-3.24,12.49),(-3.30,12.49)],0,1.87,'warm_walnut')
 for y in [11.76,12.43]:poly('NG_CommonStorageEnd_'+str(y),[(-3.30,y),(-2.84,y),(-2.84,y+.06),(-3.30,y+.06)],0,1.87,'warm_walnut')
 for j,z in enumerate([.12,.56,1.14,1.81]):poly('NG_CommonStorageShelf_'+str(j),storage,z,z+.055,'warm_walnut')
 for j in range(3):poly('NG_StoredTextile_'+str(j),[(-3.18,11.85),(-2.88,11.85),(-2.88,12.22),(-3.18,12.22)],.62+j*.08,.69+j*.08,'teal_weave')
 # The real finite window has a reachable side sitting edge and two low
 # central ledges beyond the exact rear beds, never a generic space screen.
 for side in [-1,1]:
  a,b=sorted([side*.62,side*1.03]);ex('NG_WindowLowLedge_'+str(side),[(a,12.36),(b,12.36),(b,12.58),(a,12.58)],.50,.56,'warm_walnut')
  ex('NG_WindowLedgeLeg_'+str(side),[(a,12.42),(a+.07,12.42),(a+.07,12.54),(a,12.54)],0,.50,'warm_walnut')
 # Every authored lamp is supported by a visible wall/ceiling mount. Evaluated
 # datum coordinates, not object.location on a baked transform, drive fixtures.
 for i,a in enumerate(cfg['bed_anchors']):
  x,y,z=a['source_xyz'];side=-1 if x<0 else 1;host=ns['at'](ns['left']if side<0 else ns['right'],y)
  wall('NG_BedLanternMount_'+str(i),(host,y),(host-side*.18,y),1.64,1.98,1.98,'warm_walnut',.18)
  ex('NG_BedLanternHousing_'+str(i),[(host-side*.23,y-.15),(host-side*.07,y-.15),(host-side*.07,y+.15),(host-side*.23,y+.15)],1.68,1.94,'champagne_metal')
  ex('NG_BedLanternOpal_'+str(i),[(host-side*.24,y-.11),(host-side*.225,y-.11),(host-side*.225,y+.11),(host-side*.24,y+.11)],1.72,1.90,'lens')
  datum('night_bed_light_'+str(i),(host-side*.255,y,1.81))
 wall('NG_ReadLanternWallMount',(-h*3.32,7.80),(-h*3.13,7.80),1.70,2.02,2.02,'warm_walnut',.18)
 poly('NG_ReadLanternHousing',[(-3.15,7.63),(-2.99,7.63),(-2.99,7.94),(-3.15,7.94)],1.73,1.99,'champagne_metal')
 poly('NG_ReadLanternOpal',[(-2.99,7.67),(-2.975,7.67),(-2.975,7.90),(-2.99,7.90)],1.77,1.95,'lens')
 datum('night_read_light',(-h*2.96,7.78,1.85))
 # Directional source preview. It does not establish glTF/runtime shader parity.
 m=ns['mats']['glass'];m.name='NG_SourceDirectionalPrivacy_NOT_RUNTIME_ACCEPTED';nodes=m.node_tree.nodes;nodes.clear();links=m.node_tree.links
 out=nodes.new('ShaderNodeOutputMaterial');opaque=nodes.new('ShaderNodeBsdfPrincipled');opaque.inputs['Base Color'].default_value=(.07,.12,.12,1);opaque.inputs['Metallic'].default_value=.62;opaque.inputs['Roughness'].default_value=.23;clear=nodes.new('ShaderNodeBsdfTransparent');clear.inputs[0].default_value=(1,1,1,1)
 geom=nodes.new('ShaderNodeNewGeometry');tr=nodes.new('ShaderNodeVectorTransform');tr.vector_type='VECTOR';tr.convert_from='WORLD';tr.convert_to='OBJECT';sep=nodes.new('ShaderNodeSeparateXYZ');test=nodes.new('ShaderNodeMath');test.operation='LESS_THAN';test.inputs[1].default_value=0;mix=nodes.new('ShaderNodeMixShader')
 links.new(geom.outputs['Incoming'],tr.inputs[0]);links.new(tr.outputs[0],sep.inputs[0]);links.new(sep.outputs['Y'],test.inputs[0]);links.new(test.outputs[0],mix.inputs[0]);links.new(opaque.outputs[0],mix.inputs[1]);links.new(clear.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],out.inputs[0]);return ns

def export_shell(dest):
 groups={}
 for ob in list(bpy.context.scene.objects):
  if ob.type!='MESH':continue
  c=ob.copy();c.data=ob.data.copy();bpy.context.collection.objects.link(c);groups.setdefault(tuple(m.name for m in c.data.materials),[]).append(c)
 meshes=[]
 for key,obs in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for o in obs:o.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();o=bpy.context.object;o.name='NG_Runtime_'+key[0];meshes.append(o)
 bpy.ops.object.select_all(action='DESELECT')
 for o in meshes:o.select_set(True)
 for o in bpy.context.scene.objects:
  if o.type=='EMPTY':o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(dest/'shell.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
 for o in meshes:bpy.data.objects.remove(o,do_unlink=True)

def evaluated():
 deps=bpy.context.evaluated_depsgraph_get();out=[]
 for o in bpy.context.scene.objects:
  if o.type not in ['MESH','CURVE']:continue
  ev=o.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();v=[tuple(o.matrix_world@q.co)for q in me.vertices]
  out.append({'name':o.name,'assembly_member':o.get('assembly_member',''),'source_asset':o.get('source_asset',''),'bounds':[list(map(min,zip(*v))),list(map(max,zip(*v)))],'vertices':v,'triangles':[list(t.vertices)for t in me.loop_triangles]});ev.to_mesh_clear()
 return out

receipts=[]
for cfg in plan['prototypes']:
 key=cfg['address'];dest=OUT/key;dest.mkdir();bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.cycles.use_denoising=False
 ns=night_shell(cfg);bpy.context.view_layer.update();shellstats=visual_mesh_stats()
 fixtures=[]
 for o in list(scene.objects):
  if o.type=='EMPTY'and o.name.startswith(('DATUM_light_','DATUM_bath_light','DATUM_night_')):
   p=list(o.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation)
   assert 1.60<p[2]<4.25, (o.name,p)
   fixtures.append({'name':o.name,'source_xyz':p,'world_transform_rule':'Use evaluated/authored datum then exact unit origin+yaw; assert elevation above floor'})
 (dest/'SOURCE_FIXTURES.json').write_text(json.dumps(fixtures,indent=2)+'\n')
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(dest/'shell.blend'));export_shell(dest)
 for c in cfg['component_placements']:append_source(c.get('candidate_source')or c['catalogue_source'],c['label'],c['source_xyz'],c['source_yaw'])
 scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;stats=visual_mesh_stats();(dest/'EVALUATED_GEOMETRY.json').write_text(json.dumps(evaluated(),separators=(',',':'))+'\n')
 # Fixture nodes are deliberately sourced from the evaluated datum list. This
 # assembly can be inspected/rendered without lights collapsed to the room origin.
 for f in fixtures:
  light=bpy.data.lights.new('NG_Light_'+f['name'],'AREA');light.energy=32 if 'night_'in f['name']else 65;light.color=(1,.90,.77);light.shape='DISK';light.size=.30
  ob=bpy.data.objects.new(light.name,light);scene.collection.objects.link(ob);ob.location=f['source_xyz'];assert ob.location.z>1.60
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(dest/'assembly.blend'))
 rec={'prototype':key,'representative_unit':cfg['representative_unit_id'],'placements':cfg['component_placements'],'shell_stats':shellstats,'assembly_stats':stats,'files':{n:sha(dest/n)for n in ['shell.blend','shell.glb','assembly.blend','EVALUATED_GEOMETRY.json','SOURCE_FIXTURES.json']},'sealed_profile':'sealed_window_r010','operable_source_doors':['AST-DOR-001','AST-DOR-002'],'exact_recovered_bed_coordinates_preserved':True,'fixture_datum_count':len(fixtures),'runtime_privacy_and_doors_accepted':False,'scope':'Night Garden source only; installed pilots not edited'}
 (dest/'SOURCE_RECEIPT.json').write_text(json.dumps(rec,indent=2)+'\n');receipts.append(rec);print('NIGHT_GARDEN_SOURCE_READY',key,flush=True)
assert all(sha(p)==h for p,h in pins.items()),'Protected input changed during authoring'
(OUT/'BATCH_RECEIPT.json').write_text(json.dumps({'prototypes':receipts,'units_mapped':80,'rest_slots_mapped':210,'protected_installed_units':2,'source_build_complete':True,'Game_or_Catalogue_writes':False,'runtime_acceptance':False,'retained_inputs_unchanged':pins},indent=2)+'\n')
print('NIGHT_GARDEN_BATCH_COMPLETE',len(receipts),flush=True)
