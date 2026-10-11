extends RefCounted
static func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D,candidate_only:bool=false)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_STARBOARD_FULL_COMMONS.json"))
 if not p.active and not candidate_only:return null
 var districts:Node3D=ship.get_node("ShipSpace/Districts")
 if districts.has_node("D04StarboardFullCommons"):return districts.get_node("D04StarboardFullCommons")
 if p.active:
  assert(FileAccess.get_sha256("res://artifacts/d04_starboard_full_commons_geometry.json")==p.sealed_receipt_sha256)
  var gate:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://artifacts/d04_starboard_full_commons_geometry.json"));assert(gate.status=="PASS"and gate.model_pins==p.model_pins)
 var original:Node3D=districts.get_node("D04StarboardSouthHomeCandidates/ReceivingFrame")
 assert(FileAccess.get_sha256("res://assets/models/D04_STARBOARD_SOUTH_RECEIVING_r003.glb")==p.source_pins["Game/assets/models/D04_STARBOARD_SOUTH_RECEIVING_r003.glb"])
 for pre in p.preimages:
  var mesh:MeshInstance3D=original.find_child(str(pre.name).replace(".","_"),true,false);assert(mesh!=null)
  var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for v in pre.preimage.verts:lo=lo.min(vec(v));hi=hi.max(vec(v))
  var b:AABB=mesh.global_transform*mesh.get_aabb();assert(b.position.distance_to(lo)<.00006 and b.end.distance_to(hi)<.00006);mesh.free()
 var root:=Node3D.new();root.name="D04StarboardFullCommons";districts.add_child(root)
 assert(FileAccess.get_sha256("res://assets/models/"+p.structure.model_file)==p.structure.model_sha256)
 load("res://scripts/d04_port_forward_homes_fifth.gd").visual(root,p.structure.model_file,p.structure.collision_policy)
 for item in p.lights:
  var mesh:MeshInstance3D=root.find_child(str(item.name).replace(".","_"),true,false);assert(mesh!=null);mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
  var light:=SpotLight3D.new();light.name=item.name+"_Light";root.add_child(light);light.position=vec(item.at);light.rotation.x=-PI/2;light.light_color=Color(.86,.93,1)if item.staff else Color(1,.92,.81);light.light_energy=.8;light.spot_range=7;light.spot_angle=75;light.shadow_enabled=false
 root.set_meta("preserved_home_allocations",20);root.set_meta("preserved_reserved_rests",25);root.set_meta("primary_engineering_accepted",false);root.set_meta("dedicated_staff_network_complete",false)
 return root
