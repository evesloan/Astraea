"""Eight authored Family Terrace sources. Coordinated Blender source slot, two threads."""
from pathlib import Path
import bpy,bmesh,json,math,hashlib,ast,types,importlib.util,sys
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];W=R.parents[1];ROOT=W/'residential-batch-neighborhood-20261006/scale_domestic_r011';CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
args=types.SimpleNamespace(domestic=True);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=ROOT/'source/build_family.py'
for node in ast.parse(base.read_text()).body:
 if isinstance(node,ast.FunctionDef):exec(compile(ast.Module(body=[node],type_ignores=[]),str(base),'exec'),globals())
plan=json.loads((R/'FAMILY_TERRACE_82_PLACEMENT_MAP.json').read_text());OUT=R/'outputs/interiors_r003';assert not OUT.exists(),'Preserve every prior revision';OUT.mkdir()
pins={str(p):sha(p)for p in[base,ROOT/'assemblies/GODOT_BATCH_INSTANCE_MAP.json',ROOT/'PROTOTYPE_PLAN.json',R/'FAMILY_TERRACE_82_PLACEMENT_MAP.json']}
def drop(prefixes):
 for o in list(bpy.context.scene.objects):
  if any(o.name.startswith(p)for p in prefixes):bpy.data.objects.remove(o,do_unlink=True)
def family_shell(cfg):
 cc=dict(cfg);cc.update(historical_class='standard',view_lounge_replan=False,family_sleep_bay_privacy=False);ns=author_shell(cc)
 # Reuse finite service/shell engineering; replace all living and rest composition.
 drop(['SUI_LivingCase','SUI_SleepThresholdWing','SUI_ThresholdTimberCap','SUI_SleepingValance','SUI_Writing','SUI_LoungeCarpet','SUI_BedSconce','DATUM_bed_light_','DATUM_bed_table_','DATUM_writing_chair','SUI_AcousticLiving','SUI_TwinRetreatSpine'])
 ex,wall,mesh,datum=[ns[k]for k in['extrusion','wall','mesh','datum']];h=cfg['family_terrace_handing'];design=cfg['family_terrace_design'];at=ns['at'];left=ns['left'];right=ns['right']
 def poly(name,p,lo,hi,role):return ex(name,[(h*x,y)for x,y in p],lo,hi,role)
 def rect(name,x0,x1,y0,y1,lo,hi,role):return poly(name,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],lo,hi,role)
 # A broad enclosed domestic vestibule has a usable drop shelf at the kitchen
 # shoulder and a high portal tied into both real curved walls.
 ex('FT_ArrivalShelf',[(1.25,3.49),(2.42,3.49),(2.42,3.79),(1.43,3.88),(1.25,3.77)],.77,.83,'warm_walnut')
 for x in[1.35,2.33]:ex('FT_ArrivalShelfBracket_'+str(x),[(x,3.53),(x+.06,3.53),(x+.06,3.75),(x,3.75)],.25,.78,'champagne_metal')
 front=4.10;back=4.38
 # Exact selected shell profile is used, never an A-profile guess for B.
 fp=[(at(left,front)+.08,front),(at(right,front)-.08,front),(at(right,back)-.08,back),(at(left,back)+.08,back)]
 ex('FT_BroadDomesticPortal',fp,2.64,2.85,'warm_walnut');ex('FT_PortalAcousticUnderside',[(x*.99,y)for x,y in fp],2.61,2.64,'oatmeal_weave')
 for s,profile in[(-1,left),(1,right)]:
  x=at(profile,front)+(-s*.10);xb=at(profile,back)+(-s*.10);wall('FT_PortalShoulder_'+str(s),(x,front),(xb,back),0,2.65,2.65,'ivory_enamel',.14)
 # Shared table is a purpose-sized new joinery component: 1.56m long with
 # rounded/chanfered ends, two bearing trestles and real three-person seating.
 tx,ty,_=cfg['group_surface_xyz'];shape=[(tx-.47,ty-.64),(tx-.33,ty-.78),(tx+.33,ty-.78),(tx+.47,ty-.64),(tx+.47,ty+.64),(tx+.33,ty+.78),(tx-.33,ty+.78),(tx-.47,ty+.64)]
 ex('FT_GroupWorktop',shape,.70,.77,'warm_walnut')
 for j,y in enumerate([ty-.46,ty+.46]):ex('FT_GroupTableTrestle_'+str(j),[(tx-.31,y-.055),(tx+.31,y-.055),(tx+.31,y+.055),(tx-.31,y+.055)],0,.71,'ivory_enamel')
 # A fitted carpet defines living and a full ceiling change defines sleep.
 p=[(at(left,y)+.18,y)for y in[4.45,5.2,6.2,6.82]]+[(at(right,y)-.18,y)for y in[6.82,6.2,5.2,4.45]]
 ex('FT_LivingWovenField',p,.013,.020,'clay_weave')
 for k,y in enumerate([7.00,7.16]):
  a=at(left,y)+.07;b=at(right,y)-.07
  sec=[(a,2.67),(-1.1,2.67),(-.74,3.12),(.74,3.12),(1.1,2.88),(b,2.88),(b,3.34),(a,3.34)]
  n=len(sec);mesh('FT_SectionalSleepPortal_'+str(k),[(x,yy,z)for yy in[y,y+.10]for x,z in sec],[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],'warm_walnut'if k==0 else'oatmeal_weave')
 # Shared storage changes side and depth with the plan, with three open cubbies
 # instead of a blind cabinet block; each has a reachable shelf.
 sx0,sx1=(2.53,3.16)if design=='shared_table'else(2.61,3.20)
 sy0,sy1=(4.65,6.35)if design=='shared_table'else(7.35,9.18)
 # Fit handed asymmetric profile by explicitly limiting both x edges.
 x0,x1=sorted([h*sx0,h*sx1]);ys=[sy0,sy1]
 if h>0:x1=min(at(right,y)-.14 for y in ys+[5.1,6.2]if sy0<=y<=sy1)
 else:x0=max(at(left,y)+.14 for y in ys+[5.2,6.2]if sy0<=y<=sy1)
 for name,lo,hi in[('Plinth',0,.13),('LowShelf',.46,.51),('MiddleShelf',.99,1.04),('TopShelf',1.51,1.57)]:ex('FT_SharedStorage'+name,[(x0,sy0),(x1,sy0),(x1,sy1),(x0,sy1)],lo,hi,'warm_walnut')
 backx=x1 if h>0 else x0
 ex('FT_SharedStorageBack',[(backx-.035,sy0),(backx+.035,sy0),(backx+.035,sy1),(backx-.035,sy1)],.13,1.57,'ivory_enamel')
 for j,y in enumerate([sy0,sy0+(sy1-sy0)/3,sy0+2*(sy1-sy0)/3,sy1-.055]):ex('FT_SharedCubbieDivider_'+str(j),[(x0,y),(x1,y),(x1,y+.055),(x0,y+.055)],.13,1.57,'warm_walnut')
 # Shallow window-edge communal writing ledge preserves the clear outlook.
 rect('FT_WindowSharedLedge',-.72,.72,12.26,12.59,.74,.81,'warm_walnut')
 for x in[-.61,.61]:rect('FT_WindowLedgeLeg_'+str(x),x-.05,x+.05,12.30,12.55,0,.75,'champagne_metal')
 # Mounted task lights have receiving geometry against each actual shell side.
 for i,a in enumerate(cfg['bed_anchors']):
  x,y,z=a['source_xyz'];side=-1 if x<0 else 1;host=at(left if side<0 else right,y)
  wall('FT_BedTaskMount_'+str(i),(host,y),(host-side*.18,y),1.60,1.95,1.95,'warm_walnut',.21)
  xx=host-side*.20;ex('FT_BedTaskHousing_'+str(i),[(xx-.055,y-.14),(xx+.055,y-.14),(xx+.055,y+.14),(xx-.055,y+.14)],1.67,1.92,'champagne_metal')
  ex('FT_BedTaskLens_'+str(i),[(xx-.058,y-.105),(xx+.058,y-.105),(xx+.058,y+.105),(xx-.058,y+.105)],1.69,1.71,'lens');datum('family_rest_approach_'+str(i),(x-math.copysign(1.02,x),y,0))
 # Group lamp is carried by the actual source living ceiling beam.
 yy=5.62;a=at(left,yy)+.06;b=at(right,yy)-.06;wall('FT_GroupLampReceiver',(a,yy),(b,yy),3.27,3.40,3.40,'warm_walnut',.18)
 ex('FT_GroupTaskStem',[(tx-.035,yy-.035),(tx+.035,yy-.035),(tx+.035,yy+.035),(tx-.035,yy+.035)],2.61,3.28,'champagne_metal')
 ex('FT_GroupTaskHousing',[(tx-.27,yy-.14),(tx+.27,yy-.14),(tx+.27,yy+.14),(tx-.27,yy+.14)],2.56,2.63,'ivory_enamel')
 ex('FT_GroupTaskLens',[(tx-.23,yy-.10),(tx+.23,yy-.10),(tx+.23,yy+.10),(tx-.23,yy+.10)],2.54,2.56,'lens');datum('family_group_task',(tx,yy,2.53))
 m=ns['mats']['glass'];m.name='FT_SourceDirectionalPrivacy_NOT_RUNTIME_ACCEPTED';nodes=m.node_tree.nodes;nodes.clear();links=m.node_tree.links
 out=nodes.new('ShaderNodeOutputMaterial');opaque=nodes.new('ShaderNodeBsdfPrincipled');opaque.inputs['Base Color'].default_value=(.09,.14,.16,1);opaque.inputs['Metallic'].default_value=.66;opaque.inputs['Roughness'].default_value=.20;clear=nodes.new('ShaderNodeBsdfTransparent');clear.inputs[0].default_value=(1,1,1,1)
 geom=nodes.new('ShaderNodeNewGeometry');tr=nodes.new('ShaderNodeVectorTransform');tr.vector_type='VECTOR';tr.convert_from='WORLD';tr.convert_to='OBJECT';sep=nodes.new('ShaderNodeSeparateXYZ');test=nodes.new('ShaderNodeMath');test.operation='LESS_THAN';test.inputs[1].default_value=0;mix=nodes.new('ShaderNodeMixShader')
 links.new(geom.outputs['Incoming'],tr.inputs[0]);links.new(tr.outputs[0],sep.inputs[0]);links.new(sep.outputs['Y'],test.inputs[0]);links.new(test.outputs[0],mix.inputs[0]);links.new(opaque.outputs[0],mix.inputs[1]);links.new(clear.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],out.inputs[0]);cfg['actual_shell_profile']={'layout':cfg['layout'],'left':left,'right':right};return ns
def export_shell(dest):
 groups={};copies=[]
 for ob in list(bpy.context.scene.objects):
  if ob.type!='MESH':continue
  c=ob.copy();c.data=ob.data.copy();bpy.context.collection.objects.link(c);groups.setdefault(tuple(m.name for m in c.data.materials),[]).append(c)
 meshes=[]
 for key,obs in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for o in obs:o.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();o=bpy.context.object;o.name='FT_Runtime_'+key[0];meshes.append(o)
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
 ns=family_shell(cfg);shellstats=visual_mesh_stats();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(dest/'shell.blend'));export_shell(dest)
 for c in cfg['component_placements']:append_source(c.get('candidate_source')or c['catalogue_source'],c['label'],c['source_xyz'],c['source_yaw'])
 bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1;stats=visual_mesh_stats();(dest/'EVALUATED_GEOMETRY.json').write_text(json.dumps(evaluated(),separators=(',',':'))+'\n');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(dest/'assembly.blend'))
 rec={'actual_shell_profile':cfg['actual_shell_profile'],'prototype':key,'representative_unit':cfg['representative_unit_id'],'placements':cfg['component_placements'],'shell_stats':shellstats,'assembly_stats':stats,'files':{n:sha(dest/n)for n in['shell.blend','shell.glb','assembly.blend','EVALUATED_GEOMETRY.json']},'sealed_profile':'sealed_window_r010','operable_source_doors':['AST-DOR-001','AST-DOR-002'],'runtime_privacy_and_doors_accepted':False,'scope':'Source only Family Terrace eight-family library; no registered capacity change'}
 (dest/'SOURCE_RECEIPT.json').write_text(json.dumps(rec,indent=2)+'\n');receipts.append(rec);print('FAMILY_TERRACE_INTERIOR_SOURCE_READY',key,flush=True)
assert all(sha(p)==h for p,h in pins.items())
(OUT/'BATCH_RECEIPT.json').write_text(json.dumps({'prototypes':receipts,'retained_inputs_unchanged':pins,'units_mapped':82,'rest_slots_mapped':214,'source_build_complete':True,'Game_or_Catalogue_writes':False,'runtime_acceptance':False},indent=2)+'\n');print('FAMILY_TERRACE_INTERIOR_BATCH_COMPLETE',len(receipts),flush=True)
