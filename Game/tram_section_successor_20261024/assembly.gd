extends RefCounted
# New empty assembly only. Never hot-swap a live tram or create a second owner.
const ROOT:="res://tram_section_successor_20261024/"
const SOURCE:="res://source_derivatives/group4_completion_20261011/"

static func verify()->bool:
	var contracts:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(ROOT+"CONTRACTS.json"))
	for group in [contracts.prerequisites,contracts.owned]:
		for path:String in group:
			if FileAccess.get_sha256(path)!=str(group[path]):
				push_error("Tram section exact source mismatch: "+path);return false
	return true

static func raw_model(path:String)->Node3D:
	var document:=GLTFDocument.new();var state:=GLTFState.new()
	var error:=document.append_from_file(ProjectSettings.globalize_path(path),state)
	if error!=OK:push_error("Tram section GLTF error: "+path);return null
	return document.generate_scene(state)

static func rebuild_contacts(owner:Node3D,policies:Dictionary)->void:
	for body:StaticBody3D in owner.find_children("*","StaticBody3D",true,false):body.free()
	var selected:Array[Node]=[]
	for mesh:MeshInstance3D in owner.find_children("*","MeshInstance3D",true,false):
		assert(policies.has(str(mesh.name)))
		if policies[str(mesh.name)]!="no_collision_detail":selected.append(mesh)
	load("res://scripts/static_contact_cache.gd").attach_group(owner,selected)

static func create(parent:Node3D)->Node3D:
	if not verify():return null
	assert(not parent.has_node("Group4Completion") and not parent.has_node("Group4SectionSuccessor20261024"),"Build once into an empty owner; never replace surviving Group4")
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(ROOT+"section_plan_r002.json"))
	assert(not plan.active and plan.unresolved_receivers.is_empty())
	var assembly:Node3D=load("res://scripts/group4_completion.gd").build(parent,true,true)
	assembly.name="Group4SectionSuccessor20261024"
	assembly.set_meta("tram_operations_admitted",false)
	assembly.set_meta("source_candidate",true)
	assembly.set_meta("tram_operation_hold","Installed-neighbor/body sweep, curved boarding, caster/joint and passenger acceptance pending")
	load("res://scripts/group4_aftmid_upper_successor.gd").build(assembly)
	var completion:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GROUP4_COMPLETION_CANDIDATE.json"))
	for item:Dictionary in completion.models:
		var stem:String=str(item.file).get_basename()
		if "016_continuous_guideway" in stem:
			assembly.get_node(stem).free()
		elif "017_receiving_module" in stem or "014_central_source" in stem:
			var owner:Node3D=assembly.get_node(stem)
			var policies:Dictionary={}
			for name:String in item.policies:policies[name.validate_node_name()]=item.policies[name]
			for mesh:MeshInstance3D in owner.find_children("*","MeshInstance3D",true,false):
				var name:=str(mesh.name)
				var remove:=name.begins_with("M003_Site_") or name.begins_with("M003_UnderwebGirder_") or name.begins_with("M003_SouthFoot_")
				for exact in ["V2_Central_NorthEnd_infill","V2_Central_NorthEnd_rail","V2__CENTRAL__Boarding_Post_-73.2","V2__CENTRAL__Boarding_Post_-70.8","V2__CENTRAL__Boarding_Header"]:
					if name==str(exact).validate_node_name():remove=true
				if remove:mesh.free()
			rebuild_contacts(owner,policies)
	var section:Node3D=raw_model(ROOT+"section_r002.glb")
	assert(section!=null);section.name="NamedSectionReceiving20261024";assembly.add_child(section)
	var fixed:Array[Node]=[];var rolling:Array[Node]=[]
	for mesh:MeshInstance3D in section.find_children("*","MeshInstance3D",true,false):
		if str(mesh.name) in ["TSC23_ContinuousWeb","TSC23_RailPort","TSC23_RailStarboard"]:rolling.append(mesh)
		else:fixed.append(mesh)
	var support:=Node3D.new();support.name="FixedReceivingContacts";section.add_child(support)
	# Contact builder requires meshes below its root. Keep identity transforms.
	for mesh in fixed:mesh.reparent(support,true)
	load("res://scripts/static_contact_cache.gd").attach_group(support,fixed)
	var rail:=Node3D.new();rail.name="RollingGuidewayContacts";section.add_child(rail)
	for mesh in rolling:mesh.reparent(rail,true)
	load("res://scripts/static_contact_cache.gd").attach_group(rail,rolling)
	assembly.get_node("Group4Bridge_CENTRAL").free()
	var bridge:Node3D=load(ROOT+"bridge.gd").new();bridge.name="Group4Bridge_CENTRAL"
	bridge.model_path=ROOT+"bridge.glb";bridge.panel_reach=plan.central.bridge_reach_m
	bridge.position=Vector3(plan.central.bridge_origin_xyz[0],56.1,plan.central.bridge_origin_xyz[2]);bridge.rotation.y=plan.central.bridge_yaw
	assembly.add_child(bridge)
	var body:AnimatableBody3D=load("res://scripts/group4_boarding_safety.gd").create_candidate_vehicle(assembly,Vector3(plan.central.new_pose[1],56.1,plan.central.new_pose[2]))
	body.name="Group4OwnedTram_Source024";body.sync_to_physics=false;body.rotation.y=plan.central.new_pose[3]
	body.set_meta("group4_initial_source_cursor",plan.central.new_pose[0])
	var safety:Node3D=load(ROOT+"boarding.gd").build(assembly,assembly,body,true)
	assert(safety.phase=="secured" and not safety.get_meta("integration_boarding_admitted"))
	return assembly

static func attach_original_cart(assembly:Node3D,cart:RigidBody3D)->Node3D:
	assert(not assembly.has_node("Group4OriginalCartRestraint"))
	var body:AnimatableBody3D=assembly.get_node("Group4OwnedTram_Source024")
	var safety:Node3D=assembly.get_node("Group4BoardingSafety")
	var restraint:Node3D=load("res://scripts/group4_cart_restraint.gd").build(assembly,body,safety,cart,true)
	restraint.set_meta("integration_joint_admitted",false)
	var motor:Node3D=load(ROOT+"motor.gd").attach_section(assembly,body,safety,restraint)
	assert(not motor.moving and not motor.get_meta("integration_motion_admitted"))
	return motor
