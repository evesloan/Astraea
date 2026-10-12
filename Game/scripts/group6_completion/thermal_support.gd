extends RefCounted
# Additive fixed thermal construction; apply after entry complement and before
# the original residency/light-budget setup. No player or water hook supplied.
const CONTRACT="res://data/architecture/group6_completion/THERMAL_SUPPORT_CONTRACT.json"
static func build(room:Node3D)->Node3D:
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(CONTRACT));var spec:Dictionary={}
	for item in data.rooms:
		if str(item.programme_key)==str(room.get_meta("programme_key")):spec=item
	assert(not spec.is_empty() and room.get_node_or_null("Group6ThermalSupport")==null)
	var entry:Node3D=room.get_node_or_null("Group6ThermalEntries")
	assert(entry!=null and str(entry.get_meta("persistent_id"))=="aquatic_thermal_"+str(spec.programme_key)+"_entry_successor_001")
	for pair in [[spec.current_room_runtime,spec.current_room_runtime_sha256],[spec.required_entry_export,spec.required_entry_export_sha256],[spec.runtime_addition,spec.export_sha256]]:
		assert(FileAccess.get_sha256("res://"+str(pair[0]).trim_prefix("Game/"))==str(pair[1]))
	var addition:Node3D=load("res://"+str(spec.runtime_addition).trim_prefix("Game/")).instantiate();addition.name="Group6ThermalSupport";room.add_child(addition)
	var count:=0
	for mesh:MeshInstance3D in addition.find_children("*","MeshInstance3D",true,false):
		assert(spec.new_mesh_roles.has(str(mesh.name)));var role:String=str(spec.new_mesh_roles[str(mesh.name)])
		mesh.set_meta("group6_contact_role",role)
		if role=="fixed_support_architecture":load("res://scripts/static_contact_cache.gd").attach(mesh)
		else:assert(role in ["visual_control_interface","visual_soft_furnishing","fixture_lens"])
		count+=1
	assert(count==spec.new_meshes.size())
	for station in spec.stations:
		var fitting:Dictionary=station.task_light;var source:=Vector3(float(fitting.source_xyz[0]),float(fitting.source_xyz[1]),float(fitting.source_xyz[2]));var target:=Vector3(float(fitting.target_xyz[0]),float(fitting.target_xyz[1]),float(fitting.target_xyz[2]))
		var light:=SpotLight3D.new();light.name=str(fitting.id)+"_PhysicalSource";addition.add_child(light);light.position=source;light.light_energy=float(fitting.energy);light.light_color=Color(1,.95,.86);light.spot_range=float(fitting.range_m);light.spot_angle=float(fitting.half_cone_degrees)
		light.look_at(addition.to_global(target),Vector3.UP);light.shadow_enabled=true;light.set_meta("illumination_anchor",target)
	addition.set_meta("persistent_id","aquatic_thermal_"+str(spec.programme_key)+"_support_001")
	addition.set_meta("occupied_hoist_water_species_accepted",false);addition.set_meta("new_room_capacity",0);addition.set_meta("checked_export_sha256",str(spec.export_sha256))
	return addition
