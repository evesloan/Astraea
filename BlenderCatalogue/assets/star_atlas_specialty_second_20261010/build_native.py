from pathlib import Path
import bpy,json,math,hashlib,shutil,sys
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.loads((W/'PLAN.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1]);records=[];palette={'warm_stone':(.58,.54,.45,1),'warm_walnut':(.25,.12,.065,1),'ivory_enamel':(.78,.73,.63,1),'champagne_metal':(.46,.4,.27,1),'teal_weave':(.09,.25,.23,1),'hospitality_glass':(.22,.4,.44,.4),'opal_glow':(1,.87,.65,1)}
sys.path.insert(0,str(R/'Game/tools'));from validate_production_glb import validate_and_copy,preview_only
for room in P['rooms']:
 idx=room['allocation']['source_envelope_index'];bpy.ops.wm.read_factory_settings(use_empty=True);mats={}
 for part in room['parts']:
  role=part['role']
  if role not in mats:
   mat=bpy.data.materials.new('StarAtlasSpecialty_'+role);mat.diffuse_color=palette[role];mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=palette[role];bs.inputs['Roughness'].default_value=.7;bs.inputs['Metallic'].default_value=.45 if role=='champagne_metal'else 0
   path=R/'Game/assets/models'/('AST-LIB-011_'+role+'.png')
   if not path.exists()and role=='teal_weave':path=next((R/'Game/assets/models').glob('*_teal_weave.png'))
   if path.exists():node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(path),check_existing=True);node.image.pack();node.interpolation='Closest';mat.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color'])
   if role=='hospitality_glass':mat.surface_render_method='DITHERED';bs.inputs['Alpha'].default_value=.4
   if role=='opal_glow':bs.inputs['Emission Color'].default_value=palette[role];bs.inputs['Emission Strength'].default_value=1.2
   mats[role]=mat
  mesh=bpy.data.meshes.new(part['name']);mesh.from_pydata([B(v)for v in part['verts']],[],part['faces']);mesh.update();mesh.materials.append(mats[role]);uv=mesh.uv_layers.new(name='MetreScaled')
  for face in mesh.polygons:
   n=face.normal;u=Vector((1,0,0))if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
   for li in face.loop_indices:co=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(co.dot(u),co.dot(v))
  ob=bpy.data.objects.new(part['name'],mesh);bpy.context.collection.objects.link(ob);ob['runtime_collision']=part['runtime_collision'];ob['construction_role']=part['category'];ob['material_role']=role;ob['source_plan_sha256']=sha(W/'PLAN.json')
 for binding in room['components']:
  a=next(a for a in P['sources']if a['catalogue_id']==binding['catalogue_id']);source=R/'BlenderCatalogue'/a['source'];assert sha(source)==a['source_sha256']
  with bpy.data.libraries.load(str(source),link=False)as(src,dst):dst.objects=src.objects
  obs=[o for o in dst.objects if o and not preview_only(o.name,{k:o.get(k,False)for k in ["preview_only","presentation_only","exclude_from_production"]})];root=bpy.data.objects.new(f'SA{idx}_'+binding['name'],None);bpy.context.collection.objects.link(root)
  for o in obs:bpy.context.collection.objects.link(o)
  for o in obs:
   if o.parent not in obs:o.parent=root
   o.name=f'SA{idx}_'+binding['name']+'__'+o.name
   if o.type=='MESH':
    policy=str(o.get('collision_policy',''));o['runtime_collision']='NO_SOLID_COLLISION'not in policy and not any(t in o.name for t in ['WaterSurface_VisualOnly','Ripple'])
    o['retained_component_id']=a['catalogue_id'];o['retained_component_source_sha256']=a['source_sha256']
  root.location=B(binding['position']);root.rotation_euler.z=binding['yaw'];root['role']=binding['name'];root['operation_hold']=True
 bpy.ops.file.pack_all();native=W/f'StarAtlasSpecialty_{idx}.blend';out=W/room['model_file'];bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_extras=True,export_yup=True,export_apply=True);first=sha(out);bpy.ops.wm.open_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_extras=True,export_yup=True,export_apply=True);assert sha(out)==first
 record={'source_index':idx,'native':native.name,'native_sha256':sha(native),'export':out.name,'export_sha256':sha(out),'mesh_count':sum(o.type=='MESH'for o in bpy.data.objects),'fresh_native_repeat_identical':True};records.append(record);room.update(model_sha256=record['export_sha256'],mesh_count=record['mesh_count']);validate_and_copy(out,R/'Game/assets/models'/out.name);print('EXPORTED',idx,record['mesh_count'],flush=True)
P['native_export_records']=records;P['status']='authored_second_four_unassigned_interiors_pending_receiving_and_actual_main';(W/'RUNTIME_PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps({'status':'PASS','blender_version':bpy.app.version_string,'rooms':records,'original_sources_unchanged':True},indent=2)+'\n')
for a in P['sources']:assert sha(R/'BlenderCatalogue'/a['source'])==a['source_sha256'] and sha(R/'BlenderCatalogue'/a['export'])==a['export_sha256']
