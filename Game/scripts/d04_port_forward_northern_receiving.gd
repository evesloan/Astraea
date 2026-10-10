extends RefCounted
static func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D)->Node3D:
 var districts:Node3D=ship.get_node("ShipSpace/Districts")
 if districts.has_node("D04PortForwardNorthernReceiving"):return districts.get_node("D04PortForwardNorthernReceiving")
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_FORWARD_NORTHERN_RECEIVING.json"))
 assert(FileAccess.get_sha256("res://assets/models/"+str(p.model_file))==p.model_sha256)
 var original:Node=ship.find_child("D04PortForwardReceiving",true,false);assert(original!=null)
 if p.open_receiving_connection:
  assert(FileAccess.get_sha256("res://artifacts/d04_port_forward_northern_sealed.json")==p.sealed_receipt_sha256)
  var gate:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://artifacts/d04_port_forward_northern_sealed.json"));assert(gate.status=="PASS"and gate.model_sha256==p.model_sha256)
  assert(FileAccess.get_sha256("res://assets/models/D04_PORT_FORWARD_RECEIVING_r001.glb")==p.source_pins["Game/assets/models/D04_PORT_FORWARD_RECEIVING_r001.glb"])
  for record in p.guard_preimages:
   var mesh:MeshInstance3D=original.find_child(str(record.name),true,false);assert(mesh!=null)
   var lo:=Vector3(INF,INF,INF);var hi:=-lo
   for vertex in record.verts:lo=lo.min(vec(vertex));hi=hi.max(vec(vertex))
   var bounds:AABB=mesh.global_transform*mesh.get_aabb();assert(bounds.position.distance_to(lo)<.00005 and bounds.end.distance_to(hi)<.00005);mesh.free()
 var root:=Node3D.new();root.name="D04PortForwardNorthernReceiving";districts.add_child(root)
 root.set_meta("house_id",p.house_id);root.set_meta("new_guest_units",0);root.set_meta("new_rest_places",0);root.set_meta("new_interiors_built",0);root.set_meta("remaining_interiors",10);root.set_meta("remaining_reserved_rests",13);root.set_meta("primary_load_accepted",false);root.set_meta("cart_safe_vertical_accepted",false);root.set_meta("always_present_support_and_receiving",true)
 var visual:Node3D=load("res://assets/models/"+str(p.model_file)).instantiate();root.add_child(visual)
 for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
  var name:String=str(mesh.name);assert(p.collision_policy.has(name));var spec:Dictionary=p.collision_policy[name]
  if spec.collide:load("res://scripts/static_contact_cache.gd").attach(mesh)
  if spec.category=="light_source":mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
 for item in p.lights:
  assert(visual.find_child(str(item.name),true,false)!=null)
  var lamp:=SpotLight3D.new();root.add_child(lamp);lamp.position=vec(item.at);lamp.rotation.x=-PI/2;lamp.light_color=Color(1,.92,.81);lamp.light_energy=.9;lamp.spot_range=10;lamp.spot_angle=75;lamp.shadow_enabled=false
 return root
