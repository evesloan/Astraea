extends "res://grand_arrivals_tram_20261026/crossing_r002/loaded_actuator.gd"
# A fresh assembly only: the original six portal frames are converted exactly
# once by inherited _ready. No second motor, preconverted clone or bypass.
static func attach_section(parent:Node3D,body:AnimatableBody3D,boarding:Node3D,cart_restraint:Node3D)->Node3D:
 assert(parent.get_meta("lower_arrivals_integration_candidate",false))
 assert(not body.has_meta("group4_source_actuator") and not body.has_meta("exact_original_portal_contact_components"))
 var originals:=0
 for col:CollisionShape3D in body.find_children("*","CollisionShape3D",false,false):
  if col.shape is ConcavePolygonShape3D:originals+=1
 assert(originals==6,"Fresh original boarding portals must precede the one motor")
 var n:Node3D=load("res://grand_arrivals_tram_20261026/integration_r001/motor.gd").new()
 n.name="Group4LoadedSourceTravelActuator"
 n.plan=JSON.parse_string(FileAccess.get_file_as_string("res://grand_arrivals_tram_20261026/integration_r001/MOTOR_PLAN.json"))
 n.vehicle=body;n.safety=boarding;n.restraint=cart_restraint
 n.set_meta("integration_motion_admitted",false)
 cart_restraint.motor=n
 parent.add_child(n)
 body.set_meta("group4_source_actuator",n.get_instance_id())
 n.configure_crossing(parent.get_node("ForwardGroundCrossing"))
 return n
