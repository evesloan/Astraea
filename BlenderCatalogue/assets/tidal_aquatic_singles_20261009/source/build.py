from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parents[2]
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for item in json.load(open(B/'BATCH_PLAN.json'))['rooms']:
 O=B/'units'/str(item['source_index']);P=O/'PLAN.json';plan=json.load(open(P))
 bpy.ops.wm.read_factory_settings(use_empty=True);materials={};palette={'warm_stone':(.58,.54,.45,1),'warm_walnut':(.25,.12,.065,1),'ivory_enamel':(.78,.73,.63,1),'champagne_metal':(.46,.4,.27,1),'teal_weave':(.09,.25,.23,1),'hospitality_glass':(.22,.4,.44,.4),'opal_glow':(1,.87,.65,1)}
 for q in plan['parts']:
  role=q['role']
  if role not in materials:
   m=bpy.data.materials.new('TidalSpecialty_'+role);m.diffuse_color=palette[role];m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=palette[role];bs.inputs['Roughness'].default_value=.7;bs.inputs['Metallic'].default_value=.45 if role=='champagne_metal'else 0
   tex=R/'Game/assets/models'/('AST-LIB-011_'+role+'.png')
   if not tex.exists()and role=='teal_weave':tex=sorted((R/'Game/assets/models').glob('*_teal_weave.png'))[0]
   if tex.exists():
    image=bpy.data.images.load(str(tex),check_existing=True);image.pack();node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;m.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color'])
   if role=='opal_glow':bs.inputs['Emission Color'].default_value=palette[role];bs.inputs['Emission Strength'].default_value=1.2
   materials[role]=m
  me=bpy.data.meshes.new(q['name']);me.from_pydata([(v[0],-v[2],v[1])for v in q['verts']],[],q['faces']);me.update();me.materials.append(materials[role]);uv=me.uv_layers.new(name='MetreScaled')
  for f in me.polygons:
   n=f.normal;u=Vector((1,0,0))if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
   for li in f.loop_indices:a=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(a.dot(u),a.dot(v))
  ob=bpy.data.objects.new(q['name'],me);bpy.context.collection.objects.link(ob);ob['role']=role;ob['category']=q['category'];ob['runtime_collision']=q['runtime_collision'];ob['source_plan_sha256']=h(P)
 bpy.ops.wm.save_as_mainfile(filepath=str(O/'source/TidalSpecialty.blend'),compress=True)
 (O/'exports').mkdir(exist_ok=True)
 bpy.ops.export_scene.gltf(filepath=str(O/'exports/TidalSpecialty.glb'),export_format='GLB',export_yup=True,export_extras=True)
 rec={'parts':len(plan['parts']),'plan_sha256':h(P),'native_sha256':h(O/'source/TidalSpecialty.blend'),'export_sha256':h(O/'exports/TidalSpecialty.glb'),'limits':plan['limits']}
 (O/'SOURCE_RECEIPT.json').write_text(json.dumps(rec,indent=2)+'\n');print('TIDAL_SPECIALTY_SOURCE',json.dumps(rec),flush=True)
