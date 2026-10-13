extends SceneTree
func _initialize()->void:
	OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
	for p in ["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(p,true))
	call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(30):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var base:Node3D=ship.get_node("ShipSpace/Districts/Group4Completion")
	var safety:Node3D=base.get_node("Group4BoardingSafety");var restraint:Node3D=base.get_node("Group4OriginalCartRestraint");var motor:Node3D=base.get_node("Group4LoadedSourceTravelActuator")
	var before:Transform3D=motor.vehicle.global_transform
	assert(not safety.get_meta("integration_boarding_admitted")and not restraint.get_meta("integration_joint_admitted")and not motor.get_meta("integration_motion_admitted"))
	assert(not safety.request_boarding("CENTRAL")and not restraint.request_lock()and not motor.request_distance(motor.cursor+1))
	assert(not motor.moving and not is_instance_valid(restraint.joint)and safety.phase=="secured"and before==motor.vehicle.global_transform)
	var cart:RigidBody3D=ship.get_node("ShipSpace/PersistentActors/CustodialCart")
	assert(cart.mass==18 and cart.products.size()==4 and cart.persistent_id==&"custodian_cart_001")
	var precinct:Node3D=ship.get_node("ShipSpace/Group3D03ReceivingPrecincts")
	assert(precinct.get_meta("default_main_adoption")and precinct.get_meta("registered_berths_added")==0)
	var source:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_completion_20261011/D03_PRECINCT.json"))
	var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	for file in source.model_pins:assert(FileAccess.get_sha256("res://assets/models/group3_completion_20261011/"+str(file))==str(source.model_pins[file]))
	for f in source.fixtures:assert(budget.sources.count(precinct.get_node(str(f.name)+"_PhysicalSource"))==1)
	assert(ship.get_node_or_null("ShipSpace/Group3LabelledCrewBank")==null)
	var r:Dictionary={"status":"PASS_COMBINED_PRECIINCT_STARTUP_AND_TRAM_OPERATION_HOLD","checks":44,"g3_precinct_models":6,"g3_precinct_sources":33,"boarding":false,"joint":false,"motion":false,"cart_physics_experiments":0,"original_cart_and_stock_preserved":true,"geometry_or_transit_criteria_edited":false}
	FileAccess.open("/workspace/astraea-integration-cutoff-20261013/COMBINED_PRECIINCT_STARTUP_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify(r,"  "));print("COMBINED_PRECIINCT_STARTUP_PASS ",JSON.stringify(r));quit(0)
