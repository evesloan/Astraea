extends RefCounted
# Apply once to the exact existing received room, before residency setup.
# Original source files, room IDs, entrance and compiler floor owners stay intact.
const CONTRACT="res://data/architecture/group6_completion/THERMAL_ENTRY_CONTRACT.json"
static func build(room:Node3D)->Node3D:
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	var key:String=str(room.get_meta("programme_key"));var spec:Dictionary={}
	for item in data.rooms:
		if item.programme_key==key:spec=item
	assert(not spec.is_empty() and room.get_node_or_null("Group6ThermalEntries")==null)
	assert(FileAccess.get_sha256("res://"+str(spec.current_room_runtime).trim_prefix("Game/"))==str(spec.current_room_runtime_sha256))
	assert(FileAccess.get_sha256("res://"+str(spec.runtime_addition).trim_prefix("Game/"))==str(spec.new_export_sha256))
	var affected:Dictionary={}
	for name in spec.affected_original_bounds_xyz:
		var mesh:MeshInstance3D=room.find_child(str(name),true,false);assert(mesh!=null,"Missing scoped original "+str(name))
		var actual:AABB=mesh.global_transform*mesh.get_aabb();var expected:Array=spec.affected_original_bounds_xyz[name]
		for axis in range(3):
			assert(absf(actual.position[axis]-float(expected[axis][0]))<.002 and absf(actual.end[axis]-float(expected[axis][1]))<.002,"Thermal source/runtime bounds mismatch "+str(name))
		affected[name]=mesh
	# Validate every mesh before changing any contacts or visibility.
	for name in spec.runtime_visual_exclusions:
		var mesh:MeshInstance3D=affected[name];var contact:Node=mesh.get_node_or_null("StaticContact");assert(contact!=null)
		contact.free();mesh.visible=false;mesh.set_meta("group6_source_successor","visible continuous entry package")
	for name in spec.water_visual_contact_exclusions:
		var mesh:MeshInstance3D=affected[name];var contact:Node=mesh.get_node_or_null("StaticContact");assert(contact!=null)
		contact.free();mesh.set_meta("group6_contact_role","water_visual_no_contact");mesh.set_meta("swimming_implemented",false)
	var root:Node3D=load("res://"+str(spec.runtime_addition).trim_prefix("Game/")).instantiate();root.name="Group6ThermalEntries";room.add_child(root)
	var count:=0
	for mesh:MeshInstance3D in root.find_children("*","MeshInstance3D",true,false):
		assert(spec.new_mesh_roles.has(str(mesh.name)))
		var role:String=str(spec.new_mesh_roles[str(mesh.name)]);mesh.set_meta("group6_contact_role",role)
		if role=="visible_entry_architecture":load("res://scripts/static_contact_cache.gd").attach(mesh)
		else:assert(role=="visual_grip_no_contact")
		count+=1
	assert(count==spec.new_meshes.size())
	root.set_meta("persistent_id","aquatic_thermal_"+key+"_entry_successor_001")
	root.set_meta("water_gameplay_implemented",false);root.set_meta("production_accepted",false)
	return root
