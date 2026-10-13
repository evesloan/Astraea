"""Immutable r003: recognizable textile/repair equipment and finished retained staff room."""
from pathlib import Path
import bpy,json,hashlib,importlib.util,shutil,math
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2];CAT=P.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
definition=ROOT/'Game/data/architecture/group5/THREAD_STOCK_REPAIR.json';j=json.loads(definition.read_text())
assert j['native'].endswith('thread_stock_repair_r002.blend'),'Selected revision must be r002;never rewrite a successor'
old=ROOT/j['native'];old_glb=ROOT/j['model_path'].replace('res://','Game/');pins={str(p):sha(p) for p in [old,old_glb,ROOT/j['original_native'],ROOT/j['original_model'].replace('res://','Game/')]}
native=P/'source/thread_stock/thread_stock_repair_r003.blend';export=P/'exports/thread_stock/thread_stock_repair_r003.glb'
assert not native.exists() and not export.exists(),'Immutable successor already exists;inspect before continuing'
bpy.ops.wm.open_mainfile(filepath=str(old));root=next(o for o in bpy.context.scene.objects if o.parent is None and o.type=='EMPTY');root.name='GROUP5_THREAD_CONSTRUCTION_R003'
kept={o.name:tuple(tuple(r) for r in o.matrix_world) for o in bpy.context.scene.objects if o.type=='MESH' and '_generic_fold_' not in o.name and '_fixture_' not in o.name}
for o in list(bpy.context.scene.objects):
    if '_generic_fold_' in o.name or '_fixture_' in o.name:bpy.data.objects.remove(o,do_unlink=True)
F=load('forms',P/'source/construction_form_helpers.py').Forms(load('palette',CAT/'standards/retail_materials.py').materials(),root,(8,52.5,-216))
supports=[];form_counts={'folded_cloth_stacks':0,'fabric_bolts':0,'thread_spools':0,'repair_tools':0,'open_sorting_bins':0}
for i,row in enumerate(j['generic_support_contacts']):
    name=row['mesh'];x,y,z=row['world_contact_xyz'];module=name.split('_')[0]
    if module=='RepairReturn':
        F.folded(name,42.08,42.52,y,z-.30,z+.30,'teal_weave',1);form_counts['folded_cloth_stacks']+=1
    elif i%3==1:
        radius=.15;F.cylinder(name,(42.34,y+radius,z),radius,.53,0,['clay_weave','teal_weave','oatmeal_weave'][i%3])
        F.cylinder(name+'_paper_core',(42.045,y+radius,z),.044,.035,0,'warm_walnut')
        F.torus(name+'_rolled_edge',(42.070,y+radius,z),.132,.006,0,'oatmeal_weave')
        F.box(name+'_paper_band',(42.23,y+.035,z-.025),(42.32,y+.265,z+.025),'ivory_enamel',.004);form_counts['fabric_bolts']+=1
    else:
        F.folded(name,42.025,42.665,y,z-.49,z+.49,['clay_weave','teal_weave','oatmeal_weave'][i%3]);form_counts['folded_cloth_stacks']+=1
    supports.append(row)
# Open bins on the reserve top shelf: rims, contrasting contents and visible open mouths.
for i,z in enumerate([-206.7,-204.15,-201.6]):
    y=54.975;prefix='Reserve_OpenNotionsBin_'+str(i)
    F.box(prefix+'_base',(42.04,y,z-.43),(42.68,y+.025,z+.43),'ivory_enamel',.01)
    for a,b in [((42.04,y+.025,z-.43),(42.68,y+.24,z-.405)),((42.04,y+.025,z+.405),(42.68,y+.24,z+.43)),((42.655,y+.025,z-.405),(42.68,y+.24,z+.405)),((42.04,y+.025,z-.405),(42.065,y+.10,z+.405))]:F.box(prefix+'_rim_'+str(a),a,b,'retail_terracotta_enamel',.005)
    for k in range(3):F.spool(prefix+'_spool_'+str(k),42.35,y+.025,z-.22+k*.22,['teal_weave','clay_weave','oatmeal_weave'][k]);form_counts['thread_spools']+=1
    form_counts['open_sorting_bins']+=1
# Usable, visible repair bench: spools on the lower tool shelf, measuring rule and scissors.
for i,z in enumerate([-213.8,-213.4,-213.0,-212.6]):
    F.spool('Repair_ThreadSpool_'+str(i),42.49,54.125,z,['teal_weave','clay_weave','oatmeal_weave','clay_weave'][i],.09,.22);form_counts['thread_spools']+=1
F.box('Repair_MetricRule',(41.79,53.393,-213.93),(42.64,53.408,-213.87),'champagne_metal')
for i in range(17):F.box('Repair_RuleGraduation_'+str(i),(41.80+i*.048,53.408,-213.93),(41.803+i*.048,53.412,-213.90),'dark_rubber')
for k,z in enumerate([-212.48,-212.28]):F.torus('Repair_ScissorHandle_'+str(k),(41.99,53.403,z),.075,.018,1,'champagne_metal')
F.beam('Repair_ScissorBlade_A',(42.07,53.406,-212.42),(42.43,53.406,-212.13),.018,'champagne_metal',4)
F.beam('Repair_ScissorBlade_B',(42.07,53.406,-212.34),(42.43,53.406,-212.57),.018,'champagne_metal',4)
F.cylinder('Repair_ScissorPivot',(42.12,53.421,-212.38),.029,.016,1,'dark_rubber')
F.cylinder('Repair_TapeMeasureRoll',(42.40,53.447,-211.75),.105,.11,1,'oatmeal_weave')
F.box('Repair_UnrolledMeasure',(41.88,53.392,-211.80),(42.4,53.400,-211.74),'oatmeal_weave');form_counts['repair_tools']=4
# Long suspended diffusers belong to each fitted station; two ceiling ties per run.
j['fixtures']=[];j['ceiling_mount_names']=[]
for mod in j['modules']:
    name=mod['name'];z=sum(p[1] for p in mod['world_xz'])/2;half=1.05 if name=='RepairReturn' else 2.25
    for k,dz in enumerate([-half+.25,half-.25]):
        n=name+'_fixture_stem' if k==0 else name+'_fixture_stem_secondary';F.box(n,(41.405,55.71,z+dz-.035),(41.465,56.205,z+dz+.035),'champagne_metal');j['ceiling_mount_names'].append(n)
    F.box(name+'_fixture_housing',(41.12,55.63,z-half),(41.75,55.76,z+half),'ivory_enamel',.025)
    F.box(name+'_fixture_lens',(41.17,55.612,z-half+.07),(41.70,55.630,z+half-.07),'ivory_enamel')
    F.box(name+'_fixture_edge',(41.10,55.65,z-half),(41.13,55.71,z+half),'champagne_metal')
    j['fixtures'].append({'name':name+'_TaskLight','lens':name+'_fixture_lens','mount':name+'_fixture_stem','world_xyz':[41.435,55.592,z],'range_m':6,'energy':.85,'color':[1,.95,.84],'mount_type':'ceiling'})
# Linear under-shelf task light illuminates the repair surface without a hanging box.
F.box('Repair_BenchLight_housing',(42.19,54.00,-213.85),(42.73,54.045,-211.55),'champagne_metal')
F.box('Repair_BenchLight_lens',(42.22,53.982,-213.80),(42.68,54.0,-211.6),'ivory_enamel')
F.box('Repair_BenchLight_wall_mount',(42.80,54.01,-212.76),(42.935,54.08,-212.64),'champagne_metal')
j['wall_mount_names'].append('Repair_BenchLight_wall_mount')
j['fixtures'].append({'name':'RepairBenchTaskLight','lens':'Repair_BenchLight_lens','mount':'Repair_BenchLight_wall_mount','world_xyz':[42.45,53.962,-212.7],'range_m':3,'energy':.45,'color':[1,.95,.84],'mount_type':'wall'})
# Finish the existing service enclosure. Applied finishes are visual only; original physics remains.
floor_path=ROOT/'Game/data/generated/structural_meshes.json';floor=next(r for r in json.loads(floor_path.read_text())['regions'] if r['id']=='D09_thread_shell_floor')
region=[]
for tri in floor['triangles']:
    if all(x>=37-.00001 and z<=-197+.00001 for x,z in tri):region.append(tri)
verts=[];faces=[]
for tri in region:
    k=len(verts);verts.extend([(x,52.5006,z) for x,z in tri]);faces.append((k,k+1,k+2))
F.mesh('Group5VisualFinish_ThreadStoneFloor',verts,faces,'warm_stone')
F.box('Group5VisualFinish_ThreadCeiling',(37.10,56.196,-233.90),(42.90,56.198,-197.10),'ivory_enamel')
for side,x0,x1 in [('West',37.094,37.12),('East',42.88,42.905)]:
    for a,b in [(-233.9,-216.80),(-214.20,-197.1)]:
        F.box('Group5VisualFinish_'+side+'Wall_'+str(a),(x0,52.66,a),(x1,55.96,b),'ivory_enamel')
        F.box(side+'_Skirting_'+str(a),(x0,52.501,a),(x1+.035,52.66,b),'warm_walnut')
        F.box(side+'_CeilingCove_'+str(a),(x0,55.96,a),(x1+.06,56.17,b),'warm_walnut')
        F.box(side+'_CoveReveal_'+str(a),(x0,56.17,a),(x1+.02,56.193,b),'champagne_metal')
        for z in [a+(b-a)*i/6 for i in range(1,6)]:F.box('Group5VisualFinish_'+side+'WallJoint_'+str(z),(x0-.0003,52.66,z-.005),(x1+.002,55.96,z+.005),'warm_walnut')
# Applied return surrounds respect the retained 2.50 m service opening and its controls.
for k,(a,b) in enumerate([(-216.93,-216.78),(-214.22,-214.07)]):F.box('ServiceOpening_Return_'+str(k),(37.095,52.501,a),(37.235,55.10,b),'warm_walnut')
F.box('ServiceOpening_Header',(37.095,55.135,-216.78),(37.235,55.28,-214.22),'warm_walnut')
F.box('Group5VisualFinish_ServiceThreshold',(36.95,52.5009,-216.75),(37.60,52.5011,-214.25),'champagne_metal')
F.text('Repair_StaffWallIdentity','TEXTILE REPAIR  /  STOCK',(37.123,54.63,-213.0),.20,False,'warm_walnut')
bpy.context.view_layer.update()
assert all(tuple(tuple(r) for r in bpy.data.objects[n].matrix_world)==m for n,m in kept.items())
bpy.context.scene['scope']='Purposeful textile stock and repair construction;retained shelf/cabinet/aisle/opening geometry;no economy or capacity acceptance'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_texcoords=True,export_materials='EXPORT',export_extras=True)
native_sha=sha(native);export_sha=sha(export);bpy.ops.wm.open_mainfile(filepath=str(native));repeat=Path('/tmp/group5_thread_r003_repeat.glb');bpy.ops.export_scene.gltf(filepath=str(repeat),export_format='GLB',export_yup=True,export_texcoords=True,export_materials='EXPORT',export_extras=True);assert sha(repeat)==export_sha and sha(native)==native_sha
assert all(sha(Path(p))==h for p,h in pins.items())
target=ROOT/'Game/assets/models/group5/thread_stock'/export.name;assert not target.exists();shutil.copyfile(export,target)
j['construction_successor']={'revision':'r003','parent_native':str(old.relative_to(ROOT)),'parent_native_sha256':pins[str(old)],'parent_model':str(old_glb.relative_to(ROOT)),'parent_model_sha256':pins[str(old_glb)],'retained_furniture_meshes':list(kept),'retained_furniture_poses_unchanged':True,'recognizable_forms':form_counts,'visual_only_finish_prefix':'Group5VisualFinish_','floor_source_sha256':sha(floor_path),'fresh_native_repeat_export_byte_identical':True,'previous_visual_construction_review':'r002 rejected as primitive storage aisle;retained honestly'}
j['native']=str(native.relative_to(ROOT));j['native_sha256']=native_sha;j['model_path']='res://assets/models/group5/thread_stock/'+export.name;j['model_sha256']=export_sha
j['native_mesh_count']=sum(o.type=='MESH' for o in bpy.context.scene.objects);j['editable_lettering_count']=sum(o.type=='FONT' for o in bpy.context.scene.objects);j['scope']='Recognizable textile/repair forms,room finishes,opening surrounds and task fixtures in original staff lane;unchanged shelf dimensions/doors/aisles,capacity and shared structure;gameplay economy,structural sizing,final art and whole-group acceptance held'
definition.write_text(json.dumps(j,indent=2)+'\n');print('THREAD_CONSTRUCTION_R003',j['native_mesh_count'],form_counts,export_sha)
