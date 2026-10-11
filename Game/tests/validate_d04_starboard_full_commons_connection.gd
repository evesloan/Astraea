extends "res://tests/validate_d04_commons_receiving_routes.gd"
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var commons:Node3D=ship.find_child("D04StarboardFullCommons",true,false);var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_STARBOARD_FULL_COMMONS.json"));var legs:Array=[]
 record("connected_once",commons!=null and ship.find_children("D04StarboardFullCommons","Node3D",true,false).size()==1)
 if commons==null:quit(1);return
 var space:=ship.get_world_3d().direct_space_state
 var stair:Node3D=commons.find_child("D04SC_StaffStair450",true,false)
 for item in [{"name":"LOWER","at":Vector3(64.45,12,-372.3)},{"name":"MID","at":Vector3(66.2,14.25,-381.3)},{"name":"UPPER","at":Vector3(67.95,16.5,-372.3)}]:
  var datum:Node3D=stair.find_child("D04SC_StaffStair450__DATUM_"+item.name,true,false);record("original_stair_datum_"+item.name,datum!=null and datum.global_position.distance_to(item.at)<.00006)
 for name in p.stair_detailed_contact_replacements:
  var mesh:MeshInstance3D=commons.find_child(name,true,false);record("local_detailed_contact_replaced_"+name,mesh!=null and mesh.find_children("*","StaticBody3D",true,false).is_empty())
 for flight in range(2):
  for j in range(1,6):
   var t:float=j/6.0;var at:=Vector3(64.45 if flight==0 else 67.95,12+2.25*t if flight==0 else 16.5-2.25*t,-372.3-7.5*t);var h:=ray(space,at+Vector3.UP*.03,at-Vector3.UP*.03);record("source_derived_flight_contact_"+str(flight)+"_"+str(j),not h.is_empty()and commons.is_ancestor_of(h.collider)and absf(h.position.y-at.y)<.002);record("source_derived_flight_capsule_"+str(flight)+"_"+str(j),capsule_clear(space,at))
 var routes:Array=[{"label":"public_receiving_to_activity_quiet","start":Vector3(60,16.53,-369.5),"goals":[Vector3(70,16.5,-369.5),Vector3(70,16.5,-364.8),Vector3(78.4,16.5,-364.8),Vector3(78.4,16.5,-360.3),Vector3(81.25,16.5,-360.3)]},{"label":"actual_D03_fore_spine_interface","start":Vector3(3,12.03,-381.2),"goals":[Vector3(8,12,-381.2)]},{"label":"lower_dogleg_original_stair_stock_closed_returns","start":Vector3(58,12.03,-381.2),"goals":[Vector3(61.6,12,-381.2),Vector3(61.6,12,-371.3),Vector3(64.45,12,-371.3),Vector3(64.45,14.25,-381.3),Vector3(67.95,14.25,-381.3),Vector3(67.95,16.5,-372.3),Vector3(67.95,16.5,-364),Vector3(71,16.5,-364),Vector3(71,16.5,-361),Vector3(71,16.5,-364),Vector3(75.9,16.5,-364),Vector3(75.9,16.5,-361)]}]
 for route in routes:
  actor.global_position=route.start;actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
  for i in range(20):await physics_frame
  for target in route.goals:
   var w:Dictionary=await walk_to(actor,target);w.scope=route.label;legs.append(w);record("representative_controller_leg_"+str(legs.size()),w.reached and w.floor_contact)
   if not w.reached:break
 var staff:Node3D=ship.find_child("ForwardStaffLift",true,false);record("protected_D04_D07_blank",staff.deck_numbers==[1,2,3,8,9,13,14,15,16,17]);record("20homes25reservations",commons.get_meta("preserved_home_allocations")==20 and commons.get_meta("preserved_reserved_rests")==25)
 var result={"status":"PASS"if errors.is_empty()else"FAIL","checks":checks.size(),"errors":errors,"controller_legs":legs,"model_pins":p.model_pins,"scope":"Representative public approach/activity/quiet, true D03 fore spine interface, and local screened staff dogleg/original stair/stock/closed-return walks","loaded_cart_stairs_full_staff_network_provider_occupancy_save_biology_engineering_final_accepted":false}
 FileAccess.open("res://artifacts/d04_starboard_full_commons_connection.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks.size(),"errors":errors}));quit(0 if errors.is_empty()else 1)
