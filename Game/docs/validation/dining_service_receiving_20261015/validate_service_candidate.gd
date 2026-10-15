extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/dining_service_receiving_20261015/"
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip",D+"SERVICE_CANDIDATE_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func floor_points(p:Dictionary)->Array[Vector3]:
 var points:Array[Vector3]=[];var seen:Dictionary={}
 for site in p.sites:
  for rect in site.floor_rectangles:
   var x:float=rect[0]+.35
   while x<float(rect[1])-.25:
    var z:float=rect[2]+.35
    while z<float(rect[3])-.25:
     var key:=str(roundi(x*1000))+"_"+str(roundi(z*1000))
     if not seen.has(key):seen[key]=true;points.append(Vector3(x,61,z))
     z+=3.
    x+=3.
 return points
func box_contacts(space:PhysicsDirectSpaceState3D,rect:Array,lo:float,hi:float,exclude:Array[RID])->Array:
 var shape:=BoxShape3D.new();shape.size=Vector3(rect[1]-rect[0],hi-lo,rect[3]-rect[2]);shape.margin=0.;var query:=PhysicsShapeQueryParameters3D.new();query.shape=shape;query.margin=0.;query.transform.origin=Vector3((rect[0]+rect[1])/2,(lo+hi)/2,(rect[2]+rect[3])/2);query.exclude=exclude;var paths:Array=[]
 for hit in space.intersect_shape(query,512):paths.append(str(hit.collider.get_path()))
 return paths
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/dining_service_receiving_20261015/NATIVE_RECEIVER_VERIFICATION.json"));var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(90);var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state;var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.set_physics_process(false);player.global_position=Vector3(0,0,0);var stream:Node=ship.get_node("ShipSystems/RemainingBatchStreaming");var points:=floor_points(p);var preimages:Array=[]
 for at in points:
  var h:=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02)
  if not h.is_empty():preimages.append({"at":str(at),"old_floor":str(h.collider.get_path())})
 var group:Node3D=load("res://scripts/dining_service_receiving_20261015/package.gd").build(ship);await frames(3);var excluded:Array[RID]=[]
 for body:CollisionObject3D in group.find_children("*","CollisionObject3D",true,false):excluded.append(body.get_rid())
 var document:=GLTFDocument.new();var state:=GLTFState.new();assert(document.append_from_file("res://validation/dining_service_receiving_20261015/"+str(p.raw_authoring_file),state)==OK);var authored:Node3D=document.generate_scene(state);root.add_child(authored);authored.visible=false;assert(authored.find_children("*","CollisionObject3D",true,false).is_empty());var contacts:Array=[];var embedded_bearings:Array=[];var legs:Array=[];var stances:Array=[];var carts:Array=[];var cart_sweeps:Array=[];var wheel_samples:Array=[];var cart_config:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/cleaning_cart_contacts.json"));var source_counts:Dictionary={};var preserved:=true
 for site in p.sites:
  var side:float=site.side;var clean:float=site.clean_z;var used:float=site.used_z;var join:float=site.axial_join_z;stream.set_physics_process(true);player.global_position=Vector3(side*50,61.03,(clean+used)/2);stream.prepare_position(player.global_position);await frames(4);var old_room:Node3D=stream.rooms[str(site.key)];var before:Dictionary={}
  for mesh:MeshInstance3D in old_room.find_children("*","MeshInstance3D",true,false):before[mesh]={"pose":mesh.global_transform,"mesh":mesh.mesh}
  assert(before.size()>1000,"Original dining source must be resident during contact and route checks");source_counts[str(site.key)]=before.size()
  for mesh:MeshInstance3D in authored.find_children("D10S_"+str(site.unit)+"_*","MeshInstance3D",true,false):
   var paths:Array=[]
   if "MissingOnlyFloor"in str(mesh.name)or"SourceJoinedRoof"in str(mesh.name):
    for rect in site.floor_rectangles:
     for path in box_contacts(space,rect,60.76 if"MissingOnlyFloor"in str(mesh.name)else 64.8,61. if"MissingOnlyFloor"in str(mesh.name)else 64.98,excluded):
      if not path in paths:paths.append(path)
   elif not"Lens"in str(mesh.name):
    var query:=PhysicsShapeQueryParameters3D.new();query.shape=mesh.mesh.create_convex_shape(true,false);query.shape.margin=0.;query.margin=0.;query.transform=mesh.global_transform;query.exclude=excluded
    for hit in space.intersect_shape(query,256):paths.append(str(hit.collider.get_path()))
   if not paths.is_empty():contacts.append({"programme_key":site.key,"part":str(mesh.name),"old_contacts":paths})
   if "RetainedFloorUnderlap"in str(mesh.name):
    var box:AABB=mesh.global_transform*mesh.get_aabb();var point:=Vector3(side*53.85,61,box.get_center().z);var query:=PhysicsRayQueryParameters3D.create(point+Vector3.UP*.03,point-Vector3.UP*.03);query.exclude=excluded;var hit:=space.intersect_ray(query);embedded_bearings.append({"part":str(mesh.name),"plate_min_y":box.position.y,"plate_max_y":box.end.y,"old_floor_solid_y":[60.76,61.],"floor_contact":not hit.is_empty()and absf(hit.position.y-61)<.003,"old_floor_owner":str(hit.collider.get_path())if not hit.is_empty()else"","ceiling_clear":box.position.y>60.7599983215332+.019,"embedded":box.position.y>60.76 and box.end.y<61.})
  player.global_position=Vector3(side*2,61.03,join);player.velocity=Vector3.ZERO;player.set_physics_process(true);player.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position);await frames(20)
  for point:Vector3 in[Vector3(68,61,join),Vector3(68,61,clean),Vector3(60,61,clean),Vector3(52.8,61,clean),Vector3(60,61,clean),Vector3(68,61,clean),Vector3(68,61,used),Vector3(60,61,used),Vector3(52.8,61,used),Vector3(60,61,used),Vector3(68,61,used),Vector3(68,61,join),Vector3(2,61,join)]:
   var leg:Dictionary=await walk_to(player,Vector3(side*point.x,point.y,point.z));leg["programme_key"]=site.key;legs.append(leg)
   if not leg.reached or not leg.floor_contact:break
  for mesh in before:
   if not is_instance_valid(mesh)or not mesh.global_transform.is_equal_approx(before[mesh].pose)or mesh.mesh!=before[mesh].mesh:preserved=false
  stream.set_physics_process(false);player.set_physics_process(false);player.global_position=Vector3(0,0,0);player.force_update_transform();await frames(2)
  for point:Vector3 in[Vector3(60,61,clean-1),Vector3(60,61,clean+2.8),Vector3(57.3,61,clean+3),Vector3(62.7,61,clean+3),Vector3(62.7,61,used+3.2),Vector3(57.3,61,used-3),Vector3(68,61,clean),Vector3(68,61,used)]:
   var at:=Vector3(side*point.x,point.y,point.z);var h:=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02);stances.append({"programme_key":site.key,"at":str(at),"capsule_clear":capsule_clear(space,at),"floor":not h.is_empty()and absf(h.position.y-61)<.003})
  for point:Vector3 in[Vector3(68,61,join),Vector3(68,61,clean),Vector3(60,61,clean),Vector3(54,61,clean),Vector3(68,61,used),Vector3(60,61,used),Vector3(54,61,used)]:
   for yaw in[0.,PI/2]:
    var at:=Vector3(side*point.x,point.y,point.z);carts.append({"programme_key":site.key,"at":str(at),"yaw":yaw,"original_static_cart_clear":cart_clear(space,at,yaw)})
  for z in [clean,used]:
   for x in range(54,69):
    for yaw in [0.,PI/2]:
     var at:=Vector3(side*x,61,z);cart_sweeps.append({"programme_key":site.key,"at":str(at),"yaw":yaw,"clear":cart_clear(space,at,yaw)});var pose:=Transform3D(Basis(Vector3.UP,yaw),at+Vector3.UP*.005)
     for wheel in cart_config.wheel_contacts:
      var foot:Vector3=pose*vec(wheel.center)-Vector3.UP*float(wheel.radius);var hit:=ray(space,foot+Vector3.UP*.03,foot-Vector3.UP*.03);wheel_samples.append({"at":str(foot),"supported":not hit.is_empty()and absf(hit.position.y-61)<.003})
  for mesh in before:
   if not is_instance_valid(mesh)or not mesh.global_transform.is_equal_approx(before[mesh].pose)or mesh.mesh!=before[mesh].mesh:preserved=false
 var floors:Array=[]
 for at in points:
  var h:=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02);floors.append({"at":str(at),"supported":not h.is_empty()and absf(h.position.y-61)<.003,"owner":str(h.collider.get_path())if not h.is_empty()else""})
 var light_rows:Array=[];var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 for light:Light3D in group.find_children("*","Light3D",true,false):light_rows.append({"name":str(light.name),"registered_once":budget.sources.count(light)==1})
 var ok:bool=preimages.is_empty()and legs.size()==39 and legs.all(func(a):return a.reached and a.floor_contact)and stances.all(func(a):return a.capsule_clear and a.floor)and carts.all(func(a):return a.original_static_cart_clear)and cart_sweeps.all(func(a):return a.clear)and wheel_samples.all(func(a):return a.supported)and floors.all(func(a):return a.supported)and embedded_bearings.size()==18 and embedded_bearings.all(func(a):return a.floor_contact and a.embedded and a.ceiling_clear)and preserved and light_rows.size()==80 and light_rows.all(func(a):return a.registered_once)
 FileAccess.open(D+"SERVICE_CANDIDATE_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS"if ok else"FAIL","unexplained_old_floor_preimages":preimages,"new_floor_samples":floors,"actual_controller_legs":legs,"required_controller_legs":39,"work_stances":stances,"static_original_cart_poses":carts,"continuous_portal_cart_poses":cart_sweeps,"cart_wheel_floor_samples":wheel_samples,"old_contact_inventory":contacts,"embedded_floor_bearing_witnesses":embedded_bearings,"original_source_mesh_counts":source_counts,"original_room_poses_and_mesh_resources_preserved":preserved,"lights":light_rows,"native_authoring_meshes":2753,"runtime_batches":39,"new_floor_room_ids_capacity_or_lift_stops":0,"loaded_cart_food_water_stock_species_save_primary_engineering_or_final_art_accepted":false},"  "));print("PASS_D10_SERVICE_RECEIVING_CURRENT_SHIP"if ok else"FAIL_D10_SERVICE_RECEIVING_CURRENT_SHIP");authored.queue_free();quit(0 if ok else 1)
