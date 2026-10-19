extends "res://scripts/group6_completion/buoyant_float.gd"
# Source force integrator is retained. This adds a bounded reference-load model
# and a game boarding hold, not a physical mooring/hoist engineering claim.
var dock:Dictionary
var entry:Dictionary
var seat:Area3D
var anchor:Vector3
var seat_local:Vector3
var mode:="docked"
var departed:=false
var return_requested:=false
var reference_displacement_kg:=100.0
var occupant_load_kg:=0.0
var maximum_load_kg:=90.0
func _ready()->void:
 super._ready()
 center_of_mass_mode=RigidBody3D.CENTER_OF_MASS_MODE_CUSTOM
 center_of_mass=Vector3.ZERO
 set_meta("source_catalogue_id","AST-AQU-006")
 set_meta("source_boarding_id",str(dock.id))
 set_meta("persistent_save_identity_assigned",false)
 set_meta("buoyancy_scope","Reference occupied-load gameplay model; source forces retained; no species, engineering, AFK/save or visual acceptance")
 seat=load("res://scripts/group6_float_20261019/float_seat.gd").new();seat.body=self;add_child(seat)
func get_interaction_label()->String:return seat.get_interaction_label()
func interact(actor:CharacterBody3D)->void:seat.interact(actor)
func load_occupant(actor:CharacterBody3D)->void:
 occupant_load_kg=float(actor.aquatic_reference_load_kg) if is_instance_valid(actor) else 0.0
 mass=12.0+occupant_load_kg
 center_of_mass=Vector3(0,occupant_load_kg*.40/mass,0)
 if is_instance_valid(actor):
  actor.add_collision_exception_with(self);add_collision_exception_with(actor)
func unload_occupant(actor:CharacterBody3D)->void:
 if is_instance_valid(actor):
  actor.remove_collision_exception_with(self);remove_collision_exception_with(actor)
 occupant_load_kg=0;mass=12;center_of_mass=Vector3.ZERO
 if mode=="riding":request_return()
func _physics_process(_delta:float)->void:
 if occupant_load_kg>0 and not is_instance_valid(seat.occupant):unload_occupant(null)
func settled_at_dock()->bool:
 return mode=="docked" and Vector2(global_position.x-anchor.x,global_position.z-anchor.z).length()<.12 and linear_velocity.length()<.15 and global_basis.y.dot(Vector3.UP)>.98
func launch()->bool:
 if not settled_at_dock() or not is_instance_valid(seat.occupant):return false
 mode="riding";departed=false;return_requested=false;return true
func request_return()->void:
 return_requested=true
func _integrate_forces(state:PhysicsDirectBodyState3D)->void:
 super._integrate_forces(state)
 # Constant displacement capacity means added occupant mass increases draft.
 # It is a declared game parameter, not inferred certified buoyancy from art.
 if field.sample(state.transform.origin).get("wet",false):
  for local in probes:
   var offset:Vector3=state.transform.basis*local;var p:Vector3=state.transform.origin+offset
   if field.contains_xz(p):
    var displacement:=clampf(maxf(0,field.water_y-p.y)/draft_m,0,2)
    state.apply_force(Vector3.UP*(reference_displacement_kg-mass)*9.8*displacement/4.0,offset)
 var flat:=Vector3(anchor.x-state.transform.origin.x,0,anchor.z-state.transform.origin.z)
 if mode=="riding":
  if flat.length()>3.0:departed=true
  if return_requested and departed and flat.length()<1.8:mode="docked"
 if mode=="docked":
  var water:Dictionary=field.sample(state.transform.origin)
  var current:Vector3=water.get("water_velocity",Vector3.ZERO);current.y=0
  var horizontal:=Vector3(state.linear_velocity.x,0,state.linear_velocity.z)
  state.apply_central_force(flat.limit_length(2)*mass*8-horizontal*mass*3-current*mass*3)
  var forward:Vector3=state.transform.basis.z
  var yaw_error:=atan2(forward.x,forward.z)
  var inverse_yaw_inertia:float=Vector3.UP.dot(state.inverse_inertia_tensor*Vector3.UP)
  if inverse_yaw_inertia>0:
   state.apply_torque(Vector3.UP*(-yaw_error*6-state.angular_velocity.y*5)/inverse_yaw_inertia)
