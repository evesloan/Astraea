extends "res://tests/validate_d04_physical_connections_candidate.gd"
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PHYSICAL_CONNECTIONS_CANDIDATE.json"));var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(90):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.global_position=Vector3(-57,12.03,-449);player.velocity=Vector3.ZERO
 ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
 for i in range(15):await physics_frame
 var built:Dictionary=load("res://scripts/d04_physical_connections_candidate.gd").build(ship,player,p)
 for i in range(10):await physics_frame
 for gate in built.controls:give_visit(gate,player);gate.interact(player)
 for i in range(100):await physics_frame
 for planter in range(3):
  for leaf in range(3):load("res://scripts/static_contact_cache.gd").attach(ship.find_child("D04HC2_west_LeafMass_"+str(planter)+"_"+str(leaf),true,false))
 for i in range(3):await physics_frame
 var probe=load("res://tests/d04_care_terminal_probe.gd");var tool:Dictionary=probe.setup(built.owner,p);var mesh:MeshInstance3D=ship.find_child("D04HC2_west_LeafMass_1_1",true,false);var bounds:AABB=mesh.global_transform*mesh.get_aabb();var results:Array=[];var space:=ship.get_world_3d().direct_space_state
 for height in [bounds.position.y+.04,bounds.get_center().y,bounds.end.y-.02]:
  var result:Dictionary=probe.probe(space,ship,tool,str(mesh.name),height);results.append(result);record("angled_terminal_middle_central_"+str(height),result.passed)
 var receipt:Dictionary={"status":"PASS"if errors.is_empty()else"FAIL","errors":errors,"checks":checks,"results":results,"model_pins":p.model_pins,"runtime_plan_sha256":FileAccess.get_sha256("res://data/architecture/D04_PHYSICAL_CONNECTIONS_CANDIDATE.json"),"probe_source_sha256":FileAccess.get_sha256("res://tests/d04_care_terminal_probe.gd"),"production_active":false,"temporary_visit_only":true}
 FileAccess.open("res://artifacts/d04_care_terminal_candidate.json",FileAccess.WRITE).store_string(JSON.stringify(receipt,"  "));print(JSON.stringify({"status":receipt.status,"errors":errors,"results":results}));quit(0 if errors.is_empty()else 1)
