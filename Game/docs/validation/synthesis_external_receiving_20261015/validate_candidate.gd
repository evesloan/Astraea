extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/synthesis_external_receiving_20261015/"
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/DINING_SERVICE_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ORCHARD_RECEIVING_ADOPTION_OVERLAY.zip",D+"CANDIDATE_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func volume(space:PhysicsDirectSpaceState3D,lo:Vector3,hi:Vector3,exclude:Array[RID])->Array:
 var shape:=BoxShape3D.new();shape.size=hi-lo;shape.margin=0.;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.margin=0.;q.transform.origin=(lo+hi)/2;q.exclude=exclude;var out:Array=[]
 for hit in space.intersect_shape(q,512):out.append(str(hit.collider.get_path()))
 return out
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(90);var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.set_physics_process(false);player.global_position=Vector3(0,12,0);var space:=ship.get_world_3d().direct_space_state;var room:Node3D=ship.get_node("ShipSpace/Districts/Group8SynthesisPlant_Candidate");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/synthesis_external_receiving_20261015/NATIVE_VERIFICATION.json"));var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"NATIVE_PLAN.json"));var before:Dictionary={};var old_doors:Dictionary={}
 for mesh:MeshInstance3D in room.find_children("*","MeshInstance3D",true,false):before[mesh]={"pose":mesh.global_transform,"mesh":mesh.mesh}
 for n:Node3D in room.find_children("Synthesis*Door","Node3D",true,false):old_doors[n]={"pose":n.global_transform,"id":str(n.persistent_id),"open":n.desired_open}
 var group:Node3D=load("res://scripts/synthesis_external_receiving_20261015/package.gd").build(ship);await frames(3);var exclude:Array[RID]=[]
 for body:CollisionObject3D in group.find_children("*","CollisionObject3D",true,false):exclude.append(body.get_rid())
 var preimages:Array=[];var floors:Array=[]
 for link in plan.links:
  var rect:Array=link.rect;var x:float=rect[0]+.35
  while x<float(rect[1])-.25:
   var z:float=rect[2]+.35
   while z<float(rect[3])-.25:
    var at:=Vector3(x,0,z);var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.03,at-Vector3.UP*.03);q.exclude=exclude;var old:=space.intersect_ray(q)
    if not old.is_empty():preimages.append({"at":str(at),"owner":str(old.collider.get_path())})
    var h:=ray(space,at+Vector3.UP*.03,at-Vector3.UP*.03);floors.append({"at":str(at),"supported":not h.is_empty()and absf(h.position.y)<.003});z+=1.5
   x+=1.5
 var contacts:Array=[];var unexplained:Array=[]
 for row in p.bounds:
  if "Lens"in str(row.name):continue
  var paths:Array=volume(space,vec(row.min),vec(row.max),exclude)
  for path in paths:
   var classification:=""
   if "/G8S_BATCH_0185_D01_directory_05/"in path or"/G8S_BATCH_0187_D01_directory_05/"in path:classification="positive_bearing_on_exact_retained_plant_enclosure_edge"
   elif "/Group1SynthesisSupportingFloor/"in path or"/D01_port_service_spine/"in path:classification="embedded_tie_or_edge_bearing_on_exact_retained_supporting_floor"
   var entry:Dictionary={"part":row.name,"owner":path,"classification":classification};contacts.append(entry)
   if classification.is_empty():unexplained.append(entry)
 var legs:Array=[];var stances:Array=[];var carts:Array=[];var wheels:Array=[];var cart:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/cleaning_cart_contacts.json"))
 for link in plan.links:
  var z:float=link.z;var front:float=signf(z)*25.5;player.global_position=Vector3(-46,.03,z);player.velocity=Vector3.ZERO;player.set_physics_process(true);player.set_controls_enabled(true);await frames(20)
  for at:Vector3 in[Vector3(-61.8,0,z),Vector3(-61.8,0,front),Vector3(-64.8,0,front),Vector3(-61.8,0,front),Vector3(-61.8,0,z),Vector3(-46,0,z)]:
   var leg:Dictionary=await walk_to(player,at);leg["receiving_kind"]=link.kind;legs.append(leg)
   if not leg.reached:break
  player.set_physics_process(false);player.global_position=Vector3(0,12,0);player.force_update_transform();await frames(3)
  for x in[-65.8,-64.8,-63.8]:
   var at:=Vector3(x,0,front);var h:=ray(space,at+Vector3.UP*.03,at-Vector3.UP*.03);stances.append({"at":str(at),"clear":capsule_clear(space,at),"supported":not h.is_empty()and absf(h.position.y)<.003})
  for x in range(-61,-45):
   for yaw in[0.,PI/2]:
    var at:=Vector3(x,0,z);carts.append({"at":str(at),"yaw":yaw,"clear":cart_clear(space,at,yaw)});var pose:=Transform3D(Basis(Vector3.UP,yaw),at+Vector3.UP*.005)
    for wheel in cart.wheel_contacts:
     var foot:Vector3=pose*vec(wheel.center)-Vector3.UP*float(wheel.radius);var h:=ray(space,foot+Vector3.UP*.03,foot-Vector3.UP*.03);wheels.append({"at":str(foot),"supported":not h.is_empty()and absf(h.position.y)<.003})
 var preserved:=true;var changed:Array=[]
 for mesh in before:
  if not is_instance_valid(mesh)or not mesh.global_transform.is_equal_approx(before[mesh].pose):preserved=false
  elif mesh.mesh!=before[mesh].mesh:changed.append(str(mesh.name))
 changed.sort();var expected:Array=plan.original_wall_names;expected.sort();preserved=preserved and changed==expected
 for n in old_doors:
  if not n.global_transform.is_equal_approx(old_doors[n].pose)or str(n.persistent_id)!=old_doors[n].id or n.desired_open!=old_doors[n].open:preserved=false
 var lights:Array=[];var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 for light:Light3D in group.find_children("*","Light3D",true,false):lights.append({"name":str(light.name),"registered_once":budget.sources.count(light)==1})
 var ok:bool=preimages.is_empty()and unexplained.is_empty()and floors.size()>20 and floors.all(func(a):return a.supported)and legs.size()==12 and legs.all(func(a):return a.reached and a.floor_contact)and stances.all(func(a):return a.clear and a.supported)and carts.all(func(a):return a.clear)and wheels.all(func(a):return a.supported)and preserved and old_doors.size()==2 and lights.size()==4 and lights.all(func(a):return a.registered_once)
 FileAccess.open(D+"CANDIDATE_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS"if ok else"FAIL","new_floor_preimages":preimages,"new_floor_samples":floors,"source_contacts":contacts,"unexplained_contacts":unexplained,"original_controller_legs":legs,"fixture_stances":stances,"portal_cart_poses":carts,"wheel_floor_samples":wheels,"original_mesh_count":before.size(),"exact_changed_mesh_names":changed,"original_other_meshes_poses_doors_ids_preserved":preserved,"original_plant_doors":old_doors.size(),"lights":lights,"operational_or_final_acceptance":false},"  "));print("PASS_SEPARATE_SYNTHESIS_EXTERNAL_RECEIVING"if ok else"FAIL_SEPARATE_SYNTHESIS_EXTERNAL_RECEIVING");quit(0 if ok else 1)
