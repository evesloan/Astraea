extends RefCounted
const CONTRACT="res://data/architecture/group6_completion/FIT_CONTRACT.json"
static func build(annex:Node3D,ship:Node3D)->Node3D:
	assert(annex.name=="AquaticRiverSlideAnnex_WIP")
	assert(annex.get_node_or_null("Group6Completion")==null,"Group 6 adapter must be applied exactly once")
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	assert(FileAccess.get_sha256("res://assets/models/AquaticCompletion_r019.glb")==str(p.export_sha256))
	var previous:Node3D=annex.get_node("ExactAquaticArchitecture")
	previous.free() # Runtime replacement only; original source/export stays immutable.
	var visual:Node3D=load("res://assets/models/AquaticCompletion_r019.glb").instantiate()
	visual.name="ExactAquaticArchitecture";annex.add_child(visual);visual.set_meta("checked_group6_export_sha256",str(p.export_sha256))
	var root:=Node3D.new();root.name="Group6Completion";annex.add_child(root)
	root.set_meta("persistent_id","group6_aquatic_construction_successor_001")
	root.set_meta("production_accepted",false);root.set_meta("water_gameplay_implemented",false)
	var policy:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_completion/COLLISION_POLICY.json"))
	for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
		assert(policy.has(str(mesh.name)),"Unreviewed Group 6 contact "+str(mesh.name))
		var role:String=policy[str(mesh.name)];mesh.set_meta("aquatic_contact_role",role)
		if role not in ["water_visual","tube_static_visual","plant_static","fixture_lens","finish_visual","privacy_leaf","privacy_door_proposal","valve_wheel"]:load("res://scripts/static_contact_cache.gd").attach(mesh)
		if role=="fixture_lens":mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	for fitting in p.doors:
		var door:Node3D=load("res://scripts/group6_completion/privacy_leaf.gd").new()
		door.name=str(fitting.id);door.persistent_id=StringName(fitting.id);door.fitting=fitting
		for leaf in fitting.leaves:
			var mesh:MeshInstance3D=visual.find_child(str(leaf.mesh),true,false);assert(mesh!=null);door.source_meshes.append(mesh)
		for name in fitting.control_names:
			var control:Node=visual.find_child(str(name),true,false);assert(control!=null);door.fixed_controls.append(control)
		door.open_fraction=0;door.desired_open=false;root.add_child(door)
	if p.has("water_care_cell"):
		var spec:Dictionary=p.water_care_cell.gate
		assert(FileAccess.get_sha256("res://assets/models/"+str(spec.source_asset))==str(spec.source_sha256))
		var gate:Node3D=load("res://scripts/group6_completion/wet_service_gate.gd").new()
		gate.name=str(spec.id);gate.persistent_id=StringName(spec.id);gate.position=Vector3(spec.xyz[0],spec.xyz[1],spec.xyz[2]);gate.rotation.y=float(spec.yaw_radians)
		gate.open_fraction=0;gate.desired_open=false;root.add_child(gate)
		for fitting in p.water_care_cell.valves:
			var control:Node3D=load("res://scripts/group6_completion/valve_control.gd").new()
			control.name=str(fitting.id);control.fitting=fitting
			control.source_mesh=visual.find_child(str(fitting.mesh),true,false);assert(control.source_mesh!=null)
			root.add_child(control)
	var optical:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_completion/OPTICAL_PROFILE001.json"))
	assert(str(optical.model_sha256)==str(p.export_sha256))
	for fitting in p.additional_lights:
		var spec:Dictionary=optical.fixtures[str(fitting.id)]
		var source:=Vector3(fitting.xyz[0],fitting.xyz[1],fitting.xyz[2]);var target:=Vector3(spec.target_xyz[0],spec.target_xyz[1],spec.target_xyz[2])
		assert(source.distance_to(Vector3(spec.source_xyz[0],spec.source_xyz[1],spec.source_xyz[2]))<.00001)
		var light:=SpotLight3D.new();light.name=str(fitting.id)+"_PhysicalSource";root.add_child(light)
		light.position=source;light.light_energy=float(spec.energy);light.light_color=Color(1,.95,.86)
		light.spot_range=float(spec.range_m);light.spot_angle=float(spec.half_cone_degrees)
		light.look_at(root.to_global(target),Vector3.RIGHT if absf((target-source).normalized().dot(Vector3.UP))>.99 else Vector3.UP)
		light.shadow_enabled=true;light.set_meta("illumination_anchor",target)
		light.set_meta("receiver_kind",str(spec.receiver_kind));light.set_meta("group6_optical_profile","OPTICAL_PROFILE001")
	# Normal integration must call this before the existing budget configure step.
	# Candidate tests add late and register explicitly without resetting old requests.
	return root
