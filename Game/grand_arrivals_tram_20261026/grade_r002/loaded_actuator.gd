extends "res://grand_arrivals_tram_20261026/grade_r002/actuator.gd"
# Successor of the retained single source actuator: physical original-cart departure guard, no global controller.
var restraint:Node3D
static func attach_loaded(parent:Node3D,body:AnimatableBody3D,boarding:Node3D,cart_restraint:Node3D,candidate_only:bool=false)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GROUP4_LOADED_CART_SOURCE_CANDIDATE.json"))
 if not candidate_only:return null # Unselected graded route cannot be attached by production callers.
 assert(not body.has_meta("group4_source_actuator"),"Exactly one actuator owns this vehicle")
 var n:Node3D=load("res://grand_arrivals_tram_20261026/grade_r002/loaded_actuator.gd").new();n.name="Group4LoadedSourceTravelActuator";n.plan=JSON.parse_string(FileAccess.get_file_as_string(DATA));n.vehicle=body;n.safety=boarding;n.restraint=cart_restraint;cart_restraint.motor=n;parent.add_child(n);body.set_meta("group4_source_actuator",n.get_instance_id());return n
func request_distance(at:float)->bool:
 if not restraint.loaded_clear_to_depart():return false
 return super.request_distance(at)
func _physics_process(delta:float)->void:
 if moving and not restraint.loaded_clear_to_depart():motion_fault=true;moving=false;speed=0;return
 super._physics_process(delta)
