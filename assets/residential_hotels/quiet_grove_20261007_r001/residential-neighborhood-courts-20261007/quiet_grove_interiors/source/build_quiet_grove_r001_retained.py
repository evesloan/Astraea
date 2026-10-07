"""Source-only eight-recipe Quiet Grove authoring. Blender -b -t 2 --python FILE."""
from pathlib import Path
import bpy,bmesh,json,math,hashlib,ast,types,importlib.util,sys
from mathutils import Vector,Matrix
HERE=Path(__file__).resolve().parents[1];W=HERE.parents[1]
ROOT=W/'residential-batch-neighborhood-20261006/scale_domestic_r011'
CAT=next(q for q in Path(__file__).resolve().parents if (q/'catalogue_manifest.json').is_file())
args=types.SimpleNamespace(domestic=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=ROOT/'source/build_family.py';tree=ast.parse(base.read_text())
# Execute only reusable definitions, never the retained command line/output loop.
for node in tree.body:
 if isinstance(node,ast.FunctionDef):exec(compile(ast.Module(body=[node],type_ignores=[]),str(base),'exec'),globals())
plan_path=HERE/'QUIET_GROVE_83_PLACEMENT_MAP.json';plan=json.loads(plan_path.read_text())
OUT=HERE/'outputs/source_r001';assert not OUT.exists(),'Use a fresh source revision'
OUT.mkdir()
protected=[base,ROOT/'PROTOTYPE_PLAN.json',ROOT/'RESIDENTIAL_500_CURRENT_APPLICATION.json',ROOT/'assemblies/GODOT_BATCH_INSTANCE_MAP.json',HERE.parent/'outputs/sf_house_r002/PLAN.json']
pins={str(p):sha(p) for p in protected}

def drop(prefixes):
 for o in list(bpy.context.scene.objects):
  if any(o.name.startswith(p) for p in prefixes):bpy.data.objects.remove(o,do_unlink=True)

def qg_shell(cfg):
 shellcfg=dict(cfg);shellcfg.update(historical_class='standard',view_lounge_replan=False,family_sleep_bay_privacy=False)
 ns=author_shell(shellcfg)
 # Retain curved perimeter walls/main ceiling, wet enclosure, finite sealed
 # aperture and real entry/kitchen interfaces. Recompose internal furniture zones.
 drop(['SUI_LivingCase','SUI_SleepThresholdWing','SUI_ThresholdTimberCap','SUI_SleepingValance','SUI_Writing','SUI_LoungeCarpet','SUI_TwinRetreat','SUI_RetreatVault','SUI_BedSconce','DATUM_bed_light_','DATUM_bed_table_','DATUM_writing_chair'])
 ex,wall,mesh,datum=[ns[k] for k in ('extrusion','wall','mesh','datum')]
 h=cfg['quiet_grove_handing'];design=cfg['quiet_grove_design']
 def poly(name,points,lo,hi,role):return ex(name,[(h*x,y)for x,y in points],lo,hi,role)
 def line(name,a,b,lo,hi,role,width=.12):return wall(name,(h*a[0],a[1]),(h*b[0],b[1]),lo,hi,hi,role,width)
 # Fixed wet-room geometry permits a useful wide right-hand arrival turn. This
 # acoustic return protects sleeping even with the entry door open.
 wall('QG_AcousticEntryReturn',(-.64,4.28),(.36,4.28),0,2.32,2.32,'oatmeal_weave',.14)
 wall('QG_EntryReturnTimberCap',(-.64,4.28),(.36,4.28),2.32,2.40,2.40,'warm_walnut',.18)
 ex('QG_EntryQuietSoffit',[(-.62,3.44),(2.35,3.44),(2.55,3.83),(1.9,4.65),(.5,4.65),(-.62,4.1)],2.65,2.77,'oatmeal_weave')
 ex('QG_EntryDropShelf',[(1.85,2.95),(2.43,2.95),(2.43,3.37),(1.85,3.37)],.76,.82,'warm_walnut')
 datum('qg_entry_turn',(1.10,4.28,0));datum('qg_kitchen_work',(1.90,1.60,0))
 # Useful separate luggage/book joinery. Open shelves have real depth, backing,
 # ends and top, not a solid furniture proxy or a label on an empty wall.
 if design=='staggered_side':x0,x1,y0,y1=2.80,3.30,8.20,9.62
 else:x0,x1,y0,y1=2.85,3.32,8.86,9.77
 poly('QG_StoragePlinth',[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],0,.16,'warm_walnut')
 poly('QG_StorageBack',[(x1-.055,y0),(x1,y0),(x1,y1),(x1-.055,y1)],.16,2.12,'warm_walnut')
 for j,y in enumerate([y0,y1-.065]):poly('QG_StorageEnd_'+str(j),[(x0,y),(x1,y),(x1,y+.065),(x0,y+.065)],.16,2.12,'warm_walnut')
 for j,z in enumerate([.67,1.17,1.62,2.12]):poly('QG_StorageShelf_'+str(j),[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z,z+.06,'warm_walnut')
 for j in range(3):poly('QG_StoredBook_'+str(j),[(x0+.09,y0+.2+j*.16),(x1-.08,y0+.2+j*.16),(x1-.08,y0+.3+j*.16),(x0+.09,y0+.3+j*.16)],1.23,1.52+.035*j,'teal_weave')
 if design=='staggered_side':
  line('QG_BetweenRestAcousticReturn',(-3.07,7.31),(-.48,7.31),0,1.62,'oatmeal_weave',.13)
  line('QG_RestReturnTimberCap',(-3.07,7.31),(-.48,7.31),1.62,1.69,'warm_walnut',.17)
  canopy_ranges=[(-2.78,-.28,5.02,6.60),(-3.26,-.50,8.04,9.57)]
  if cfg['historical_class']=='family':
   line('QG_ThirdRestShoulder',(1.14,7.94),(2.98,7.94),0,1.50,'oatmeal_weave',.12)
   canopy_ranges.append((1.0,2.95,5.18,7.94))
 else:
  # Offset low shoulders produce different sleeping approaches; they do not
  # create luxury bedrooms or obstruct the central circulation band.
  line('QG_LeftSleepShoulder',(-2.78,7.57),(-1.17,7.57),0,1.60,'oatmeal_weave',.12)
  line('QG_RightSleepShoulder',(1.12,5.63),(2.98,5.63),0,1.48,'oatmeal_weave',.12)
  canopy_ranges=[(-2.70,-1.02,4.70,7.51),(1.04,2.97,5.71,8.39)]
  if cfg['historical_class']=='family':
   line('QG_ThirdRestShoulder',(-3.25,8.49),(-.59,8.49),0,1.55,'oatmeal_weave',.12)
   canopy_ranges.append((-3.28,-.52,8.85,10.36))
 # New segmented retreat canopies sit below, and never replace, the retained
 # continuously rising curved main ceiling/walnut crowns.
 for j,(a,b,y0,y1) in enumerate(canopy_ranges):
  mid=(a+b)/2;sections=[(a,2.55),(mid,2.75),(b,2.65)]
  for k,(u,v) in enumerate(zip(sections,sections[1:])):
   q=[(h*u[0],y0,u[1]),(h*v[0],y0,v[1]),(h*v[0],y1,v[1]),(h*u[0],y1,u[1])]
   mesh('QG_RetreatCanopy_%s_%s'%(j,k),q+[(x,y,z+.075)for x,y,z in q],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'oatmeal_weave')
 # Window living is related to the actual assigned outer court or inner planted
 # garden in the full house. Nothing is represented as a hull/space aperture.
 poly('QG_WindowReadingRug',[(-3.21,10.47),(-.42,10.47),(.18,10.01),(3.25,10.01),(3.25,12.58),(-3.21,12.58)],.013,.020,'teal_weave')
 poly('QG_WindowReadingLedge',[(-3.20,11.10),(-2.70,11.10),(-2.70,12.29),(-3.20,12.29)],.73,.79,'warm_walnut')
 for y in [11.18,12.18]:poly('QG_WindowLedgeSupport_'+str(y),[(-3.14,y),(-2.78,y),(-2.78,y+.065),(-3.14,y+.065)],0,.73,'champagne_metal')
 for i,a in enumerate(cfg['bed_anchors']):
  x,y,z=a['source_xyz'];yaw=a['source_yaw'];head=Vector((x,y,0))+Matrix.Rotation(yaw,3,'Z')@Vector((0,1.3,0))
  # Narrow source light held just outside support volume, below its canopy.
  ex('QG_BedTaskLens_'+str(i),[(head.x-.1,head.y-.065),(head.x+.1,head.y-.065),(head.x+.1,head.y+.065),(head.x-.1,head.y+.065)],1.76,1.91,'lens')
  datum('qg_bed_task_'+str(i),(head.x,head.y,1.73))
 datum('qg_window_sitting',(h*1.7,11.42,0));datum('qg_window_reading',(-h*1.05,11.65,0))
 return ns

def export_shell(dest):
 scene=bpy.context.scene;groups={};copies=[]
 for ob in list(scene.objects):
  if ob.type!='MESH':continue
  c=ob.copy();c.data=ob.data.copy();bpy.context.collection.objects.link(c);copies.append(c);groups.setdefault(tuple(m.name for m in c.data.materials),[]).append(c)
 meshes=[]
 for k,obs in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for o in obs:o.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();ob=bpy.context.object;ob.name='QG_Runtime_'+k[0];meshes.append(ob)
 bpy.ops.object.select_all(action='DESELECT')
 for ob in meshes:ob.select_set(True)
 for ob in scene.objects:
  if ob.type=='EMPTY':ob.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(dest/'shell.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
 for ob in meshes:bpy.data.objects.remove(ob,do_unlink=True)

def evaluated_objects():
 deps=bpy.context.evaluated_depsgraph_get();out=[]
 for ob in bpy.context.scene.objects:
  if ob.type not in ['MESH','CURVE']:continue
  ev=ob.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();verts=[tuple(ob.matrix_world@v.co)for v in me.vertices];tris=[list(t.vertices)for t in me.loop_triangles]
  out.append({'name':ob.name,'assembly_member':ob.get('assembly_member',''),'source_asset':ob.get('source_asset',''),'bounds':[list(map(min,zip(*verts))),list(map(max,zip(*verts)))],'vertices':verts,'triangles':tris})
  ev.to_mesh_clear()
 return out
receipts=[]
for cfg in plan['prototypes']:
 key=cfg['address'];dest=OUT/key;dest.mkdir();bpy.ops.wm.read_factory_settings(use_empty=True);ns=qg_shell(cfg)
 shell_stats=visual_mesh_stats();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(dest/'shell.blend'));export_shell(dest)
 for c in cfg['component_placements']:append_source(c.get('candidate_source') or c['catalogue_source'],c['label'],c['source_xyz'],c['source_yaw'])
 bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
 stats=visual_mesh_stats();objects=evaluated_objects()
 (dest/'EVALUATED_GEOMETRY.json').write_text(json.dumps(objects,separators=(',',':'))+'\n')
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(dest/'assembly.blend'))
 rec={'prototype':key,'representative_unit':cfg['representative_unit_id'],'representative_source_index':cfg['representative_source_index'],'placements':cfg['component_placements'],'shell_stats':shell_stats,'assembly_stats':stats,'files':{n:sha(dest/n)for n in ['shell.blend','shell.glb','assembly.blend','EVALUATED_GEOMETRY.json']},'sealed_profile':'sealed_window_r010','privacy_runtime_accepted':False,'main_ceiling_curves_retained':True,'operable_source_doors':['AST-DOR-001','AST-DOR-002'],'runtime_door_tested':False,'scope':'Source prototype for explicit 83-unit family mapping; not registry or Game adoption'}
 (dest/'SOURCE_RECEIPT.json').write_text(json.dumps(rec,indent=2)+'\n');receipts.append(rec);print('QUIET_GROVE_SOURCE_COMPLETE',key,flush=True)
assert all(sha(p)==s for p,s in pins.items())
(OUT/'BATCH_RECEIPT.json').write_text(json.dumps({'prototypes':receipts,'retained_inputs_unchanged':pins,'units_mapped':83,'rest_slots_mapped':215,'source_build_complete':True,'runtime_acceptance':False,'Game_or_Catalogue_writes':False},indent=2)+'\n')
print('QUIET_GROVE_BATCH_COMPLETE',len(receipts),flush=True)
