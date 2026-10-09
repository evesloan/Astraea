extends RefCounted
# Exact physical successor, never a historical reconstructed scene.
const MANIFEST="res://data/architecture/packages/botanical_pair_runtime/COURT_SUCCESSOR.json"
const MANIFEST_SHA="23e793d9b84306b4e7c08d81ab35bfb6550331b40dc3c4118f90849f344c4b6d"
static var checked:=false
static var physical_checked:=false
static var moss_roster_checked:=false
static var data:Dictionary={}
static var expected:Dictionary={}
static var import_to_source:Dictionary={}
static func ensure()->void:
 if checked:return
 load("res://tests/botanical_pair_successor_guard.gd").ensure()
 assert(FileAccess.get_sha256(MANIFEST)==MANIFEST_SHA)
 data=JSON.parse_string(FileAccess.get_file_as_string(MANIFEST))
 assert(data.schema==1 and data.removed_source_names.size()==16 and data.expected_source_meshes==120)
 assert(data.changed_source_name=="BOTCOURT_starboard_EDGE_1_Post_3" and float(data.world_z_delta_m)==.05)
 for pair in [[data.source_closed_geometry_path,data.source_closed_geometry_sha256],[data.source_closed_export_path,data.source_closed_export_sha256],[data.successor_geometry_path,data.successor_geometry_sha256],["assets/models/"+str(data.successor_file),data.successor_export_sha256]]:
  assert(FileAccess.get_sha256("res://"+str(pair[0]))==str(pair[1]))
 var prior:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://"+str(data.source_closed_geometry_path)))
 expected=JSON.parse_string(FileAccess.get_file_as_string("res://"+str(data.successor_geometry_path)))
 assert(prior.objects.size()==136 and expected.objects.size()==120)
 var projected:Dictionary=prior.duplicate(true)
 projected.source_export_sha256=str(data.successor_export_sha256)
 for key in data.removed_source_names:
  assert(str(key).begins_with("BOTCOURT_starboard_PORTAL_CLOSURE_") and projected.objects.has(key))
  projected.objects.erase(key)
 var points:Array=projected.objects[str(data.changed_source_name)].vertices_world
 assert(points.size()==18 and data.post_translation_binary_witness.size()==18)
 var target_points:Array=expected.objects[str(data.changed_source_name)].vertices_world
 assert(target_points.size()==18)
 for index in range(points.size()):
  var point:Array=points[index];var target:Array=target_points[index]
  var witness:Dictionary=data.post_translation_binary_witness[index]
  assert(int(witness.vertex)==index and point[0]==target[0] and point[1]==target[1])
  assert(var_to_bytes(point[2]).hex_encode()==str(witness.old_z_variant_bytes))
  var shifted:float=float(point[2])+.05
  assert(var_to_bytes(shifted).hex_encode()==str(witness.projected_z_variant_bytes))
  assert(var_to_bytes(target[2]).hex_encode()==str(witness.expected_z_variant_bytes))
  # Two exact independently pinned binary encodings, not an epsilon comparison.
  point[2]=target[2]
 assert(projected==expected,"Only16 exact closure removals and one exact post transform may change")
 var aliases:Dictionary={}
 assert(data.explicit_source_import_aliases.size()==3)
 for pair in data.explicit_source_import_aliases:
  assert(expected.objects.has(str(pair.source_name)) and not expected.objects.has(str(pair.imported_name)))
  assert(not aliases.has(str(pair.source_name)))
  aliases[str(pair.source_name)]=str(pair.imported_name)
 for source_name in expected.objects:
  var name_key:String=str(aliases.get(str(source_name),str(source_name)))
  assert(not import_to_source.has(name_key));import_to_source[name_key]=str(source_name)
 assert(import_to_source.size()==120)
 checked=true
static func validate_moss_roster(wrapper:Node,opened:int,closed:int,opened_names:Array)->void:
 moss_roster_checked=false
 ensure()
 assert(checked)
 assert(opened==14 and closed==106 and opened_names.size()==14)
 assert(wrapper.name==str(data.root_name) and wrapper.get_meta("catalogue_file","")==str(data.successor_file))
 var seen:Dictionary={}
 for visual in wrapper.find_children("*","MeshInstance3D",true,false):
  assert(import_to_source.has(str(visual.name)))
  var key:String=str(import_to_source[str(visual.name)])
  assert(not seen.has(key));seen[key]=true
  assert((str(visual.name) in opened_names)==key.begins_with("BOTCOURT_port_PORTAL_CLOSURE_"))
 assert(seen.size()==120)
 moss_roster_checked=true
static func validate(floors:Node,predecessor_proof:Dictionary)->void:
 physical_checked=false
 ensure()
 assert(checked)
 assert(str(predecessor_proof.guard_geometry_path)==str(data.source_closed_geometry_path))
 assert(str(predecessor_proof.guard_file)==str(data.source_closed_export_path).get_file())
 var medical=load("res://tests/medical_triage_successor_guard.gd")
 var wrapper:Node3D=floors.get_parent().get_node(str(data.root_name)) as Node3D
 assert(wrapper!=null and wrapper.global_transform==Transform3D.IDENTITY)
 assert(wrapper.get_meta("catalogue_file","")==str(data.successor_file) and wrapper.get_child_count()==1)
 var options:=ConfigFile.new();assert(options.load("res://assets/models/"+str(data.successor_file)+".import")==OK)
 assert(bool(options.get_value("params","meshes/force_disable_compression",false)))
 var visual_root:Node=wrapper.get_child(0)
 var meshes:Array=visual_root.find_children("*","MeshInstance3D",true,false)
 assert(meshes.size()==120 and visual_root.find_children("*","StaticBody3D",true,false).size()==120 and visual_root.find_children("*","CollisionShape3D",true,false).size()==120)
 assert(visual_root.find_children("*","Area3D",true,false).is_empty())
 var seen:Dictionary={};var opened:=0;var closed:=0
 for value in meshes:
  var mesh:MeshInstance3D=value as MeshInstance3D
  assert(import_to_source.has(str(mesh.name)))
  var key:String=str(import_to_source[str(mesh.name)])
  assert(not seen.has(key));seen[key]=true
  var is_open:bool=key.begins_with("BOTCOURT_port_PORTAL_CLOSURE_")
  assert(mesh.visible==not is_open and mesh.material_override==null and mesh.mesh!=null)
  var spec:Dictionary=expected.objects[key];var reference:Dictionary={}
  for triangle in spec.triangles:
   var ids:Array[int]=[]
   for val in triangle:ids.append(int(val))
   ids.sort();var triangle_key:String=str(ids);reference[triangle_key]=int(reference.get(triangle_key,0))+1
  assert(medical._botanical_guard_triangles(medical._botanical_faces(mesh.mesh),mesh.global_transform,spec)==reference)
  var contacts:Array=mesh.find_children("*","CollisionShape3D",true,false)
  assert(contacts.size()==1 and contacts[0].disabled==is_open and contacts[0].shape is ConcavePolygonShape3D)
  var contact:CollisionShape3D=contacts[0] as CollisionShape3D
  var native_expected:ConcavePolygonShape3D=mesh.mesh.create_trimesh_shape()
  assert(medical._botanical_triangles(contact.shape.get_faces(),contact.global_transform)==medical._botanical_triangles(native_expected.get_faces(),mesh.global_transform))
  assert(contact.get_parent() is StaticBody3D and contact.get_parent().collision_layer==1 and contact.get_parent().collision_mask==1)
  if is_open:assert(mesh.get_meta("moss_supported_portal_open",false));opened+=1
  else:assert(not mesh.has_meta("moss_supported_portal_open"));closed+=1
 assert(opened==14 and closed==106 and seen.size()==120)
 var template:Node3D=(load("res://assets/models/"+str(data.successor_file)) as PackedScene).instantiate()
 var expected_paths:Dictionary={};var actual_paths:Dictionary={}
 for node in template.find_children("*","Node",true,false):expected_paths[str(template.get_path_to(node))]=node.get_class()
 for node in visual_root.find_children("*","Node",true,false):
  if node is StaticBody3D or node is CollisionShape3D:continue
  actual_paths[str(visual_root.get_path_to(node))]=node.get_class()
 assert(actual_paths==expected_paths,"Every original surviving hierarchy identity must remain exact")
 template.free()
 assert(moss_roster_checked)
 physical_checked=true

static func physical_validation_succeeded()->bool:
 return checked and moss_roster_checked and physical_checked
