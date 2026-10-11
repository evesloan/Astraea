from pathlib import Path
import json,hashlib,bpy,sys,math
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'RUNTIME_PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1])
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
mat=bpy.data.materials.new('D04CareToolChampagne');mat.diffuse_color=(.46,.40,.27,1);mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=mat.diffuse_color;bs.inputs['Metallic'].default_value=.6;bs.inputs['Roughness'].default_value=.45
members=[]
for i,(outer,inner)in enumerate([(.012,.0105),(.010,.0085),(.008,0)]):
 vs=[];fs=[];n=16
 if inner:
  for z,r in [(0,outer),(1.2,outer),(0,inner),(1.2,inner)]:vs.extend([B([r*math.cos(k*math.tau/n),r*math.sin(k*math.tau/n),z])for k in range(n)])
  for k in range(n):
   K=(k+1)%n;fs.extend([[k,K,n+K,n+k],[2*n+k,3*n+k,3*n+K,2*n+K],[k,2*n+k,2*n+K,K],[n+k,n+K,3*n+K,3*n+k]])
 else:
  for z in [0,1.2]:vs.extend([B([outer*math.cos(k*math.tau/n),outer*math.sin(k*math.tau/n),z])for k in range(n)])
  fs.extend([list(reversed(range(n))),list(range(n,2*n))]);fs.extend([[k,(k+1)%n,n+(k+1)%n,n+k]for k in range(n)])
 me=bpy.data.meshes.new('D04PC_CareTube_'+str(i));me.from_pydata(vs,[],fs);me.update();me.materials.append(mat);ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob);ob['runtime_collision']=True;ob['category']='telescoping_care_tool';members.append({'name':ob.name,'radius':outer,'bore_radius':inner,'length':1.2,'rigid_translation_only':True})
bpy.ops.wm.save_as_mainfile(filepath=str(W/'D04CareReachTool_r002.blend'),compress=True)
def export():bpy.ops.export_scene.gltf(filepath=str(W/'D04_CARE_REACH_TOOL_r002.glb'),export_format='GLB',export_extras=True,export_apply=True)
export();h=sha(W/'D04_CARE_REACH_TOOL_r002.glb');bpy.ops.wm.open_mainfile(filepath=str(W/'D04CareReachTool_r002.blend'));export();assert sha(W/'D04_CARE_REACH_TOOL_r002.glb')==h
sys.path.insert(0,str(R/'Game/tools'));from validate_production_glb import validate_and_copy;validate_and_copy(W/'D04_CARE_REACH_TOOL_r002.glb',R/'Game/assets/models/D04_CARE_REACH_TOOL_r002.glb')
rec={'native':'D04CareReachTool_r002.blend','native_sha256':sha(W/'D04CareReachTool_r002.blend'),'export':'D04_CARE_REACH_TOOL_r002.glb','export_sha256':h,'fresh_native_repeat_identical':True,'mesh_count':3,'members':members};P['native_export_records'].append(rec);del P['model_pins'][P['reach_tool']['model']];P['model_pins'][rec['export']]=h;P['reach_tool'].update(model=rec['export'],members=members,outer_tubes_hollow_native=True,nesting_radial_clearance_m=.0005,minimum_joint_overlap_m=.1,convex_contact_envelopes_conservative=True)
(W/'RUNTIME_PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(R/'Game/data/architecture/D04_PHYSICAL_CONNECTIONS_CANDIDATE.json').write_text(json.dumps(P,indent=2)+'\n');(W/'REACH_TOOL_NATIVE_CHECK_r002.json').write_text(json.dumps({'status':'PASS','record':rec,'no_source_rescaling':True,'hollow_outer_tubes':2,'minimum_joint_overlap_m':.1},indent=2)+'\n');print('HOLLOW_REACH_NATIVE_PASS')
