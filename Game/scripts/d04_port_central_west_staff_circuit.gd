extends RefCounted
static func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D,candidate_only:bool=false)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_CENTRAL_WEST_STAFF_CIRCUIT.json"))
 if not p.active and not candidate_only:return null
 var districts:Node3D=ship.get_node("ShipSpace/Districts")
 if districts.has_node("D04PortCentralWestStaffCircuit"):return districts.get_node("D04PortCentralWestStaffCircuit")
 if p.active:assert(FileAccess.get_sha256("res://artifacts/d04_port_central_west_staff_circuit_geometry.json")==p.sealed_receipt_sha256)
 for file in p.model_pins:assert(FileAccess.get_sha256("res://assets/models/"+file)==p.model_pins[file])
 var remove:Array[MeshInstance3D]=[]
 for pre in p.runtime_preimages:
  var mesh:MeshInstance3D=districts.get_node(pre.source_root).find_child(pre.name,true,false);assert(mesh!=null)
  var faces:PackedVector3Array=mesh.mesh.get_faces();assert(faces.size()==pre.world_triangle_vertices.size())
  for i in range(faces.size()):assert((mesh.global_transform*faces[i]).distance_to(vec(pre.world_triangle_vertices[i]))<.00001)
  remove.append(mesh)
 var n:=Node3D.new();n.name="D04PortCentralWestStaffCircuit";districts.add_child(n);n.set_meta("persistent_id","D04_port_central_west_staff_circuit_001")
 for mesh in remove:mesh.free()
 var helper=load("res://scripts/d04_port_forward_homes_fifth.gd");helper.visual(n,p.patch_file,p.patch.collision_policy);var owned:Node3D=helper.visual(n,p.structure_file,p.structure.collision_policy)
 var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
 for fitting in p.gates:
  var gate:Node3D=load("res://scripts/d04_physical_service_fitting.gd").new();gate.name=fitting.name;gate.persistent_id=StringName(fitting.id);gate.fitting=fitting;gate.authored_visual=owned;gate.custodian=weakref(player);n.add_child(gate)
 for item in p.lights:
  var light:=SpotLight3D.new();light.name=item.name+"_Light";n.add_child(light);light.position=vec(item.at);light.rotation.x=-PI/2;light.light_color=Color(.88,.94,1);light.light_energy=.8;light.spot_range=4;light.spot_angle=70;light.shadow_enabled=false
 n.set_meta("production_private_consent_provider_available",false);n.set_meta("new_floor_m2",p.new_floor_m2);n.set_meta("private_home_entry_authorized",false)
 return n
