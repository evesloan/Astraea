extends RefCounted
static func build(ship:Node3D)->Node3D:
 assert(ship.get_node_or_null("ShipSpace/ApprovedSixHouseReceiving")!=null)
 assert(ship.get_node_or_null("ShipSpace/AftRetainedAdjunctCare")==null)
 var root:=Node3D.new();root.name="AftRetainedAdjunctCare";ship.get_node("ShipSpace").add_child(root)
 root.set_meta("capacity_migrated",false);root.set_meta("operating_private_admission_or_service",false);root.set_meta("default_main_adoption",true)
 for key in["port_aft_upper_house","starboard_aft_upper_house"]:
  var contract:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_completion/contracts/"+key+".json"))
  assert(FileAccess.get_sha256("res://assets/group2_completion/"+key+".glb")==contract.export_sha256)
  var section:Node3D=load("res://scripts/group2_completion/package.gd").build_section(root,key)
  load("res://scripts/group2_care_programmes/package.gd").build(section,key,true)
  var lights:Array[Light3D]=[]
  for light:Light3D in section.find_children("*","Light3D",true,false):lights.append(light)
  load("res://scripts/receiving_source_lights.gd").register(lights,ship)
 return root
