extends "res://tests/validate_d04_commons_receiving_routes.gd"
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var n:Node3D=ship.find_child("D04StarboardForwardNorthReceiving",true,false)
 record("receiving_installed_once",n!=null and ship.find_children("D04StarboardForwardNorthReceiving","Node3D",true,false).size()==1)
 record("allocations_preserved",n.get_meta("preserved_guest_allocations")==20 and n.get_meta("preserved_proposed_rests")==25 and n.get_meta("new_capacity")==0)
 var staff:Node3D=ship.find_child("ForwardStaffLift",true,false);record("forward_D04_D07_blank",staff.deck_numbers==[1,2,3,8,9,13,14,15,16,17])
 actor.global_position=Vector3(2.5,16.53,-288.7);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true)
 for i in range(20):await physics_frame
 var legs:Array=[]
 for target in [Vector3(8,16.5,-288.7),Vector3(44,16.5,-288.7),Vector3(44,16.5,-330.6)]:
  var w:Dictionary=await walk_to(actor,target);legs.append(w);record("receiving_controller_leg_"+str(legs.size()),w.reached and w.floor_contact)
  if not w.reached:break
 var result={"status":"PASS"if errors.is_empty()else"FAIL","checks":checks.size(),"errors":errors,"controller_legs":legs,"new_floor_m2":457.33,"rooms_built":0,"capacity_added":0,"full_segregation_cart_vertical_provider_save_biology_final_accepted":false}
 FileAccess.open("res://artifacts/d04_starboard_north_receiving_connection.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks.size(),"errors":errors}));quit(0 if errors.is_empty()else 1)
