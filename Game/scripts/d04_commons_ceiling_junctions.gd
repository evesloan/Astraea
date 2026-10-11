extends RefCounted
static func build(ship:Node3D,candidate_only:bool=false)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_COMMONS_CEILING_JUNCTIONS.json"))
 if not p.active and not candidate_only:return null
 var districts:Node3D=ship.get_node("ShipSpace/Districts")
 if districts.has_node("D04CommonsCeilingJunctions"):return districts.get_node("D04CommonsCeilingJunctions")
 if p.active:assert(FileAccess.get_sha256("res://artifacts/d04_commons_ceiling_junctions_geometry.json")==p.sealed_receipt_sha256)
 for file in p.model_pins:assert(FileAccess.get_sha256("res://assets/models/"+file)==p.model_pins[file])
 var n:=Node3D.new();n.name="D04CommonsCeilingJunctions";districts.add_child(n);load("res://scripts/d04_port_forward_homes_fifth.gd").visual(n,p.structure_file,p.structure.collision_policy);return n
