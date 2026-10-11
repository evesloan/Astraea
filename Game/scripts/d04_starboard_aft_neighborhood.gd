extends RefCounted
static func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D,candidate_only:bool=false)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_STARBOARD_AFT_NEIGHBORHOOD.json"))
 if not p.active and not candidate_only:return null
 var districts:Node3D=ship.get_node("ShipSpace/Districts")
 if districts.has_node("D04StarboardAftHabitatNeighborhood"):return districts.get_node("D04StarboardAftHabitatNeighborhood")
 if p.active:
  assert(FileAccess.get_sha256("res://artifacts/d04_starboard_aft_neighborhood_geometry.json")==p.sealed_receipt_sha256)
  var gate:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://artifacts/d04_starboard_aft_neighborhood_geometry.json"));assert(gate.status=="PASS"and gate.model_pins==p.model_pins)
 var root:=Node3D.new();root.name="D04StarboardAftHabitatNeighborhood";districts.add_child(root)
 for key in ["combinedstructure_structure","co_structure"]:
  var spec:Dictionary=p[key];assert(FileAccess.get_sha256("res://assets/models/"+spec.model_file)==spec.model_sha256);load("res://scripts/d04_port_forward_homes_fifth.gd").visual(root,spec.model_file,spec.collision_policy)
 for quad in p.walking_contacts:
  var points:Array[Vector3]=[]
  for at in quad:points.append(vec(at))
  load("res://scripts/aquatic_section.gd")._contact(root,points)
 for item in p.lights:
  var mesh:MeshInstance3D=root.find_child(str(item.name).replace(".","_"),true,false);assert(mesh!=null);mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
  var light:=SpotLight3D.new();light.name=item.name+"_Light";root.add_child(light);light.position=vec(item.at);light.rotation.x=-PI/2;light.light_color=Color(.86,.93,1)if item.staff else Color(1,.92,.81);light.light_energy=.8;light.spot_range=7;light.spot_angle=75;light.shadow_enabled=false
 for r in p.rooms:
  assert(FileAccess.get_sha256("res://assets/models/"+r.model_file)==r.model_sha256)
  var home:=Node3D.new();home.name=r.allocation.proposed_runtime_id;root.add_child(home);home.set_meta("allocation_sha256",r.allocation.allocation_sha256);home.set_meta("rest_slot_ids",r.allocation.proposed_rest_slot_ids);home.set_meta("reserved_rest_count",r.allocation.proposed_rest_place_count);home.set_meta("species_ready",false);home.set_meta("historical_save_identity_recovered",false)
  load("res://scripts/d04_port_forward_homes_fifth.gd").visual(home,r.model_file,r.collision_policy)
  var door:Node3D=load("res://scripts/guest_entry_door.gd").new();door.name="HomeEntry";door.open_fraction=0;door.desired_open=false;door.persistent_id=StringName(r.entry.persistent_id);door.position=vec(r.entry.origin);door.rotation.y=r.entry.yaw;door.door_description="habitat entry";home.add_child(door)
  for item in r.lights:
   var mesh:MeshInstance3D=home.find_child(str(item.name).replace(".","_"),true,false);assert(mesh!=null);mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
   var light:=SpotLight3D.new();light.name=item.name+"_Light";home.add_child(light);light.position=vec(item.at);light.rotation.x=-PI/2;light.light_color=Color(1,.92,.81);light.light_energy=.8;light.spot_range=7;light.spot_angle=75;light.shadow_enabled=false
 root.set_meta("preserved_home_allocations",20);root.set_meta("preserved_reserved_rests",25);root.set_meta("primary_engineering_accepted",false);root.set_meta("dedicated_staff_network_complete",false)
 return root
