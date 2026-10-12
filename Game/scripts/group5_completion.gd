extends RefCounted
# Integration contract: invoke once after shopping adoption and before residency setup.
# Permanent door truth belongs to the existing chunk; static visual reloads leave it intact.
static func build(ship:Node3D)->void:
	var root:Node3D=ship.get_node("ShipSpace/Districts/ShoppingPromenadeChunks")
	assert(not root.has_meta("group5_completion_attached"))
	var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group5/CONSTRUCTION.json"))
	for revision in definition.get("fitout_revisions",[]):
		assert(FileAccess.get_sha256(str(revision.original_model))==str(revision.original_sha256))
		assert(FileAccess.get_sha256(str(revision.model_path))==str(revision.model_sha256))
		assert(FileAccess.get_sha256(str(revision.scene_path))==str(revision.scene_sha256))
		var chunk:Node3D=_chunk(ship,root,str(revision.chunk_id))
		assert(str(chunk.get_meta("deferred_visual_path"))==str(revision.original_scene))
		var was_resident:bool=chunk.has_meta("resident_visual")
		load("res://scripts/deferred_home_visual.gd").release(chunk)
		chunk.set_meta("deferred_visual_path",str(revision.scene_path))
		chunk.set_meta("group5_fitout_revision",str(revision.model_sha256))
		# Original bounded material batches, mesh policy, shell, floor, lights and
		# shell-only occluder remain owned by this same retained room.
		if was_resident:load("res://scripts/deferred_home_visual.gd").ensure(chunk)
	var count:=0
	for row in definition.doors:
		var chunk:Node3D=_chunk(ship,root,str(row.chunk_id))
		var door:=Node3D.new()
		door.name=str(row.local_name)
		door.set_script(load("res://scripts/group5_retail_slider.gd"))
		door.persistent_id=StringName(str(row.physical_id))
		door.width=float(row.width)
		door.height=float(row.height)
		door.model_path=str(row.model_path)
		door.position=Vector3(row.local_xyz[0],row.local_xyz[1],row.local_xyz[2])
		door.rotation.y=float(row.rotation_y)
		door.controls=row.get("controls",[])
		chunk.add_child(door)
		count+=1
	for spec in definition.wayfinding:
		var chunk:Node3D=_chunk(ship,root,str(spec.chunk_id))
		var sign:Node3D=(load(str(spec.model_path)) as PackedScene).instantiate()
		sign.name=str(spec.id)
		sign.position=Vector3(spec.local_xyz[0],spec.local_xyz[1],spec.local_xyz[2])
		sign.rotation.y=float(spec.rotation_y)
		chunk.add_child(sign)
		for mesh:MeshInstance3D in sign.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
	assert(count==297)
	root.set_meta("group5_completion_attached",true)
	root.set_meta("group5_operating_doors",count)
	root.set_meta("whole_group_accepted",false)
static func _chunk(ship:Node3D,root:Node3D,key:String)->Node3D:
	var found:Node3D=root.get_node_or_null(key)
	if found!=null:return found
	# Review fixtures may bind after normal startup; use the existing cached owner.
	var residency:Node=ship.get_node_or_null("ShipSystems/ReceivedRoomResidency")
	assert(residency!=null)
	for entry in residency.entries:
		if str(entry.room.name)==key:return entry.room
	assert(false,"Missing retained shopping chunk "+key)
	return null
