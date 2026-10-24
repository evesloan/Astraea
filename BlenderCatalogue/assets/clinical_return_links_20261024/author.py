"""Editable through routes and a named receiving-source gate ownership successor."""
from pathlib import Path
import bpy,json,hashlib,os,math
from mathutils import Vector
R=Path(__file__).resolve().parents[3];N=Path(__file__).resolve().parent;P=R/'Game/clinical_return_links_20261024';plan=json.loads((P/'PLAN.json').read_text());walls=json.loads((P/'evidence/WALL_SUCCESSORS.json').read_text());B=lambda p:Vector((p[0],-p[2],p[1]));receiving=N/'ClinicalRoomReceiving_r002.blend';through=N/'ClinicalThroughRoutes_r001.blend';assert not receiving.exists()and not through.exists()
for path,digest in plan['source_pins'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,path
prior=R/'BlenderCatalogue/assets/clinical_room_receiving_20261024/ClinicalRoomReceiving_r001.blend';assert hashlib.sha256(prior.read_bytes()).hexdigest()=='777be1290e40fc4fc03a66c8dfd1bf4c054eecd22e5b16c8a04b2a10996455bc'
bpy.ops.wm.open_mainfile(filepath=str(prior));bpy.context.preferences.filepaths.save_version=0
for row in plan['retained_gate_bindings']:
 obj=bpy.data.objects[row['receiver']];assert obj.instance_type=='COLLECTION';obj.instance_type='NONE';obj.instance_collection=None;obj['retained_closed_gate_mesh_names']=json.dumps(row['canonical_mesh_names']);obj['source_binding_only']=True
for library in bpy.data.libraries:library.filepath='//'+os.path.relpath(bpy.path.abspath(library.filepath),str(N))
bpy.data.texts.new('Canonical gate bindings.json').write(json.dumps(plan['retained_gate_bindings'],indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(receiving),compress=True,relative_remap=False)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;materials={};groups={}
for file in ['AST-MED-G3-007.blend','AST-MED-G3-008.blend']:
 with bpy.data.libraries.load(str(R/plan['native_library']/file),link=True)as(a,b):b.materials=[n for n in a.materials if n.startswith('ASTRAEA_staff_')]
 for material in b.materials:materials.setdefault(material.name.removeprefix('ASTRAEA_'),material)
for route in plan['routes']:
 group=bpy.data.collections.new(route['id']);bpy.context.scene.collection.children.link(group);groups[route['id']]=group
for row in plan['parts']:
 mesh=bpy.data.meshes.new(row['name']);mesh.from_pydata([B(p)for p in row['verts']],[],row['faces']);mesh.update();mesh.materials.append(materials[row['role']]);uv=mesh.uv_layers.new(name='MetreScaled')
 for poly in mesh.polygons:
  for li in poly.loop_indices:
   p=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(p.x*.5,-p.y*.5)if abs(poly.normal.z)>.7 else(-p.y*.5,p.z*.5)
 obj=bpy.data.objects.new(row['name'],mesh);groups[row['zone']].objects.link(obj)
wallgroup=bpy.data.collections.new('Exact retained partition skin successors');bpy.context.scene.collection.children.link(wallgroup)
for row in walls:
 for si,surface in enumerate(row['surfaces']):
  indices=surface['indices']or list(range(len(surface['positions'])));faces=[(indices[i],indices[i+2],indices[i+1])for i in range(0,len(indices),3)];name=row['name']+'_ThroughRouteSkin';mesh=bpy.data.meshes.new(name);mesh.from_pydata([B(p)for p in surface['positions']],[],faces);mesh.update();mesh.materials.append(materials[surface['material'].removeprefix('ASTRAEA_')]);uv=mesh.uv_layers.new(name='RetainedSourceUV')
  for poly in mesh.polygons:
   for li in poly.loop_indices:uv.data[li].uv=surface['uvs'][mesh.loops[li].vertex_index]
  obj=bpy.data.objects.new(name,mesh);wallgroup.objects.link(obj)
for route in plan['routes']:
 for row in route['lights']:
  data=bpy.data.lights.new(row['name'],'SPOT');data.color=row['color'];data.energy=80;data.spot_size=math.radians(130);obj=bpy.data.objects.new(row['name'],data);obj.location=B(row['position']);obj['Godot_energy']=row['energy'];obj['Godot_range']=row['range'];obj['Blender_watts_not_runtime_calibration']=True;groups[route['id']].objects.link(obj)
bpy.data.texts.new('Scope and holds.json').write(json.dumps({'plan':'Game/clinical_return_links_20261024/PLAN.json','source_pins':plan['source_pins'],'holds':plan['holds'],'new_capacity':0,'visual_accepted':False},indent=2))
for library in bpy.data.libraries:library.filepath='//'+os.path.relpath(bpy.path.abspath(library.filepath),str(N))
bpy.ops.wm.save_as_mainfile(filepath=str(through),compress=True,relative_remap=False)
receipt={'status':'SAVED_EDITABLE_UNFINISHED_NATIVE','files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in [receiving,through]],'parts':len(plan['parts']),'partition_successors':len(walls),'receiving_gate_references':len(plan['retained_gate_bindings']),'original_sources_preserved':True,'visual_accepted':False}
(P/'evidence/NATIVE.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
