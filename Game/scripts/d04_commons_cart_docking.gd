extends RefCounted
static func build(ship:Node3D)->Node3D:
 var districts:Node3D=ship.get_node("ShipSpace/Districts")
 if districts.has_node("D04CommonsCartDocks"):return districts.get_node("D04CommonsCartDocks")
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_COMMONS_CART_DOCKING.json"))
 if p.active:
  assert(FileAccess.get_sha256("res://artifacts/d04_commons_docks_sealed.json")==p.sealed_receipt_sha256)
  var gate:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://artifacts/d04_commons_docks_sealed.json"));assert(gate.status=="PASS")
 var root:=Node3D.new();root.name="D04CommonsCartDocks";districts.add_child(root)
 assert(FileAccess.get_sha256("res://assets/models/"+str(p.structure.model_file))==p.structure.model_sha256)
 load("res://scripts/d04_port_forward_commons_service.gd").visual(root,p.structure.model_file,p.structure.collision_policy)
 for dock in p.docks:
  var sign:=Label3D.new();sign.name=dock.name+"DockLabel";sign.text="CLEAN STOCK / PARK"if dock.name=="Clean"else"CLOSED RETURNS / PARK";sign.position=Vector3(dock.position[0],18.8,-356.45);sign.rotation.y=PI;sign.pixel_size=.003;sign.font_size=24;root.add_child(sign)
 root.set_meta("new_floor_m2",0);root.set_meta("new_rest_places",0);root.set_meta("protected_D04_D07_shaft_blank",true);root.set_meta("cart_vertical_accepted",false);root.set_meta("whole_neighborhood_complete",false)
 return root
