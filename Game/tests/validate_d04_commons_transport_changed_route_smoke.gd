extends "res://tests/validate_d04_commons_receiving_routes.gd"
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_COMMONS_TRANSPORT_ROUTE.json"));var chair:Node3D=ship.find_child(p.chair_revision.node,true,false)
 record("actual_r002_chair_installed",chair.global_position.distance_to(vec(p.chair_revision.position))<.00005 and absf(wrapf(chair.global_rotation.y-p.chair_revision.yaw,-PI,PI))<.00005)
 record("one_rigid_routing_adapter",ship.find_child("D04CommonsTransportRouting",true,false)!=null)
 var staff:Node3D=ship.find_child("ForwardStaffLift",true,false);record("protected_blank_forward_D04_D07",staff.deck_numbers==[1,2,3,8,9,13,14,15,16,17]and staff.floor_heights==[0.0,6.0,12.0,46.2,52.5,84.0,88.5,93.0,97.5,102.0])
 actor.global_position=Vector3(-64,16.53,-361.8);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true)
 for i in range(20):await physics_frame
 var results:Array=[]
 for target in [Vector3(-64,16.5,-369.5),Vector3(-44.6,16.5,-369.5),Vector3(-44.6,16.5,-404.8),Vector3(-44,16.5,-405.2),Vector3(-8,16.5,-405.2),Vector3(-8,16.5,-406),Vector3(-2,16.5,-406)]:
  var w:Dictionary=await walk_to(actor,target);results.append(w);record("changed_route_controller_leg_"+str(results.size()),w.reached and w.floor_contact)
  if not w.reached:break
 var result={"status":"PASS"if errors.is_empty()else"FAIL","checks":checks.size(),"errors":errors,"controller_legs":results,"scope":"One bounded changed public receiving route smoke, one initial player fixture, original controller; original cart untouched","loaded_cart_vertical_accepted":false,"dedicated_clean_used_segregation_accepted":false,"dock_contact_latch_accepted":false,"provider_save_biology_final_accepted":false}
 FileAccess.open("res://artifacts/d04_commons_transport_changed_route_smoke.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks.size(),"walks":results.size(),"errors":errors}));quit(0 if errors.is_empty()else 1)
