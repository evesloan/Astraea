extends RefCounted
static func build(ship:Node3D)->Node3D:
 var districts:Node3D=ship.get_node("ShipSpace/Districts")
 if districts.has_node("D04SocialDayroom"):return districts.get_node("D04SocialDayroom")
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_SOCIAL_DAYROOM.json"))
 if p.open_gallery_connection:
  assert(FileAccess.get_sha256("res://artifacts/d04_social_dayroom_sealed.json")==p.sealed_receipt_sha256)
  var gate:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://artifacts/d04_social_dayroom_sealed.json"));assert(gate.status=="PASS")
  for pre in p.preimages:
   var mesh:MeshInstance3D=ship.find_child(pre.name,true,false);assert(mesh!=null)
   var lo:=Vector3(INF,INF,INF);var hi:=-lo
   for v in pre.verts:var at:=Vector3(v[0],v[1],v[2]);lo=lo.min(at);hi=hi.max(at)
   var bounds:=mesh.global_transform*mesh.get_aabb();assert(bounds.position.distance_to(lo)<.00004 and bounds.end.distance_to(hi)<.00004);mesh.free()
 var room:=Node3D.new();room.name="D04SocialDayroom";districts.add_child(room)
 for spec in [p.structure,p.entry_successors]if p.open_gallery_connection else[p.structure]:
  assert(FileAccess.get_sha256("res://assets/models/"+str(spec.model_file))==spec.model_sha256)
  load("res://scripts/d04_port_forward_commons_service.gd").visual(room,spec.model_file,spec.collision_policy)
 for item in p.lights:
  var lamp:=SpotLight3D.new();lamp.name=item.name;room.add_child(lamp);lamp.position=Vector3(item.at[0],item.at[1],item.at[2]);lamp.rotation.x=-PI/2;lamp.light_color=Color(1,.92,.81);lamp.light_energy=.8;lamp.spot_range=7;lamp.spot_angle=75
 room.set_meta("programme_key",p.programme_key);room.set_meta("new_floor_m2",p.new_floor_m2);room.set_meta("preserved_homes",20);room.set_meta("preserved_rest_places",25);room.set_meta("whole_neighborhood_complete",false)
 return room
