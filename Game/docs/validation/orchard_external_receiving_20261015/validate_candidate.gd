extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/orchard_external_receiving_20261015/"
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/DINING_SERVICE_ADOPTION_OVERLAY.zip",D+"CANDIDATE_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func volume(space:PhysicsDirectSpaceState3D,lo:Vector3,hi:Vector3,exclude:Array[RID])->Array:
 var shape:=BoxShape3D.new();shape.size=hi-lo;shape.margin=0.;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.margin=0.;q.transform.origin=(lo+hi)/2;q.exclude=exclude;var out:Array=[]
 for hit in space.intersect_shape(q,512):out.append(str(hit.collider.get_path()))
 return out
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(90);var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.set_physics_process(false);player.global_position=Vector3(0,0,0);var space:=ship.get_world_3d().direct_space_state;var room:Node3D=ship.get_node("ShipSpace/Districts/D10_OrchardFoodHall_WIP");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/orchard_external_receiving_20261015/NATIVE_VERIFICATION.json"));var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"NATIVE_PLAN.json"));var before:Dictionary={};var old_doors:Dictionary={}
 for mesh:MeshInstance3D in room.find_children("*","MeshInstance3D",true,false):before[mesh]={"pose":mesh.global_transform,"mesh":mesh.mesh}
 for n:Node3D in room.find_children("OrchardFood_*","Node3D",true,false):old_doors[n]={"pose":n.global_transform,"id":str(n.persistent_id),"open":n.desired_open}
 var group:Node3D=load("res://scripts/orchard_external_receiving_20261015/package.gd").build(ship);await frames(3);var exclude:Array[RID]=[]
 for body:CollisionObject3D in group.find_children("*","CollisionObject3D",true,false):exclude.append(body.get_rid())
 var seen:Dictionary={};var preimages:Array=[];var floors:Array=[]
 for rect in plan.floor_rectangles:
  var x:float=rect[0]+.35
  while x<float(rect[1])-.25:
   var z:float=rect[2]+.35
   while z<float(rect[3])-.25:
    var key:=str(roundi(x*100))+"_"+str(roundi(z*100))
    if not seen.has(key):
     seen[key]=true;var at:=Vector3(x,61,z);var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.03,at-Vector3.UP*.03);q.exclude=exclude;var old:=space.intersect_ray(q)
     if not old.is_empty():preimages.append({"at":str(at),"owner":str(old.collider.get_path())})
     var hit:=ray(space,at+Vector3.UP*.03,at-Vector3.UP*.03);floors.append({"at":str(at),"supported":not hit.is_empty()and absf(hit.position.y-61)<.003})
    z+=2.
   x+=2.
 var contacts:Array=[];var unexplained:Array=[]
 for row in p.bounds:
  if "Lens"in str(row.name):continue
  var lo:=vec(row.min);var hi:=vec(row.max);var paths:Array=[]
  if "MissingOnlyFloor"in str(row.name)or"SourceJoinedRoof"in str(row.name):
   for rect in plan.floor_rectangles:
    for path in volume(space,Vector3(rect[0],lo.y,rect[2]),Vector3(rect[1],hi.y,rect[3]),exclude):
     if not path in paths:paths.append(path)
  else:paths=volume(space,lo,hi,exclude)
  for path in paths:
   var classification:=""
   if "/ORCH_PerimeterWall_1/"in path or"/ORCH_PerimeterDado_1/"in path:classification="positive_bearing_into_exact_retained_enclosure_edge"
   elif "/D10_orchard_foodhall_floor/"in path or"/D10_fore_route/"in path:classification="embedded_tie_or_floor_edge_bearing_on_exact_existing_floor"
   elif "/ORCH_StaffFloorFinish_"in path and("MissingOnlyFloor"in str(row.name)or"EmbeddedDiningTie"in str(row.name)):classification="retained_floor_finish_edge_contact"
   elif "/ORCH_ShapedCeiling_"in path and"SourceJoinedRoof"in str(row.name):classification="new_roof_bearing_on_retained_ceiling_edge"
   var entry:Dictionary={"part":row.name,"owner":path,"classification":classification};contacts.append(entry)
   if classification.is_empty():unexplained.append(entry)
 var door:Node3D=room.get_node("OrchardFood_staff_door");var initially_closed:bool=not door.desired_open and not capsule_clear(space,Vector3(49,61,-214));var legs:Array=[];player.global_position=Vector3(2,61.03,-176);player.velocity=Vector3.ZERO;player.set_physics_process(true);player.set_controls_enabled(true);await frames(20)
 for at:Vector3 in[Vector3(62,61,-176),Vector3(62,61,-214),Vector3(51.5,61,-214),Vector3(51.5,61,-228),Vector3(52.4,61,-228),Vector3(51.5,61,-228),Vector3(51.5,61,-222),Vector3(52.4,61,-222),Vector3(51.5,61,-222),Vector3(51.5,61,-209),Vector3(52.4,61,-209),Vector3(51.5,61,-209),Vector3(51.5,61,-214),Vector3(50.8,61,-214)]:
  legs.append(await walk_to(player,at))
  if not legs[-1].reached:break
 player.set_physics_process(false);player.global_position=Vector3(0,0,0);player.force_update_transform();await frames(3);door.interact(player);await frames(100);var opened:bool=door.desired_open and door.open_fraction>.99;player.global_position=Vector3(50.8,61.03,-214);player.velocity=Vector3.ZERO;player.set_physics_process(true);await frames(20)
 for at:Vector3 in[Vector3(47,61,-214),Vector3(50.8,61,-214),Vector3(62,61,-214),Vector3(62,61,-176),Vector3(2,61,-176)]:
  legs.append(await walk_to(player,at))
  if not legs[-1].reached:break
 player.set_physics_process(false);player.global_position=Vector3(0,0,0);player.force_update_transform();await frames(3);door.interact(player);await frames(100);var reclosed:bool=not door.desired_open and door.open_fraction<.01 and not capsule_clear(space,Vector3(49,61,-214));var stances:Array=[]
 for z in[-228.,-222.,-209.]:
  for x in[51.5,52.4]:
   var at:=Vector3(x,61.007,z);var hit:=ray(space,at+Vector3.UP*.03,at-Vector3.UP*.03);stances.append({"at":str(at),"clear":capsule_clear(space,at),"supported":not hit.is_empty()and absf(hit.position.y-61.007)<.003})
 var carts:Array=[];var wheels:Array=[];var cart:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/cleaning_cart_contacts.json"))
 for x in range(50,64):
  for yaw in[0.,PI/2]:
   var at:=Vector3(x,61.007,-214);carts.append({"at":str(at),"yaw":yaw,"clear":cart_clear(space,at,yaw)});var pose:=Transform3D(Basis(Vector3.UP,yaw),at+Vector3.UP*.005)
   for wheel in cart.wheel_contacts:
    var foot:Vector3=pose*vec(wheel.center)-Vector3.UP*float(wheel.radius);var h:=ray(space,foot+Vector3.UP*.03,foot-Vector3.UP*.03);wheels.append({"at":str(foot),"supported":not h.is_empty()and absf(h.position.y-61)<.012})
 var preserved:=true;var changed_names:Array=[]
 for mesh in before:
  if not is_instance_valid(mesh)or not mesh.global_transform.is_equal_approx(before[mesh].pose):preserved=false
  elif mesh.mesh!=before[mesh].mesh:changed_names.append(str(mesh.name))
 changed_names.sort();var expected:Array=plan.original_wall_names;expected.sort();preserved=preserved and changed_names==expected
 for n in old_doors:
  if not n.global_transform.is_equal_approx(old_doors[n].pose)or str(n.persistent_id)!=old_doors[n].id or n.desired_open!=old_doors[n].open:preserved=false
 var lights:Array=[];var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 for light:Light3D in group.find_children("*","Light3D",true,false):lights.append({"name":str(light.name),"registered_once":budget.sources.count(light)==1})
 var seats:int=room.find_children("OrchardChair_*","Node3D",false,false).size();var ok:bool=preimages.is_empty()and unexplained.is_empty()and floors.size()>100 and floors.all(func(a):return a.supported)and legs.size()==19 and legs.all(func(a):return a.reached and a.floor_contact)and initially_closed and opened and reclosed and stances.all(func(a):return a.clear and a.supported)and carts.all(func(a):return a.clear)and wheels.all(func(a):return a.supported)and preserved and seats==240 and lights.size()==8 and lights.all(func(a):return a.registered_once)
 FileAccess.open(D+"CANDIDATE_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS"if ok else"FAIL","new_floor_preimages":preimages,"new_floor_samples":floors,"source_contacts":contacts,"unexplained_contacts":unexplained,"original_controller_legs":legs,"fixture_stances":stances,"portal_cart_poses":carts,"wheel_floor_samples":wheels,"original_staff_door_initially_closed":initially_closed,"original_staff_door_opened":opened,"original_staff_door_reclosed":reclosed,"original_mesh_count":before.size(),"exact_changed_mesh_names":changed_names,"original_other_meshes_poses_doors_ids_preserved":preserved,"source_chairs":seats,"lights":lights,"operational_or_final_acceptance":false},"  "));print("PASS_ORCHARD_RECEIVING_CONNECTED_CURRENT_SHIP"if ok else"FAIL_ORCHARD_RECEIVING_CONNECTED_CURRENT_SHIP");quit(0 if ok else 1)
