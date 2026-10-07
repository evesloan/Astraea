"""Author eight Star Atlas room sources. Blender only after parent slot coordination."""
from pathlib import Path
import bpy,bmesh,json,math,hashlib,ast,types,importlib.util,sys
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];W=R.parents[1];ROOT=W/'residential-batch-neighborhood-20261006/scale_domestic_r011';CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
args=types.SimpleNamespace(domestic=True);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=ROOT/'source/build_family.py'
for node in ast.parse(base.read_text()).body:
 if isinstance(node,ast.FunctionDef):exec(compile(ast.Module(body=[node],type_ignores=[]),str(base),'exec'),globals())
plan=json.loads((R/'STAR_ATLAS_85_PLACEMENT_MAP.json').read_text());OUT=R/'outputs/source_r002';assert not OUT.exists(),'Fresh revision required';OUT.mkdir(parents=True)
pins={str(p):sha(p)for p in[base,ROOT/'assemblies/GODOT_BATCH_INSTANCE_MAP.json',ROOT/'RESIDENTIAL_500_CURRENT_APPLICATION.json',ROOT/'qa/EXPLICIT_1296_ANCHOR_BINDINGS.json',R/'STAR_ATLAS_85_PLACEMENT_MAP.json']};pins.update(json.loads((R/'qa/REFERENCE_INSPECTION.json').read_text())['owners_read_and_protected'])
def drop(prefixes):
 for o in list(bpy.context.scene.objects):
  if any(o.name.startswith(p)for p in prefixes):bpy.data.objects.remove(o,do_unlink=True)
def atlas_shell(cfg):
 cc=dict(cfg);cc.update(historical_class='standard',view_lounge_replan=False,family_sleep_bay_privacy=False);ns=author_shell(cc)
 # Reuse retained shell/interfaces; author all lived room joinery/composition.
 drop(['SUI_LivingCase','SUI_SleepThresholdWing','SUI_ThresholdTimberCap','SUI_SleepingValance','SUI_Writing','SUI_LoungeCarpet','SUI_BedSconce','DATUM_bed_light_','DATUM_bed_table_','DATUM_writing_chair','SUI_AcousticLiving','SUI_Gallery','SUI_LibraryShelf','SUI_Gathering'])
 ex,wall,mesh,datum=[ns[k]for k in['extrusion','wall','mesh','datum']];h=cfg['star_atlas_handing'];design=cfg['star_atlas_design'];family=cfg['historical_class']=='family'
 def poly(name,p,lo,hi,role):return ex(name,[(h*x,y)for x,y in p],lo,hi,role)
 def rect(name,x0,x1,y0,y1,lo,hi,role):return poly(name,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],lo,hi,role)
 def line(name,a,b,lo,hi,role,width=.12):return wall(name,(h*a[0],a[1]),(h*b[0],b[1]),lo,hi,hi,role,width)
 def shelf(name,x0,x1,y0,y1,top=2.12):
  rect(name+'_Plinth',x0,x1,y0,y1,0,.12,'warm_walnut');rect(name+'_Back',x1-.065 if x0+x1>0 else x0,x1 if x0+x1>0 else x0+.065,y0,y1,.12,top,'warm_walnut')
  for j,y in enumerate([y0,y1-.055]):rect(name+'_End_'+str(j),x0,x1,y,y+.055,.12,top,'warm_walnut')
  for j,z in enumerate([.42,.86,1.31,1.76,top-.055]):rect(name+'_Shelf_'+str(j),x0,x1,y0,y1,z,z+.055,'warm_walnut')
  for j in range(max(2,int((y1-y0-.18)/.14))):
   y=y0+.1+j*.14
   rect(name+'_Book_'+str(j),x0+.09,x1-.09,y,y+.082,.915,1.19+.045*(j%3),'teal_weave'if j%3 else'clay_weave')
  # No opaque proxy fronts: the real open shelf and luggage space remain visible.
 # A common narrow arrival dogleg belongs to the bathroom backing, leaving the
 # existing entrance and bathroom moving components byte-for-byte source imports.
 wall('SA_ArrivalBookEnd',(-.64,3.99),(-.64,4.26),0,2.48,2.48,'warm_walnut',.13)
 ex('SA_ArrivalDropTray',[(1.92,3.22),(2.39,3.22),(2.45,3.49),(2.20,3.67),(1.92,3.61)],.78,.85,'warm_walnut')
 # Domestic reading canopy fans from a low entry to the library edge, not a
 # decorative flat ring. It stops before the quiet sleep approaches.
 if design=='shelf_spine':
  canopy=[(-.52,3.95),(2.47,3.95),(2.59,4.60),(2.58,5.50),(2.90,6.54),(1.94,6.85),(.65,6.48),(-.23,5.97),(-.52,5.22)]
  desk=[(1.88,4.49),(2.57,4.49),(2.60,5.53),(2.39,5.80),(1.90,5.72),(1.76,5.44),(1.88,5.14)]
  poly('SA_ShapedWritingEdge',desk,.735,.80,'warm_walnut')
  for y in [4.57,5.58]:rect('SA_DeskEndSupport_'+str(y),2.03,2.49,y,y+.075,0,.736,'champagne_metal')
  shelf('SA_DeepIndexSpine',2.56,3.06,6.72,7.47,2.23)
  if not family:
   # The two-rest plan gets a real browsing alcove rather than an empty third bed.
   shelf('SA_DeepBrowseReturn',-3.24 if h==1 else -2.68,-2.66 if h==1 else -2.10,4.40,6.68,2.20)
   poly('SA_BrowseFolioLedge',[(x+(0 if h==1 else .56),y) for x,y in [(-2.67,4.77),(-2.28,4.80),(-2.12,5.35),(-2.30,5.90),(-2.67,5.90)]],.87,.94,'warm_walnut')
  else:
   # Three-rest version carries storage above its side-facing rest with a clear
   # 1.55m vertical gap above the floor and a dedicated front approach.
   rect('SA_ThirdRestHighShelf',-2.68,-.55,6.73,7.13,1.82,1.89,'warm_walnut')
   for x in [-2.63,-.60]:rect('SA_ThirdShelfUpright_'+str(x),x,x+.055,6.80,7.07,0,2.41,'warm_walnut')
  # Two separated longitudinal sleep approaches flank an unobstructed aisle.
  for side in [-1,1]:
   x0,x1=sorted([side*1.00,side*2.77]);rect('SA_SleepPortalTop_'+str(side),x0,x1,7.16,7.32,2.47,2.57,'oatmeal_weave')
   line('SA_SleepPortalSide_'+str(side),(side*2.78,7.18),(side*2.78,7.62),0,2.55,'warm_walnut',.085)
 else:
  canopy=[(-2.89 if h==1 else -2.60,4.20),(2.56,4.20),(2.57,5.29),(2.83,6.05),(1.48,6.44),(.15,6.72),(-1.60,6.63),(-2.96 if h==1 else -2.85,6.13)]
  desk=[(1.03,4.39),(2.58,4.39),(2.61,4.97),(2.29,5.28),(1.23,5.20),(.97,4.92)]
  poly('SA_AngledBrowseDesk',desk,.735,.80,'warm_walnut')
  for x in [1.18,2.45]:rect('SA_DeskEndSupport_'+str(x),x,x+.075,4.49,4.95,0,.736,'champagne_metal')
  shelf('SA_DeepBrowseWall',-3.18 if h==1 else -2.68,-2.62 if h==1 else -2.10,4.35,6.63,2.18)
  shelf('SA_ReturnIndexShelf',2.61,3.03,6.54,7.15,2.18)
  # Offset book-end screens conceal sideways sleep from the entry without
  # closing the central spine; their front thresholds differ in plan and section.
  line('SA_FirstRestBookEnd',(-2.79,6.90),(-.76,6.90),0,1.32,'warm_walnut',.14)
  line('SA_FirstRestBookCap',(-2.79,6.90),(-.76,6.90),1.32,1.39,'ivory_enamel',.21)
  line('SA_SecondRestBookEnd',(1.03,8.63),(2.98,8.63),0,1.18,'warm_walnut',.14)
  # Curved/faceted head portals preserve actual main ceiling above each pocket.
  for n,(x0,x1,y)in enumerate([(-2.90,-.26,7.04),(.31,2.99,8.81)]):
   spans=[(x0,2.32),(x0+.40,2.54),((x0+x1)/2,2.65),(x1-.4,2.54),(x1,2.32)]
   for j,(a,b)in enumerate(zip(spans,spans[1:])):
    q=[(h*a[0],y,a[1]),(h*b[0],y,b[1]),(h*b[0],y+.16,b[1]),(h*a[0],y+.16,a[1])]
    mesh('SA_CurvedRestPortal_%d_%d'%(n,j),q+[(x,y,z+.08)for x,y,z in q],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'oatmeal_weave')
 def lower(y):return 2.55+(y-3.95)*.115
 n=len(canopy);v=[(h*x,y,lower(y)+dz)for dz in [0,.11]for x,y in canopy];mesh('SA_FanningLibraryCanopy',v,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],'warm_walnut')
 # The canopy is explicitly carried back to the retained curved main ceiling.
 for j,(x,y)in enumerate([canopy[0],canopy[1],canopy[-2]]):rect('SA_CanopyRoofReturn_'+str(j),x-.035,x+.035,y-.035,y+.035,lower(y)+.11,ns['height'](y)+.025,'champagne_metal')
 poly('SA_LibraryWovenField',[(-2.52,4.25),(2.42,4.25),(2.54,5.64),(2.26,6.60),(.42,7.04),(-2.50,6.84)],.013,.021,'teal_weave')
 # Rear luggage/library furniture is outside the sealed view opening and makes
 # the outlook a real shared sitting activity, separated from sleeping.
 shelf('SA_OutlookLibrary',-3.27,-2.74,10.45,12.32,1.54)
 poly('SA_OutlookWovenField',[(-2.60,10.48),(-.70,10.30),(.70,10.30),(2.97,10.51),(3.24,12.58),(-3.23,12.58)],.013,.021,'clay_weave')
 # A tangible under-shelf task strip serves the actual reading chair.
 task=(h*2.26,5.07,2.53)if design=='shelf_spine'else(h*1.79,4.81,2.55)
 x,y,z=task;ex('SA_WriteTaskHousing',[(x-.24,y-.11),(x+.24,y-.11),(x+.24,y+.11),(x-.24,y+.11)],z,z+.08,'champagne_metal');ex('SA_WriteTaskLens',[(x-.21,y-.085),(x+.21,y-.085),(x+.21,y+.085),(x-.21,y+.085)],z-.018,z,'lens');datum('atlas_write_light',(x,y,z-.033));ex('SA_WriteTaskStem',[(x-.03,y-.03),(x+.03,y-.03),(x+.03,y+.03),(x-.03,y+.03)],z+.08,lower(y)+.11,'champagne_metal')
 for i,a in enumerate(cfg['bed_anchors']):
  x,y,z=a['source_xyz'];side=-1 if x<0 else 1;host=ns['at'](ns['left']if side<0 else ns['right'],y)
  wall('SA_BedTaskBearing_'+str(i),(host,y),(host-side*.18,y),1.63,1.95,1.95,'warm_walnut',.21)
  ex('SA_BedTaskHousing_'+str(i),[(host-side*.30,y-.12),(host-side*.15,y-.12),(host-side*.15,y+.12),(host-side*.30,y+.12)],1.68,1.91,'champagne_metal')
  ex('SA_BedTaskLens_'+str(i),[(host-side*.314,y-.09),(host-side*.30,y-.09),(host-side*.30,y+.09),(host-side*.314,y+.09)],1.72,1.87,'lens');datum('atlas_bed_light_'+str(i),(host-side*.335,y,1.79))
 datum('atlas_writing_approach',(h*.62,5.60,0));datum('atlas_outlook_approach',(h*.65,11.66,0));datum('atlas_library_approach',(-h*2.23,10.64,0))
 # Source-only directional preview; adopted runtime must reuse its project
 # shader and re-test whole room/vertical cross-court exposure for these layouts.
 m=ns['mats']['glass'];m.name='SA_SourceDirectionalPrivacy_NOT_RUNTIME_ACCEPTED';nodes=m.node_tree.nodes;nodes.clear();links=m.node_tree.links
 out=nodes.new('ShaderNodeOutputMaterial');opaque=nodes.new('ShaderNodeBsdfPrincipled');opaque.inputs['Base Color'].default_value=(.09,.13,.16,1);opaque.inputs['Metallic'].default_value=.55;opaque.inputs['Roughness'].default_value=.25;clear=nodes.new('ShaderNodeBsdfTransparent');clear.inputs[0].default_value=(1,1,1,1)
 geom=nodes.new('ShaderNodeNewGeometry');tr=nodes.new('ShaderNodeVectorTransform');tr.vector_type='VECTOR';tr.convert_from='WORLD';tr.convert_to='OBJECT';sep=nodes.new('ShaderNodeSeparateXYZ');test=nodes.new('ShaderNodeMath');test.operation='LESS_THAN';test.inputs[1].default_value=0;mix=nodes.new('ShaderNodeMixShader')
 links.new(geom.outputs['Incoming'],tr.inputs[0]);links.new(tr.outputs[0],sep.inputs[0]);links.new(sep.outputs['Y'],test.inputs[0]);links.new(test.outputs[0],mix.inputs[0]);links.new(opaque.outputs[0],mix.inputs[1]);links.new(clear.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],out.inputs[0]);return ns
# Shared engineering export/evaluated geometry utilities; no Tidal room design.
shared=R.parent/'tidal_garden_house/source/build_interiors.py'
for node in ast.parse(shared.read_text()).body:
 if isinstance(node,ast.FunctionDef)and node.name in ['export_shell','evaluated']:exec(compile(ast.unparse(ast.Module(body=[node],type_ignores=[])).replace('TG_Runtime_', 'SA_Runtime_'),str(shared),'exec'),globals())
receipts=[]
for cfg in plan['prototypes']:
 key=cfg['address'];dest=OUT/key;dest.mkdir();bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.threads_mode='FIXED';bpy.context.scene.render.threads=2;bpy.context.scene.cycles.use_denoising=False
 ns=atlas_shell(cfg);bpy.context.view_layer.update();shellstats=visual_mesh_stats();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(dest/'shell.blend'));export_shell(dest)
 for c in cfg['component_placements']:append_source(c.get('candidate_source')or c['catalogue_source'],c['label'],c['source_xyz'],c['source_yaw'])
 bpy.context.view_layer.update();datums={o.name:list(o.matrix_world.translation)for o in bpy.context.scene.objects if o.type=='EMPTY'and o.name.startswith('DATUM_')}
 fixtures=[]
 for name,pt in datums.items():
  if 'light'not in name:continue
  assert pt[2]>1.4,(name,pt)
  fixtures.append({'datum':name,'source_xyz':pt,'evaluated_z_m':pt[2],'direct_world_matrix_after_update':True})
 bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1;stats=visual_mesh_stats();(dest/'EVALUATED_GEOMETRY.json').write_text(json.dumps(evaluated(),separators=(',',':'))+'\n');(dest/'DATUMS.json').write_text(json.dumps({'datums':datums,'fixture_positions':fixtures},indent=2)+'\n');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(dest/'assembly.blend'))
 rec={'prototype':key,'representative_unit':cfg['representative_unit_id'],'placements':cfg['component_placements'],'shell_stats':shellstats,'assembly_stats':stats,'fixtures':fixtures,'files':{n:sha(dest/n)for n in['shell.blend','shell.glb','assembly.blend','EVALUATED_GEOMETRY.json','DATUMS.json']},'sealed_profile':'sealed_window_r010','operable_source_doors':['AST-DOR-001','AST-DOR-002'],'runtime_privacy_and_doors_accepted':False,'scope':'Star Atlas isolated source; full house148 remains explicit, specialty46/VIP7 and D17standard10 are separate'}
 (dest/'SOURCE_RECEIPT.json').write_text(json.dumps(rec,indent=2)+'\n');receipts.append(rec);print('STAR_ATLAS_SOURCE_READY',key,flush=True)
assert all(sha(p)==h for p,h in pins.items())
(OUT/'BATCH_RECEIPT.json').write_text(json.dumps({'prototypes':receipts,'retained_inputs_unchanged':pins,'units_mapped':85,'rest_slots_mapped':221,'source_build_complete':True,'revision':'source_r002','correction':'Actual asymmetric inner-wall containment for mirrored shelves/canopy and task housings; no rest-coordinate change','Game_or_Catalogue_writes':False,'runtime_acceptance':False},indent=2)+'\n');print('STAR_ATLAS_BATCH_COMPLETE',len(receipts),flush=True)
