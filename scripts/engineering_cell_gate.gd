extends "res://scripts/service_door.gd"
# Draft source-bound fitting only. The existing service-door state/input lifecycle is inherited.
# No old fitting is rescaled or overwritten. Source/group/shape proof is mandatory before adoption.
var fitting: Dictionary
var authored_visual: Node3D
var closed_pose: Transform3D
var travel_in_gate: Vector3
var swept_local: AABB

func configure(visual: Node3D, source_fitting: Dictionary) -> void:
	assert(not is_inside_tree() and visual != null)
	authored_visual = visual
	fitting = source_fitting
	persistent_id = StringName(str(fitting.persistent_id))
	assert(persistent_id == &"D02_secondary_engineering_workbay_cell_gate")
	assert(str(fitting.source_node) == "LEAF_WORKBAY_CELL")
	open_fraction = 0.0
	desired_open = false

func _xyz(value: Array) -> Vector3:
	assert(value.size() == 3)
	return Vector3(float(value[0]),float(value[1]),float(value[2]))

func _bounds(value: Array) -> AABB:
	assert(value.size() == 6)
	var low := Vector3(float(value[0]),float(value[1]),float(value[2]))
	var high := Vector3(float(value[3]),float(value[4]),float(value[5]))
	assert(high.x > low.x and high.y > low.y and high.z > low.z)
	return AABB(low,high-low)

func _ready() -> void:
	assert(not persistent_id.is_empty() and authored_visual != null and not fitting.is_empty())
	assert(authored_visual.has_meta("catalogue_file"))
	set_meta("catalogue_file",authored_visual.get_meta("catalogue_file"))
	set_meta("source_bound_single_leaf_fitting",true)
	var source := authored_visual.find_child(str(fitting.source_node),true,false) as Node3D
	var datum := authored_visual.find_child(str(fitting.source_rest_marker),true,false) as Node3D
	assert(source != null and datum != null)
	var expected_pivot := authored_visual.global_transform*_xyz(fitting.closed_rest_pivot_xyz)
	assert(source.global_position.distance_to(expected_pivot)<.001)
	assert(datum.global_position.distance_to(expected_pivot)<.001)
	var closed := _bounds(fitting.closed_leaf_bounds_xyz)
	var opened := _bounds(fitting.open_leaf_bounds_xyz)
	var actual_closed := _bounds(fitting.actual_closed_leaf_bounds_xyz)
	assert(actual_closed.position.distance_to(closed.position)<.001 and actual_closed.end.distance_to(closed.end)<.001)
	var movement := _xyz(fitting.opening_translation_xyz)
	assert(movement.distance_to(Vector3(0,0,-1.22))<.00001)
	assert((closed.position+movement).distance_to(opened.position)<.00001 and closed.size.distance_to(opened.size)<.00001)
	swept_local = closed.merge(opened).grow(.04)
	var body := AnimatableBody3D.new()
	body.name = "EngineeringCellMovingLeaf"
	body.sync_to_physics = false
	body.transform = global_transform.affine_inverse()*source.global_transform
	add_child(body)
	closed_pose = body.transform
	travel_in_gate = global_basis.inverse()*(authored_visual.global_basis*movement)
	source.reparent(body,true)
	source.transform = Transform3D.IDENTITY
	# Build the faithful source leaf box in body-local axes. No whole-cell hull or pocket fill.
	var local_box := AABB()
	for corner in range(8):
		var point := body.to_local(authored_visual.to_global(actual_closed.get_endpoint(corner)))
		if corner == 0: local_box = AABB(point,Vector3.ZERO)
		else: local_box = local_box.expand(point)
	var contact := CollisionShape3D.new()
	contact.name = "SourceLeafContact"
	var box := BoxShape3D.new()
	box.size = local_box.size
	box.margin = .001
	contact.shape = box
	contact.position = local_box.get_center()
	body.add_child(contact)
	leaves.append(body)
	_apply_pose()
	body.sync_to_physics = true

func _apply_pose() -> void:
	assert(leaves.size() == 1)
	leaves[0].transform = closed_pose
	leaves[0].position = closed_pose.origin+travel_in_gate*clampf(open_fraction,0.0,1.0)

func _sweep_occupied() -> bool:
	if not is_inside_tree() or authored_visual == null: return true
	var query := PhysicsShapeQueryParameters3D.new()
	var box := BoxShape3D.new()
	box.size = swept_local.size
	box.margin = .001
	query.shape = box
	query.transform = authored_visual.global_transform*Transform3D(Basis.IDENTITY,swept_local.get_center())
	query.collision_mask = 1
	query.collide_with_areas = false
	var excluded: Array[RID] = []
	for leaf in leaves: excluded.append(leaf.get_rid())
	query.exclude = excluded
	var hits := get_world_3d().direct_space_state.intersect_shape(query,128)
	# Conservatively stop if a bounded result buffer fills; never silently miss an occupant.
	if hits.size()>=128: return true
	for hit in hits:
		if hit.collider is CharacterBody3D or hit.collider is RigidBody3D: return true
	return false

func get_interaction_label() -> String:
	if obstructed: return "Clear cell gate travel"
	return "E · Close service cell gate" if desired_open else "E · Open service cell gate"
