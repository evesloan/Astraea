from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
O=Path(__file__).resolve().parents[1];p=O/'RECEIVING_PLAN.json';plan=json.loads(p.read_text());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.wm.read_factory_settings(use_empty=True);materials={}
for q in plan['parts']:
 role=q['role']
 if role not in materials:
  m=bpy.data.materials.new('SunsetRoof_'+role);m.diffuse_color=(.72,.69,.60,1) if 'chord'in role else(.35,.36,.37,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=m.diffuse_color;bs.inputs['Roughness'].default_value=.65;bs.inputs['Metallic'].default_value=.35;materials[role]=m
 me=bpy.data.meshes.new(q['name']);me.from_pydata([(v[0],-v[2],v[1])for v in q['verts']],[],q['faces']);me.update();me.materials.append(materials[role]);uv=me.uv_layers.new(name='MetreScaled')
 for f in me.polygons:
  n=f.normal;u=Vector((1,0,0))if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
  for li in f.loop_indices:
   a=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(a.dot(u),a.dot(v))
 ob=bpy.data.objects.new(q['name'],me);bpy.context.collection.objects.link(ob);ob['construction_role']=role;ob['source_plan_sha256']=h(p);ob['runtime_collision']=True
bpy.ops.wm.save_as_mainfile(filepath=str(O/'source/SunsetVesperReceiver.blend'),compress=True)
(O/'exports').mkdir(exist_ok=True)
bpy.ops.export_scene.gltf(filepath=str(O/'exports/SunsetVesperReceiver.glb'),export_format='GLB',export_yup=True,export_extras=True)
report={'status':'SOURCE_EXPORTED_NOT_RUNTIME_ADOPTED','parts':len(plan['parts']),'plan_sha256':h(p),'native_sha256':h(O/'source/SunsetVesperReceiver.blend'),'export_sha256':h(O/'exports/SunsetVesperReceiver.glb'),'scope':plan['scope']};(O/'SOURCE_RECEIPT.json').write_text(json.dumps(report,indent=2)+'\n');print('SUNSET_VESPER_SOURCE',json.dumps(report),flush=True)
