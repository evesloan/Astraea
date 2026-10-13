extends SceneTree
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
 for path in ["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(30):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var added:Node3D=ship.get_node("ShipSpace/Group2ForwardSupportedPairs");var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_forward_receiving_20261013/FORWARD.json"))
 assert(added.get_meta("default_main_adoption")and added.get_meta("registered_units_or_capacity")==0 and not added.get_meta("operating_care_private_admission_or_services")and not added.get_meta("structural_capacity_or_lower_section_accepted"))
 for path in p.model_pins:assert(FileAccess.get_sha256("res://"+str(path))==str(p.model_pins[path]))
 assert(added.get_node("ForwardFrames").find_children("*","MeshInstance3D",true,false).size()==155)
 assert(added.find_children("*","OmniLight3D",true,false).size()==4)
 for light:Light3D in added.find_children("*","Light3D",true,false):assert(budget.sources.count(light)==1)
 var space:=ship.get_world_3d().direct_space_state
 for site in p.sites:
  assert(added.get_node(str(site.key)).get_node("RetainedSource").find_child("CareStoneSurface",true,false)!=null)
  for at:Vector3 in [Vector3(site.centre,102,-395),Vector3(site.centre,102,-385)]:
   var hit:Dictionary=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.02,at-Vector3.UP*.02));assert(not hit.is_empty()and added.get_node("ForwardFrames").is_ancestor_of(hit.collider)and absf(hit.position.y-at.y)<.002)
  assert(space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(site.centre,102.7,-384.3),Vector3(site.centre,102.7,-383.7))).is_empty())
 assert(ship.get_node("ShipSpace/Group2CentralSupportedAdjunct").get_meta("default_main_adoption"))
 var clinical:Node3D=ship.get_node("ShipSpace/Group3CompleteClinical");assert(clinical.find_children("*","OmniLight3D",true,false).size()==193 and not clinical.get_meta("clinical_operational_acceptance")and not clinical.get_meta("operating_gates_or_dispatch_admitted"))
 assert(ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms").get_child_count()==303)
 FileAccess.open("/workspace/astraea-integration-cutoff-20261013/g2_remaining_five_pairs_20261013/INSTALLED_STARTUP_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_INSTALLED_FORWARD_ADJUNCT_CARE_PAIRS","new_frame_parts":155,"source_adjuncts":2,"care_kits":2,"source_floor_derivative_m2":394.845,"pierassembly_void_m2":1.155,"missing_connector_m2":7.2,"operating_or_structuralcapacity_accepted":false,"prior_central_pair_and_clinical_holds_unchanged":true,"full_build_accepted":false},"  "));print("FORWARD_PAIRS_INSTALLED_STARTUP_PASS");quit(0)
