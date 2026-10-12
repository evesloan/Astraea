extends RefCounted
# Group1 invokes on its existing receiver. No duplicate chairs or shared-root write.
static func apply(receiver:Node3D)->int:
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_meal_arrangement/CHAIR_POSE_SUCCESSOR.json"))
	assert(FileAccess.get_sha256("res://assets/models/AST-FUR-002.glb")==str(data.chair_model_sha256))
	var parent:Node3D=receiver.get_node("RetainedLandscapeAndSeating")
	var targets:Array[Node3D]=[];var changed:=0
	# Validate every preimage before changing any instance.
	for row in data.rows:
		var chair:Node3D=parent.get_node(str(row.name));var p:Array=row.world_xyz
		assert(chair.position.is_equal_approx(Vector3(p[0],p[1],p[2])))
		assert(chair.scale.is_equal_approx(Vector3.ONE*float(row.scale)))
		assert(str(chair.get_meta("catalogue_id"))==str(row.catalogue_id))
		var forward:Vector3=chair.transform.basis*Vector3(0,0,1)
		var old_front:=Vector3(sin(deg_to_rad(float(row.old_yaw_degrees))),0,cos(deg_to_rad(float(row.old_yaw_degrees))))
		var new_front:=Vector3(sin(deg_to_rad(float(row.corrected_yaw_degrees))),0,cos(deg_to_rad(float(row.corrected_yaw_degrees))))
		assert(forward.normalized().is_equal_approx(old_front)or forward.normalized().is_equal_approx(new_front),"Changed receiving pose requires Group1 reconciliation")
		targets.append(chair)
	for i in range(targets.size()):
		var chair:=targets[i];var yaw:=deg_to_rad(float(data.rows[i].corrected_yaw_degrees))
		if not (chair.transform.basis*Vector3(0,0,1)).normalized().is_equal_approx(Vector3(sin(yaw),0,cos(yaw))):
			chair.rotation.y=yaw;changed+=1
		chair.set_meta("group2_meal_facing_successor","inward_v1")
	receiver.set_meta("group2_meal_chairs_inward_v1",true)
	return changed
