extends "res://scripts/group4_loaded_tram_actuator.gd"
# Isolated comparison successor. Inherits original route integration and all safety.
# Installed on the existing factory-created motor only while closed, empty and stopped.
static func install(existing:Node3D,successor:Script)->void:
 assert(existing.get_script().resource_path=="res://scripts/group4_loaded_tram_actuator.gd")
 assert(not existing.moving and not existing.motion_fault and existing.safety.phase=="secured")
 var state:Dictionary={}
 for property in existing.get_property_list():
  if int(property.usage)&PROPERTY_USAGE_SCRIPT_VARIABLE:state[property.name]=existing.get(property.name)
 var identity:=existing.get_instance_id()
 existing.set_script(successor)
 for key in state:existing.set(key,state[key])
 assert(existing.get_instance_id()==identity and existing.vehicle.get_meta("group4_source_actuator")==identity)
 existing.vehicle.sync_to_physics=true
 # No pose changes here. Original factory target commits during existing warm-up.
 existing.last_vehicle_pose=existing.expected_pose()
func expected_pose()->Transform3D:
 var p:Array=pose_at(cursor)
 return Transform3D(Basis(Vector3.UP,p[3]),Vector3(p[1],56.1,p[2]))
func apply_pose(at:float)->void:
 var p:Array=pose_at(at)
 # Atomic write is necessary: sync=true restores the committed transform after each write.
 vehicle.global_transform=Transform3D(Basis(Vector3.UP,p[3]),Vector3(p[1],56.1,p[2]))
 # Exact original bogie/wheel placement, not a second route or passenger integrator.
 for i in range(2):
  var column:=4+i*3;bogies[i].position=Vector3(p[column],-.2,-1.5 if i==0 else 1.5);bogies[i].rotation=Vector3(0,p[column+1],0)
 for wheel in wheel_pivots:wheel.rotation.x=wheel_spin
func _physics_process(delta:float)->void:
 super._physics_process(delta)
 if not motion_fault:
  # Next callback must receive this target. Never relax the inherited foreign-write guard.
  last_vehicle_pose=expected_pose()
