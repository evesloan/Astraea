from pathlib import Path
import bpy,json,hashlib
from mathutils import Matrix,Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));expected={};mods={}
def evaluated(o):
 dg=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(dg);me=e.to_mesh();v=[o.matrix_world@q.co for q in me.vertices];faces=[tuple(q.vertices)for q in me.polygons];uv=[[tuple(q.uv)for q in layer.data]for layer in me.uv_layers];e.to_mesh_clear();return v,faces,uv
for f in sorted({q['source_native']for q in P['furniture_meshes']}):
 bpy.ops.wm.open_mainfile(filepath=str(R/f));bpy.context.view_layer.update()
 for q in P['furniture_meshes']:
  if q['source_native']==f:
   o=bpy.data.objects[q['source_name']];expected[q['name']]=evaluated(o);mods[q['name']]=[(m.type,m.name)for m in o.modifiers]
bpy.ops.wm.open_mainfile(filepath=str(W/P['structure']['native']));bpy.context.view_layer.update();rows=[];bounds=[]
for q in P['furniture_meshes']:
 o=bpy.data.objects[q['name']];v,faces,uv=evaluated(o);old,F,U=expected[q['name']];s=q['placement'];T=Matrix.Translation(Vector((s['at'][0],-s['at'][2],s['at'][1])))@Matrix.Rotation(s['yaw'],4,'Z');assert faces==F and uv==U and len(v)==len(old),q['name'];delta=max((at-T@before).length for at,before in zip(v,old));assert delta<.0001,(q['name'],delta);assert [(m.type,m.name)for m in o.modifiers]==mods[q['name']]
 real=[T@at for at in old];xyz=[[at.x,at.z,-at.y]for at in real];bounds.append({'name':q['name'].replace('.','_'),'bounds':[[min(at[k]for at in xyz)for k in range(3)],[max(at[k]for at in xyz)for k in range(3)]]});rows.append({'name':q['name'],'max_evaluated_rigid_world_vertex_delta_m':delta,'source_modifier_stack':mods[q['name']]})
P['runtime_furniture_expected_bounds']=bounds
for f in [W/'PLAN.json',W/'RUNTIME_PLAN.json',R/'Game/data/architecture/AFT_CROWN_SITTING_BAYS.json']:f.write_text(json.dumps(P,indent=2)+'\n')
(W/'EXACT_EVALUATED_SOURCE_AUDIT.json').write_text(json.dumps({'status':'PASS','exact_evaluated_source_meshes':len(rows),'source_evaluated_faces_UVs_modifiers_preserved':True,'geometry_and_native_outputs_unchanged':True,'max_world_vertex_delta_m':max(q['max_evaluated_rigid_world_vertex_delta_m']for q in rows),'rows':rows},indent=2)+'\n');print('PASS exact evaluated source',len(rows),'meshes')
