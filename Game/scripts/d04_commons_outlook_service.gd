extends RefCounted
static func build(ship:Node3D)->Node3D:
 var districts:Node3D=ship.get_node("ShipSpace/Districts")
 if districts.has_node("D04CommonsGardenOutlook"):return districts.get_node("D04CommonsGardenOutlook")
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_COMMONS_OUTLOOK_SERVICE.json"))
 if p.active:
  assert(FileAccess.get_sha256("res://artifacts/d04_commons_outlook_sealed.json")==p.sealed_receipt_sha256)
  var gate:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://artifacts/d04_commons_outlook_sealed.json"));assert(gate.status=="PASS")
  var mesh:MeshInstance3D=ship.find_child(str(p.preimage.name),true,false);assert(mesh!=null)
  var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for v in p.preimage.verts:var at:=Vector3(v[0],v[1],v[2]);lo=lo.min(at);hi=hi.max(at)
  var bounds:=mesh.global_transform*mesh.get_aabb();assert(bounds.position.distance_to(lo)<.00004 and bounds.end.distance_to(hi)<.00004);mesh.free()
 var root:=Node3D.new();root.name="D04CommonsGardenOutlook";districts.add_child(root)
 assert(FileAccess.get_sha256("res://assets/models/"+str(p.structure.model_file))==p.structure.model_sha256)
 load("res://scripts/d04_port_forward_commons_service.gd").visual(root,p.structure.model_file,p.structure.collision_policy)
 root.set_meta("new_floor_m2",0);root.set_meta("new_rest_places",0);root.set_meta("dedicated_clean_used_separation_accepted",false);root.set_meta("whole_commons_complete",false)
 return root
