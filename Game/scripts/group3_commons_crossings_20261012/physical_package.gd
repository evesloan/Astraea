extends RefCounted
static func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D,resolved_ids:Dictionary={},entry_authorization:Dictionary={},adopt_exact_wall_patch:bool=false,adopt_rechecked_thresholds:bool=false)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_commons_crossings_20261012/CROSSINGS.json"));var space:Node3D=ship.get_node("ShipSpace");assert(space.get_node_or_null("Group3CommonsCrossings")==null)
 assert(adopt_exact_wall_patch,"Group1 must explicitly adopt the six exact wall derivatives")
 assert(adopt_rechecked_thresholds,"Group1 must recheck current floor owners before adopting missing-only thresholds")

 var seen:Dictionary={}
 for q in p.door_bindings:
  assert(entry_authorization.has(q.name)and entry_authorization[q.name] is Callable and entry_authorization[q.name].is_valid(),"Each gate needs owner entry authorization")
  assert(resolved_ids.has(q.name)and not str(resolved_ids[q.name]).is_empty());assert(not seen.has(str(resolved_ids[q.name])));seen[str(resolved_ids[q.name])]=true
 for file in p.original_source_model_pins:assert(FileAccess.get_sha256("res://assets/models/"+file)==p.original_source_model_pins[file],"Wall source differs from the verified exact preimage")
 for q in p.exact_runtime_preimages:
  var mesh:MeshInstance3D=ship.get_node_or_null(q.path);assert(mesh!=null);var b:AABB=mesh.global_transform*mesh.get_aabb();assert(b.position.distance_to(vec(q.min))<.0001 and b.end.distance_to(vec(q.max))<.0001);mesh.free()
 var n:=Node3D.new();n.name="Group3CommonsCrossings";space.add_child(n);n.set_meta("new_registered_berths",0);n.set_meta("whole_network_accepted",false)
 for file in["AST-STF-G3-061.glb","AST-STF-G3-063.glb"]:
  assert(FileAccess.get_sha256("res://assets/models/group3_commons_crossings_20261012/"+file)==p.model_pins[file]);var visual:Node3D=(load("res://assets/models/group3_commons_crossings_20261012/"+file)as PackedScene).instantiate();visual.name=file.trim_suffix(".glb");n.add_child(visual)
  for mesh in visual.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
 for q in p.door_bindings:
  var door:Node3D=load("res://scripts/group3_starboard3_private_20261011/entry_gate.gd").new();door.name=q.name;door.position=vec(q.position);door.rotation.y=q.yaw;door.persistent_id=StringName(resolved_ids[q.name]);door.can_enter=entry_authorization[q.name];door.open_fraction=0;door.desired_open=false;n.add_child(door)
 return n
