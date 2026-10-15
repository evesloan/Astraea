extends RefCounted
static func ensure(room:Node3D)->void:
 if not room.has_meta("retained_group2_home"):
  load("res://scripts/deferred_home_visual.gd").ensure(room);return
 if room.has_meta("resident_visual"):
  var cached:Node3D=room.get_meta("resident_visual")
  if cached.get_parent()==null:room.add_child(cached)
  return
 var source:Node3D=load("res://scripts/group2_completion/package.gd").build_section(room,str(room.get_meta("group2_source_key")))
 room.set_meta("resident_visual",source)
 var ship:Node3D=room.get_meta("receiving_ship")
 var lights:Array[Light3D]=[]
 for light:Light3D in source.find_children("*","Light3D",true,false):
  if light.get_meta("group2_fixture",false):lights.append(light)
 load("res://scripts/receiving_source_lights.gd").register(lights,ship)
 source.set_meta("fixture_registration_count",1)
 source.set_meta("private_access_or_capacity_admitted",false)
static func release(room:Node3D)->void:
 if not room.has_meta("retained_group2_home"):
  load("res://scripts/deferred_home_visual.gd").release(room);return
 if room.has_meta("resident_visual"):
  var cached:Node3D=room.get_meta("resident_visual")
  if cached.get_parent()==room:room.remove_child(cached)
