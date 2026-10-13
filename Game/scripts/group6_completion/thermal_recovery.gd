extends RefCounted
# Inactive additive fit-out around five existing benches. Adopt before the
# original residency/light-budget setup. Existing fitting bindings are optional
# and require reconciliation by the sole shared integration writer.
const CONTRACT="res://data/architecture/group6_completion/THERMAL_RECOVERY_CONTRACT.json"
static func build(room:Node3D,bind_existing_fittings:bool=false)->Node3D:
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(CONTRACT));var spec:Dictionary={}
	for item in data.rooms:
		if str(item.programme_key)==str(room.get_meta("programme_key")):spec=item
	assert(not spec.is_empty() and room.get_node_or_null("Group6ThermalRecovery")==null)
	var support:Node3D=room.get_node_or_null("Group6ThermalSupport");assert(support!=null and str(support.get_meta("checked_export_sha256"))==str(spec.required_support_export_sha256))
	for pair in [[spec.current_room_runtime,spec.current_room_runtime_sha256],[spec.required_support_export,spec.required_support_export_sha256],[spec.runtime_addition,spec.export_sha256]]:
		assert(FileAccess.get_sha256("res://"+str(pair[0]).trim_prefix("Game/"))==str(pair[1]))
	var originals:Array=spec.bays+spec.optional_existing_fixture_bindings
	for original in originals:
		var name:String=str(original.get("existing_bench_mesh",original.get("original_source_mesh","")));var expected:Array=original.get("existing_bench_bounds_xyz",original.get("original_source_mesh_bounds_xyz",[]));var mesh:MeshInstance3D=room.find_child(name,true,false);assert(mesh!=null)
		var actual:AABB=mesh.global_transform*mesh.get_aabb()
		for k in range(3):assert(absf(actual.position[k]-float(expected[k][0]))<.002 and absf(actual.end[k]-float(expected[k][1]))<.002,"Thermal recovery current source mismatch "+name)
	# Complete preflight before applying the narrowly scoped fixture successor.
	if spec.corner_fixture_repair!=null:
		for name in spec.corner_fixture_repair.original_source_parts_to_successors:
			var mesh:MeshInstance3D=room.find_child(str(name),true,false);assert(mesh!=null and mesh.get_node_or_null("StaticContact")!=null)
		for name in spec.corner_fixture_repair.original_source_parts_to_successors:
			var mesh:MeshInstance3D=room.find_child(str(name),true,false);mesh.get_node("StaticContact").free();mesh.visible=false;mesh.set_meta("group6_source_successor",str(spec.corner_fixture_repair.original_source_parts_to_successors[name]))
	var addition:Node3D=load("res://"+str(spec.runtime_addition).trim_prefix("Game/")).instantiate();addition.name="Group6ThermalRecovery";room.add_child(addition)
	var count:=0
	for mesh:MeshInstance3D in addition.find_children("*","MeshInstance3D",true,false):
		assert(spec.new_mesh_roles.has(str(mesh.name)));var role:String=str(spec.new_mesh_roles[str(mesh.name)]);mesh.set_meta("group6_contact_role",role)
		if role in ["recovery_architecture","retained_fixture_successor"]:load("res://scripts/static_contact_cache.gd").attach(mesh)
		else:assert(role in ["fixture_lens","visual_vessel_rest"])
		count+=1
	assert(count==spec.new_meshes.size())
	var fittings:Array=spec.new_task_fittings.duplicate()
	if bind_existing_fittings:fittings.append_array(spec.optional_existing_fixture_bindings)
	for fitting in fittings:
		if fitting.has("source_mesh"):
			var source_mesh:MeshInstance3D=room.find_child(str(fitting.source_mesh),true,false);assert(source_mesh!=null);var aabb:AABB=source_mesh.global_transform*source_mesh.get_aabb();var actual_source:=Vector3(aabb.get_center().x,aabb.position.y-.025,aabb.get_center().z);var declared:=Vector3(float(fitting.source_xyz[0]),float(fitting.source_xyz[1]),float(fitting.source_xyz[2]));assert(actual_source.distance_to(declared)<.0001,"Legacy emitter differs from actual lens")
		var source:=Vector3(float(fitting.source_xyz[0]),float(fitting.source_xyz[1]),float(fitting.source_xyz[2]));var target:=Vector3(float(fitting.target_xyz[0]),float(fitting.target_xyz[1]),float(fitting.target_xyz[2]));var light:=SpotLight3D.new();light.name=str(fitting.id)+"_PhysicalSource";addition.add_child(light);light.position=source;light.light_energy=float(fitting.energy);light.light_color=Color(float(fitting.color_rgb[0]),float(fitting.color_rgb[1]),float(fitting.color_rgb[2]));light.spot_range=float(fitting.range_m);light.spot_angle=float(fitting.half_cone_degrees)
		light.look_at(addition.to_global(target),Vector3.RIGHT if absf((target-source).normalized().dot(Vector3.UP))>.99 else Vector3.UP);light.shadow_enabled=true;light.set_meta("illumination_anchor",target);light.set_meta("source_fixture_mesh",str(fitting.get("source_mesh","new recovery canopy task")))
	addition.set_meta("persistent_id","aquatic_thermal_"+str(spec.programme_key)+"_recovery_001");addition.set_meta("checked_export_sha256",str(spec.export_sha256));addition.set_meta("new_seats_rooms_floors_or_capacity",0);addition.set_meta("dayrest_species_acoustic_service_accepted",false);addition.set_meta("existing_source_bindings_enabled",bind_existing_fittings)
	return addition
