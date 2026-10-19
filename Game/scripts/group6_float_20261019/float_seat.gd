extends Area3D
var body:RigidBody3D
var occupant:CharacterBody3D:
 set(value):
  if occupant==value:return
  if is_instance_valid(occupant):body.unload_occupant(occupant)
  occupant=value
  if is_instance_valid(occupant):body.load_occupant(occupant)
var reason:=""
func _ready()->void:
 name="SourceFloatSeat";position=body.seat_local+Vector3.UP*.03
 collision_layer=1;collision_mask=0
 var contact:=CollisionShape3D.new();var shape:=BoxShape3D.new();shape.size=Vector3(.35,.45,.4);contact.shape=shape;contact.position.y=.3;add_child(contact)
func seat_world_position()->Vector3:return global_position
func exit_world_position()->Vector3:
 var q:Array=body.entry.supported_bed_stance_xyz
 return Vector3(q[0],q[1]+.03,q[2])
func get_interaction_label()->String:
 if reason in ["Remain seated until the boarding hold settles","Wait for the boarding hold to settle","Board only at the settled boarding point"] and body.settled_at_dock():reason=""
 if not reason.is_empty():return reason
 if not is_instance_valid(occupant):return "E · Board float" if body.settled_at_dock() else "Float settling at boarding point"
 if body.mode=="riding":return "Returning to "+str(body.dock.id) if body.return_requested else "E · Request return to boarding point"
 if not body.settled_at_dock():return "Boarding hold settling · remain seated"
 return "E · Leave float" if body.return_requested else "E · Start drifting · Space to leave"
func interact(actor:CharacterBody3D)->void:
 reason=""
 if not actor.has_method("try_mount_parked_seat") or not "aquatic_reference_load_kg" in actor:return
 if is_instance_valid(occupant):
  if occupant!=actor:reason="Float occupied";return
  if body.mode=="riding":body.request_return()
  elif body.return_requested:request_leave(actor)
  elif not body.launch():reason="Wait for the boarding hold to settle"
 else:
  if not body.settled_at_dock():reason="Board only at the settled boarding point";return
  if actor.aquatic_reference_load_kg<=0 or actor.aquatic_reference_load_kg>body.maximum_load_kg:reason="Reference load outside implemented range";return
  if not actor.try_mount_parked_seat(self):reason="Boarding path obstructed · approach with hands free"
func request_leave(actor:CharacterBody3D)->void:
 reason=""
 if occupant!=actor:return
 if not body.settled_at_dock():body.request_return();reason="Remain seated until the boarding hold settles";return
 if not actor.try_leave_parked_seat():reason="Exit obstructed · clear the entry landing"
func transfer_clear(actor:CharacterBody3D,standing_at:Vector3)->bool:
 if not body.settled_at_dock():return false
 if not "aquatic_reference_load_kg" in actor or actor.aquatic_reference_load_kg<=0 or actor.aquatic_reference_load_kg>body.maximum_load_kg:return false
 # Step over the source coaming, then lower into the actual open well.
 var high:Vector3=body.to_global(Vector3(0,.65,.06))
 var raised:=Vector3(standing_at.x,high.y,standing_at.z)
 for at in [high,raised]:
  if not actor.body_space_clear(at,1.2):return false
 return actor.passage_clear(standing_at,raised) and actor.passage_clear(raised,high) and actor.passage_clear(high,seat_world_position())
