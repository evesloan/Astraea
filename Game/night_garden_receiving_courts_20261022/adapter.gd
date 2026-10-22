extends RefCounted
const P:="res://night_garden_receiving_courts_20261022/"
static func build(ship:Node3D)->Node3D:
 var parent:Node3D=ship.get_node("ShipSpace/Districts")
 assert(not parent.has_node("NightGardenReceivingCourts20261022"))
 var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/BUILD_R003.json"))
 var baked:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/BAKE_R003.json"))
 for path in d.source_pins:
  if str(path).begins_with("Game/"):assert(FileAccess.get_sha256("res://"+str(path).trim_prefix("Game/"))==str(d.source_pins[path]))
 assert(FileAccess.get_sha256(str(baked.scene))==str(baked.sha256))
 var entrances:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/ENTRANCES.json"))
 var entrances_bake:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/ENTRANCES_BAKE_POLICY.json"))
 assert(FileAccess.get_sha256("res://assets/models/"+str(entrances.source_model))==str(entrances.source_model_sha256))
 assert(FileAccess.get_sha256(str(entrances_bake.scene))==str(entrances_bake.sha256))
 var street:Node3D=parent.get_node("NightGardenD15SpecialtyReceiving20261020/ConnectedStreetsAndPortalSuccessors")
 var predecessor:Node3D=street.get_node("NightGardenD15ConnectedReceiving_r003")
 assert(predecessor.find_children("*","MeshInstance3D",true,false).size()==248)
 for changed_name in entrances.changed_source_meshes:assert(predecessor.find_child(str(changed_name),true,false)!=null)
 var successor:Node3D=load(str(entrances_bake.scene)).instantiate()
 var pose:=predecessor.transform
 predecessor.free();street.add_child(successor);successor.transform=pose
 successor.set_meta("predecessor_source_sha256",entrances.source_model_sha256)
 var scene:Node3D=load(str(baked.scene)).instantiate();parent.add_child(scene)
 for row in d.lights:
  var lamp:=SpotLight3D.new();lamp.name=str(row.name);scene.add_child(lamp)
  lamp.position=Vector3(row.position[0],row.position[1],row.position[2]);lamp.look_at(Vector3(row.target[0],row.target[1],row.target[2]),Vector3.RIGHT)
  lamp.light_color=Color(1,.78,.51);lamp.light_energy=float(row.energy);lamp.spot_range=float(row.range);lamp.spot_angle=float(row.angle);lamp.shadow_enabled=true
 scene.set_meta("finished",false);scene.set_meta("new_room_ids",0)
 return scene
