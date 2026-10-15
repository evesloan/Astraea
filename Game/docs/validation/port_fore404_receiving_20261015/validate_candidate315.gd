extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/port_fore404_receiving_20261015/"
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/DINING_SERVICE_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ORCHARD_RECEIVING_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/SYNTHESIS_EXTERNAL_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/D09_RETAIL_SERVICE_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/AQUATIC_EXTERNAL_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ARRIVALS_STAFF_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/THREAD_SUCCESSOR_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ARRIVALS_UPPER_STAFF_ADOPTION_OVERLAY.zip",D+"CANDIDATE_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func source_ray(space:PhysicsDirectSpaceState3D,a:Vector3,b:Vector3,actor:CharacterBody3D)->Dictionary:
 var q:=PhysicsRayQueryParameters3D.create(a,b);q.exclude=[actor.get_rid()];return space.intersect_ray(q)
func source_clear(space:PhysicsDirectSpaceState3D,at:Vector3,actor:CharacterBody3D)->bool:
 var q:=PhysicsShapeQueryParameters3D.new();var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8;shape.margin=.001;q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*.925);q.exclude=[actor.get_rid()]
 if not space.intersect_shape(q,32).is_empty():return false
 for delta in[Vector3(.3,0,0),Vector3(0,0,.3)]:
  if not source_ray(space,at+Vector3.UP-delta,at+Vector3.UP+delta,actor).is_empty():return false
 return true
func box_contacts(space:PhysicsDirectSpaceState3D,lo:Vector3,hi:Vector3,exclude:Array[RID])->Array:
 var shape:=BoxShape3D.new();shape.size=hi-lo;shape.margin=0.;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.margin=0.;q.transform.origin=(lo+hi)/2;q.exclude=exclude;var rows:Array=[]
 for hit in space.intersect_shape(q,256):rows.append(str(hit.collider.get_path()))
 return rows
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(90);var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false);actor.global_position=Vector3(-62,52.53,-404);actor.force_update_transform();ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position);ship.get_node("ShipSystems/RemainingBatchStreaming").prepare_position(actor.global_position);await frames(4);var space:=ship.get_world_3d().direct_space_state;var group:Node3D=ship.get_node("ShipSpace/PortFore404Receiving20261015");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/port_fore404_receiving_20261015/NATIVE_VERIFICATION.json"));var original:Node3D=ship.get_node("ShipSpace/Districts/GrandPoolOrchardSection_WIP/GrandPoolConnectedArchitecture");var before:Dictionary={}
 var reference:Node3D=load("res://assets/models/AST-AQU-016.glb").instantiate();reference.visible=false;root.add_child(reference);var source_preserved:=true;var source_count:=0
 for mesh:MeshInstance3D in reference.find_children("*","MeshInstance3D",true,false):
  var actual:MeshInstance3D=original.find_child(str(mesh.name),true,false);assert(actual!=null);source_count+=1;before[actual]={"pose":actual.global_transform,"mesh":actual.mesh}
  if str(mesh.name)==str(p.walls[0].source_name).validate_node_name():continue
  if actual.mesh!=mesh.mesh or not actual.global_transform.is_equal_approx(mesh.global_transform):source_preserved=false
 var excluded:Array[RID]=[actor.get_rid()]
 for body:CollisionObject3D in group.find_children("*","CollisionObject3D",true,false):excluded.append(body.get_rid())
 var doc:=GLTFDocument.new();var state:=GLTFState.new();assert(doc.append_from_file(D+"AUTHORING_COMPONENTS_r002.glb",state)==OK);var authored:Node3D=doc.generate_scene(state);authored.visible=false;root.add_child(authored);var contacts:Array=[];var unexplained:Array=[]
 for row in p.bounds:
  if str(row.name).ends_with("_Lens"):continue
  var paths:Array=[]
  if str(row.name)=="PFR_SourceJoinedCanopy":
   for rect in[[-60.39995,-53.8,-405.,-401.4],[-60.49995,-60.39995,-402.99995,-401.4]]:
    for path in box_contacts(space,Vector3(rect[0],56.05,rect[2]),Vector3(rect[1],56.23,rect[3]),excluded):
     if not path in paths:paths.append(path)
  else:
   var mesh:MeshInstance3D=authored.find_child(str(row.name).validate_node_name(),true,false);assert(mesh!=null);var shape:=mesh.mesh.create_convex_shape(true,false);shape.margin=0.;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.margin=0.;q.transform=mesh.global_transform;q.exclude=excluded
   for hit in space.intersect_shape(q,256):paths.append(str(hit.collider.get_path()))
  for path in paths:
   var classification:="";var wall:bool=str(p.walls[0].source_name).validate_node_name()in path;var staff_floor:bool="ShoppingPromenadeOwnedFloors/STAFFLINK_D09_PF404__floor"in path or"SERVICE_D09_PF_inner_00"in path;var market_floor:bool="/D09_orchard_market_gallery/"in path;var old_roof:bool="STAFFLINK_D09_PF404"in path and not"OwnedFloors"in path
   if str(row.name).begins_with("PFR_StaffEmbeddedTie")and staff_floor:classification="embedded_exact_original_fore404_floor_bearing"
   elif str(row.name).begins_with("PFR_MarketEmbeddedTie")and(market_floor or wall):classification="embedded_exact_original_market_slab_or_west_wall_band_bearing_below_unchanged_floor_datum"
   elif str(row.name).begins_with("PFR_ExistingRoofEmbeddedSplice")and old_roof:classification="embedded_exact_original_fore404_roof_splice"
   elif wall and(str(row.name).begins_with("PFR_NorthSide_")or str(row.name).begins_with("PFR_SouthSide_")or str(row.name)=="PFR_SourceJoinedCanopy"):classification="measured_receiving_panel_end_or_header_bearing_in_exact_original_market_wall_outside_aperture"
   elif str(row.name)=="PFR_ReceivingFloor"and(staff_floor or market_floor or wall):classification="contiguous_source_floor_or_wall_band_edge_with_50micron_new_floor_relief"
   elif str(row.name)=="PFR_SourceJoinedCanopy"and old_roof:classification="empty_notch_exact_original_roof_edge_adjacency_with_50micron_relief"
   contacts.append({"part":row.name,"source":path,"classification":classification})
   if classification.is_empty():unexplained.append(contacts[-1])
 var floors:Array=[];var preimages:Array=[]
 for x in[-60.3,-59.5,-58.5,-57.5,-56.5,-55.5,-54.2]:
  for z in[-404.7,-403.8,-402.7,-401.7]:
   var at:=Vector3(x,52.5,z);var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.025,at-Vector3.UP*.025);q.exclude=excluded;var old:=space.intersect_ray(q)
   if not old.is_empty():preimages.append({"at":str(at),"source":str(old.collider.get_path())})
   var hit:=source_ray(space,at+Vector3.UP*.03,at-Vector3.UP*.03,actor);floors.append({"at":str(at),"supported":not hit.is_empty()and absf(hit.position.y-52.5)<.003,"owner":str(hit.collider.get_path())if not hit.is_empty()else""})
 var bearings:Array=[]
 for row in p.source_bearings:
  var at:=vec(row.point);var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.02,at-Vector3.UP*.02);q.exclude=excluded;var hit:=space.intersect_ray(q);bearings.append({"part":row.name,"at":str(at),"expected_source":row.source_region,"actual_source":str(hit.collider.get_path())if not hit.is_empty()else"","supported":not hit.is_empty()and absf(hit.position.y-at.y)<.003 and str(row.source_region)in str(hit.collider.get_path())})
 var stances:Array=[]
 for at:Vector3 in[Vector3(-62,52.53,-404),Vector3(-60,52.53,-403.2),Vector3(-57.3,52.53,-403.2),Vector3(-54.5,52.53,-403.2),Vector3(-52.5,52.53,-403.2),Vector3(-51.5,52.53,-400.9),Vector3(-45.9,52.53,-400.9)]:stances.append({"at":str(at),"clear":source_clear(space,at,actor)})
 actor.set_physics_process(true);actor.set_controls_enabled(true);actor.velocity=Vector3.ZERO;await frames(20);var legs:Array=[]
 for at:Vector3 in[Vector3(-62,52.5,-403.2),Vector3(-60,52.5,-403.2),Vector3(-57.3,52.5,-403.2),Vector3(-54.5,52.5,-403.2),Vector3(-52.5,52.5,-403.2),Vector3(-51.5,52.5,-400.9),Vector3(-45.9,52.5,-400.9),Vector3(-51.5,52.5,-400.9),Vector3(-52.5,52.5,-403.2),Vector3(-54.5,52.5,-403.2),Vector3(-57.3,52.5,-403.2),Vector3(-60,52.5,-403.2),Vector3(-62,52.5,-403.2),Vector3(-62,52.5,-404)]:
  legs.append(await walk_to(actor,at))
  if not legs[-1].reached:break
 for mesh in before:
  if not is_instance_valid(mesh)or not mesh.global_transform.is_equal_approx(before[mesh].pose)or mesh.mesh!=before[mesh].mesh:source_preserved=false
 var lights:Array=[];var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 for light:Light3D in group.find_children("*","Light3D",true,false):lights.append({"name":str(light.name),"registered_once":budget.sources.count(light)==1})
 var joins=ship.get_node("ShipSpace/Districts/ShoppingPromenadeChunks").get_meta("unresolved_address_joins");var ok:bool=unexplained.is_empty()and preimages.is_empty()and floors.all(func(a):return a.supported)and bearings.size()==8 and bearings.all(func(a):return a.supported)and stances.all(func(a):return a.clear)and legs.size()==14 and legs.all(func(a):return a.reached and a.floor_contact)and source_preserved and lights.size()==1 and lights.all(func(a):return a.registered_once)and joins==84
 FileAccess.open(D+"CANDIDATE_RUNTIME315.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS"if ok else"FAIL","source_contacts":contacts,"unexplained_contacts":unexplained,"old_floor_preimages":preimages,"new_floor_samples":floors,"source_bearings":bearings,"clear_operator_stances":stances,"actual_original_controller_legs":legs,"teleports_within_continuous_route":0,"original_market_mesh_poses_resources_preserved_except_one_exact_wall_successor":source_preserved,"original_market_mesh_count":source_count,"lights":lights,"all84addressjoins_still_unresolved":joins,"port_physical_receiver":"D09_orchard_market_gallery","starboard_receiver_or_logical_riser_address_mapping_admitted":false,"primary_engineering_loaded_cart_species_stock_roles_save_final_art_accepted":false},"  "));print("PASS_PORT_FORE404_CURRENT_MAIN"if ok else"FAIL_PORT_FORE404_CURRENT_MAIN");authored.queue_free();reference.queue_free();quit(0 if ok else 1)
