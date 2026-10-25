extends RefCounted
static func ensure(room:Node3D)->void:
 if not room.has_meta("retained_group2_home"):
  if not load("res://group2_resource_lifetime_20261025/mesh_lease.gd").resume(room):
   push_error("Received section mesh restoration failed");room.get_tree().quit(1);return
  load("res://scripts/deferred_home_visual.gd").ensure(room);return
 if room.has_meta("resident_visual"):
  var cached:Node3D=room.get_meta("resident_visual")
  if not load("res://group2_resource_lifetime_20261025/mesh_lease.gd").resume(cached):
   push_error("Group2 mesh restoration failed");room.get_tree().quit(1);return
  if cached.get_parent()==null:room.add_child(cached)
  return
 var source:Node3D=load("res://scripts/group2_completion/package.gd").build_section(room,str(room.get_meta("group2_source_key")))
 if source==null:
  push_error("Group2 source construction failed");room.get_tree().quit(1);return
 room.set_meta("resident_visual",source)
 var key:String=str(room.get_meta("group2_source_key"))
 if key in["787","792","794","795","797"]:
  load("res://scripts/group2_private_vertical/package.gd").build_conversation_receiver(source,key,true)
  load("res://scripts/group2_pit_perimeters/package.gd").build(source,key,true)
  var lift:Node3D=load("res://scripts/group2_private_vertical/package.gd").build_for_section(source,key,false)
  lift.set_meta("physical_receiver_adopted",true)
  source.set_meta("private_pit_and_perimeter_fitted",true)
  source.set_meta("retained_furniture_pose_successors",550)
 var ship:Node3D=room.get_meta("receiving_ship")
 var lights:Array[Light3D]=[]
 for light:Light3D in source.find_children("*","Light3D",true,false):
  lights.append(light)
 load("res://scripts/receiving_source_lights.gd").register(lights,ship)
 source.set_meta("fixture_registration_count",1)
 source.set_meta("private_access_or_capacity_admitted",false)
static func release(room:Node3D)->void:
 if not room.has_meta("retained_group2_home"):
  load("res://scripts/deferred_home_visual.gd").release(room)
  # Later construction adapters still inspect detached originals. Wait until
  # all construction has finished before releasing these source meshes.
  if room.has_meta("source_mesh_lease_host"):
   var host:Node=room.get_meta("source_mesh_lease_host").get_ref()
   if host!=null and bool(host.get_meta("runtime_ready",false)):
    load("res://group2_resource_lifetime_20261025/mesh_lease.gd").suspend(room)
  return
 if room.has_meta("resident_visual"):
  var cached:Node3D=room.get_meta("resident_visual")
  # Residency already detached the entire room. Keep its owned subtree so
  # room destruction also destroys controllers and shapes, without orphan leaks.
  load("res://group2_resource_lifetime_20261025/mesh_lease.gd").suspend(cached)
