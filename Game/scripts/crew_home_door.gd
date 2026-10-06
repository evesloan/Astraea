extends "res://scripts/service_door.gd"
# Source-fitting initialization only. Existing interaction, timing, pause and
# first-open/last-close sequence remain inherited from the current service door.
var authored_visual: Node3D
var fitting: Dictionary
var moving_parts: Array
var sweep_box: Dictionary

static func xyz(value: Array) -> Vector3:
	return Vector3(float(value[0]),float(value[1]),float(value[2]))

func _ready() -> void:
	assert(not persistent_id.is_empty() and authored_visual!=null)
	assert(fitting.original_door_not_scaled and leaves.is_empty())
	set_meta("source_door_family","AST-STF-008")
	set_meta("first_pass_accepted",false)
	open_fraction=0.0
	desired_open=false
	pose_initialized=false
	authored_visual.reparent(self,true)
	authored_visual.transform=Transform3D.IDENTITY
	for index in range(2):
		var side: String="LEFT" if index==0 else "RIGHT"
		var hinge: Node3D=authored_visual.find_child("HOME_HINGE_"+side,true,false) as Node3D
		assert(hinge!=null)
		var body: AnimatableBody3D=AnimatableBody3D.new()
		body.name="MovingLeaf_"+side
		body.sync_to_physics=false
		body.position=Vector3(float(fitting.hinge_local_x[index]),0,0)
		add_child(body)
		hinge.reparent(body,true)
		hinge.transform=Transform3D.IDENTITY
		for value in moving_parts:
			var part: Dictionary=value
			if str(part.parent)!="HOME_HINGE_"+side: continue
			assert(str(part.shape)=="door_prism" and str(part.collision_contract)=="kinematic_source_part")
			var profile: Array=part.profile_x_y
			var low_x: float=INF
			var low_y: float=INF
			var high_x: float=-INF
			var high_y: float=-INF
			for point_value in profile:
				var point: Array=point_value
				low_x=minf(low_x,float(point[0]))
				low_y=minf(low_y,float(point[1]))
				high_x=maxf(high_x,float(point[0]))
				high_y=maxf(high_y,float(point[1]))
			# Compare the original JSON scalars before float32 Vector conversion.
			# All moving source parts are rectangles, not hulls over a cavity.
			assert(profile.size()==4)
			for point_value in profile:
				var point: Array=point_value
				assert(float(point[0]) in [low_x,high_x] and float(point[1]) in [low_y,high_y])
			var depth: Array=part.depth_z
			var shape: BoxShape3D=BoxShape3D.new()
			shape.size=Vector3(high_x-low_x,high_y-low_y,float(depth[1])-float(depth[0]))
			shape.margin=.001
			var contact: CollisionShape3D=CollisionShape3D.new()
			contact.name=str(part.name)+"_SourceContact"
			contact.shape=shape
			contact.position=Vector3((low_x+high_x)*.5,(low_y+high_y)*.5,(float(depth[0])+float(depth[1]))*.5)
			body.add_child(contact)
		leaves.append(body)
	_apply_pose()
	for leaf in leaves: leaf.sync_to_physics=true

func _sweep_occupied() -> bool:
	var query: PhysicsShapeQueryParameters3D=PhysicsShapeQueryParameters3D.new()
	var box: BoxShape3D=BoxShape3D.new()
	box.size=xyz(sweep_box.size)
	query.shape=box
	query.transform=global_transform*Transform3D(Basis.IDENTITY,xyz(sweep_box.center))
	var hits: Array[Dictionary]=get_world_3d().direct_space_state.intersect_shape(query,64)
	if hits.size()==64: return true
	for hit in hits:
		var body: Object=hit.get("collider")
		if body is CharacterBody3D or body is RigidBody3D: return true
	return false
