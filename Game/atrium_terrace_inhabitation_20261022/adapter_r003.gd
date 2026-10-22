extends RefCounted
const P:="res://atrium_terrace_inhabitation_20261022/"
static func lights(scene:Node3D,rows:Array)->void:
 for row in rows:
  var light:=SpotLight3D.new();light.name=str(row.name);scene.add_child(light)
  light.position=Vector3(row.position[0],row.position[1],row.position[2]);light.look_at(Vector3(row.target[0],row.target[1],row.target[2]),Vector3.RIGHT)
  light.light_color=Color(1,.81,.59);light.light_energy=float(row.energy);light.spot_range=float(row.range);light.spot_angle=float(row.angle);light.shadow_enabled=true
static func finish(ship:Node3D)->Node3D:
 var pre:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/PREREQUISITES.json"))
 for path in pre.source_pins:assert(FileAccess.get_sha256("res://"+str(path))==str(pre.source_pins[path]))
 var parent:Node3D=ship.get_node("ShipSpace/Districts")
 assert(not parent.has_node("UpperAtriumTerraceInhabitation20261022"))
 var old:Node3D=parent.get_node("AtriumLanternCeiling20261022")
 assert(old.scene_file_path=="res://atrium_ceiling_completion_20261022/runtime/AtriumLanternCeiling_r001.scn")
 var kept:={}
 for key in ["terrace_finish_records","cap_geometry_sha256","cap_contacts_unchanged"]:kept[key]=old.get_meta(key)
 var baked:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/BAKE_R003.json"))
 for key in ["ceiling","terraces"]:assert(FileAccess.get_sha256(str(baked[key].scene))==str(baked[key].sha256))
 var ceiling:Node3D=load(str(baked.ceiling.scene)).instantiate();old.free();parent.add_child(ceiling)
 for key in kept:ceiling.set_meta(key,kept[key])
 ceiling.set_meta("finished",false)
 var c:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/CEILING_BUILD.json"));lights(ceiling,c.lights)
 var scene:Node3D=load(str(baked.terraces.scene)).instantiate();parent.add_child(scene)
 var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/BUILD_R003.json"));lights(scene,d.lights)
 scene.set_meta("group_count",d.groups.size());scene.set_meta("catalogue_instances",d.instances.size());scene.set_meta("finished",false)
 return scene
