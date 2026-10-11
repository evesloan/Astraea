extends RefCounted
static func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D,candidate_only:bool=false)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_STARBOARD_FORWARD_SOUTH_PACKAGE.json"))
 if not p.active and not candidate_only:return null
 var districts:Node3D=ship.get_node("ShipSpace/Districts")
 if districts.has_node("D04StarboardSouthHomeCandidates"):return districts.get_node("D04StarboardSouthHomeCandidates")
 if p.active:
  assert(FileAccess.get_sha256("res://artifacts/d04_starboard_south_package_geometry.json")==p.sealed_receipt_sha256)
  var gate:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://artifacts/d04_starboard_south_package_geometry.json"));assert(gate.status=="PASS"and gate.model_pins==p.model_pins)
 var original:Node3D=districts.get_node("D04StarboardForwardNorthReceiving")
 assert(FileAccess.get_sha256("res://assets/models/D04_STARBOARD_NORTH_RECEIVING_r001.glb")==p.source_pins["Game/assets/models/D04_STARBOARD_NORTH_RECEIVING_r001.glb"])
 for pre in p.north_end_guard_preimages:
  var mesh:MeshInstance3D=original.find_child(str(pre.name).replace(".","_"),true,false);assert(mesh!=null)
  var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for v in pre.preimage.verts:lo=lo.min(vec(v));hi=hi.max(vec(v))
  var b:AABB=mesh.global_transform*mesh.get_aabb();assert(b.position.distance_to(lo)<.00006 and b.end.distance_to(hi)<.00006);mesh.free()
 var root:=Node3D.new();root.name="D04StarboardSouthHomeCandidates";districts.add_child(root)
 var receiving:=Node3D.new();receiving.name="ReceivingFrame";root.add_child(receiving)
 assert(FileAccess.get_sha256("res://assets/models/"+p.receiving_structure.model_file)==p.receiving_structure.model_sha256)
 load("res://scripts/d04_port_forward_homes_fifth.gd").visual(receiving,p.receiving_structure.model_file,p.receiving_structure.collision_policy)
 for pre in p.guard_preimages:
  var mesh:MeshInstance3D=receiving.find_child(str(pre.name).replace(".","_"),true,false);assert(mesh!=null)
  var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for v in pre.preimage.verts:lo=lo.min(vec(v));hi=hi.max(vec(v))
  var b:AABB=mesh.global_transform*mesh.get_aabb();assert(b.position.distance_to(lo)<.00006 and b.end.distance_to(hi)<.00006);mesh.free()
 for item in p.receiving_lights:
  var mesh:MeshInstance3D=receiving.find_child(item.name,true,false);assert(mesh!=null);mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
  var light:=SpotLight3D.new();light.name=item.name+"_Light";receiving.add_child(light);light.position=vec(item.at);light.rotation.x=-PI/2;light.light_color=Color(1,.92,.81);light.light_energy=.8;light.spot_range=7;light.spot_angle=75;light.shadow_enabled=false
 var sign:=Label3D.new();sign.text="STARBOARD-FORWARD\nSouthern receiving";sign.position=Vector3(40.3,17.75,-406.50);sign.font_size=48;sign.pixel_size=.0025;receiving.add_child(sign)
 var structure:=Node3D.new();structure.name="StructureAndCourts";root.add_child(structure)
 for spec in [p.structure,p.entry_guard_successor]:
  assert(FileAccess.get_sha256("res://assets/models/"+spec.model_file)==spec.model_sha256)
  load("res://scripts/d04_port_forward_homes_fifth.gd").visual(structure,spec.model_file,spec.collision_policy)
 for r in p.rooms:
  assert(FileAccess.get_sha256("res://assets/models/"+r.model_file)==r.model_sha256)
  var home:=Node3D.new();home.name=r.allocation.proposed_runtime_id;root.add_child(home)
  home.set_meta("allocation_sha256",r.allocation.allocation_sha256);home.set_meta("rest_slot_ids",r.allocation.proposed_rest_slot_ids);home.set_meta("reserved_rest_count",r.allocation.proposed_rest_place_count);home.set_meta("species_ready",false);home.set_meta("historical_save_identity_recovered",false)
  load("res://scripts/d04_port_forward_homes_fifth.gd").visual(home,r.model_file,r.collision_policy)
  var door:Node3D=load("res://scripts/guest_entry_door.gd").new();door.name="HomeEntry";door.open_fraction=0;door.desired_open=false;door.persistent_id=StringName(r.entry.persistent_id);door.position=vec(r.entry.origin);door.rotation.y=r.entry.yaw;door.door_description="habitat entry";home.add_child(door)
  for item in r.lights:
   var mesh:MeshInstance3D=home.find_child(str(item.name),true,false);assert(mesh!=null);mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
   var light:=SpotLight3D.new();light.name=item.name+"_Light";home.add_child(light);light.position=vec(item.at);light.rotation.x=-PI/2;light.light_color=Color(1,.92,.81);light.light_energy=.8;light.spot_range=7;light.spot_angle=75;light.shadow_enabled=false
 root.set_meta("house_id",p.house_id);root.set_meta("total_house_reservation_count",20);root.set_meta("capacity_preserved",25);root.set_meta("physical_candidates",10);root.set_meta("fitted_reserved_rests",12);root.set_meta("physical_house_proposals_after_batch",20);root.set_meta("remaining_interiors",0);root.set_meta("full_commons_unbuilt",true);root.set_meta("dedicated_service_circulation_unfinished",true);root.set_meta("species_ready_rooms",0);root.set_meta("primary_load_accepted",false)
 return root
