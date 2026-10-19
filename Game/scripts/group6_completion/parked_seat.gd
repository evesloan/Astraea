extends Area3D
# Fixed source seat only. No hoist motion, load transfer or new capacity.
var station:Dictionary
var occupant:CharacterBody3D
var seat_position:Vector3
var exit_position:Vector3
var unavailable_reason:=""

func _ready()->void:
	name=str(station.id)+"_PlayerControl"
	set_meta("persistent_id",str(station.id))
	seat_position=Vector3(station.seat_top_xyz[0],station.seat_top_xyz[1],station.seat_top_xyz[2])+Vector3.UP*.03
	exit_position=Vector3(station.operator_xyz[0],station.operator_xyz[1],station.operator_xyz[2])+Vector3.UP*.03
	position=seat_position
	collision_layer=1;collision_mask=0
	var contact:=CollisionShape3D.new();var box:=BoxShape3D.new()
	box.size=Vector3(.65,.65,.65);contact.shape=box;contact.position.y=.35;add_child(contact)
	set_meta("parked_mount_implemented",true)
	set_meta("occupied_hoist_accepted",false)

func get_interaction_label()->String:
	if not unavailable_reason.is_empty():return unavailable_reason
	return "E · Leave parked seat" if is_instance_valid(occupant) else "E · Sit on parked seat"

func interact(actor:CharacterBody3D)->void:
	if not actor.has_method("try_mount_parked_seat"):return
	unavailable_reason=""
	if is_instance_valid(occupant):
		if occupant!=actor:unavailable_reason="Seat occupied";return
		if not actor.try_leave_parked_seat():unavailable_reason="Exit obstructed · clear the landing"
	elif not actor.try_mount_parked_seat(self):unavailable_reason="Seat unavailable · approach with hands free and clear space"

func seat_world_position()->Vector3:
	return get_parent().to_global(seat_position)

func exit_world_position()->Vector3:
	return get_parent().to_global(exit_position)

func transfer_clear(actor:CharacterBody3D,standing_at:Vector3)->bool:
	# The source sling is closed at either side. Enter through the open front,
	# away from its pinned mast, with the seated torso above the source pan.
	var mast:=Vector3(station.mast_anchor_xyz[0],station.mast_anchor_xyz[1],station.mast_anchor_xyz[2])
	var front:Vector3=seat_position-mast;front.y=0;front=front.normalized()
	var target:=seat_world_position()
	var approach:Vector3=get_parent().to_global(seat_position+front*.9)
	var raised:=Vector3(standing_at.x,target.y,standing_at.z)
	for at in [raised,approach]:
		if not actor.body_space_clear(at,1.2):return false
	return actor.passage_clear(standing_at,raised) and actor.passage_clear(raised,approach) and actor.passage_clear(approach,target)
