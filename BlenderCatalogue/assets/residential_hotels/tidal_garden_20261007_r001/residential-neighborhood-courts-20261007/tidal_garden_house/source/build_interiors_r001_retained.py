"""Eight authored Tidal sources. Coordinated Blender source slot, two threads."""
from pathlib import Path
import bpy,bmesh,json,math,hashlib,ast,types,importlib.util,sys
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];W=R.parents[1];ROOT=W/'residential-batch-neighborhood-20261006/scale_domestic_r011';CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
args=types.SimpleNamespace(domestic=True);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=ROOT/'source/build_family.py'
for node in ast.parse(base.read_text()).body:
 if isinstance(node,ast.FunctionDef):exec(compile(ast.Module(body=[node],type_ignores=[]),str(base),'exec'),globals())
plan=json.loads((R/'TIDAL_GARDEN_85_PLACEMENT_MAP.json').read_text());OUT=R/'outputs/interiors_r001';assert not OUT.exists(),'Preserve every prior revision';OUT.mkdir()
pins={str(p):sha(p)for p in[base,ROOT/'assemblies/GODOT_BATCH_INSTANCE_MAP.json',ROOT/'PROTOTYPE_PLAN.json',R/'TIDAL_GARDEN_85_PLACEMENT_MAP.json']}
def drop(prefixes):
 for o in list(bpy.context.scene.objects):
  if any(o.name.startswith(p)for p in prefixes):bpy.data.objects.remove(o,do_unlink=True)
def tidal_shell(cfg):
 cc=dict(cfg);cc.update(historical_class='standard',view_lounge_replan=False,family_sleep_bay_privacy=False);ns=author_shell(cc)
 # Engineering reuse is confined to genuine finite shell, bath, doors, kitchen
 # and metric conventions. Tidal room composition is authored below.
 drop(['SUI_LivingCase','SUI_SleepThresholdWing','SUI_ThresholdTimberCap','SUI_SleepingValance','SUI_Writing','SUI_LoungeCarpet','SUI_BedSconce','DATUM_bed_light_','DATUM_bed_table_','DATUM_writing_chair','SUI_AcousticLiving'])
 ex,wall,mesh,datum=[ns[k]for k in['extrusion','wall','mesh','datum']];h=cfg['tidal_handing'];design=cfg['tidal_design']
 def poly(name,p,lo,hi,role):return ex(name,[(h*x,y)for x,y in p],lo,hi,role)
 def line(name,a,b,lo,hi,role,width=.12):return wall(name,(h*a[0],a[1]),(h*b[0],b[1]),lo,hi,hi,role,width)
 # Deep entry shoulders create a real 4m domestic transition and protect rest
 # when the retained front door opens. Bathroom and kitchenette stay fixed.
 wall('TG_EntryShoulderRoot',(-.64,3.94),(-.64,4.24),0,2.42,2.42,'ivory_enamel',.14)
 wall('TG_EntryShoulderReturn',(-.64,4.24),(.30,4.47),0,2.42,2.42,'ivory_enamel',.14)
 wall('TG_EntryShoulderCap',(-.64,4.24),(.30,4.47),2.42,2.49,2.49,'warm_walnut',.18)
 foyer=[(-.61,3.45),(2.42,3.45),(2.60,3.75),(2.26,4.36),(1.78,4.73),(.90,4.90),(.26,4.67),(-.61,4.39)]
 ex('TG_CurvedEntrySoffit',foyer,2.70,2.82,'warm_walnut');ex('TG_EntrySoffitWovenInset',[(x*.95,y)for x,y in foyer],2.67,2.70,'oatmeal_weave')
 ex('TG_EntrySoffitBearing',[(-.77,3.47),(-.55,3.47),(-.55,3.94),(-.77,3.94)],2.57,2.73,'warm_walnut')
 ex('TG_ArrivalDropShelf',[(1.95,3.16),(2.40,3.16),(2.47,3.45),(2.06,3.58),(1.95,3.48)],.77,.83,'warm_walnut')
 # Actual usable luggage bench, deep shelves and open joinery on the rest edge.
 x0,x1=2.77,3.29;y0,y1=(8.36,9.70)if design=='broad_salon'else(8.40,9.68)
 poly('TG_SharedStoragePlinth',[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],0,.13,'warm_walnut')
 poly('TG_SharedStorageBack',[(x1-.06,y0),(x1,y0),(x1,y1),(x1-.06,y1)],.13,1.64,'warm_walnut')
 for j,y in enumerate([y0,y1-.06]):poly('TG_SharedStorageEnd_'+str(j),[(x0,y),(x1,y),(x1,y+.06),(x0,y+.06)],.13,1.64,'warm_walnut')
 for j,z in enumerate([.47,.94,1.59]):poly('TG_SharedStorageShelf_'+str(j),[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z,z+.05,'warm_walnut')
 poly('TG_LuggageSoftSeat',[(x0+.03,y0+.06),(x1-.08,y0+.06),(x1-.08,y0+.65),(x0+.03,y0+.65)],.52,.61,'oatmeal_weave')
 for j in range(4):poly('TG_StoredBook_'+str(j),[(x0+.08,y0+.76+j*.11),(x1-.10,y0+.76+j*.11),(x1-.10,y0+.83+j*.11),(x0+.08,y0+.83+j*.11)],.99,1.25+.04*(j%2),'teal_weave')
 # Different rest-to-salon thresholds: broad low sideboard vs crescent shoulder.
 if design=='broad_salon':
  line('TG_RestHeadShelf',(-2.80,7.76),(-1.05,7.76),.88,.96,'warm_walnut',.32)
  line('TG_RestHeadShelfLeg',(-2.80,7.76),(-2.66,7.76),0,.89,'warm_walnut',.32)
  line('TG_RestHeadShelfLeg2',(-1.18,7.76),(-1.05,7.76),0,.89,'warm_walnut',.32)
  outline=[(-3.22,10.19),(-2.45,9.98),(-.40,10.14),(.42,9.97),(3.22,10.07),(3.25,12.59),(-3.22,12.59)]
 else:
  arc=[(-3.08+2.37*k/8,7.16+.24*math.sin(math.pi*k/8))for k in range(9)]
  for j,(a,b)in enumerate(zip(arc,arc[1:])):line('TG_CrescentRestShoulder_'+str(j),a,b,0,1.12,'ivory_enamel',.14)
  outline=[(-3.23,10.38),(-2.90,10.08),(-1.80,9.92),(-.65,10.04),(.50,9.83),(3.22,10.00),(3.25,12.59),(-3.22,12.59)]
 poly('TG_SalonFittedRug',outline,.013,.020,'clay_weave')
 # Low curved reading ledge sits at the window flank, not across the aperture.
 ledge=[(-3.23,10.84),(-2.90,10.74),(-2.69,10.90),(-2.64,11.34),(-2.68,11.94),(-2.92,12.27),(-3.23,12.26)]
 poly('TG_WindowCurvedReadingLedge',ledge,.73,.80,'warm_walnut')
 for y in[10.90,12.15]:poly('TG_ReadingLedgeSupport_'+str(y),[(-3.15,y),(-2.80,y),(-2.80,y+.07),(-3.15,y+.07)],0,.74,'champagne_metal')
 # Tidal salon has one rising framed canopy opening, not individual sleep pods.
 spans=[(-3.36,3.25),(-2.70,3.50),(-1.55,3.68),(0,3.74),(1.55,3.68),(2.70,3.50),(3.36,3.25)]
 for j,(a,b)in enumerate(zip(spans,spans[1:])):
  q=[(h*a[0],10.06,a[1]),(h*b[0],10.06,b[1]),(h*b[0],10.24,b[1]),(h*a[0],10.24,a[1])]
  mesh('TG_CurvedSalonFrame_'+str(j),q+[(x,y,z+.08)for x,y,z in q],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'warm_walnut')
 # Supported head-task fixtures use the actual wall; no free-floating light.
 for i,a in enumerate(cfg['bed_anchors']):
  x,y,z=a['source_xyz'];side=-1 if x<0 else 1;host=ns['at'](ns['left']if side<0 else ns['right'],y)
  wall('TG_BedLightMount_'+str(i),(host,y),(host-side*.17,y),1.65,1.98,1.98,'warm_walnut',.20)
  ex('TG_BedTaskHousing_'+str(i),[(host-side*.21,y-.13),(host-side*.07,y-.13),(host-side*.07,y+.13),(host-side*.21,y+.13)],1.71,1.91,'champagne_metal')
  ex('TG_BedTaskLens_'+str(i),[(host-side*.225,y-.10),(host-side*.21,y-.10),(host-side*.21,y+.10),(host-side*.225,y+.10)],1.74,1.88,'lens')
  datum('tidal_bed_light_'+str(i),(host-side*.24,y,1.80))
 datum('tidal_salon_approach',(0,10.34,0));datum('tidal_kitchen_work',(1.85,1.60,0))
 # Finite aperture retains all r010 overlaps. This source preview shader is
 # directional; glTF/runtime needs the existing project privacy shader contract.
 m=ns['mats']['glass'];m.name='TG_SourceDirectionalPrivacy_NOT_RUNTIME_ACCEPTED';nodes=m.node_tree.nodes;nodes.clear();links=m.node_tree.links
 out=nodes.new('ShaderNodeOutputMaterial');opaque=nodes.new('ShaderNodeBsdfPrincipled');opaque.inputs['Base Color'].default_value=(.07,.16,.17,1);opaque.inputs['Metallic'].default_value=.60;opaque.inputs['Roughness'].default_value=.22;clear=nodes.new('ShaderNodeBsdfTransparent');clear.inputs[0].default_value=(1,1,1,1)
 geom=nodes.new('ShaderNodeNewGeometry');tr=nodes.new('ShaderNodeVectorTransform');tr.vector_type='VECTOR';tr.convert_from='WORLD';tr.convert_to='OBJECT';sep=nodes.new('ShaderNodeSeparateXYZ');test=nodes.new('ShaderNodeMath');test.operation='LESS_THAN';test.inputs[1].default_value=0;mix=nodes.new('ShaderNodeMixShader')
 links.new(geom.outputs['Incoming'],tr.inputs[0]);links.new(tr.outputs[0],sep.inputs[0]);links.new(sep.outputs['Y'],test.inputs[0]);links.new(test.outputs[0],mix.inputs[0]);links.new(opaque.outputs[0],mix.inputs[1]);links.new(clear.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],out.inputs[0]);return ns
def export_shell(dest):
 groups={};copies=[]
 for ob in list(bpy.context.scene.objects):
  if ob.type!='MESH':continue
  c=ob.copy();c.data=ob.data.copy();bpy.context.collection.objects.link(c);groups.setdefault(tuple(m.name for m in c.data.materials),[]).append(c)
 meshes=[]
 for key,obs in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for o in obs:o.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();o=bpy.context.object;o.name='TG_Runtime_'+key[0];meshes.append(o)
 bpy.ops.object.select_all(action='DESELECT')
 for o in meshes:o.select_set(True)
 for o in bpy.context.scene.objects:
  if o.type=='EMPTY':o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(dest/'shell.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
 for o in meshes:bpy.data.objects.remove(o,do_unlink=True)
def evaluated():
 deps=bpy.context.evaluated_depsgraph_get();out=[]
 for o in bpy.context.scene.objects:
  if o.type not in['MESH','CURVE']:continue
  ev=o.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();v=[tuple(o.matrix_world@q.co)for q in me.vertices];out.append({'name':o.name,'assembly_member':o.get('assembly_member',''),'source_asset':o.get('source_asset',''),'bounds':[list(map(min,zip(*v))),list(map(max,zip(*v)))],'vertices':v,'triangles':[list(t.vertices)for t in me.loop_triangles]});ev.to_mesh_clear()
 return out
receipts=[]
for cfg in plan['prototypes']:
 key=cfg['address'];dest=OUT/key;dest.mkdir();bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.threads_mode='FIXED';bpy.context.scene.render.threads=2;bpy.context.scene.cycles.use_denoising=False
 ns=tidal_shell(cfg);shellstats=visual_mesh_stats();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(dest/'shell.blend'));export_shell(dest)
 for c in cfg['component_placements']:append_source(c.get('candidate_source')or c['catalogue_source'],c['label'],c['source_xyz'],c['source_yaw'])
 bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1;stats=visual_mesh_stats();(dest/'EVALUATED_GEOMETRY.json').write_text(json.dumps(evaluated(),separators=(',',':'))+'\n');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(dest/'assembly.blend'))
 rec={'prototype':key,'representative_unit':cfg['representative_unit_id'],'placements':cfg['component_placements'],'shell_stats':shellstats,'assembly_stats':stats,'files':{n:sha(dest/n)for n in['shell.blend','shell.glb','assembly.blend','EVALUATED_GEOMETRY.json']},'sealed_profile':'sealed_window_r010','operable_source_doors':['AST-DOR-001','AST-DOR-002'],'runtime_privacy_and_doors_accepted':False,'scope':'Source only Tidal eight-family library; no registered capacity change'}
 (dest/'SOURCE_RECEIPT.json').write_text(json.dumps(rec,indent=2)+'\n');receipts.append(rec);print('TIDAL_INTERIOR_SOURCE_READY',key,flush=True)
assert all(sha(p)==h for p,h in pins.items())
(OUT/'BATCH_RECEIPT.json').write_text(json.dumps({'prototypes':receipts,'retained_inputs_unchanged':pins,'units_mapped':85,'rest_slots_mapped':221,'source_build_complete':True,'Game_or_Catalogue_writes':False,'runtime_acceptance':False},indent=2)+'\n');print('TIDAL_INTERIOR_BATCH_COMPLETE',len(receipts),flush=True)
