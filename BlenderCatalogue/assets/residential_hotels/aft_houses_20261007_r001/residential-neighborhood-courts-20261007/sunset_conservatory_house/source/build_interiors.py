"""Sunset source library: retained engineering, purpose-authored plan and section."""
from pathlib import Path
import bpy,bmesh,json,math,hashlib,ast,types,importlib.util,sys
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];W=R.parents[1];ROOT=W/'residential-batch-neighborhood-20261006/scale_domestic_r011';CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
args=types.SimpleNamespace(domestic=True);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=ROOT/'source/build_family.py'
for node in ast.parse(base.read_text()).body:
 if isinstance(node,ast.FunctionDef):exec(compile(ast.Module(body=[node],type_ignores=[]),str(base),'exec'),globals())
plan=json.loads((R/'SUNSET_83_PLACEMENT_MAP.json').read_text());OUT=R/'outputs/interiors_r002';assert not OUT.exists(),'Preserve every prior revision';OUT.mkdir()
pins={str(p):sha(p)for p in[base,ROOT/'assemblies/GODOT_BATCH_INSTANCE_MAP.json',ROOT/'PROTOTYPE_PLAN.json',R/'SUNSET_83_PLACEMENT_MAP.json']}
def drop(prefixes):
 for o in list(bpy.context.scene.objects):
  if any(o.name.startswith(p)for p in prefixes):bpy.data.objects.remove(o,do_unlink=True)
def sunset_shell(cfg):
 cc=dict(cfg);cc.update(historical_class='standard',view_lounge_replan=False,family_sleep_bay_privacy=False);ns=author_shell(cc)
 # Keep the source finite window, enclosed bath, operable door fittings, kitchen,
 # fixed floor and identity datums. Replace the living form and roof completely.
 drop(['SUI_LivingCase','SUI_SleepThresholdWing','SUI_ThresholdTimberCap','SUI_SleepingValance','SUI_Writing','SUI_LoungeCarpet','SUI_BedSconce','DATUM_bed_light_','DATUM_bed_table_','DATUM_writing_chair','SUI_AcousticLiving','SUI_Base_','SUI_Wall_','SUI_Crown_','SUI_TimberWainscot_','SUI_Ceiling_','SUI_FittedCarpet','SUI_CarpetBinding','SUI_RecessedFixture_','SUI_OpalLens_'])
 ex,wall,mesh,datum=[ns[k]for k in['extrusion','wall','mesh','datum']];h=cfg['sunset_handing'];design=cfg['sunset_design'];family=cfg['historical_class']=='family'
 def poly(name,p,lo,hi,role):return ex(name,[(h*x,y)for x,y in p],lo,hi,role)
 def line(name,a,b,lo,hi,role,width=.12):return wall(name,(h*a[0],a[1]),(h*b[0],b[1]),lo,hi,hi,role,width)
 # The shaped enclosure now shoulders the writing threshold then widens to a
 # full salon front. The rear three metres are an inhabitable gathering space.
 left=[(-3.50,.12),(-3.50,4.12),(-3.37,4.8),(-3.37,9.42),(-3.50,10.12),(-3.50,12.75)]
 right=[(3.50,.12),(3.50,3.1),(3.25,3.85),(3.25,5.20),(3.40,5.70),(3.40,9.4),(3.50,10.12),(3.50,12.75)]
 def at(path,y):
  for a,b in zip(path,path[1:]):
   if a[1]<=y<=b[1]:return a[0]+(b[0]-a[0])*(y-a[1])/(b[1]-a[1])
  return path[-1][0]
 def edgeheight(y):return 2.95+.55*max(0,min(1,(y-3.8)/8.95))
 for side,path in [('L',left),('R',right)]:
  for i,(a,b)in enumerate(zip(path,path[1:])):
   ha,hb=edgeheight(a[1]),edgeheight(b[1]);wall(f'SC_Enclosure_{side}{i}',a,b,0,ha,hb,'ivory_enamel',.12)
   wall(f'SC_TimberDado_{side}{i}',a,b,.08,.84,.84,'warm_walnut',.145)
   wall(f'SC_SoffitBearing_{side}{i}',a,b,ha-.07,ha+.08,hb+.08,'warm_walnut',.20)
 carpet=[(-.55,1.4),(2.45,1.4),(2.45,2.7),(3.15,3.85),(3.15,5.2),(3.30,5.70),(3.30,9.4),(3.40,10.12),(3.40,12.64),(-3.40,12.64),(-3.40,10.12),(-3.27,9.42),(-3.27,4.8),(-3.40,4.12),(-.55,4.12)]
 ex('SC_DomesticWovenField',carpet,.001,.012,'oatmeal_weave')
 # Continuous curved ceiling has a deliberately low writing threshold and
 # rising ribbed barrel across the salon, with actual attached timber ribs.
 ys=[.12,3.85,5.4,7.7,9.85,11.4,12.75];fractions=[0,.16,.34,.5,.66,.84,1]
 def roofpt(y,t):
  x=at(left,y)+(at(right,y)-at(left,y))*t
  crown=(.07 if y<3.9 else .32 if y<9.8 else .39)*math.sin(math.pi*t)
  return (x,y,edgeheight(y)+crown)
 for i,(ya,yb)in enumerate(zip(ys,ys[1:])):
  for j,(a,b)in enumerate(zip(fractions,fractions[1:])):
   q=[roofpt(ya,a),roofpt(ya,b),roofpt(yb,b),roofpt(yb,a)]
   mesh(f'SC_CurvedRoof_{i}_{j}',q+[(x,y,z+.14)for x,y,z in q],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'ivory_enamel')
 for i,y in enumerate([3.86,5.40,7.70,9.86,10.75,11.63,12.54]):
  for j,(a,b)in enumerate(zip(fractions,fractions[1:])):
   aa,bb=roofpt(y,a),roofpt(y,b);q=[(aa[0],y-.09,aa[2]-.06),(bb[0],y-.09,bb[2]-.06),(bb[0],y+.09,bb[2]-.06),(aa[0],y+.09,aa[2]-.06)]
   mesh(f'SC_SalonTimberRib_{i}_{j}',q+[(x,y,z+.10)for x,y,z in q],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'warm_walnut')
 # Recessed writing niche is part of the fixed asymmetric domestic threshold.
 desk=[(2.00,3.94),(3.16,3.94),(3.16,5.17),(2.18,5.17),(1.96,4.97)]
 ex('SC_RecessedWritingTop',desk,.74,.80,'warm_walnut')
 for y in[4.05,5.04]:ex('SC_WritingUpright_'+str(y),[(2.14,y),(3.11,y),(3.11,y+.07),(2.14,y+.07)],0,.74,'warm_walnut')
 for z in[1.35,1.78]:ex('SC_RecessedWritingShelf_'+str(z),[(2.84,3.98),(3.16,3.98),(3.16,5.14),(2.84,5.14)],z,z+.06,'warm_walnut')
 for j in range(5):ex('SC_WritingBook_'+str(j),[(2.89,4.10+j*.13),(3.12,4.10+j*.13),(3.12,4.17+j*.13),(2.89,4.17+j*.13)],1.41,1.64+.015*j,'clay_weave'if j%2 else'teal_weave')
 # Each sleep slot has an independent open approach from the centre. These
 # alcove walls and shaped overhead lips separate rest from the broad salon.
 screen_y=[7.34,9.61]if design=='fanned_front'else[8.27]
 for j,y in enumerate(screen_y):
  host=at(left if h==1 else right,y)+h*.055
  wall('SC_QuietAlcoveWall_'+str(j),(host,y),(-h*.88,y),0,1.90,1.90,'ivory_enamel',.13)
  wall('SC_QuietAlcoveCap_'+str(j),(host,y),(-h*.88,y),1.90,1.96,1.96,'warm_walnut',.18)
 if family and design=='fanned_front':
  host=at(right if h==1 else left,8.30)-h*.055
  wall('SC_ThirdAlcoveReturn',(host,8.30),(h*.90,8.30),0,1.90,1.90,'ivory_enamel',.13)
  wall('SC_ThirdAlcoveCap',(host,8.30),(h*.90,8.30),1.90,1.96,1.96,'warm_walnut',.18)
 # True shared luggage volume with open cubbies, outside the walking path.
 storage_y=(8.75,9.74)if design=='fanned_front'else(8.63,9.63)
 a,b=storage_y
 poly('SC_SharedLuggagePlinth',[(2.70,a),(3.28,a),(3.28,b),(2.70,b)],0,.12,'warm_walnut')
 poly('SC_SharedLuggageBack',[(3.22,a),(3.28,a),(3.28,b),(3.22,b)],.12,1.75,'warm_walnut')
 for yy in[a,b-.06]:poly('SC_LuggageEnd_'+str(yy),[(2.70,yy),(3.28,yy),(3.28,yy+.06),(2.70,yy+.06)],.12,1.75,'warm_walnut')
 for z in[.49,1.06,1.69]:poly('SC_LuggageShelf_'+str(z),[(2.70,a),(3.26,a),(3.26,b),(2.70,b)],z,z+.06,'warm_walnut')
 # Fanned floor pattern follows the actual conversation group and long view.
 poly('SC_FannedSalonRug',[(-3.27,10.07),(-1.10,10.04),(.25,9.95),(2.64,9.88),(3.30,10.16),(3.38,12.59),(-3.38,12.59)],.013,.020,'clay_weave')
 for k in range(3):
  y=10.18+k*.31
  line('SC_FanRugBinding_'+str(k),(-2.91,y),(2.87,y+.45),.020,.024,'oatmeal_weave',.045)
 for i,a in enumerate(cfg['bed_anchors']):
  x,y,z=a['source_xyz'];side=-1 if x<0 else 1;host=at(left if side<0 else right,y)
  wall('SC_BedTaskBearing_'+str(i),(host,y),(host-side*.13,y),1.55,1.90,1.90,'warm_walnut',.24)
  ex('SC_BedTaskHousing_'+str(i),[(host-side*.22,y-.15),(host-side*.06,y-.15),(host-side*.06,y+.15),(host-side*.22,y+.15)],1.58,1.86,'champagne_metal')
  ex('SC_BedTaskLens_'+str(i),[(host-side*.235,y-.11),(host-side*.22,y-.11),(host-side*.22,y+.11),(host-side*.235,y+.11)],1.62,1.82,'lens');datum('sunset_bed_light_'+str(i),(host-side*.25,y,1.73))
 for i,(x,y)in enumerate([(1.20,2.65),(.35,4.40),(0,7.65),(0,10.72)]):
  z=roofpt(y,(x-at(left,y))/(at(right,y)-at(left,y)))[2]-.04
  ex('SC_CeilingFixture_'+str(i),[(x-.23,y-.14),(x+.23,y-.14),(x+.23,y+.14),(x-.23,y+.14)],z-.16,z+.05,'champagne_metal')
  ex('SC_CeilingLens_'+str(i),[(x-.20,y-.11),(x+.20,y-.11),(x+.20,y+.11),(x-.20,y+.11)],z-.18,z-.16,'lens');datum('sunset_room_light_'+str(i),(x,y,z-.19))
 datum('sunset_salon_approach',(-h*.90,10.63,0));datum('sunset_writing_approach',(.53,4.56,0))
 # Camera-direction source shader, explicitly NOT a runtime privacy pass.
 m=ns['mats']['glass'];m.name='SC_SourceDirectionalPrivacy_NOT_RUNTIME_ACCEPTED';nodes=m.node_tree.nodes;nodes.clear();links=m.node_tree.links
 out=nodes.new('ShaderNodeOutputMaterial');opaque=nodes.new('ShaderNodeBsdfPrincipled');opaque.inputs['Base Color'].default_value=(.14,.10,.075,1);opaque.inputs['Metallic'].default_value=.62;opaque.inputs['Roughness'].default_value=.20;clear=nodes.new('ShaderNodeBsdfTransparent');clear.inputs[0].default_value=(1,1,1,1)
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
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();o=bpy.context.object;o.name='SC_Runtime_'+key[0];meshes.append(o)
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
 ns=sunset_shell(cfg);shellstats=visual_mesh_stats();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(dest/'shell.blend'));export_shell(dest)
 for c in cfg['component_placements']:append_source(c.get('candidate_source')or c['catalogue_source'],c['label'],c['source_xyz'],c['source_yaw'])
 bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1;stats=visual_mesh_stats();(dest/'EVALUATED_GEOMETRY.json').write_text(json.dumps(evaluated(),separators=(',',':'))+'\n');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(dest/'assembly.blend'))
 rec={'prototype':key,'representative_unit':cfg['representative_unit_id'],'placements':cfg['component_placements'],'shell_stats':shellstats,'assembly_stats':stats,'files':{n:sha(dest/n)for n in['shell.blend','shell.glb','assembly.blend','EVALUATED_GEOMETRY.json']},'sealed_profile':'sealed_window_r010','operable_source_doors':['AST-DOR-001','AST-DOR-002'],'runtime_privacy_and_doors_accepted':False,'scope':'Source only Sunset eight-family library; no registered capacity change'}
 (dest/'SOURCE_RECEIPT.json').write_text(json.dumps(rec,indent=2)+'\n');receipts.append(rec);print('SUNSET_INTERIOR_SOURCE_READY',key,flush=True)
assert all(sha(p)==h for p,h in pins.items())
(OUT/'BATCH_RECEIPT.json').write_text(json.dumps({'prototypes':receipts,'retained_inputs_unchanged':pins,'units_mapped':83,'rest_slots_mapped':215,'source_build_complete':True,'Game_or_Catalogue_writes':False,'runtime_acceptance':False},indent=2)+'\n');print('SUNSET_INTERIOR_BATCH_COMPLETE',len(receipts),flush=True)
