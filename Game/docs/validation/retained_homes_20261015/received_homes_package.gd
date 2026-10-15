extends RefCounted
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D)->Node3D:
 assert(ship.get_node_or_null("ShipSpace/ApprovedSixHouseReceiving")!=null)
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/received_homes_20261015/HOMES.json"))
 var group:=Node3D.new();group.name="ApprovedGroup2Homes";ship.get_node("ShipSpace/Districts").add_child(group)
 group.set_meta("source_homes_registered",75)
 group.set_meta("private_multilevel_dependency_gate",["787","792","794","795","797"])
 group.set_meta("registry_identity_or_capacity_migrated",false)
 group.set_meta("default_main_adoption",false)
 for row in data.homes:
  if not row.selected_for_first_source_home_package:continue
  var path:String="res://assets/group2_completion/"+str(row.key)+".glb"
  assert(FileAccess.get_sha256(path)==str(row.source_sha256))
  var room:Node3D=load("res://scripts/received_homes_20261015/cached_home_root.gd").new()
  room.name="Group2Home_"+str(row.key)
  room.set_meta("retained_group2_home",true)
  room.set_meta("group2_source_key",str(row.key))
  room.set_meta("receiving_ship",ship)
  room.set_meta("deferred_visual_bounds",AABB(v(row.bounds_min_world),v(row.bounds_max_world)-v(row.bounds_min_world)))
  room.set_meta("deferred_visual_meshes",int(row.mesh_nodes))
  room.set_meta("installed_acceptance",false)
  room.set_meta("capacity_migrated",false)
  group.add_child(room)
 return group
