extends Node3D
# Group-local sequencing of existing service doors; no door or transport lifecycle.
var doors:Array[Node3D]=[]
var selected_axis:="closed"
var requested_axis:="closed"
var blocked_reason:=""
# Owner supplies actual dispatch/closed-load validation; absence rejects return flow.
var sealed_load_ready:Callable
var switching:=false
func buffer_occupied()->bool:
 var shape:=BoxShape3D.new();shape.size=Vector3(4.48,2.8,4.28)
 var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,Vector3(-57.1,22.4,-297));q.margin=.001
 var hits:=get_world_3d().direct_space_state.intersect_shape(q,128)
 if hits.size()==128:return true
 for hit in hits:
  if hit.collider is CharacterBody3D or hit.collider is RigidBody3D:return true
 return false
func request_axis(axis:String)->bool:
 assert(axis in ["closed","clean","sealed_return"])
 if switching:blocked_reason="Wait for crossing gates";return false
 if axis=="sealed_return"and(not sealed_load_ready.is_valid()or not sealed_load_ready.call()):
  blocked_reason="Sealed return dispatch required";return false
 if axis!=selected_axis and buffer_occupied():blocked_reason="Clear crossing before changing flow";return false
 blocked_reason="";requested_axis=axis;switching=true
 for door in doors:door.desired_open=false
 return true
func _physics_process(_delta:float)->void:
 if not switching:return
 for door in doors:
  if door.open_fraction>.0001 or door._sweep_occupied():return
 if buffer_occupied():blocked_reason="Clear crossing before changing flow";return
 if requested_axis=="sealed_return"and(not sealed_load_ready.is_valid()or not sealed_load_ready.call()):
  requested_axis="closed";blocked_reason="Sealed return dispatch required"
 selected_axis=requested_axis
 for door in doors:door.desired_open=(door.flow_axis==selected_axis)
 switching=false
func exclusive_state()->bool:
 var clean:=false;var used:=false
 for door in doors:
  if door.open_fraction>.0001 or door.desired_open:
   if door.flow_axis=="clean":clean=true
   else:used=true
 return not(clean and used)
