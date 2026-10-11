extends "res://scripts/commons_lift.gd"
# Keep sleeping bodies physically inside the cabin awake during travel. Gravity/contact
# then carries them; no passenger is reparented, teleported or given a velocity.
var departure_wake_events := 0
var last_woken_body_count := 0
func _physics_process(delta: float) -> void:
	var before := phase
	if phase == "moving":
		_wake_cabin_bodies()
	super._physics_process(delta)
	if before == "closing" and phase == "moving":
		_wake_cabin_bodies()
		departure_wake_events += 1

func _wake_cabin_bodies() -> void:
	var shape := ConvexPolygonShape3D.new()
	var points := PackedVector3Array()
	for height in [.01, 2.75]:
		for p in [Vector2(-2,0),Vector2(2,0),Vector2(2,3.25),Vector2(1.65,3.6),Vector2(-1.65,3.6),Vector2(-2,3.25)]:
			points.append(Vector3(p.x,height,-p.y))
	shape.points = points
	shape.margin = .001
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = shape
	query.transform = cabin.global_transform
	query.exclude = [cabin.get_rid()]
	last_woken_body_count = 0
	for hit in get_world_3d().direct_space_state.intersect_shape(query,64):
		if hit.collider is RigidBody3D:
			hit.collider.sleeping = false
			last_woken_body_count += 1
