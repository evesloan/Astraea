extends RefCounted
static func build(ship:Node3D)->Array[Node3D]:
	var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group5/LARGE_VENUE_DOORS.json"))
	var doors:Array[Node3D]=[]
	for row in definition.doors:
		assert(FileAccess.get_sha256(str(row.source_model))==str(row.source_sha256))
		assert(FileAccess.get_sha256(str(row.model_path))==str(row.model_sha256))
		var owner:Node3D=load("res://scripts/group5_large_venue_lighting.gd")._owner(ship,str(row.programme_key))
		assert(owner!=null)
		if owner.has_node(str(row.door_name)):
			doors.append(owner.get_node(str(row.door_name)));continue
		var door:=Node3D.new()
		door.name=str(row.door_name)
		door.set_script(load("res://scripts/group5_retail_slider.gd"))
		door.persistent_id=StringName(str(row.physical_id))
		door.width=float(row.width);door.height=float(row.height);door.model_path=str(row.model_path)
		door.position=Vector3(row.local_xyz[0],row.local_xyz[1],row.local_xyz[2]);door.rotation.y=float(row.rotation_y)
		door.controls=row.controls
		owner.add_child(door);doors.append(door)
	assert(doors.size()==5)
	ship.set_meta("group5_large_venue_doors_attached",true)
	return doors
