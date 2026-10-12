"""Additive fitted textile stock/repair strip in the retained Thread & Shell lane."""
from pathlib import Path
import bpy,bmesh,json,hashlib,importlib.util,ast,math,shutil
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2];CAT=P.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
original=ROOT/'BlenderCatalogue/assets/thread_shell_architecture/source/AST-RTL-007.blend'
runtime=ROOT/'Game/assets/models/AST-RTL-007.glb'
assert sha(original)=='ad3f07d85d5c831eccb2dae97c7008f2a8d7adc60b867665f281a6d141b4fb49'
assert sha(runtime)=='90625dda129fa2ea27ba675137e12d76adab055cea2ec972723dd8d1d787184d'
native=P/'source/thread_stock/thread_stock_repair_r001.blend'
export=P/'exports/thread_stock/thread_stock_repair_r001.glb'
assert not native.exists() and not export.exists(),'Saved revisions are immutable'
spec=importlib.util.spec_from_file_location('palette',CAT/'standards/retail_materials.py')
palette=importlib.util.module_from_spec(spec);spec.loader.exec_module(palette);M=palette.materials()
template=P/'source/build_components.py';tree=ast.parse(template.read_text())
FACES=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='FACES' for t in n.targets)))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['cube','empty']],type_ignores=[]),str(template),'exec'),globals())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
root=empty('GROUP5_THREAD_STOCK_REPAIR_R001')
def block(name,x0,x1,y0,y1,z0,z1,role,parent=None):
    return cube(name,(x0-8,y0,z0+216),(x1-8,y1,z1+216),role,parent or root)
def text(name,label,x,y,z,size=.16):
    d=bpy.data.curves.new(name,'FONT');d.body=label;d.size=size;d.align_x='CENTER';d.align_y='CENTER';d.extrude=.0008
    o=bpy.data.objects.new(name,d);bpy.context.scene.collection.objects.link(o);o.parent=root
    o.location=(x-8,-(z+216),y);o.rotation_euler=(math.pi/2,0,-math.pi/2);d.materials.append(M['ivory_enamel'])
    # Native retains editable lettering. Export uses evaluated meshes.
    return o
stock=[];feet=[];mounts=[];fixtures=[];roles=[]
def module(name,z0,z1,kind):
    roles.append({'name':name,'purpose':kind,'world_xz':[[41.75,z0],[42.84,z1]],'staff_stance_world_xyz':[40.7,52.53,(z0+z1)/2]})
    block(name+'_plinth',41.95,42.82,0,.16,z0,z1,'warm_walnut')
    block(name+'_back',42.78,42.84,.16,2.62,z0,z1,'ivory_enamel')
    for z in [z0,z1]:block(name+'_side_'+str(z),41.85,42.84,.16,2.64,z-.04,z+.04,'ivory_enamel')
    block(name+'_crown',41.75,42.84,2.64,2.72,z0-.04,z1+.04,'retail_terracotta_enamel')
    for z in [z0+.3,z1-.3]:
        for x in [42.02,42.74]:feet.append([x,52.5,z])
        for level in [.32,2.5]:
            n=name+'_wall_anchor_'+str(z)+'_'+str(level)
            block(n,42.80,42.935,level,level+.07,z-.05,z+.05,'champagne_metal');mounts.append(n)
    text(name+'_label',kind.upper(),41.738,2.678,(z0+z1)/2,.11)
    if kind=='repair and parcel return':
        block(name+'_cabinet',41.95,42.78,.16,.79,z0,z1,'warm_walnut')
        block(name+'_worktop',41.72,42.84,.79,.89,z0-.035,z1+.035,'warm_stone')
        for i in range(3):
            a=z0+(z1-z0)*i/3+.05;b=z0+(z1-z0)*(i+1)/3-.05
            block(name+'_drawer_'+str(i),41.922,41.952,.28,.70,a,b,'retail_terracotta_enamel')
            block(name+'_handle_'+str(i),41.87,41.91,.58,.61,a+.22,b-.22,'champagne_metal')
        for i in range(2):
            z=z0+.65+i*1.35
            block(name+'_tray_base_'+str(i),41.96,42.62,.89,.925,z-.43,z+.43,'warm_walnut')
            for dz in [-.43,.43]:block(name+'_tray_rim_'+str(i)+'_'+str(dz),41.94,42.64,.925,1.00,z+dz-.025,z+dz+.025,'champagne_metal')
            block(name+'_generic_fold_'+str(i),42.07,42.53,.925,.995,z-.31,z+.31,'teal_weave')
            stock.append({'mesh':name+'_generic_fold_'+str(i),'support':name+'_tray_base_'+str(i),'world_contact_xyz':[42.3,52.5+.925,z]})
        for level in [1.55,2.08]:block(name+'_tool_shelf_'+str(level),42.2,42.78,level,level+.075,z0,z1,'warm_walnut')
    else:
        cells=5 if kind=='folded textile stock' else 4
        for i in range(1,cells):
            z=z0+(z1-z0)*i/cells;block(name+'_divider_'+str(i),41.89,42.78,.16,2.64,z-.025,z+.025,'ivory_enamel')
        for level in [.55,1.18,1.81,2.40]:
            block(name+'_shelf_'+str(level),41.88,42.78,level,level+.075,z0,z1,'warm_walnut')
            if level==2.40:continue
            for i in range(cells):
                z=z0+(z1-z0)*(i+.5)/cells
                n=name+'_generic_fold_'+str(level)+'_'+str(i)
                block(n,42.02,42.67,level+.075,level+.235,z-.55,z+.55,['clay_weave','teal_weave','oatmeal_weave'][i%3])
                stock.append({'mesh':n,'support':name+'_shelf_'+str(level),'world_contact_xyz':[42.3,52.5+level+.075,z]})
    z=(z0+z1)/2
    # Direct ceiling tie preserves the original service roof at local3.70.
    block(name+'_fixture_stem',42.16,42.23,3.26,3.705,z-.04,z+.04,'champagne_metal')
    block(name+'_fixture_housing',41.74,42.42,3.13,3.28,z-.4,z+.4,'ivory_enamel')
    block(name+'_fixture_lens',41.79,42.37,3.112,3.13,z-.34,z+.34,'champagne_metal')
    fixtures.append({'name':name+'_TaskLight','lens':name+'_fixture_lens','mount':name+'_fixture_stem','world_xyz':[42.08,55.592,z],'range_m':6,'energy':.85,'color':[.86,.93,1]})
module('TextileStock',-231.5,-221.7,'folded textile stock')
module('RepairReturn',-214.2,-211.2,'repair and parcel return')
module('TextileReserve',-208.3,-200.0,'reserve textile stock')
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene['scope']='Group5 additive stock/repair furniture in original ThreadShell rear lane;generic props only,no inventory/economy or capacity records'
native.parent.mkdir(exist_ok=True);export.parent.mkdir(exist_ok=True);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native))
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_texcoords=True,export_materials='EXPORT',export_extras=True)
initial=sha(export);native_sha=sha(native)
bpy.ops.wm.open_mainfile(filepath=str(native));repeat=Path('/tmp/group5_thread_stock_repeat.glb')
bpy.ops.export_scene.gltf(filepath=str(repeat),export_format='GLB',export_yup=True,export_texcoords=True,export_materials='EXPORT',export_extras=True)
assert sha(repeat)==initial and sha(native)==native_sha
target=ROOT/'Game/assets/models/group5/thread_stock'/export.name;target.parent.mkdir(exist_ok=True)
assert not target.exists();shutil.copyfile(export,target)
contract={'schema':'astraea.group5.thread_stock.v1','programme_key':'D09_directory_04','historical_room_id':'D09_tailor3','original_native':str(original.relative_to(ROOT)),'original_native_sha256':sha(original),'original_model':'res://assets/models/AST-RTL-007.glb','original_model_sha256':sha(runtime),'native':str(native.relative_to(ROOT)),'native_sha256':native_sha,'model_path':'res://assets/models/group5/thread_stock/'+export.name,'model_sha256':initial,'model_origin_world_xyz':[8,52.5,-216],'native_mesh_count':sum(o.type=='MESH' for o in scene.objects),'editable_lettering_count':sum(o.type=='FONT' for o in scene.objects),'modules':roles,'generic_support_contacts':stock,'foundation_contacts_world_xyz':feet,'wall_mount_names':mounts,'fixtures':fixtures,'fresh_native_repeat_export_byte_identical':True,'public_entry_and_doors_unchanged':True,'shared_floor_ceiling_and_foodhall_unchanged':True,'inventory_or_browse_capacity_created':False,'scope':'Three fitted stock/repair modules in original rear lane;source fit and ordinary controller routes checked separately;commerce,species,loaded-cart,engineering,final-art and whole-group acceptance held'}
(ROOT/'Game/data/architecture/group5/THREAD_STOCK_REPAIR.json').write_text(json.dumps(contract,indent=2)+'\n')
print('THREAD_STOCK_SOURCE_PASS',contract['native_mesh_count'],len(stock),len(fixtures),initial)
