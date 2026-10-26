extends RefCounted
static func add_supports(ship:Node3D)->void:
 var owner:=Node3D.new();owner.name="LowerArrivalsSourceReceiving_UNSELECTED"
 var districts:Node3D=ship.get_node("ShipSpace/Districts")
 assert(not districts.has_node(owner.name));districts.add_child(owner)
 var proof:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://grand_arrivals_tram_20261026/integration_r001/WORLD_RECEIVING.json"))
 for path:String in proof.supports:
  assert(FileAccess.get_sha256(path)==str(proof.supports[path]))
  var visual:Node3D=load("res://grand_arrivals_tram_20261026/integration_r001/assembly.gd").raw_model(path)
  assert(visual!=null);owner.add_child(visual)
  load("res://scripts/static_contact_cache.gd").attach_group(visual,visual.find_children("*","MeshInstance3D",true,false))
 owner.set_meta("operation_holds",proof.holds)
