extends "res://tests/validate_d04_commons_receiving_routes.gd"
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var district:Node3D=ship.find_child("D04StarboardAftHabitatNeighborhood",true,false);var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_STARBOARD_AFT_NEIGHBORHOOD.json"));var legs:Array=[]
 record("connected_once",district!=null and ship.find_children("D04StarboardAftHabitatNeighborhood","Node3D",true,false).size()==1)
 if district==null:quit(1);return
 record("geometry_seal",FileAccess.get_sha256("res://artifacts/d04_starboard_aft_neighborhood_geometry.json")==p.sealed_receipt_sha256)
 var stair:Node3D=district.find_child("SAC_StaffStair450",true,false)
 for item in [{"name":"LOWER","at":Vector3(67.95,12,372.3)},{"name":"MID","at":Vector3(66.2,14.25,381.3)},{"name":"UPPER","at":Vector3(64.45,16.5,372.3)}]:
  var datum:Node3D=stair.find_child("SAC_StaffStair450__DATUM_"+item.name,true,false);record("rigid_original_stair_datum_"+item.name,datum!=null and datum.global_position.distance_to(item.at)<.00006)

 for r in p.rooms:
  var home:Node3D=district.get_node(r.allocation.proposed_runtime_id);record("original_allocation_"+str(int(r.source_index)),home.get_meta("allocation_sha256")==r.allocation.allocation_sha256 and home.get_meta("rest_slot_ids")==r.allocation.proposed_rest_slot_ids and not home.get_meta("species_ready"))
 var routes:Array=[{"label":"actual_D04_public_spine_junction","start":Vector3(3.5,16.53,405.2),"goals":[Vector3(10,16.5,405.2)]},{"label":"actual_north_south_street_joint","start":Vector3(44,16.53,337),"goals":[Vector3(44,16.5,331)]},{"label":"reading_to_low_screened_quiet_bay","start":Vector3(63.5,16.53,369.5),"goals":[Vector3(71.7,16.5,369.5),Vector3(81.2,16.5,369.5),Vector3(81.2,16.5,364.6),Vector3(81.2,16.5,361.8),Vector3(80.5,16.5,361.8)]},{"label":"actual_D03_shared_aft_spine_junction","start":Vector3(3,12.03,381.2),"goals":[Vector3(8,12,381.2)]},{"label":"local_source_stair_stock_closed_returns","start":Vector3(61.6,12.03,381.2),"goals":[Vector3(61.6,12,371.3),Vector3(67.95,12,371.3),Vector3(67.95,14.25,381.3),Vector3(64.45,14.25,381.3),Vector3(64.45,16.5,372.3),Vector3(64.45,16.5,364.3),Vector3(64.45,16.5,360.8),Vector3(64.45,16.5,364.3),Vector3(68.4,16.5,364.3),Vector3(68.4,16.5,361.3)]}]
 for route in routes:
  actor.global_position=route.start;actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
  for i in range(20):await physics_frame
  for target in route.goals:
   var w:Dictionary=await walk_to(actor,target);w.scope=route.label;legs.append(w);record("representative_controller_leg_"+str(legs.size()),w.reached and w.floor_contact)
   if not w.reached:break
 for r in p.rooms:
  if int(r.source_index)not in [885,975]:continue
  var home:Node3D=district.get_node(r.allocation.proposed_runtime_id);var side:float=1 if r.court_side=="east"else -1;var front:float=r.allocation.allocation_x[0]if side>0 else r.allocation.allocation_x[1];var cz:float=r.entry.origin[2];var foyer:=Vector3(front+side*.72,16.5,cz);var care:=vec(r.approach_world)
  actor.global_position=Vector3(44,16.53,cz);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
  for i in range(20):await physics_frame
  var door:Node3D=home.get_node("HomeEntry");door.interact(null)
  for i in range(100):await physics_frame
  # Quiet route is the proper180degree rotation of retained source886's route.
  var goals:Array=[foyer,Vector3(foyer.x,16.5,cz-1.3),Vector3(care.x,16.5,cz-1.3),care]
  if r.has("entry_to_care_waypoints"):goals=r.entry_to_care_waypoints.map(func(a):return vec(a))
  for target in goals:
   var w:Dictionary=await walk_to(actor,target);w.scope="representative_original_home_entry_care";w.room=int(r.source_index);legs.append(w);record("representative_home_leg_"+str(legs.size()),w.reached and w.floor_contact)
   if not w.reached:break
  door.interact(null)
  for i in range(100):await physics_frame
  record("connected_home_door_roundtrip_"+str(int(r.source_index)),door.open_fraction<.001)
 var staff:Node3D=ship.find_child("ForwardStaffLift",true,false);record("protected_D04_D07_staff_blank",staff.deck_numbers==[1,2,3,8,9,13,14,15,16,17]);record("20homes25reservedrests",district.get_meta("preserved_home_allocations")==20 and district.get_meta("preserved_reserved_rests")==25)
 var result={"status":"PASS"if errors.is_empty()else"FAIL","checks":checks.size(),"errors":errors,"controller_legs":legs,"model_pins":p.model_pins,"geometry_seal_sha256":p.sealed_receipt_sha256,"scope":"Bounded real D04 aft public junction, street joint, activity/quiet, real D03 shared aft spine junction, local original stair/stock/closed returns, quiet885 and paired975 entry/care routes","dedicated_network_north_lateral_portal_loaded_cart_vertical_gameplay_engineering_final_accepted":false}
 FileAccess.open("res://artifacts/d04_starboard_aft_neighborhood_connection.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks.size(),"errors":errors}));quit(0 if errors.is_empty()else 1)
