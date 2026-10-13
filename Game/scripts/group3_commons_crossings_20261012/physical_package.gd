extends RefCounted
static func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_commons_crossings_20261012/CROSSINGS.json"))
 var space:Node3D=ship.get_node("ShipSpace");assert(space.get_node_or_null("Group3CommonsCrossings")==null)
 assert(space.get_node_or_null("Group3D03RemainingStreets")!=null)
 var scenes:Dictionary={}
 for file in p.model_pins:
  assert(FileAccess.get_sha256("res://assets/models/group3_commons_crossings_20261012/"+str(file))==str(p.model_pins[file]))
  var packed:PackedScene=load("res://assets/models/group3_commons_crossings_20261012/"+str(file));assert(packed!=null);scenes[file]=packed
 for file in p.original_source_model_pins:assert(FileAccess.get_sha256("res://assets/models/"+str(file))==str(p.original_source_model_pins[file]))
 var preimages:Array[MeshInstance3D]=[]
 for q in p.exact_runtime_preimages:
  var mesh:MeshInstance3D=ship.get_node_or_null(str(q.path));assert(mesh!=null)
  var b:AABB=mesh.global_transform*mesh.get_aabb();assert(b.position.distance_to(vec(q.min))<.0001 and b.end.distance_to(vec(q.max))<.0001);preimages.append(mesh)
 assert(preimages.size()==6)
 # Verify every resource and exact current preimage before the six declared wall mutations.
 var n:=Node3D.new();n.name="Group3CommonsCrossings";space.add_child(n)
 n.set_meta("new_registered_berths",0);n.set_meta("whole_network_accepted",false);n.set_meta("operating_gates_admitted",false);n.set_meta("authoritative_identity_mapping",false);n.set_meta("default_main_adoption",true)
 for mesh in preimages:mesh.free()
 for file in ["AST-STF-G3-061.glb","AST-STF-G3-062.glb","AST-STF-G3-063_current_receiving_successor001.glb"]:
  var visual:Node3D=scenes[file].instantiate();visual.name=file.trim_suffix(".glb");n.add_child(visual)
  for mesh in visual.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
 # Retain authored closed leaf meshes and exact contacts. No unresolved IDs, authorization provider or operation backend is created.
 return n
