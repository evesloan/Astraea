extends "res://tests/validate_d04_court_controls_staff_candidate.gd"
var legs:Array=[]
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/AFT_CROWN_SITTING_BAYS.json"));var n:Node3D=ship.find_child("AftCrownSittingBays",true,false)
 record("connected_once",n!=null and ship.find_children("AftCrownSittingBays","Node3D",true,false).size()==1)
 record("geometry_sealed",p.sealed_receipt_sha256==FileAccess.get_sha256("res://artifacts/aft_crown_sitting_bays_geometry.json"))
 if n==null:quit(1);return
 for row in p.runtime_furniture_expected_bounds:
  var mesh:MeshInstance3D=n.find_child(row.name,true,false);record("original_furniture_runtime_mesh_"+row.name,mesh!=null)
  if mesh!=null:
   var a:AABB=mesh.global_transform*mesh.get_aabb();record("exact_rigid_furniture_runtime_placement_"+row.name,a.position.distance_to(vec(row.bounds[0]))<.001 and a.end.distance_to(vec(row.bounds[1]))<.001)
 actor.global_position=Vector3(-16,106.53,142);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
 for i in range(20):await physics_frame
 for goal in [Vector3(-16,106.5,161.5),Vector3(-20,106.5,161.5),Vector3(-26,106.5,161.5),Vector3(-20,106.5,161.5),Vector3(-16,106.5,161.5),Vector3(-16,106.5,145),Vector3(0,106.5,145),Vector3(16,106.5,145),Vector3(16,106.5,161.5),Vector3(20,106.5,161.5),Vector3(26,106.5,161.5),Vector3(20,106.5,161.5),Vector3(16,106.5,161.5),Vector3(16,106.5,145),Vector3(0,106.5,145),Vector3(-16,106.5,145),Vector3(-16,106.5,142)]:
  var w:Dictionary=await walk_to(actor,goal);w.scope="original supported platform public loop,receiving crosslink and both open sitting bay portals";legs.append(w);record("original_player_leg_"+str(legs.size()),w.reached and w.floor_contact)
  if not errors.is_empty():break
 var platform:Node3D=ship.find_child("AftCrownPlatform_WIP",true,false)
 for door:Node in platform.get_children():
  if door.get_script()!=null and door.get_script().resource_path=="res://scripts/service_door.gd":record("original_platform_door_identity_and_closed_default_"+str(door.persistent_id),door.open_fraction==0 and not door.desired_open)
 for name in ["D04StarboardAftCommonsEnclosure","LowerSharedAftStaffRoute","D04PortAftCourtRoutes"]:record("previous_connected_package_retained_"+name,ship.find_child(name,true,false)!=null)
 physical_key(false)
 var result={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks.size(),"errors":errors,"model_pins":p.model_pins,"geometry_seal_sha256":p.sealed_receipt_sha256,"original_player_controller_legs":legs,"single_original_platform_fixture_seed":true,"route_teleports":0,"no_new_door_or_permissions":true,"ordinary_game_sitting_engineering_or_final_visual_acceptance":false,"limits":p.limits};FileAccess.open("res://artifacts/aft_crown_sitting_bays_connection.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":result.checks,"errors":errors,"legs":legs.size()}));quit(0 if errors.is_empty()else 1)
