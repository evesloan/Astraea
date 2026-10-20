extends SceneTree
func _initialize():call_deferred("run")
func digest(bytes: PackedByteArray) -> String:
 var h=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(bytes);return h.finish().hex_encode()
func pose(node: Node3D, top: Node3D) -> Transform3D:
 var t=node.transform
 var parent=node.get_parent()
 while parent!=null:
  if parent is Node3D:t=parent.transform*t
  if parent==top:break
  parent=parent.get_parent()
 return t
func run():
 var file=OS.get_cmdline_user_args()[0]
 var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(file))
 assert(FileAccess.get_sha256(d.model_file)==d.input_sha256)
 var source:Node3D=load(d.model_file).instantiate()
 var policy:Dictionary=d.get("source_collision_policy",{})
 for mesh:MeshInstance3D in source.find_children("*","MeshInstance3D",true,false):
  if not policy.is_empty() and str(policy[str(mesh.name)].get("role",""))=="hospitality_glass":
   var material=ShaderMaterial.new();material.shader=load("res://shaders/hospitality_glass.gdshader");mesh.material_override=material
 var total=0
 for cell in d.collision_cells:
  var expected=PackedVector3Array()
  for path in cell.source_paths:
   var mesh:MeshInstance3D=source.get_node(path)
   var transform=pose(mesh,source)
   for vertex in mesh.mesh.get_faces():expected.append(transform*vertex)
  var shape:ConcavePolygonShape3D=load(cell.path)
  assert(expected.size()==int(cell.triangles)*3)
  assert(digest(expected.to_byte_array())==digest(shape.get_faces().to_byte_array()),"Exact transformed contact face mismatch: "+str(cell.id))
  total+=expected.size()/3
 var visual:Node3D=load(d.visual_path).instantiate()
 var transparent_count=0
 for row in d.get("retained_transparent_contacts",[]):
  var original:MeshInstance3D=source.get_node(row.source_path)
  var kept:MeshInstance3D=visual.get_node(row.output_mesh_path)
  var colliders=kept.find_children("*","CollisionShape3D",true,false)
  assert(colliders.size()==1 and colliders[0].get_parent().get_parent()==kept)
  assert(digest(original.mesh.get_faces().to_byte_array())==digest(colliders[0].shape.get_faces().to_byte_array()))
  if original.get_active_material(0) is ShaderMaterial:
   assert(kept.get_active_material(0) is ShaderMaterial and "glass" in kept.get_active_material(0).shader.resource_path)
  else:assert(original.get_active_material(0).transparency==kept.get_active_material(0).transparency)
  transparent_count+=1
 var triangles=0
 for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
  for s in range(mesh.mesh.get_surface_count()):
   var arrays=mesh.mesh.surface_get_arrays(s)
   triangles+=(arrays[Mesh.ARRAY_INDEX].size() if arrays[Mesh.ARRAY_INDEX]!=null and not arrays[Mesh.ARRAY_INDEX].is_empty() else arrays[Mesh.ARRAY_VERTEX].size())/3
   assert(mesh.get_active_material(s)!=null,"Missing visible source material")
 assert(triangles==int(d.input_triangles))
 for light in d.lights:
  var old:Light3D=source.get_node(light.source_path)
  var fresh:Light3D=visual.get_node(light.output_path)
  assert(old.name==fresh.name and old.get_class()==fresh.get_class())
  assert(pose(old,source).is_equal_approx(pose(fresh,visual)))
  assert(old.light_color==fresh.light_color and old.light_energy==fresh.light_energy)
 print("EXACT_CONTACT_VALIDATION ",JSON.stringify({"file":file,"cells":d.collision_cells.size(),"exact_collision_triangles":total,"visual_triangles":triangles,"source_lights":d.lights.size(),"transparent_contact_ancestry_preserved":transparent_count,"passed":true}))
 source.free();visual.free();quit()
