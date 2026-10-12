extends RefCounted
# Inactive shared-interface proposal. Owner chooses adoption; no automatic install.
const CONTRACT="res://data/architecture/group6_completion/CASCADE_PROPOSAL001.json"
static func build(annex:Node3D)->Node3D:
	assert(annex.name=="AquaticRiverSlideAnnex_WIP" and annex.get_node_or_null("Group6CascadeInterfaceProposal")==null)
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	assert(FileAccess.get_sha256("res://assets/models/Group6CascadeInterfaceProposal_r002.glb")==str(p.export_sha256))
	assert(str(annex.get_node("ExactAquaticArchitecture").get_meta("checked_group6_export_sha256",""))==str(p.required_annex_runtime_sha256),"Cascade proposal needs the exact fitted r019 source")
	assert(FileAccess.get_sha256("res://assets/models/AST-AQU-015.glb")==str(p.required_registered_watercourse_sha256))
	var root:=Node3D.new();root.name="Group6CascadeInterfaceProposal";root.set_meta("persistent_id","aquatic_cascade_maintenance_console_proposal_001");root.set_meta("programme_key","D08_directory_08");root.set_meta("production_accepted",false);root.set_meta("fluid_or_acoustic_operation_implemented",false);annex.add_child(root)
	var visual:Node3D=load("res://assets/models/Group6CascadeInterfaceProposal_r002.glb").instantiate();root.add_child(visual);var count:=0
	for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
		assert(p.new_mesh_roles.has(str(mesh.name)));var role:String=str(p.new_mesh_roles[str(mesh.name)])
		if role=="architecture":load("res://scripts/static_contact_cache.gd").attach(mesh)
		elif role=="fixture_lens":mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		else:assert(role=="mechanical_wheel")
		count+=1
	assert(count==p.new_mesh_hashes.size())
	for fitting in p.valves:
		var control:Node3D=load("res://scripts/group6_completion/cascade_isolator.gd").new();control.name=str(fitting.id);control.fitting=fitting;control.source_mesh=visual.find_child(str(fitting.mesh),true,false);assert(control.source_mesh!=null);root.add_child(control)
	var spec:Dictionary=p.task_light;var source:=vec(spec.source_xyz);var target:=vec(spec.target_xyz);var light:=SpotLight3D.new();light.name=str(spec.id);root.add_child(light);light.position=source;light.look_at(target,Vector3.UP);light.light_energy=float(spec.energy);light.light_color=Color(1,.95,.86);light.spot_range=float(spec.range_m);light.spot_angle=float(spec.half_cone_degrees);light.shadow_enabled=true;light.set_meta("illumination_anchor",target)
	return root
static func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
