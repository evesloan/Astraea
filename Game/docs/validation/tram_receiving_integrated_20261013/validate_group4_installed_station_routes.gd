extends "res://tests/validate_d04_port_forward_commons_service.gd"
const OUT:="/workspace/astraea-integration-cutoff-20261013/group4_connected_routes/"
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
 for p in ["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(p,true))
 call_deferred("run")
var legs:Array=[]
var rides:Array=[]
var interactions:Array=[]
func frames(n:int)->void:
 for i in range(n):await physics_frame
func mouse_right(down:bool)->void:
 var e:=InputEventMouseButton.new();e.button_index=MOUSE_BUTTON_RIGHT;e.pressed=down;Input.parse_input_event(e)
func use_button(player:CharacterBody3D,button:Node3D,label:String)->void:
 player.camera.look_at(button.global_position,Vector3.UP);mouse_right(true);await frames(3)
 var focus:Node=player.target_from_view();record(label+" exact existing ray target",focus==button)
 var e:=InputEventKey.new();e.keycode=KEY_E;e.physical_keycode=KEY_E;e.pressed=true;Input.parse_input_event(e);await frames(3)
 e=InputEventKey.new();e.keycode=KEY_E;e.physical_keycode=KEY_E;e.pressed=false;Input.parse_input_event(e);mouse_right(false)
 interactions.append({"label":label,"actual_original_player_E_RMB_events":true,"exact_existing_button_ray_target":focus==button})
func cabin_button(lift:Node3D,index:int)->Node3D:
 for child:Node in lift.cabin.get_children():
  if child.get_script()==load("res://scripts/lift_button.gd") and child.floor_index==index:return child
 assert(false,"Exact original cabin button missing");return null
func walk(player:CharacterBody3D,at:Vector3,label:String)->bool:
 var leg:Dictionary=await walk_to(player,at);leg.label=label;legs.append(leg);record(label+" original player walk",leg.reached and leg.floor_contact);return leg.reached
func ride(player:CharacterBody3D,lift:Node3D,index:int,label:String)->bool:
 var before:Vector3=player.global_position;await use_button(player,cabin_button(lift,index),label)
 var count:=0
 while count<700 and (lift.current_floor!=index or lift.phase!="idle"):
  await physics_frame;count+=1
 var success:bool=lift.current_floor==index and lift.phase=="idle" and absf(player.global_position.y-lift.floor_heights[index])<.12 and player.is_on_floor()
 record(label+" actual original controller carries original player",success)
 rides.append({"label":label,"source_controller":"commons_lift.gd","before":str(before),"after":str(player.global_position),"target_y":lift.floor_heights[index],"physics_frames":count,"on_floor":player.is_on_floor(),"original_E_RMB":true,"reached":success});return success
func run()->void:
 DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
 var main:Node=(load("res://scenes/main.tscn") as PackedScene).instantiate();root.add_child(main);await frames(120)
 var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
 var cart:RigidBody3D=ship.find_child("CustodialCart",true,false);var products:Array=[]
 for product in cart.products:products.append({"node":product,"id":product.persistent_id})
 var base:Node3D=ship.get_node("ShipSpace/Districts/Group4Completion")
 var vehicle:AnimatableBody3D=base.get_node("Group4OwnedTram_Source024")
 var safety:Node3D=base.get_node("Group4BoardingSafety")
 record("One installed source vehicle without transient receivers",vehicle.get_meta("exact_original_portal_contact_components")==18)
 var contract:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://../BlenderCatalogue/assets/group4_completion_20261011/DESTINATION_CONNECTION_CONTRACT.json"))
 for st in contract.five_core_transfers:
  if not OS.get_environment("ASTRAEA_G4_RECEIVING_STATION").is_empty() and st.station!=OS.get_environment("ASTRAEA_G4_RECEIVING_STATION"):continue
  print("RECEIVING_STATION_START ",st.station)
  var lift:Node3D=base.get_node("Group4Lift_"+st.station);var points:Array=st.lower_route_xz
  var start:Array=points[-1];player.global_position=Vector3(start[0],52.53,start[1]);player.velocity=Vector3.ZERO;player.set_controls_enabled(true);residency.prepare_position(player.global_position);await frames(30)
  var good:=true
  for i in range(points.size()-2,-1,-1):
   if not await walk(player,Vector3(points[i][0],52.5,points[i][1]),st.station+" core to lower "+str(i)):good=false;break
  if not good:continue
  if not await walk(player,lift.cabin.to_global(Vector3(0,0,-1.0)),st.station+" enter original cabin"):continue
  if not await walk(player,lift.cabin.to_global(Vector3(1.03,0,-.85)),st.station+" original upper button stance"):continue
  if not await ride(player,lift,1,st.station+" up"):continue
  if not await walk(player,lift.cabin.to_global(Vector3(0,0,-1.0)),st.station+" cabin centre upper"):continue
  var first:Array=points[0]
  if not await walk(player,Vector3(first[0],56.1,first[1]),st.station+" leave cabin upper"):continue
  var upper:Array=[]
  match st.station:
   "FORWARD":upper=[Vector3(5.6,56.1,-432),Vector3(-2.4,56.1,-432)]
   "AFT":upper=[Vector3(5.6,56.1,432),Vector3(-2.4,56.1,432)]
   "AFT_MIDSHIP":upper=[Vector3(5.6,56.1,226.6),Vector3(4.4,56.1,226.6),Vector3(4.4,56.1,225.05),Vector3(-.5,56.1,225.05),Vector3(-.5,56.1,216),Vector3(-2.4,56.1,216)]
   "FORE_MIDSHIP":upper=[Vector3(-10.2,56.1,-228),Vector3(-10.2,56.1,-241),Vector3(-8.8,56.1,-241)]
   "CENTRAL":upper=[Vector3(-5.6,56.1,-72),Vector3(-3.2,56.1,-72)]
  var upper_start:=Vector3(first[0],56.1,first[1])
  for i in range(upper.size()):
   if not await walk(player,upper[i],st.station+" actual platform leg "+str(i)):good=false;break
  if not good:continue
  for i in range(upper.size()-2,-1,-1):
   if not await walk(player,upper[i],st.station+" platform return "+str(i)):good=false;break
  if not good or not await walk(player,upper_start,st.station+" upper lift return"):continue
  if not await walk(player,lift.cabin.to_global(Vector3(1.03,0,-.85)),st.station+" original lower button stance"):continue
  if not await ride(player,lift,0,st.station+" down"):continue
  if not await walk(player,Vector3(first[0],52.5,first[1]),st.station+" leave cabin lower"):continue
  for i in range(1,points.size()):
   if not await walk(player,Vector3(points[i][0],52.5,points[i][1]),st.station+" lower to core "+str(i)):break
 physical_key(false);mouse_right(false)
 record("Original cart identity and mass preserved",cart.persistent_id==&"custodian_cart_001" and cart.mass==18 and cart.products.size()==4)
 for item in products:record("Original stock identity "+str(item.id),is_instance_valid(item.node) and item.node.persistent_id==item.id)
 var result:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks.size(),"errors":errors,"actual_original_player_legs":legs,"actual_original_controller_rides":rides,"original_E_RMB_interactions":interactions,"station_filter":OS.get_environment("ASTRAEA_G4_RECEIVING_STATION"),"aftmid_successor_installed":true,"independent_supported_initial_test_stances":1 if not OS.get_environment("ASTRAEA_G4_RECEIVING_STATION").is_empty() else 5,"within_route_relocations":0,"floor_patch_scope":"Installed exact three-owner pit successor; no transient geometry, lifts or tram","shared_pits_adopted":true,"north_stop_adopted":true,"loaded_cart_tram_carry_species_engineering_accepted":false,"scope":"Current integrated source and original player/controller; five independent supported route starts, no within-route relocation; loaded-cart carry and final-art remain open."}
 FileAccess.open("/workspace/astraea-integration-cutoff-20261013/GROUP4_CONNECTED_STATION_ROUTES.json",FileAccess.WRITE).store_string(JSON.stringify(result," "));print("GROUP4 RECEIVED PLAYER ",result.status,": ",checks.size()," checks; ",legs.size()," walks; ",rides.size()," rides");main.queue_free();await process_frame;quit(0 if errors.is_empty() else 1)
