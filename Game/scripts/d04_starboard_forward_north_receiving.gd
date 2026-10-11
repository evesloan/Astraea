extends RefCounted
static func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D,candidate_only:bool=false)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_STARBOARD_FORWARD_NORTH_RECEIVING.json"))
 if not p.active and not candidate_only:return null
 var parent:Node3D=ship.get_node("ShipSpace/Districts")
 if parent.has_node("D04StarboardForwardNorthReceiving"):return parent.get_node("D04StarboardForwardNorthReceiving")
 if p.active:
  assert(FileAccess.get_sha256("res://artifacts/d04_starboard_north_receiving_geometry.json")==p.sealed_receipt_sha256)
  var receipt:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://artifacts/d04_starboard_north_receiving_geometry.json"));assert(receipt.status=="PASS"and receipt.model_sha256==p.native_export_record.export_sha256)
 assert(FileAccess.get_sha256("res://assets/models/"+p.native_export_record.export)==p.native_export_record.export_sha256)
 var root:=Node3D.new();root.name="D04StarboardForwardNorthReceiving";parent.add_child(root)
 load("res://scripts/d04_port_forward_commons_service.gd").visual(root,p.native_export_record.export,p.native_export_record.collision_policy)
 for item in p.lights:
  var mesh:MeshInstance3D=root.find_child(item.name,true,false);assert(mesh!=null);mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
  var light:=SpotLight3D.new();light.name=item.name+"_Light";root.add_child(light);light.position=vec(item.position);light.rotation.x=-PI/2;light.light_color=Color(1,.92,.81);light.light_energy=.8;light.spot_range=8;light.spot_angle=75;light.shadow_enabled=false
 for spec in [{"text":"STARBOARD-FORWARD\nNorth receiving","position":[40.55,17.75,-289.945],"yaw":0.0},{"text":"CLEAN STOCK","position":[49.34,19.4,-287.87],"yaw":0.0},{"text":"CLOSED RETURNS","position":[55.725,19.4,-287.87],"yaw":0.0}]:
  var label:=Label3D.new();label.name="ReceivingSign"+str(root.get_child_count());label.text=spec.text;label.font_size=48;label.pixel_size=.0025;label.position=vec(spec.position);label.rotation.y=spec.yaw;root.add_child(label)
 root.set_meta("house_id",p.house_id);root.set_meta("preserved_guest_allocations",20);root.set_meta("preserved_proposed_rests",25);root.set_meta("rooms_built",0);root.set_meta("new_capacity",0);root.set_meta("new_floor_m2",p.new_floor_m2);root.set_meta("distinct_local_clean_closed_used_cells",true);root.set_meta("shared_public_service_approach",true);root.set_meta("dedicated_segregation_accepted",false);root.set_meta("primary_load_accepted",false);root.set_meta("whole_neighborhood_complete",false)
 return root
