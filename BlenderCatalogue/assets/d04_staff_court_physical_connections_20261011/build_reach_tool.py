from pathlib import Path
import json,hashlib,bpy,sys,math
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'RUNTIME_PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
mat=bpy.data.materials.new('D04CareToolChampagne');mat.diffuse_color=(.46,.40,.27,1);mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=mat.diffuse_color;bs.inputs['Metallic'].default_value=.6;bs.inputs['Roughness'].default_value=.45
members=[]
for i,radius in enumerate([.012,.010,.008]):
 bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=radius,depth=1.2,location=(0,-.6,0),rotation=(math.pi/2,0,0));ob=bpy.context.object;ob.name='D04PC_CareTube_'+str(i);ob.data.materials.append(mat);ob['runtime_collision']=True;ob['category']='telescoping_care_tool';members.append({'name':ob.name,'radius':radius,'length':1.2,'rigid_translation_only':True})
 # Native parts remain unscaled. Runtime joints slide at most1.1m, leaving
 #0.1m physical overlap per telescoping stage; usable length1.2..3.4m.
bpy.ops.wm.save_as_mainfile(filepath=str(W/'D04CareReachTool_r001.blend'),compress=True)
def export():bpy.ops.export_scene.gltf(filepath=str(W/'D04_CARE_REACH_TOOL_r001.glb'),export_format='GLB',export_extras=True,export_apply=True)
export();digest=sha(W/'D04_CARE_REACH_TOOL_r001.glb');bpy.ops.wm.open_mainfile(filepath=str(W/'D04CareReachTool_r001.blend'));export();assert sha(W/'D04_CARE_REACH_TOOL_r001.glb')==digest
sys.path.insert(0,str(R/'Game/tools'));from validate_production_glb import validate_and_copy;validate_and_copy(W/'D04_CARE_REACH_TOOL_r001.glb',R/'Game/assets/models/D04_CARE_REACH_TOOL_r001.glb')
rec={'native':'D04CareReachTool_r001.blend','native_sha256':sha(W/'D04CareReachTool_r001.blend'),'export':'D04_CARE_REACH_TOOL_r001.glb','export_sha256':digest,'fresh_native_repeat_identical':True,'mesh_count':3,'members':members};P['native_export_records'].append(rec);P['model_pins'][rec['export']]=digest;P['reach_tool']={'model':rec['export'],'members':members,'minimum_length':1.2,'maximum_length':3.4,'joint_slide_max':1.1,'task_stock_refill_or_biology_implemented':False}
(W/'RUNTIME_PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(R/'Game/data/architecture/D04_PHYSICAL_CONNECTIONS_CANDIDATE.json').write_text(json.dumps(P,indent=2)+'\n');(W/'REACH_TOOL_NATIVE_CHECK.json').write_text(json.dumps({'status':'PASS','record':rec,'no_source_rescaling':True},indent=2)+'\n');print('REACH_TOOL_NATIVE_PASS')
