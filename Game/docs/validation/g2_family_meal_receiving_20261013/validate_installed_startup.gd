extends SceneTree
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
 for p in ["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(p,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(30)
 var ship:Node3D=main.get_node("World360/Astraea");var house:Node3D=ship.get_node("ShipSpace/Districts/FamilyTerraceReceivingCandidate");var meal:Node3D=house.get_node("Group2FamilyMealReceiving")
 assert(meal.get_meta("default_main_adoption")and meal.get_meta("source_settings")==12 and meal.get_meta("new_floor_owners")==0 and meal.get_meta("new_seats_or_capacity")==0 and not meal.get_meta("food_stock_hygiene_or_staff_operation")and not meal.get_meta("programme_or_dining_designation_accepted"))
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_family_meal/COMPONENT_r001.json"));assert(FileAccess.get_sha256("res://assets/group2_family_meal/FAMILY_MEAL_FITTINGS_r001.glb")==str(data.export_sha256));assert(FileAccess.get_sha256("res://assets/models/FAMILY_TERRACE_ARCHITECTURE_lift_r003.glb")==str(data.source_runtime_sha256))
 for mesh:MeshInstance3D in meal.find_children("*","MeshInstance3D",true,false):assert(mesh.mesh.surface_get_material(0)!=null)
 var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var space:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state;var excluded:Array[RID]=[]
 for body:CollisionObject3D in meal.find_children("*","CollisionObject3D",true,false):excluded.append(body.get_rid())
 for table in data.tables:
  for setting in table.settings:
   var at:=Vector3(setting.world_xyz[0],setting.world_xyz[1],setting.world_xyz[2]);var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.08,at-Vector3.UP*.15);q.exclude=excluded;var hit:Dictionary=space.intersect_ray(q);assert(not hit.is_empty()and absf(hit.position.y-float(table.support_y))<.002)
 var captured:=false
 if OS.get_environment("ASTRAEA_CAPTURE_MEAL")=="1":
  actor.global_position=Vector3(79.5,97.53,343.8);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(false);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position);ship.get_node("ShipSystems/RemainingBatchStreaming").prepare_position(actor.global_position);await frames(35)
  assert(actor.is_on_floor()and absf(actor.global_position.y-97.5)<.12)
  actor.camera.look_at(Vector3(79.5,98.8,350.3),Vector3.UP);await frames(30);RenderingServer.force_draw(false)
  var picture:Image=root.get_texture().get_image();assert(not picture.is_empty());assert(picture.save_png("/workspace/astraea-integration-cutoff-20261013/g2_family_meal_receiving/FAMILY_MEAL_CURRENT_INSTALLED.png")==OK)
  var capture:Dictionary={"status":"CAPTURED_PIXEL_INSPECTION_PENDING","captured_utc":Time.get_datetime_string_from_system(true)+"Z","source_base_commit":"dafa10902c184e1f3aee8ce60e0ebaf47d1d2b0d","working_revision":"Installed Family meal r001 before next source seal","model_sha256":str(data.export_sha256),"ship_sha256":FileAccess.get_sha256("res://scripts/ship.gd"),"camera_world":str(actor.camera.global_position),"camera_fov":actor.camera.fov,"pixels":[picture.get_width(),picture.get_height()],"renderer":"Godot4.6.3 Compatibility","no_geometry_lighting_or_material_overrides":true,"single_manual_render_frame":true,"limits":"Physical contained fittings only;food/staff/hygiene services,dining designation,Z348 historical boundary,capacity,whole Family/art/hardware acceptance remain held."}
  FileAccess.open("/workspace/astraea-integration-cutoff-20261013/g2_family_meal_receiving/CAPTURE_RECEIPT.json",FileAccess.WRITE).store_string(JSON.stringify(capture,"  "));captured=true
 var result:Dictionary={"status":"PASS_INSTALLED_FAMILY_MEAL_STARTUP","model":1,"retained_tables":3,"source_settings":12,"original_tabletop_support_rays":12,"new_chairs_floor_or_capacity":0,"service_food_or_programme_acceptance":false,"capture_generated":captured,"whole_ship_no_omissions_build_accepted":false}
 FileAccess.open("/workspace/astraea-integration-cutoff-20261013/g2_family_meal_receiving/INSTALLED_STARTUP_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print("INSTALLED_FAMILY_MEAL_STARTUP_PASS");quit(0)
