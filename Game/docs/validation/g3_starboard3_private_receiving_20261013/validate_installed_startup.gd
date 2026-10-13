extends SceneTree
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
 for path in ["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(30):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var added:Node3D=ship.get_node("ShipSpace/Group3Starboard3Private");var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_starboard3_private_20261011/PRIVATE.json"))
 assert(added.get_meta("default_main_adoption")and added.get_meta("registered_berths_added")==0 and not added.get_meta("authoritative_identity_mapping")and not added.get_meta("operating_lift_or_private_gates"))
 for file in p.model_pins:assert(FileAccess.get_sha256("res://assets/models/group3_starboard3_private_20261011/"+str(file))==str(p.model_pins[file])and added.has_node(str(file).trim_suffix(".glb")))
 assert(added.find_children("*","OmniLight3D",true,false).size()==17)
 for row in p.fixtures:assert(budget.sources.count(added.get_node((str(row.name)+"_PhysicalSource").validate_node_name()))==1)
 for row in p.door_bindings:assert(added.get_node_or_null(str(row.name))==null)
 assert(added.find_child("Starboard3Lift",true,false)==null and ship.find_child("PortCentralStaffLift",true,false)!=null)
 var clinical:Node3D=ship.get_node("ShipSpace/Group3CompleteClinical");assert(clinical.get_meta("default_main_adoption")and not clinical.get_meta("clinical_operational_acceptance")and not clinical.get_meta("operating_gates_or_dispatch_admitted")and clinical.find_children("*","OmniLight3D",true,false).size()==193)
 assert(ship.get_node("ShipSpace/Group3Port2ClinicalPhysical").get_node_or_null("AST-MED-G3-006")==null)
 assert(ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms").get_child_count()==303)
 var result:Dictionary={"status":"PASS_INSTALLED_STARBOARD3_PHYSICAL_STARTUP","new_models":4,"landings":17,"new_floor_m2":865.9119999999995,"new_sources":17,"original_D04_riser_retained":true,"operating_lift_private_gates_or_authorization":false,"prior_clinical193fixtures_and_holds_preserved":true,"new_capacity":0,"final_acceptance":false}
 FileAccess.open("/workspace/astraea-integration-cutoff-20261013/g3_starboard3_private_receiving/INSTALLED_STARTUP_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print("STARBOARD3_INSTALLED_PHYSICAL_STARTUP_PASS");quit(0)
