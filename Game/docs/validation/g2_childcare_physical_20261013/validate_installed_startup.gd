extends SceneTree
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
 for p in ["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(p,true))
 call_deferred("run")
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(30):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var house:Node3D=ship.get_node("ShipSpace/Districts/FamilyTerraceReceivingCandidate");var child:Node3D=house.get_node("Group2ChildcarePhysicalReceiving");var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_family_childcare/COMPONENT_r001.json"));var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 assert(child.get_meta("default_main_adoption")and child.get_meta("new_floor_owners")==0 and child.get_meta("new_registered_rooms_beds_or_capacity")==0 and child.get_meta("proposed_day_rest_fittings")==4)
 assert(not child.get_meta("guardian_supervision_admission_or_child_programme_accepted")and not child.get_meta("entry_or_inside_egress_operation_admitted")and not child.get_meta("source_fixture_id_bound_to_production")and not child.get_meta("food_hygiene_or_staff_services_admitted"))
 assert(FileAccess.get_sha256("res://assets/group2_family_childcare/FAMILY_CHILDCARE_r001.glb")==str(data.export_sha256));assert(FileAccess.get_sha256("res://assets/models/"+str(data.door.file))==str(data.door.sha256));assert(FileAccess.get_sha256("res://assets/models/FAMILY_TERRACE_ARCHITECTURE_lift_r003.glb")==str(data.source_receiver_sha256))
 assert(child.get_node_or_null("CareEntry")==null)
 var closed:Node3D=child.get_node("CareEntry_StaticClosedSource");assert(not closed.has_method("interact"));assert(closed.find_child("LEAF_LEFT",true,false).position.is_equal_approx(Vector3(-.6,0,0))and closed.find_child("LEAF_RIGHT",true,false).position.is_equal_approx(Vector3(.6,0,0)))
 for row in data.lights:assert(budget.sources.count(child.get_node(str(row.source_mesh)+"_PhysicalSource"))==1)
 var meal:Node3D=house.get_node("Group2FamilyMealReceiving");assert(meal.get_meta("default_main_adoption")and not meal.get_meta("food_stock_hygiene_or_staff_operation")and not meal.get_meta("programme_or_dining_designation_accepted"))
 assert(ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms").get_child_count()==303)
 var result:Dictionary={"status":"PASS_INSTALLED_CHILDCARE_PHYSICAL_STARTUP","new_model":1,"fixtures":4,"static_closed_wide_fitting":true,"operating_entry_or_egress":false,"source_fixture_id_used_as_admission_binding":false,"new_rooms_beds_floor_or_capacity":0,"guardian_supervision_or_child_programme_admission":false,"verified_meal_fitout_preserved":true,"whole_ship_or_final_acceptance":false}
 FileAccess.open("/workspace/astraea-integration-cutoff-20261013/g2_childcare_physical_receiving/INSTALLED_STARTUP_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print("CHILDCARE_INSTALLED_PHYSICAL_STARTUP_PASS");quit(0)
