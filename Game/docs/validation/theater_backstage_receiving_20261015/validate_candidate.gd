extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/theater_backstage_receiving_20261015/"
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip",D+"CANDIDATE_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(30);var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state;var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"BACKSTAGE_CONFIG.json"));var polygon:=PackedVector2Array()
 for point in p.policy.floor_outline_xz:polygon.append(Vector2(point[0],point[1]))
 var missing_only_points:Array[Vector3]=[];var unexpected_floors:Array=[]
 for x in range(-33,-4):
  for z in range(-259,-246):
   if not Geometry2D.is_point_in_polygon(Vector2(x,z),polygon):continue
   var point:=Vector3(x,69.5,z);var h:=ray(space,point+Vector3.UP*.02,point-Vector3.UP*.02)
   if not h.is_empty():unexpected_floors.append({"at":str(point),"floor":str(h.collider.get_path())})
   missing_only_points.append(point)
 if not unexpected_floors.is_empty():
  FileAccess.open(D+"UNEXPECTED_PREEXISTING_FLOORS.json",FileAccess.WRITE).store_string(JSON.stringify(unexpected_floors,"  "));print("FAIL_PREEXISTING_FLOOR_MISMATCH");quit(1);return
 var venue:Node3D=ship.get_node("ShipSpace/Districts/GrandLanternTheater_ConnectedStaticStage_WIP");var motion:Node3D=venue.get_node("TheaterUnpoweredDoorLiftAssemblies");var old_poses:Dictionary={}
 for door:Node3D in motion.get_children():
  if door.has_meta("operation_enabled")and not door.get_meta("operation_enabled"):old_poses[door]=door.transform
 var group:Node3D=load("res://scripts/theater_backstage_receiving_20261015/package.gd").build(ship);await frames(3);var floor_samples:Array=[]
 for point:Vector3 in missing_only_points:
  var h:=ray(space,point+Vector3.UP*.02,point-Vector3.UP*.02);floor_samples.append({"at":str(point),"supported":not h.is_empty()and group.is_ancestor_of(h.collider)and absf(h.position.y-69.5)<.002})
 var exclusions:Array[RID]=[]
 for body:CollisionObject3D in group.find_children("*","CollisionObject3D",true,false):exclusions.append(body.get_rid())
 var contacts:Array=[]
 for mesh:MeshInstance3D in group.find_children("*","MeshInstance3D",true,false):
  var pieces:Array=[];var b:AABB=mesh.global_transform*mesh.get_aabb()
  if str(mesh.name)in["Backstage_MissingOnlyWalkingFloor","Backstage_PositiveHeaderTieCanopy"]:
   assert(mesh.global_transform.is_equal_approx(Transform3D.IDENTITY));var roof:bool=str(mesh.name).contains("Canopy");var xa:float=-34.7 if roof else -34.;var xb:float=-3.85 if roof else -4.;var y0:float=73.5 if roof else 69.26;var y1:float=73.66 if roof else 69.5
   for box in[[xa,-9.65,-259.15,-254.85],[-13.95,-9.65,-254.85,-246.85],[-9.65,xb,-251.15,-246.85]]:
    var shape:=BoxShape3D.new();shape.size=Vector3(box[1]-box[0],y1-y0,box[3]-box[2]);shape.margin=0.;pieces.append({"shape":shape,"pose":Transform3D(Basis.IDENTITY,Vector3((box[0]+box[1])/2,(y0+y1)/2,(box[2]+box[3])/2))})
  else:
   var shape:ConvexPolygonShape3D=mesh.mesh.create_convex_shape(true,false);shape.margin=0.;pieces.append({"shape":shape,"pose":mesh.global_transform})
  var targets:Dictionary={}
  for piece in pieces:
   var q:=PhysicsShapeQueryParameters3D.new();q.shape=piece.shape;q.margin=0.;q.transform=piece.pose;q.exclude=exclusions
   for hit in space.intersect_shape(q,256):targets[str(hit.collider.get_path())]=true
  if not targets.is_empty():contacts.append({"part":str(mesh.name),"min":[b.position.x,b.position.y,b.position.z],"max":[b.end.x,b.end.y,b.end.z],"old_contacts":targets.keys()})
 var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.global_position=Vector3(-2.5,69.53,-249);player.velocity=Vector3.ZERO;player.set_controls_enabled(true);await frames(20);var legs:Array=[]
 for goal:Vector3 in[Vector3(-6,69.5,-249),Vector3(-11.8,69.5,-249),Vector3(-11.8,69.5,-257),Vector3(-20,69.5,-257),Vector3(-30,69.5,-257),Vector3(-34.1,69.5,-257),Vector3(-30,69.5,-257),Vector3(-20,69.5,-257),Vector3(-11.8,69.5,-257),Vector3(-11.8,69.5,-249),Vector3(-6,69.5,-249),Vector3(-2.5,69.5,-249)]:
  var leg:Dictionary=await walk_to(player,goal);legs.append(leg)
  if not leg.reached or not leg.floor_contact:break
 player.set_physics_process(false);player.global_position=Vector3(0,0,0);player.force_update_transform();await frames(2)
 var cart_samples:Array=[];var wheel_samples:Array=[];var cart:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/cleaning_cart_contacts.json"))
 for point:Vector3 in[Vector3(-6,69.5,-249),Vector3(-11.8,69.5,-249),Vector3(-11.8,69.5,-257),Vector3(-33.7,69.5,-257)]:
  for i in range(8):
   var yaw:float=i*PI/4;cart_samples.append({"at":str(point),"yaw":yaw,"clear":cart_clear(space,point,yaw)})
   for wheel in cart.wheel_contacts:
    var at:Vector3=point+Basis(Vector3.UP,yaw)*vec(wheel.center)-Vector3.UP*float(wheel.radius);var h:=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02);wheel_samples.append(not h.is_empty()and absf(h.position.y-69.5)<.002)
 var lights:Array=[];var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 for light:Light3D in group.find_children("*","Light3D",true,false):lights.append({"name":str(light.name),"registered_once":budget.sources.count(light)==1})
 var doors_unchanged:=true
 for door in old_poses:
  if not door.transform.is_equal_approx(old_poses[door])or door.get_meta("operation_enabled"):doors_unchanged=false
 var ok:bool=floor_samples.all(func(a):return a.supported)and legs.size()==12 and legs.all(func(a):return a.reached and a.floor_contact)and cart_samples.all(func(a):return a.clear)and wheel_samples.all(func(a):return a)and lights.size()==4 and lights.all(func(a):return a.registered_once)and doors_unchanged
 FileAccess.open(D+"CANDIDATE_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS"if ok else"FAIL","floor_samples":floor_samples,"old_contact_inventory":contacts,"actual_controller_legs":legs,"original_cart_static_poses":cart_samples,"original_cart_wheel_floor_samples":wheel_samples,"original_doors_unchanged":doors_unchanged,"light_registration":lights,"new_floor_m2":p.policy.floor_area_m2,"original_compiled_floor_changed":false,"loaded_cart_body_primary_load_venue_operation_or_final_art_accepted":false},"  "));print("PASS_BACKSTAGE_CURRENT_SHIP"if ok else"FAIL_BACKSTAGE_CURRENT_SHIP");quit(0 if ok else 1)
