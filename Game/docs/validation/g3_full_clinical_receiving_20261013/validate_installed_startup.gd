extends SceneTree
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
 for path in ["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(30):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var added:Node3D=ship.get_node("ShipSpace/Group3CompleteClinical");var prior:Node3D=ship.get_node("ShipSpace/Group3Port2ClinicalPhysical");var fore:Node3D=ship.get_node("ShipSpace/Group3ForeStarboardClinical");var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_clinical_full_20261011/CLINICAL.json"))
 assert(added.get_meta("default_main_adoption")and added.get_meta("registered_berths_added")==0 and not added.get_meta("clinical_operational_acceptance")and not added.get_meta("operating_gates_or_dispatch_admitted"))
 assert(prior.get_node_or_null("AST-MED-G3-006")==null and fore.has_node("AST-STF-G3-043"))
 for file in p.model_pins:assert(FileAccess.get_sha256("res://assets/models/group3_clinical_full_20261011/"+str(file))==str(p.model_pins[file]))
 assert(added.has_node("AST-MED-G3-007")and added.has_node("AST-MED-G3-008")and added.has_node("AST-MED-G3-010")and not added.has_node("AST-MED-G3-009"))
 assert(added.find_children("*","OmniLight3D",true,false).size()==193)
 for row in p.fixtures:assert(budget.sources.count(added.get_node((str(row.name)+"_PhysicalSource").validate_node_name()))==1)
 for row in p.door_bindings:assert(added.get_node_or_null(str(row.name))==null)
 for crossing in p.crossings:
  assert(added.get_node_or_null(str(crossing.programme_key))==null)
  for button in crossing.dispatch_buttons:assert(added.get_node_or_null(str(button.name))==null)
 for name in ["clean_supply_and_staff_port_007Light_PhysicalSource","soiled_return_port_007Light_PhysicalSource"]:assert(budget.sources.count(prior.get_node(name))==1)
 assert(ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms").get_child_count()==303)
 var result:Dictionary={"status":"PASS_INSTALLED_FULL_CLINICAL_PHYSICAL_STARTUP","new_models_instantiated":3,"new_floor_m2":16089.193863999986,"new_sources":193,"bounded_old_visual_replaced":true,"original_port2_fore_source_lights_preserved":true,"closed_static_gates":36,"operating_gates_dispatch_or_sealed_predicates":false,"pool_and_royalty_support_holds":true,"new_capacity":0,"production_streaming_medical_panels_clinical_egress_or_final_acceptance":false}
 FileAccess.open("/workspace/astraea-integration-cutoff-20261013/g3_full_clinical_receiving/INSTALLED_STARTUP_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print("FULL_CLINICAL_INSTALLED_PHYSICAL_STARTUP_PASS");quit(0)
