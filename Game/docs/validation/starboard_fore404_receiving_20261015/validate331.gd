extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/starboard_fore404_receiving_20261015/"
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/DINING_SERVICE_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/ORCHARD_RECEIVING_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/SYNTHESIS_EXTERNAL_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/D09_RETAIL_SERVICE_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/AQUATIC_EXTERNAL_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/ARRIVALS_STAFF_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/THREAD_SUCCESSOR_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/ARRIVALS_UPPER_STAFF_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/PORT_FORE404_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/VESPER_SERVICE_ADOPTION_OVERLAY.zip",D+"CANDIDATE_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func volume(space:PhysicsDirectSpaceState3D,lo:Vector3,hi:Vector3,excluded:Array[RID])->Array:
 var q:=PhysicsShapeQueryParameters3D.new();var shape:=BoxShape3D.new();shape.size=hi-lo;shape.margin=0.;q.shape=shape;q.margin=0.;q.transform.origin=(lo+hi)/2;q.exclude=excluded;var paths:Array=[]
 for hit in space.intersect_shape(q,1024):paths.append(str(hit.collider.get_path()))
 return paths
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(90);var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false);actor.global_position=Vector3(62,52.53,-408);var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");residency.prepare_position(Vector3(50,52.5,-414));ship.get_node("ShipSystems/RemainingBatchStreaming").prepare_position(Vector3(50,52.5,-414));await frames(4);var cafe:Node3D=ship.get_node("ShipSpace/Districts/ReceivedSections/D09_directory_02");var group:Node3D=ship.get_node("ShipSpace/StarboardFore404Receiving20261015");var space:=ship.get_world_3d().direct_space_state;var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"NATIVE_VERIFICATION.json"));var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"NATIVE_PLAN.json"));var mount_proof:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"FIXTURE_MOUNT_VERIFICATION.json"));var source:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"COPPER_KETTLE_RECEIVING_PREIMAGES328.json"));var excluded:Array[RID]=[actor.get_rid()]
 for body:CollisionObject3D in group.find_children("*","CollisionObject3D",true,false):excluded.append(body.get_rid())
 var floors:Array=[];var preimages:Array=[]
 for rect in plan.floor_rectangles:
  var x:float=rect[0]+.35
  while x<float(rect[1])-.25:
   var z:float=rect[2]+.35
   while z<float(rect[3])-.25:
    var at:=Vector3(x,52.5,z);var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.03,at-Vector3.UP*.03);q.exclude=excluded;var old:=space.intersect_ray(q)
    if not old.is_empty():preimages.append({"at":str(at),"owner":str(old.collider.get_path())})
    var h:=ray(space,at+Vector3.UP*.03,at-Vector3.UP*.03);floors.append({"at":str(at),"supported":not h.is_empty()and absf(h.position.y-52.5)<.0002})
    z+=1.
   x+=1.
 var contacts:Array=[];var unexplained:Array=[]
 for row in p.bounds:
  if "Lens"in str(row.name):continue
  var lo:=vec(row.min);var hi:=vec(row.max);var paths:Array=[]
  if "MissingOnlyFloor"in str(row.name)or"SourceJoinedRoof"in str(row.name):
   var rects:Array=plan.floor_rectangles.duplicate(true)
   if "SourceJoinedRoof"in str(row.name):rects[2][1]=60.39995
   for rect in rects:
    for path in volume(space,Vector3(rect[0],lo.y,rect[2]),Vector3(rect[1],hi.y,rect[3]),excluded):
     if not path in paths:paths.append(path)
  else:paths=volume(space,lo,hi,excluded)
  for path in paths:
   var kind:=""
   if "/D09_copper_kettle_source_floor/"in path and(lo.x<52.31):kind="embedded_or_edge_joint_on_exact_retained_cafe_slab"
   elif "/ShoppingPromenadeOwnedFloors/STAFFLINK_D09_SF404"in path and hi.x>60.19:kind="embedded_or_edge_joint_on_exact_retained_staff_slab"
   elif "/Perimeter_5/"in path and lo.x<52.31:kind="finite_gateway_jamb_or_head_positive_joint"
   elif "/STAFFLINK_D09_SF404/"in path and lo.y>=55.44 and hi.x>60.24:kind="positive_bearing_to_retained_staff_roof_end"
   var r:Dictionary={"part":row.name,"owner":path,"classification":kind};contacts.append(r)
   if kind.is_empty():unexplained.append(r)
 var bearings:Array=[]
 for row in p.source_bearings:
  var at:=vec(row.point);var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.03,at-Vector3.UP*.03);q.exclude=excluded;var h:=space.intersect_ray(q);var ok:bool=not h.is_empty()and absf(h.position.y-at.y)<.0002 and str(h.collider.get_path()).contains(str(row.source_region));bearings.append({"name":row.name,"at":str(at),"owner":str(h.collider.get_path())if not h.is_empty()else"","passed":ok})
 var h:=ray(space,Vector3(52.4,56.15,-414),Vector3(51.8,56.15,-414));bearings.append({"name":"ExactRetainedCafeHeader","passed":not h.is_empty()and str(h.collider.get_path()).contains("/Perimeter_5/"),"owner":str(h.collider.get_path())if not h.is_empty()else""})
 var mounts:Array=[]
 for row in mount_proof.mounts:
  var at:=vec(row.at);var axis:=Vector3.ZERO;axis[int(row.query_axis)]=.3;h=ray(space,at-axis,at+axis);mounts.append({"fixture":row.fixture,"positive_native_overlap":row.positive_overlap_xyz_m,"passed":not h.is_empty()and group.is_ancestor_of(h.collider),"owner":str(h.collider.get_path())if not h.is_empty()else""})
 var lights:Array=[];var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 for row in p.lights:
  var light:Light3D=group.get_node(str(row.name));var at:=vec(row.at);var exit:=ray(space,at,at+Vector3.DOWN*.08);var floor:=ray(space,at,Vector3(at.x,52.47,at.z));lights.append({"name":row.name,"registered_once":budget.sources.count(light)==1,"source_exit_clear":exit.is_empty(),"actual_floor_receiver":not floor.is_empty()and absf(floor.position.y-52.5)<.0002 and group.is_ancestor_of(floor.collider)})
 var preserved:=true;var mismatch:Array=[];var expected_wall:String="Perimeter_5";var count:int=cafe.find_children("*","MeshInstance3D",true,false).size()
 for row in source.actual_cafe_meshes:
  var node:MeshInstance3D=root.get_node_or_null(str(row.path))
  if node==null:preserved=false;mismatch.append({"name":row.name,"reason":"missing"});continue
  var b:AABB=node.global_transform*node.get_aabb()
  if b.position.distance_to(vec(row.min))>.0001 or b.end.distance_to(vec(row.max))>.0001 or(str(row.name)!=expected_wall and node.mesh.resource_path!=str(row.mesh)):preserved=false;mismatch.append({"name":row.name,"reason":"bounds_or_unrelated_resource"})
 var snapshot:Dictionary={}
 for mesh:MeshInstance3D in cafe.find_children("*","MeshInstance3D",true,false):snapshot[mesh]={"pose":mesh.global_transform,"mesh":mesh.mesh}
 var lift:Node3D=ship.find_child("ForwardStaffLift",true,false);var lift_stops:Array=lift.floor_heights.duplicate();actor.global_position=Vector3(62,52.53,-404);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);actor.set_physics_process(true);await frames(20);var legs:Array=[];var ok:bool=preimages.is_empty()and floors.all(func(r):return r.supported)and unexplained.is_empty()and bearings.all(func(r):return r.passed)and mounts.all(func(r):return r.passed)and lights.all(func(r):return r.registered_once and r.source_exit_clear and r.actual_floor_receiver)and preserved and count==553
 for at:Vector3 in[Vector3(60.1,52.5,-404),Vector3(58.8,52.5,-404),Vector3(55.7,52.5,-404),Vector3(55.7,52.5,-409),Vector3(55.7,52.5,-414),Vector3(53,52.5,-414),Vector3(51,52.5,-414),Vector3(48,52.5,-414),Vector3(51,52.5,-414),Vector3(53,52.5,-414),Vector3(55.7,52.5,-414),Vector3(55.7,52.5,-409),Vector3(55.7,52.5,-404),Vector3(58.8,52.5,-404),Vector3(60.1,52.5,-404),Vector3(62,52.5,-404)]:
  if not ok:break
  var leg:Dictionary=await walk_to(actor,at);legs.append(leg)
  if not leg.reached or not leg.floor_contact:ok=false
 for mesh in snapshot:
  if not is_instance_valid(mesh)or not mesh.global_transform.is_equal_approx(snapshot[mesh].pose)or mesh.mesh!=snapshot[mesh].mesh:preserved=false
 ok=ok and legs.size()==16 and preserved and lift.floor_heights==lift_stops and str(cafe.get_meta("programme_key"))=="D09_directory_02"
 FileAccess.open(D+"CANDIDATE_RUNTIME331.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS"if ok else"FAIL","source_room_physically_loaded":cafe.is_inside_tree(),"cafe_meshes_preserved_except_exact_wall":preserved,"cafe_mesh_count":count,"baseline_mismatches":mismatch,"new_floor_preimages":preimages,"floor_samples":floors,"source_contacts":contacts,"unexplained_contacts":unexplained,"source_bearings":bearings,"fixture_mounts":mounts,"lights":lights,"original_controller_legs":legs,"exact_wall_preimage_witness":group.get_meta("exact_selected_wall_preimages"),"staff_lift_stops_preserved":lift.floor_heights==lift_stops,"all84logical_addressjoins_still_unresolved":84,"operation_or_final_art_acceptance":false},"  "));print("PASS_STARBOARD_COPPER_PHYSICAL_RECEIVING"if ok else"FAIL_STARBOARD_COPPER_PHYSICAL_RECEIVING");quit(0 if ok else 1)
