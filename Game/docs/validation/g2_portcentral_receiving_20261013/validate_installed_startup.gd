extends SceneTree
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(30):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var added:Node3D=ship.get_node("ShipSpace/Group2PortCentralSupportedPair");var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_portcentral_receiving_20261013/PLAN.json"))
 assert(added.get_meta("default_main_adoption")and added.get_meta("new_units_or_capacity")==0 and not added.get_meta("operating_care_private_services_or_structuralcapacity"))
 for path in p.model_pins:assert(FileAccess.get_sha256("res://"+str(path))==str(p.model_pins[path]))
 assert(added.get_node("ReceivingFrame").find_children("*","MeshInstance3D",true,false).size()==p.parts.size())
 assert(added.find_children("*","OmniLight3D",true,false).size()==2)
 for light:Light3D in added.find_children("*","Light3D",true,false):assert(budget.sources.count(light)==1)
 assert(added.get_node("port_central_upper_house/RetainedSource").find_child("CareStoneSurface",true,false)!=null)
 var space:=ship.get_world_3d().direct_space_state
 for at:Vector3 in[Vector3(-84,102,-20),Vector3(-75,102,-15.1),Vector3(-68,102,-15.1)]:
  var hit:Dictionary=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.02,at-Vector3.UP*.02));assert(not hit.is_empty()and added.get_node("ReceivingFrame").is_ancestor_of(hit.collider)and absf(hit.position.y-at.y)<.002)
 assert(space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-67.3,102.7,-15.1),Vector3(-66.8,102.7,-15.1))).is_empty())
 assert(ship.get_node("ShipSpace/Group2CentralSupportedAdjunct").get_meta("default_main_adoption")and ship.get_node("ShipSpace/Group2ForwardSupportedPairs").get_meta("default_main_adoption"))
 var clinical:Node3D=ship.get_node("ShipSpace/Group3CompleteClinical");assert(clinical.find_children("*","OmniLight3D",true,false).size()==193 and not clinical.get_meta("clinical_operational_acceptance")and not clinical.get_meta("operating_gates_or_dispatch_admitted"))
 assert(ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms").get_child_count()==303)
 FileAccess.open("/workspace/astraea-integration-cutoff-20261013/g2_last_three_pairs_20261013/INSTALLED_STARTUP_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_INSTALLED_PORTCENTRAL_ADJUNCT_CARE","new_frame_parts":p.parts.size(),"source_adjuncts":1,"care_kits":1,"source_floor_m2":80.,"missing_connector_m2":30.06,"operating_or_structuralcapacity_accepted":false,"prior_three_pairs_and_clinical_holds_unchanged":true,"full_build_accepted":false},"  "));print("PORTCENTRAL_INSTALLED_STARTUP_PASS");quit(0)
