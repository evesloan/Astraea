extends RefCounted
const CONTRACT="res://data/architecture/group6_completion/FIT_CONTRACT.json"
static func build(annex:Node3D,ship:Node3D)->Node3D:
	assert(annex.name=="AquaticRiverSlideAnnex_WIP")
	assert(annex.get_node_or_null("Group6Completion")==null,"Group 6 adapter must be applied exactly once")
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	assert(FileAccess.get_sha256("res://assets/models/AquaticCompletion_r013.glb")==str(p.export_sha256))
	var previous:Node3D=annex.get_node("ExactAquaticArchitecture")
	previous.free() # Runtime replacement only; original source/export stays immutable.
	var visual:Node3D=load("res://assets/models/AquaticCompletion_r013.glb").instantiate()
	visual.name="ExactAquaticArchitecture";annex.add_child(visual)
	var root:=Node3D.new();root.name="Group6Completion";annex.add_child(root)
	root.set_meta("persistent_id","group6_aquatic_construction_successor_001")
	root.set_meta("production_accepted",false);root.set_meta("water_gameplay_implemented",false)
	var policy:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_completion/COLLISION_POLICY.json"))
	for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
		assert(policy.has(str(mesh.name)),"Unreviewed Group 6 contact "+str(mesh.name))
		var role:String=policy[str(mesh.name)];mesh.set_meta("aquatic_contact_role",role)
		if role not in ["water_visual","tube_static_visual","plant_static","fixture_lens","finish_visual","privacy_leaf","privacy_door_proposal"]:load("res://scripts/static_contact_cache.gd").attach(mesh)
		if role=="fixture_lens":mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	for fitting in p.doors:
		var door:Node3D=load("res://scripts/group6_completion/privacy_leaf.gd").new()
		door.name=str(fitting.id);door.persistent_id=StringName(fitting.id);door.fitting=fitting
		for leaf in fitting.leaves:
			var mesh:MeshInstance3D=visual.find_child(str(leaf.mesh),true,false);assert(mesh!=null);door.source_meshes.append(mesh)
		for name in fitting.control_names:
			var control:Node=visual.find_child(str(name),true,false);assert(control!=null);door.fixed_controls.append(control)
		door.open_fraction=0;door.desired_open=false;root.add_child(door)
	for fitting in p.additional_lights:
		var light:=OmniLight3D.new();light.name=str(fitting.id)+"_PhysicalSource";root.add_child(light)
		light.position=Vector3(fitting.xyz[0],fitting.xyz[1],fitting.xyz[2]);light.light_energy=float(fitting.energy)
		light.omni_range=float(fitting.range_m);light.light_color=Color(1,.95,.86)
		light.shadow_enabled=true;light.omni_shadow_mode=OmniLight3D.SHADOW_CUBE
		light.set_meta("illumination_anchor",Vector3(fitting.receiver_xyz[0],fitting.receiver_xyz[1],fitting.receiver_xyz[2]))
	# Normal integration must call this before the existing budget configure step.
	# Candidate tests add late and register explicitly without resetting old requests.
	return root
