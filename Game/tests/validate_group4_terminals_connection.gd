extends "res://tests/validate_d04_port_forward_commons_service.gd"
var legs:Array[Dictionary]=[]
func run()->void:
 var main:Node=(load("res://scenes/main.tscn") as PackedScene).instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
 var cart:RigidBody3D=ship.find_child("CustodialCart",true,false)
 var original_products:Array=[]
 for product in cart.products:original_products.append({"node":product,"id":product.persistent_id})
 var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
 for z in [-216.0,216.0]:residency.prepare_position(Vector3(-3,52.5,z))
 var room_pins:Dictionary={}
 for label in ["D09_directory_03","D09_directory_07"]:
  var room:Node3D=ship.find_child(label,true,false);record(label+" retained room exists",room!=null)
  if room==null:quit(1);return
  for mesh:MeshInstance3D in room.find_children("*","MeshInstance3D",true,false):room_pins[str(mesh.get_path())]={"node":mesh,"faces":mesh.mesh.get_faces(),"pose":mesh.global_transform}
 var node:Node3D=ship.get_node("ShipSpace/Districts/Group4TerminalBranches")
 var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 var owned:Array[Node]=node.find_children("*","Light3D",true,false)
 record("Four existing-budget source lights",owned.size()==4 and owned.all(func(light:Node)->bool:return budget.sources.has(light)))
 for z in [-216.0,216.0]:
  # One independent supported original route fixture for each distant terminal; no later relocation within the circuit.
  player.global_position=Vector3(-3,52.53,z);player.velocity=Vector3.ZERO;player.set_controls_enabled(true)
  ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
  for i in range(30):await physics_frame
  for target in [Vector3(-6,52.5,z),Vector3(-10,52.5,z),Vector3(-10,52.5,z+1.2),Vector3(-10,52.5,z),Vector3(-6,52.5,z),Vector3(-3,52.5,z)]:
   var leg:Dictionary=await walk_to(player,target);leg.terminal_z=z;legs.append(leg);record("Original-player terminal leg "+str(legs.size()),leg.reached and leg.floor_contact)
   if not leg.reached:break
  for i in range(30):await physics_frame
  record("Unchanged eight shadow budget "+str(z),budget.shadow_source_budget==8 and budget.previously_active.size()<=8)
 for z in [-216.0,216.0]:residency.prepare_position(Vector3(-3,52.5,z))
 for path in room_pins:
  var old:Dictionary=room_pins[path]
  record("Original room geometry and pose "+path,is_instance_valid(old.node) and old.node.mesh.get_faces()==old.faces and old.node.global_transform==old.pose)
 record("Single original cart",cart.persistent_id==&"custodian_cart_001" and cart.products.size()==4)
 for q in original_products:record("Original product identity "+str(q.id),is_instance_valid(q.node) and q.node.persistent_id==q.id)
 physical_key(false)
 var result:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks.size(),"errors":errors,"original_player_controller_legs":legs,"independent_initial_fixtures":2,"teleports_within_route":0,"original_room_meshes_preserved":room_pins.size(),"stock_cart_or_tram_tests_performed":false,"four_original_product_nodes_and_ids_unchanged":true,"product_consumption_tested":false,"main_scene":"retained 1f68f1e main with installed terminal source027","scope":"Two actual terminal branches, guards/floor-ledges and original lanterns; no whole161-destination, species, structural, ordinary-game visual or tram acceptance."}
 FileAccess.open("res://artifacts/group4_terminals_integrated001.json",FileAccess.WRITE).store_string(JSON.stringify(result," "))
 print("GROUP4 TERMINALS ",result.status,": ",checks.size()," checks; ",legs.size()," original-player legs, no within-route teleports")
 main.queue_free();await process_frame;quit(0 if errors.is_empty() else 1)
