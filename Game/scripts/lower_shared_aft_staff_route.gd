extends RefCounted
static func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D,candidate_only:bool=false)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/LOWER_SHARED_AFT_STAFF_ROUTE.json"))
 if not p.active and not candidate_only:return null
 var districts:Node3D=ship.get_node("ShipSpace/Districts")
 if districts.has_node("LowerSharedAftStaffRoute"):return districts.get_node("LowerSharedAftStaffRoute")
 if p.active:
  assert(FileAccess.get_sha256("res://artifacts/lower_shared_aft_staff_route_geometry.json")==p.sealed_receipt_sha256)
  assert(JSON.parse_string(FileAccess.get_file_as_string("res://artifacts/lower_shared_aft_staff_route_geometry.json")).status=="PASS")
 for f in p.model_pins:assert(FileAccess.get_sha256("res://assets/models/"+f)==p.model_pins[f])
 var n:=Node3D.new();n.name="LowerSharedAftStaffRoute";districts.add_child(n);n.set_meta("persistent_id","d01_shared_aft_staff_route_001");n.set_meta("shared_upstream_and_downstream",true);n.set_meta("full_clean_used_network_accepted",false)
 load("res://scripts/d04_port_forward_homes_fifth.gd").visual(n,p.structure_file,p.structure.collision_policy)
 for item in p.service_doors:
  var door:Node3D=load("res://scripts/service_door.gd").new();door.name=item.name;door.position=vec(item.at);door.rotation.y=item.yaw;door.persistent_id=StringName(item.id);door.open_fraction=0.0;door.desired_open=false;n.add_child(door)
 for item in p.lights:
  var light:=SpotLight3D.new();light.name=item.name+"_Light";n.add_child(light);light.position=vec(item.at);light.rotation.x=-PI/2;light.light_color=Color(.82,.90,1);light.light_energy=.8;light.spot_range=7;light.spot_angle=75;light.shadow_enabled=false
 for row in [{"name":"Central","at":[-51,1.8,77.72],"text":"AFT STAFF ROUTE  |  SHARED"},{"name":"Aft","at":[-7,1.8,301.72],"text":"CENTRAL SERVICE  |  SHARED"}]:
  var sign:=Label3D.new();sign.name=row.name+"SharedRouteSign";sign.text=row.text;sign.position=vec(row.at);sign.font_size=36;sign.pixel_size=.003;n.add_child(sign)
 return n
