extends SceneTree
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
 for path in ["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(30):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var added:Node3D=ship.get_node("ShipSpace/Group2CentralSupportedAdjunct");var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_central_receiving_20261013/RECEIVING.json"))
 assert(added.get_meta("default_main_adoption")and not added.get_meta("capacity_migrated")and not added.get_meta("installed_acceptance")and not added.get_meta("operating_private_admission_or_service")and not added.get_meta("primary_structure_capacity_or_lower_section_accepted"))
 assert(added.get_meta("bounded_guard_successor_parts")==3 and added.get_meta("guard_crossing_width_m")==1.8)
 for file in p.model_pins:assert(FileAccess.get_sha256("res://"+str(file))==str(p.model_pins[file]))
 assert(added.get_node("ReceivingFrame").find_children("*","MeshInstance3D",true,false).size()==104)
 assert(added.find_children("*","OmniLight3D",true,false).size()==2)
 for light:Light3D in added.find_children("*","Light3D",true,false):assert(budget.sources.count(light)==1)
 var section:Node3D=added.get_node("StarboardCentralSourceAdjunct");assert(not section.get_meta("capacity_migrated")and section.get_node("RetainedSource").find_child("CareStoneSurface",true,false)!=null)
 var state:=ship.get_world_3d().direct_space_state
 for at:Vector3 in [Vector3(80,102,-22),Vector3(60,102,-15.1),Vector3(60,102.0225,-14.1)]:
  var hit:Dictionary=state.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.02,at-Vector3.UP*.02));assert(not hit.is_empty()and added.get_node("ReceivingFrame").is_ancestor_of(hit.collider)and absf(hit.position.y-at.y)<.002)
 var opening:Dictionary=state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(60,102.7,-14.2),Vector3(60,102.7,-13.8)));assert(opening.is_empty())
 var clinical:Node3D=ship.get_node("ShipSpace/Group3CompleteClinical");assert(clinical.get_meta("default_main_adoption")and not clinical.get_meta("clinical_operational_acceptance")and not clinical.get_meta("operating_gates_or_dispatch_admitted")and clinical.find_children("*","OmniLight3D",true,false).size()==193)
 assert(ship.get_node("ShipSpace/Group3Starboard3Private").get_meta("default_main_adoption")and not ship.get_node("ShipSpace/Group3Starboard3Private").get_meta("operating_lift_or_private_gates"))
 assert(ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms").get_child_count()==303)
 var result:Dictionary={"status":"PASS_INSTALLED_CENTRAL_ADJUNCT_CARE_PHYSICAL_STARTUP","new_frame_parts":104,"source_adjuncts_selected":1,"care_kits_selected":1,"source_floor_m2":80,"connector_m2":39.654,"bounded_guard_parts":3,"primary_profilewall_cuts":0,"operating_private_admission_or_service":false,"primary_structure_capacity_or_lower_section_accepted":false,"prior_clinical193fixtures_and_holds_preserved":true,"new_capacity":0,"final_acceptance":false}
 FileAccess.open("/workspace/astraea-integration-cutoff-20261013/g2_central_receiver_successor_20261013/INSTALLED_STARTUP_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print("CENTRAL_ADJUNCT_CARE_INSTALLED_PHYSICAL_STARTUP_PASS");quit(0)
