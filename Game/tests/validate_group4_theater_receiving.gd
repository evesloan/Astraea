extends "res://tests/validate_d04_port_forward_commons_service.gd"
const OUT:="res://../BlenderCatalogue/assets/group4_completion_20261011/theater_upper_approaches_016/"
func frames(n:int)->void:
 for i in range(n):await physics_frame
var query_actor_rid:RID
func cart_source_clear(space:PhysicsDirectSpaceState3D,at:Vector3,yaw:float)->bool:
 var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/cleaning_cart_contacts.json"));var pose:=Transform3D(Basis(Vector3.UP,yaw),at+Vector3.UP*.005)
 for item in d.boxes:
  var shape:=BoxShape3D.new();shape.size=vec(item.size);shape.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=pose*Transform3D(Basis.IDENTITY,vec(item.center));q.exclude=[query_actor_rid]
  if not space.intersect_shape(q,32).is_empty():return false
 for item in d.wheel_contacts:
  var shape:=SphereShape3D.new();shape.radius=float(item.radius);shape.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=pose*Transform3D(Basis.IDENTITY,vec(item.center));q.exclude=[query_actor_rid]
  if not space.intersect_shape(q,32).is_empty():return false
 return true
func run()->void:
 var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main);await frames(180)
 var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
 var venue:Node3D=ship.get_node("ShipSpace/Districts/GrandLanternTheater_ConnectedStaticStage_WIP");var motion:Node3D=venue.get_node("TheaterUnpoweredDoorLiftAssemblies")
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/THEATER_RUNTIME_STAGE001.json"));var upper:Array=[]
 for key:String in data.motion_groups:
  if key.begins_with("THEATER_D12_MAIN_LEAF") or key.begins_with("THEATER_D13_MAIN_LEAF"):
   var node:Node3D=motion.get_node(data.motion_node_names[key]);upper.append({"node":node,"key":key,"pose":node.transform});record(key+" original closed/inactive",not node.get_meta("operation_enabled") and node.get_meta("locked_pose_fraction")==0.0)
 query_actor_rid=player.get_rid()
 var proposal:Node3D=load("res://scripts/group4_theater_upper_approaches.gd").build(ship.get_node("ShipSpace/Districts"),true);record("All210 source meshes admitted",proposal.get_meta("verified_source_members")==210);record("New asset-owned366m2 floor",proposal.get_meta("new_asset_owned_floor_m2")==366)
 # Register test-added fixtures with the existing one selector. Production insertion belongs before configure.
 var selector:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 var sources:Array=proposal.find_children("*","SpotLight3D",true,false);record("Six original physical coffer bindings",sources.size()==6)
 for light:Light3D in sources:
  selector.sources.append(light);selector.requested_shadow[light.get_instance_id()]=true;record(str(light.name)+" physical fixture metadata",light.has_meta("source_fixture_semantic_id") and light.has_meta("illumination_anchor"))
 var cart:RigidBody3D=ship.find_child("CustodialCart",true,false);var stocks:Array=[]
 for product in cart.products:stocks.append({"node":product,"id":product.persistent_id})
 var space:PhysicsDirectSpaceState3D=player.get_world_3d().direct_space_state;var walks:Array=[];var sweeps:=0;var cart_turns:=0;var wheel_samples:=0
 for level in [["D11",69.5],["D12",78.0],["D13",84.0]]:
  var deck:String=level[0];var y:float=level[1]
  if OS.get_environment("ASTRAEA_G4_THEATER_CART_ONLY")=="1" and deck=="D11":continue
  print("G4_THEATER_RECEIVING_START ",deck)
  player.global_position=Vector3(0,y+.03,-126);player.velocity=Vector3.ZERO;player.set_controls_enabled(true);residency.prepare_position(player.global_position);await frames(40);selector.refresh()
  var goals:Array=[Vector3(-3.2,y,-126),Vector3(-6,y,-126),Vector3(-15,y,-126),Vector3(-25,y,-126),Vector3(-33.1,y,-126)]
  if deck=="D11":goals.append(Vector3(-36.5,y,-126))
  var good:=true
  if OS.get_environment("ASTRAEA_G4_THEATER_CART_ONLY")=="1":goals.clear()
  for goal:Vector3 in goals:
   var leg:Dictionary=await walk_to(player,goal);leg.deck=deck;walks.append(leg);record(deck+" original W walk "+str(walks.size()),leg.reached and leg.floor_contact)
   if not leg.reached:good=false;break
  if good:
   for i in range(goals.size()-2,-1,-1):
    var leg:Dictionary=await walk_to(player,goals[i]);leg.deck=deck;walks.append(leg);record(deck+" original W return "+str(walks.size()),leg.reached and leg.floor_contact)
    if not leg.reached:good=false;break
  if good and not goals.is_empty():
   var leg:Dictionary=await walk_to(player,Vector3(0,y,-126));leg.deck=deck;walks.append(leg);record(deck+" original W core return",leg.reached and leg.floor_contact)
  if deck!="D11":
   record(deck+" original main doorway remains physical barrier",not capsule_clear(space,Vector3(-34.25,y,-126)))
   for x in range(-33,1):
    var at:=Vector3(x,y,-126);record(deck+" source/cart corridor "+str(x),cart_source_clear(space,at,PI/2));sweeps+=1
    var hit:=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02);record(deck+" actual floor "+str(x),not hit.is_empty() and absf(hit.position.y-y)<.002)
   for angle in range(9):record(deck+" original cart receiving turn "+str(angle),cart_source_clear(space,Vector3(-31,y,-126),angle*PI/4));cart_turns+=1
   var original_cart:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/cleaning_cart_contacts.json"))
   for x in [-33.0,-4.1,-3.9,0.0]:
    var basis:=Basis(Vector3.UP,PI/2)
    for wheel in original_cart.wheel_contacts:
     var at:=Vector3(x,y,-126)+basis*vec(wheel.center)-Vector3.UP*float(wheel.radius);var hit:=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02);record(deck+" original cart wheel floor "+str(wheel_samples),not hit.is_empty() and absf(hit.position.y-y)<.002);wheel_samples+=1
  var active:=0
  for light:Light3D in selector.sources:
   if light.visible and light.shadow_enabled:active+=1
  record(deck+" existing8 shadow budget retained",active<=8)
 for item in upper:record(item.key+" exact original closed pose preserved",item.node.transform==item.pose and not item.node.get_meta("operation_enabled"))
 record("Original2200 theater chair instances preserved",venue.get_meta("source_chair_instances")==2200);record("Original cart identity/mass/stock count",cart.persistent_id==&"custodian_cart_001" and cart.mass==18 and cart.products.size()==4)
 for item in stocks:record("Original stock identity "+str(item.id),is_instance_valid(item.node) and item.node.persistent_id==item.id)
 physical_key(false)
 var result:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks.size(),"errors":errors,"actual_original_player_walks":walks,"cart_contact_query_sweeps":sweeps,"original_cart_receiving_turn_queries":cart_turns,"original_wheel_supported_samples":wheel_samples,"original_upper_main_doors_closed_and_inactive":true,"original_capacity2200_unchanged":true,"independent_supported_initial_deck_placements":2 if OS.get_environment("ASTRAEA_G4_THEATER_CART_ONLY")=="1" else 3,"focused_cart_query_only":OS.get_environment("ASTRAEA_G4_THEATER_CART_ONLY")=="1","cart_queries_exclude_only_original_player_rid":true,"opaque_original_or_new_source_contact_exclusions":0,"within_route_relocations":0,"D11_scope":"Existing original main doorway and original compiled bridge retained; walk through default operating entry and return with new exterior side receivers installed.","D12_D13_scope":"New source-owned exterior floors and original portico parts, connected to exact original fore-route seam; walk to original closed door and return. No door activation or venue interior completion claimed.","source_fixture_lighting":"Six physical source bindings registered only with existing selector;8-source limit retained. No optical calibration, normal CRT or hardware acceptance.","source_load_approval":false,"loaded_cart_physical_motion_species_save_final_art_or_whole_group_accepted":false,"production_active":false}
 FileAccess.open(OUT+"ACTUAL_PLAYER_RECEIVING.json",FileAccess.WRITE).store_string(JSON.stringify(result," "));print("G4_THEATER_RECEIVING ",result.status,": ",checks.size()," checks; ",walks.size()," original walks");main.queue_free();await process_frame;quit(0 if errors.is_empty() else 1)
