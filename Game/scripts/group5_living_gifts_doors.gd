extends RefCounted
# The aft service cassette remains an explicit Group6 integration candidate.
static func build(ship:Node3D,include_service_candidate:bool=false)->Array[Node3D]:
	var spec:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group5/LIVING_GIFTS_DOORS.json"))
	assert(FileAccess.get_sha256(str(spec.original_model))==str(spec.original_model_sha256))
	var owner:Node3D=ship.find_child("LivingGiftsInterior_WIP",true,false)
	assert(owner!=null and owner.get_meta("programme_key")==spec.programme_key and owner.get_meta("historical_room_id")==spec.historical_room_id)
	var root:Node3D=owner.get_node_or_null("Group5LivingDoors")
	if root==null:
		root=Node3D.new();root.name="Group5LivingDoors";owner.add_child(root)
	var doors:Array[Node3D]=[]
	for row in spec.doors:
		if row.cross_group_adoption_required and not include_service_candidate:continue
		assert(FileAccess.get_sha256(str(row.model_path))==str(row.model_sha256))
		if root.has_node(str(row.door_name)):
			doors.append(root.get_node(str(row.door_name)));continue
		var door:=Node3D.new();door.name=str(row.door_name);door.set_script(load("res://scripts/group5_living_slider.gd"))
		door.persistent_id=StringName(str(row.physical_id));door.width=float(row.width);door.height=float(row.height);door.mode=str(row.mode)
		door.model_path=str(row.model_path);door.controls=row.controls
		door.position=Vector3(row.world_xyz[0],row.world_xyz[1],row.world_xyz[2]);door.rotation.y=float(row.rotation_y)
		door.set_meta("cross_group_adoption_required",bool(row.cross_group_adoption_required));root.add_child(door);doors.append(door)
	ship.set_meta("group5_living_doors_attached",true)
	ship.set_meta("group5_living_service_candidate_installed",include_service_candidate)
	return doors
