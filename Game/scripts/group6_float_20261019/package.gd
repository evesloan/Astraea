extends RefCounted
static func build(annex:Node3D)->Node3D:
 assert(annex.get_node_or_null("OccupiedSourceFloats")==null)
 var pins:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_float_20261019/CONTRACT.json"))
 for file in pins.source_pins:assert(FileAccess.get_sha256("res://"+str(file))==str(pins.source_pins[file]))
 var root:=Node3D.new();root.name="OccupiedSourceFloats";annex.add_child(root)
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/AQUATIC_ANNEX_PLAN.json"))
 var fit:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_completion/FIT_CONTRACT.json"))
 var field:RefCounted=load("res://scripts/group6_completion/river_water_field.gd").new()
 for i in range(plan.boarding.size()):
  var dock:Dictionary=plan.boarding[i];var body:RigidBody3D=load("res://scripts/group6_float_20261019/float_body.gd").new()
  body.name=str(dock.id);body.dock=dock;body.entry=fit.river_entry_interfaces[i];body.field=field
  assert(str(body.entry.id)=="aquatic_river_"+str(dock.id)+"_entry_001")
  body.seat_local=load("res://scripts/group6_float_20261019/source_contacts.gd").build(body)
  # Surveyed clear positions next to retained entry ramps, derived from the
  # existing source water stations. No extra dock floor or passage is authored.
  body.anchor=Vector3(dock.water_xyz[0]-.9,dock.water_xyz[1]-.054,dock.water_xyz[2]+(-.3 if dock.id=="south_board" else .9))
  body.position=body.anchor;root.add_child(body)
 root.set_meta("whole_group_accepted",false);root.set_meta("new_capacity_or_room_ids",0)
 return root
