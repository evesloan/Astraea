extends RefCounted
const P:="res://night_garden_court_completion_20261022/"
static func finish(ship:Node3D)->Node3D:
 var pre:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/PREREQUISITES.json"))
 for path in pre.source_pins:assert(FileAccess.get_sha256("res://"+str(path))==str(pre.source_pins[path]))
 var parent:Node3D=ship.get_node("ShipSpace/Districts")
 var old:Node3D=parent.get_node("NightGardenReceivingCourts20261022")
 assert(old.scene_file_path=="res://night_garden_receiving_courts_20261022/runtime/ReceivingCourts_r003.scn")
 var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/BUILD_R003.json"))
 var baked:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/BAKE_R003.json"))
 assert(FileAccess.get_sha256(str(baked.scene))==str(baked.sha256))
 var scene:Node3D=load(str(baked.scene)).instantiate();var pose:=old.transform
 old.free();parent.add_child(scene);scene.transform=pose
 for row in d.lights:
  var lamp:=SpotLight3D.new();lamp.name=str(row.name);scene.add_child(lamp)
  lamp.position=Vector3(row.position[0],row.position[1],row.position[2]);lamp.look_at(scene.to_global(Vector3(row.target[0],row.target[1],row.target[2])),Vector3.RIGHT)
  lamp.light_color=Color(1,.78,.51);lamp.light_energy=float(row.energy);lamp.spot_range=float(row.range);lamp.spot_angle=float(row.angle);lamp.shadow_enabled=true
  lamp.set_meta("illumination_anchor",scene.to_global(Vector3(row.anchor[0],row.anchor[1],row.anchor[2])))
 var base:MeshInstance3D=scene.find_child("Base_*",true,false)
 var crown:MeshInstance3D=scene.find_child("Fore_CrownBeam_*",true,false)
 assert(base!=null and crown!=null)
 var top:Material=base.get_active_material(0);var soffit:Material=crown.get_active_material(0)
 var records:Array=[]
 for id in ["D13_atrium_circulation","D14_atrium_circulation","D15_atrium_circulation","D16_atrium_circulation","D13_window_terrace"]:
  var region:Node3D=ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms/"+id)
  var visuals:=region.find_children("*","MeshInstance3D",true,false)
  assert(visuals.size()==1,"Expected retained unchunked compiler owner: "+id)
  var mesh:MeshInstance3D=visuals[0];var original:=mesh.mesh
  assert(original.get_surface_count()==2)
  var bodies:=region.find_children("*","StaticBody3D",true,false)
  var geometry_before:=var_to_bytes(original.surface_get_arrays(0)).hex_encode().sha256_text()+var_to_bytes(original.surface_get_arrays(1)).hex_encode().sha256_text()
  mesh.set_surface_override_material(0,top);mesh.set_surface_override_material(1,soffit)
  assert(mesh.mesh==original and region.find_children("*","StaticBody3D",true,false)==bodies)
  records.append({"region":id,"geometry_sha256":geometry_before,"contacts_unchanged":true})
 scene.set_meta("compiled_finish_records",records);scene.set_meta("finished",false);scene.set_meta("new_room_ids",0)
 return scene
