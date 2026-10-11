extends RefCounted
static func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D,candidate_only:bool=false)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_AFT_CORE_THRESHOLD.json"))
 if not p.active and not candidate_only:return null
 var districts:Node3D=ship.get_node("ShipSpace/Districts")
 if districts.has_node("D04PortAftCoreThreshold"):return districts.get_node("D04PortAftCoreThreshold")
 if p.active:
  assert(FileAccess.get_sha256("res://artifacts/d04_port_aft_core_threshold_geometry.json")==p.sealed_receipt_sha256)
  var g:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://artifacts/d04_port_aft_core_threshold_geometry.json"));assert(g.status=="PASS"and g.model_pins==p.model_pins)
 for f in p.model_pins:assert(FileAccess.get_sha256("res://assets/models/"+f)==p.model_pins[f])
 var core:Node3D=districts.get_node(p.core_root);var enclosure:Node3D=core.get_node("PrimaryCoreEnclosure")
 if candidate_only:
  assert(enclosure.get_meta("catalogue_file")==p.original_core_file);enclosure.free();ship.model(core,p.core_derivative_file,"PrimaryCoreEnclosure",vec(p.core_origin))
 else:assert(enclosure.get_meta("catalogue_file")==p.core_derivative_file)
 var neighborhood:Node3D=districts.get_node("D04PortAftHabitatNeighborhood")
 for pre in p.original_runtime_guards:
  var mesh:MeshInstance3D=neighborhood.find_child(pre.name,true,false);assert(mesh!=null);var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for v in pre.verts:lo=lo.min(vec(v));hi=hi.max(vec(v))
  var b:AABB=mesh.global_transform*mesh.get_aabb();assert(b.position.distance_to(lo)<.0001 and b.end.distance_to(hi)<.0001);mesh.free()
 var n:=Node3D.new();n.name="D04PortAftCoreThreshold";districts.add_child(n);n.set_meta("persistent_id","d04_port_aft_northern_threshold_001");n.set_meta("new_public_floor_m2",p.new_floor_m2)
 load("res://scripts/d04_port_forward_homes_fifth.gd").visual(n,p.collar_file,p.collar_structure.collision_policy)
 for item in p.lights:
  var mesh:MeshInstance3D=n.find_child(item.name,true,false);assert(mesh!=null);mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
  var light:=SpotLight3D.new();light.name=item.name+"_Light";n.add_child(light);light.position=vec(item.at);light.rotation.x=-PI/2;light.light_color=Color(1,.94,.83);light.light_energy=.75;light.spot_range=5;light.spot_angle=70;light.shadow_enabled=false
 return n
