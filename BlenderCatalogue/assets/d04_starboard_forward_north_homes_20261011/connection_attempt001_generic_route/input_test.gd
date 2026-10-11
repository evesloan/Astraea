extends "res://tests/validate_d04_commons_receiving_routes.gd"
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var homes:Node3D=ship.find_child("D04StarboardNorthHomeCandidates",true,false);var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_STARBOARD_FORWARD_NORTH_HOMES.json"))
 record("northern_batch_installed_once",homes!=null and ship.find_children("D04StarboardNorthHomeCandidates","Node3D",true,false).size()==1)
 if homes==null:quit(1);return
 record("original20_25_preserved",homes.get_meta("total_house_reservation_count")==20 and homes.get_meta("capacity_preserved")==25 and homes.get_meta("physical_candidates")==10 and homes.get_meta("fitted_reserved_rests")==13)
 var legs:Array=[]
 for r in p.rooms:
  var home:Node3D=homes.get_node(r.allocation.proposed_runtime_id);record("connected_reservation_"+str(int(r.source_index)),home.get_meta("rest_slot_ids")==r.allocation.proposed_rest_slot_ids and not home.get_meta("species_ready"))
  if int(r.source_index)not in [889,997]:continue
  var side:float=1 if r.court_side=="east"else -1;var front:float=r.allocation.allocation_x[0]if side>0 else r.allocation.allocation_x[1];var cz:float=r.entry.origin[2];var foyer:=Vector3(front+side*.72,16.5,cz);var care:=vec(r.approach_world)
  actor.global_position=Vector3(44,16.53,cz);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true)
  for i in range(20):await physics_frame
  var door:Node3D=home.get_node("HomeEntry");door.interact(null)
  for i in range(100):await physics_frame
  var goals:Array=[foyer,Vector3(foyer.x,16.5,cz+1.3),Vector3(care.x,16.5,cz+1.3),care]
  for target in goals:
   var walk:Dictionary=await walk_to(actor,target);walk.room=int(r.source_index);legs.append(walk);record("home_controller_leg_"+str(legs.size()),walk.reached and walk.floor_contact)
   if not walk.reached:break
  door.interact(null)
  for i in range(100):await physics_frame
  record("connected_door_roundtrip_"+str(int(r.source_index)),door.open_fraction<.001)
 var staff:Node3D=ship.find_child("ForwardStaffLift",true,false);record("D04_D07_blank",staff.deck_numbers==[1,2,3,8,9,13,14,15,16,17])
 var result={"status":"PASS"if errors.is_empty()else"FAIL","checks":checks.size(),"errors":errors,"controller_legs":legs,"scope":"Two representative original-controller northern home entry/care walks; ten unchanged reservation checks. All ten door/static checks in separate retained geometry gate.","northern_homes":10,"reserved_rests_fitted":13,"private_courts":4,"all_house_allocations":20,"all_house_reserved_rests":25,"southern_homes_remaining":10,"southern_receiving_full_commons_unbuilt":true,"cart_vertical_full_segregation_provider_occupancy_save_biology_final_accepted":false}
 FileAccess.open("res://artifacts/d04_starboard_north_homes_connection.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks.size(),"errors":errors}));quit(0 if errors.is_empty()else 1)
