extends RefCounted
# Reviewed optional source successor. Originals and shared roots remain immutable.
static func rebuild_contacts(visual: Node3D) -> void:
	for body in visual.find_children("*","StaticBody3D",true,false):
		if not body is AnimatableBody3D and body.name in ["RoomStaticContacts","StaticContact"]:
			body.free()
	load("res://scripts/static_contact_cache.gd").attach_group(visual,visual.find_children("*","MeshInstance3D",true,false))

static func build(section: Node3D, key: String, source_receiver_ready: bool) -> Node3D:
	assert(source_receiver_ready and key != "790")
	assert(section.global_transform.is_equal_approx(Transform3D.IDENTITY))
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_pit_perimeters/PLAN_r003.json"))
	var row: Dictionary = {}
	for candidate in data.suites:
		if str(int(candidate.source_index)) == key: row = candidate
	assert(not row.is_empty())
	var visual := section.get_node("RetainedSource") as Node3D
	var targets: Array[Node] = []
	var before: Dictionary = {}
	var runtime_names: Dictionary = {}
	for mesh_name in row.furniture_pose_patch.exact_mesh_names:
		var runtime_name := str(mesh_name).validate_node_name()
		assert(not runtime_names.has(runtime_name),"Source target normalization must remain unique")
		runtime_names[runtime_name] = true
		var mesh := visual.find_child(runtime_name,true,false) as MeshInstance3D
		assert(mesh != null and not mesh.has_meta("group2_pit_pose_successor"),"Exact pose target missing/already patched: "+str(mesh_name))
		targets.append(mesh)
		before[mesh] = mesh.global_transform
	targets.sort_custom(func(a: Node,b: Node): return a.get_path().get_name_count() < b.get_path().get_name_count())
	for mesh in targets:
		var pose: Transform3D = before[mesh]
		var delta: Array = row.furniture_pose_patch.per_mesh_world_delta.get(str(mesh.name),[0,.45,0])
		pose.origin += Vector3(delta[0],delta[1],delta[2])
		mesh.global_transform = pose
		mesh.set_meta("group2_pit_pose_successor",true)
	rebuild_contacts(visual)
	var old := section.find_child("ConversationReceiver_"+key,true,false) as Node3D
	assert(old != null)
	for suffix in row.previous_receiver.deactivate_only:
		var mesh := old.find_child("G2R_"+key+"_"+str(suffix),true,false)
		assert(mesh != null)
		mesh.free()
	rebuild_contacts(old)
	var successor: Node3D = (load("res://assets/group2_pit_perimeters/PERIMETER_"+key+"_r003.glb") as PackedScene).instantiate()
	successor.name = "FullPitPerimeter_" + key
	section.add_child(successor)
	rebuild_contacts(successor)
	successor.set_meta("same_private_unit",true)
	successor.set_meta("production_adoption",false)
	return successor
