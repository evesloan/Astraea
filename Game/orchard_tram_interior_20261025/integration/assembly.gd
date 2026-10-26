extends RefCounted
# New empty assembly only. Never hot-swap a live tram or create a second owner.
const ROOT:="res://tram_section_successor_20261024/"
const SOURCE:="res://source_derivatives/group4_completion_20261011/"

static func verify()->bool:
	var own:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://orchard_tram_interior_20261025/integration/CONTRACTS.json"))
	for path:String in own.owned:
		if FileAccess.get_sha256(path)!=str(own.owned[path]):push_error("Orchard integration pin mismatch: "+path);return false
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

static func create(parent:Node3D,initial_station:String="CENTRAL")->Node3D:
	if not verify():return null
	assert(not parent.has_node("Group4Completion") and not parent.has_node("Group4SectionSuccessor20261024"),"Build once into an empty owner; never replace surviving Group4")
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://orchard_tram_interior_20261025/r006/PLAN.json"))
	assert(not plan.active and plan.unresolved_receivers.is_empty())
	var assembly:Node3D=_build_base(parent,true,true)
	assembly.name="Group4SectionSuccessor20261024"
	assembly.set_meta("tram_operations_admitted",false)
	assembly.set_meta("source_candidate",true)
	assembly.set_meta("tram_operation_hold","Installed-neighbor/body sweep, curved boarding, caster/joint and passenger acceptance pending")
	load("res://scripts/group4_aftmid_upper_successor.gd").build(assembly)
	var completion:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GROUP4_COMPLETION_CANDIDATE.json"))
	var retired:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://orchard_tram_interior_20261025/integration/RETIRED_RECEIVERS.json"))
	assert(FileAccess.get_sha256(retired.source)==retired.source_sha256)
	var removed_retired:=0
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
				if retired.members.has(name):remove=true;removed_retired+=1
				for exact in ["V2_Central_NorthEnd_infill","V2_Central_NorthEnd_rail","V2__CENTRAL__Boarding_Post_-73.2","V2__CENTRAL__Boarding_Post_-70.8","V2__CENTRAL__Boarding_Header"]:
					if name==str(exact).validate_node_name():remove=true
				if remove:mesh.free()
			rebuild_contacts(owner,policies)
	assert(removed_retired==retired.members.size())
	var section:Node3D=raw_model(ROOT+"section_r002.glb")
	assert(section!=null);section.name="NamedSectionReceiving20261024";assembly.add_child(section)
	for mesh:MeshInstance3D in section.find_children("*","MeshInstance3D",true,false):
		if str(mesh.name) in ["TSC23_ContinuousWeb","TSC23_RailPort","TSC23_RailStarboard"]:mesh.free()
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
	var initial:Dictionary={}
	for stop:Dictionary in plan.stops:
		if stop.station==initial_station:initial=stop
	assert(not initial.is_empty(),"Named initial station required; no live relocation")
	var initial_pose:=Transform3D(Basis(Vector3.UP,initial.body_yaw),Vector3(initial.world_xyz[0],56.1,initial.world_xyz[2]))
	var body:AnimatableBody3D=load("res://tram_passenger_successor_20261024/vehicle_initial_pose_r002.gd").create_candidate_vehicle(assembly,initial_pose)
	if body==null:return null
	body.sync_to_physics=false
	body.set_meta("group4_initial_source_cursor",initial.distance_m)
	var safety:Node3D=load("res://orchard_tram_interior_20261025/integration/boarding.gd").build(assembly,assembly,body,true)
	assert(safety.phase=="secured" and not safety.get_meta("integration_boarding_admitted"))
	_add_receiving(assembly)
	return assembly

static func attach_original_cart(assembly:Node3D,cart:RigidBody3D)->Node3D:
	assert(not assembly.has_node("Group4OriginalCartRestraint"))
	var body:AnimatableBody3D=assembly.get_node("Group4OwnedTram_Source024")
	var safety:Node3D=assembly.get_node("Group4BoardingSafety")
	var restraint:Node3D=load("res://scripts/group4_cart_restraint.gd").build(assembly,body,safety,cart,true)
	restraint.set_meta("integration_joint_admitted",false)
	var motor:Node3D=load("res://orchard_tram_interior_20261025/integration/motor.gd").attach_section(assembly,body,safety,restraint)
	assert(not motor.moving and not motor.get_meta("integration_motion_admitted"))
	return motor

static func _build_base(parent:Node3D, candidate_only:bool=false, receivers_confirmed:bool=false)->Node3D:
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GROUP4_COMPLETION_CANDIDATE.json"))
	var pit:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://orchard_tram_interior_20261025/integration/PIT_AND_BINDING.json"))
	for i in range(p.stations.size()):
		if p.stations[i].label=="FORE_MIDSHIP":p.stations[i]=pit.station
	if not p.active and not candidate_only:return null
	assert(receivers_confirmed,"Group4 requires exact shared pit receiving and north adoption; default main is inactive")
	assert(not parent.has_node("Group4Completion"),"One Group4 assembly per world")
	var n:=Node3D.new();n.name="Group4Completion";parent.add_child(n)
	n.set_meta("candidate_only",candidate_only)
	for item in p.models:
		assert(FileAccess.get_sha256(SOURCE+item.file)==item.sha256,"Group4 original model pin changed")
		if item.role in ["bridge_component","vehicle_component","station_FORE_MIDSHIP"]:continue
		load("res://scripts/group4_completion.gd").visual(n,item.file,item.policies)
	for st in p.stations:
		var lift:Node3D=load("res://scripts/commons_lift.gd").new()
		lift.name="Group4Lift_"+st.label
		lift.floor_heights.assign(st.floor_heights);lift.deck_numbers.assign(st.deck_numbers)
		lift.stop_ids.assign(st.stop_ids);lift.stop_names.assign(st.stop_names);lift.stop_codes.assign(st.stop_codes)
		lift.gate_origin_xz=Vector2.ZERO;lift.identity_prefix=st.identity_prefix
		lift.persistent_id=StringName(st.persistent_id);lift.district_label=st.label.replace("_"," ").capitalize()+" Townline"
		lift.position=Vector3(st.lift_root[0],0,st.lift_root[2]);lift.rotation.y=st.lift_yaw_rad
		n.add_child(lift)
		# The bridge adapter receives docking authority; it has no independent input controller.
		var bridge:Node3D=load("res://tram_section_successor_20261024/bridge.gd" if st.label=="FORE_MIDSHIP" else "res://scripts/group4_boarding_bridge.gd").new()
		bridge.name="Group4Bridge_"+st.label
		bridge.model_path=SOURCE+"AST-TRM-G4-019_boarding_bridge.glb"
		if st.label=="FORE_MIDSHIP":
			bridge.model_path="res://orchard_tram_interior_20261025/integration/ForemidBridge.glb";bridge.panel_reach=st.bridge_reach_m
		bridge.position=Vector3(st.boarding_edge_x,56.1,st.physical_docking_z)
		bridge.rotation.y=0.0 if st.vehicle_door_side=="port" else PI
		n.add_child(bridge)
	for item in p.lights:
		if str(item.source)=="AST-TRM-G4-020_foremid_north_candidate.glb":continue
		var light:=OmniLight3D.new();light.name=item.name+"_OperatingLight";n.add_child(light)
		light.position=Vector3(item.xyz[0],item.xyz[1],item.xyz[2]);light.omni_range=item.range
		light.light_energy=item.energy;light.light_color=Color(item.color[0],item.color[1],item.color[2])
		light.shadow_enabled=true;light.visible=false;light.omni_shadow_mode=OmniLight3D.SHADOW_CUBE
		light.set_meta("source_fixture",item.name);light.set_meta("fixture_powered",true)
	n.set_meta("operating_scope","Five original two-stop lift bindings; source bridge adapter. No operating tram travel or cart restraint")
	return n

static func _add_receiving(assembly:Node3D)->void:
	var receiving:Node3D=raw_model("res://orchard_tram_interior_20261025/r006/OrchardInteriorReceiving.glb")
	assert(receiving!=null);receiving.name="OrchardInteriorReceiving";assembly.add_child(receiving)
	var fixed:Array[Node]=[];var rolling:Array[Node]=[]
	for mesh:MeshInstance3D in receiving.find_children("*","MeshInstance3D",true,false):
		if "ContinuousWeb" in str(mesh.name) or "Orchard_Rail_" in str(mesh.name):rolling.append(mesh)
		else:fixed.append(mesh)
	for row in [["FixedReceivingContacts",fixed],["RollingGuidewayContacts",rolling]]:
		var owner:=Node3D.new();owner.name=row[0];receiving.add_child(owner)
		for mesh in row[1]:mesh.reparent(owner,true)
		load("res://scripts/static_contact_cache.gd").attach_group(owner,row[1])
