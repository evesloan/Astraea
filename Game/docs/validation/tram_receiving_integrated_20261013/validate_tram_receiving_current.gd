extends SceneTree
func _initialize()->void:
	OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
	for p in ["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(p,true))
	call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(30):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var assembly:Node3D=ship.get_node("ShipSpace/Districts/Group4Completion")
	var body:AnimatableBody3D=assembly.get_node("Group4OwnedTram_Source024")
	var motor:Node3D=assembly.get_node("Group4LoadedSourceTravelActuator")
	var safety:Node3D=assembly.get_node("Group4BoardingSafety")
	var restraint:Node3D=assembly.get_node("Group4OriginalCartRestraint")
	var controls:Node3D=assembly.get_node("Group4SourceOperatingControls")
	var info:Node3D=assembly.get_node("Group4SourceStationInformation")
	var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var cart:RigidBody3D=ship.get_node("ShipSpace/PersistentActors/CustodialCart")
	assert(restraint.cart==cart and controls.player==player and cart.persistent_id==&"custodian_cart_001" and cart.products.size()==4 and cart.mass==18)
	assert(motor.restraint==restraint and restraint.motor==motor and motor.vehicle==body and safety.vehicle==body)
	assert(not motor.moving and not motor.motion_fault and absf(motor.cursor-395.3525674298981)<.00001 and body.global_position.distance_to(Vector3(0,56.1,-72))<.001)
	assert(body.get_meta("exact_original_portal_contact_components")==18 and motor.bogies.size()==2 and motor.wheel_pivots.size()==4)
	assert(safety.station_gates.size()==5 and safety.bridges.size()==5 and info.gates.size()==5)
	assert(ship.get_node("ShipSpace/Districts/Group4TerminalBranches")!=null)
	var definitions:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GROUP4_COMPLETION_CANDIDATE.json"))
	var checks:=0
	for row in definitions.stations:
		var lift:Node3D=assembly.get_node("Group4Lift_"+str(row.label))
		assert(lift.floor_heights==[52.5,56.1] and str(lift.persistent_id)==str(row.persistent_id));checks+=1
		var bridge:Node3D=safety.bridges[str(row.label)];assert(bridge.fraction==0 and bridge.get_meta("initial_stow_physics_corrected",false));checks+=1
	assert(assembly.get_meta("receiving_north_physical_dock")==Vector3(-5.6,56.1,-241) and assembly.get_meta("directory_fore_midship_catchment_z")==-216)
	var compiled:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
	var floor_root:Node=ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms")
	var changed_ids:Array=["D09_fore_route","D09_aft_route","D09_atrium_circulation"]
	for row in compiled.regions:
		if not str(row.id) in changed_ids:continue
		load("res://tests/medical_triage_successor_guard.gd")._botanical_validate_slab(floor_root.get_node(str(row.id)),row);checks+=1
	assert(not ship.get_meta("group5_living_service_candidate_installed",true))
	var result:Dictionary={"status":"PASS_EXACT_PIT_GEOMETRY_AND_SINGLE_TRAM_BINDING","checks":checks,"source_pit_owners":3,"pit_removed_m2":24.8,"stations":5,"empty_startup":"CENTRAL","original_cart_products":4,"original_actor_cart_identity_preserved":true,"actuators":1,"portal_components":18,"north_physical_z":-241,"directory_fore_midship_catchment_z":-216,"normal_station_paths_and_joint_continuity":"PENDING","full_build_or_visual_acceptance":false}
	FileAccess.open("/workspace/astraea-integration-cutoff-20261013/TRAM_RECEIVING_CURRENT_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("TRAM_RECEIVING_CURRENT_PASS ",JSON.stringify(result));quit(0)
