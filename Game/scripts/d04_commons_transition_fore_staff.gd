extends RefCounted
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func model(owner:Node3D,spec:Dictionary)->Node3D:
 var n:Node3D=load("res://assets/models/"+str(spec.export)).instantiate();owner.add_child(n)
 for mesh:MeshInstance3D in n.find_children("*","MeshInstance3D",true,false):
  var item:Dictionary=spec.collision_policy[str(mesh.name)]
  if item.collide:load("res://scripts/static_contact_cache.gd").attach(mesh)
  if item.category=="stair_walk_surface":mesh.visible=false
 return n
static func fore_build(ship:Node3D,candidate_only:bool=false)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_COMMONS_TRANSITION_AND_FORE_STAFF.json"))
 if not p.active and not candidate_only:return null
 if ship.has_node("D04PortForwardStaffCourtConnection"):return ship.get_node("D04PortForwardStaffCourtConnection")
 if p.active:assert(FileAccess.get_sha256("res://artifacts/d04_commons_transition_fore_staff_geometry.json")==p.sealed_receipt_sha256)
 assert(FileAccess.get_sha256("res://assets/models/"+str(p.fore_structure.export))==p.fore_structure.export_sha256)
 var remove:Array[MeshInstance3D]=[]
 for pre in p.fore_runtime_preimages:
  var mesh:MeshInstance3D=ship.get_node(pre.relative_path);var faces:PackedVector3Array=mesh.mesh.get_faces();assert(faces.size()==pre.world_triangle_vertices.size())
  for i in range(faces.size()):assert((mesh.global_transform*faces[i]).distance_to(v(pre.world_triangle_vertices[i]))<.00001)
  remove.append(mesh)
 var owner:=Node3D.new();owner.name="D04PortForwardStaffCourtConnection";ship.add_child(owner);owner.set_meta("persistent_id","D04_port_forward_staff_court_connection_001")
 for mesh in remove:mesh.free()
 var owned:=model(owner,p.fore_structure);var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
 for i in range(p.fore_private_original_gates.size()):
  var gate:Node3D=load("res://scripts/d04_court_service_gate.gd").new();gate.name="PriorCourtGate_"+str(i);gate.persistent_id=StringName("D04_southern_east_court_service_gate_"+str(i));gate.authored_visual=owned;gate.fitting=p.fore_private_original_gates[i];gate.custodian=weakref(actor);owner.add_child(gate)
 for spec in p.fore_new_gates:
  var gate:Node3D=load("res://scripts/d04_physical_service_fitting.gd").new();gate.name=spec.name;gate.persistent_id=StringName(spec.id);gate.authored_visual=owned;gate.fitting=spec;gate.custodian=weakref(actor);owner.add_child(gate)
 owner.set_meta("production_private_consent_provider_available",false);owner.set_meta("home_tool_hatches_or_panes_installed",false);owner.set_meta("new_floor_m2",p.new_floor_m2);return owner
static func commons_candidate(ship:Node3D)->Node3D:
 # Physical fit candidate only. There is no production caller or rear-route activation.
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_COMMONS_TRANSITION_AND_FORE_STAFF.json"));assert(not p.commons_candidate_active);assert(FileAccess.get_sha256("res://assets/models/"+str(p.commons_structure.export))==p.commons_structure.export_sha256)
 var owner:=Node3D.new();owner.name="D04CommonsShortTransitionsTestOnly";ship.add_child(owner);var owned:=model(owner,p.commons_structure);var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
 for spec in p.commons_gates:
  var gate:Node3D=load("res://scripts/d04_physical_service_fitting.gd").new();gate.name=spec.name;gate.persistent_id=StringName(spec.id);gate.authored_visual=owned;gate.fitting=spec;gate.custodian=weakref(actor);owner.add_child(gate)
 return owner
