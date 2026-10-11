from pathlib import Path
import json,hashlib,sys,math,bpy
W=Path(__file__).resolve().parent;R=W.parents[2];sys.path.insert(0,str(W))
from immutable_revision import require_new,export_native
native='D04CareAngledTerminal_r001.blend';model='D04_CARE_ANGLED_TERMINAL_r001.glb'
require_new([W/native,W/model,R/'Game/assets/models'/model,W/'ANGLED_TERMINAL_PLAN_r001.json'])
P=json.load(open(W/'RUNTIME_PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
B=lambda p:(p[0],-p[2],p[1]);parts=[]
def rod(name,length,radius,axis,offset):
 vs=[];n=16
 for t in [0,length]:
  for k in range(n):
   a,b=radius*math.cos(k*math.tau/n),radius*math.sin(k*math.tau/n)
   v=[t,a,b] if axis=='X' else [a,b,t];vs.append([v[i]+offset[i]for i in range(3)])
 fs=[list(reversed(range(n))),list(range(n,2*n))]+[[k,(k+1)%n,n+(k+1)%n,n+k]for k in range(n)]
 parts.append({'name':name,'verts':vs,'faces':fs,'category':'articulated_care_terminal','role':'champagne_metal','runtime_collision':True})
rod('D04PC_CareOffsetArm',1.1,.008,'X',[0,0,0]);rod('D04PC_CareTerminalTip',.3,.008,'Z',[1.1,0,0])
lo=[1.086,-.011,-.01];hi=[1.114,.011,.01];vs=[[lo[0],lo[1],lo[2]],[hi[0],lo[1],lo[2]],[hi[0],hi[1],lo[2]],[lo[0],hi[1],lo[2]],[lo[0],lo[1],hi[2]],[hi[0],lo[1],hi[2]],[hi[0],hi[1],hi[2]],[lo[0],hi[1],hi[2]]]
parts.append({'name':'D04PC_CareTerminalJoint','verts':vs,'faces':[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],'category':'articulated_care_terminal_joint','role':'champagne_metal','runtime_collision':True})
plan={'revision':'terminal_r001','parts':parts,'offset_length_m':1.1,'terminal_length_m':.3,'terminal_pivot':[1.1,0,0],'terminal_pitch_degrees':[-90,90],'shaft_axial_roll_degrees':[0,180],'maximum_total_tool_path_m':3.4,'original_tubes_reused_without_rescaling':True,'production_active':False}
with open(W/'ANGLED_TERMINAL_PLAN_r001.json','x')as f:json.dump(plan,f,indent=2);f.write('\n')
bpy.ops.wm.read_factory_settings(use_empty=True);mat=bpy.data.materials.new('D04CareToolChampagne');mat.diffuse_color=(.46,.4,.27,1);mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=mat.diffuse_color;bs.inputs['Metallic'].default_value=.6;bs.inputs['Roughness'].default_value=.45
for part in parts:
 me=bpy.data.meshes.new(part['name']);me.from_pydata([B(v)for v in part['verts']],[],part['faces']);me.update();me.materials.append(mat);ob=bpy.data.objects.new(part['name'],me);bpy.context.collection.objects.link(ob)
 for k in ['role','category','runtime_collision']:ob[k]=part[k]
 ob['native_terminal_plan_sha256']=sha(W/'ANGLED_TERMINAL_PLAN_r001.json')
rec=export_native(bpy,W,R,native,model);rec['geometry_members']=parts;P['native_export_records'].append(rec);P['model_pins'][model]=rec['export_sha256'];P['reach_tool']['angled_terminal']={k:v for k,v in plan.items() if k!='parts'};P['reach_tool']['angled_terminal'].update(model=model,model_sha256=rec['export_sha256'],members=[{'name':q['name'],'bounds':[[min(v[i]for v in q['verts'])for i in range(3)],[max(v[i]for v in q['verts'])for i in range(3)]]}for q in parts]);P['tool_terminal_revision']='r001'
(W/'RUNTIME_PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(R/'Game/data/architecture/D04_PHYSICAL_CONNECTIONS_CANDIDATE.json').write_text(json.dumps(P,indent=2)+'\n');(W/'ANGLED_TERMINAL_NATIVE_CHECK_r001.json').write_text(json.dumps({'status':'PASS','record':rec,'original_source_pins':len(P['source_pins']),'production_active':False},indent=2)+'\n');print('ANGLED_TERMINAL_NATIVE_PASS',len(parts))
