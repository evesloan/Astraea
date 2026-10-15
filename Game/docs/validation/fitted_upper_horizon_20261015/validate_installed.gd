extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/fitted_upper_horizon_20261015/"
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(30);var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state;var districts:Node3D=ship.get_node("ShipSpace/Districts");var preserved:Dictionary={}
 for key in["AftCrownFoyerWaitingEdges","AftCrownSittingBays"]:
  var original:Node3D=districts.get_node(key)
  for mesh:MeshInstance3D in original.find_children("*","MeshInstance3D",true,false):preserved[mesh]={"pose":mesh.global_transform,"mesh":mesh.mesh}
 var group:Node3D=ship.get_node("ShipSpace/Districts/FittedUpperHorizon20261015");await frames(3);var excluded:Array[RID]=[]
 for body:CollisionObject3D in group.find_children("*","CollisionObject3D",true,false):excluded.append(body.get_rid())
 var document:=GLTFDocument.new();var state:=GLTFState.new();assert(document.append_from_file("/workspace/astraea-integration-cutoff-20261013/fitted_upper_horizon_20261015/FITTED_UPPER_HORIZON_r001_authoring.glb",state)==OK);var authored:Node3D=document.generate_scene(state);root.add_child(authored);authored.visible=false;assert(authored.find_children("*","CollisionObject3D",true,false).is_empty());var old:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/crown_interiors.json"));var records:Dictionary={}
 for row in old.meshes:
  if row.programme_key=="D18_directory_09":records[str(row.name).validate_node_name()]=row
 var contacts:Array=[];var feet:Array=[]
 for mesh:MeshInstance3D in authored.find_children("*","MeshInstance3D",true,false):
  assert(records.has(str(mesh.name)));var row:Dictionary=records[str(mesh.name)];var b:AABB=mesh.global_transform*mesh.get_aabb()
  if row.collide:
   var q:=PhysicsShapeQueryParameters3D.new();q.shape=mesh.mesh.create_convex_shape(true,false);q.shape.margin=0.;q.margin=0.;q.transform=mesh.global_transform;q.exclude=excluded;var paths:Array=[]
   for hit in space.intersect_shape(q,256):paths.append(str(hit.collider.get_path()))
   if not paths.is_empty():contacts.append({"part":str(mesh.name),"min":[b.position.x,b.position.y,b.position.z],"max":[b.end.x,b.end.y,b.end.z],"old_contacts":paths})
  if absf(b.position.y-106.5)<.003:
   var seen:Dictionary={}
   for vertex in mesh.mesh.get_faces():
    var point:Vector3=mesh.global_transform*vertex
    if absf(point.y-106.5)>.003:continue
    var key:String=str(roundi(point.x*10000))+"_"+str(roundi(point.z*10000))
    if seen.has(key):continue
    seen[key]=true;var ray_query:=PhysicsRayQueryParameters3D.create(point+Vector3.UP*.03,point-Vector3.UP*.03);ray_query.exclude=excluded;var hit:=space.intersect_ray(ray_query);feet.append({"part":str(mesh.name),"at":[point.x,point.y,point.z],"supported":not hit.is_empty()and absf(hit.position.y-106.5)<.003,"floor":str(hit.collider.get_path())if not hit.is_empty()else""})
 var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.global_position=Vector3(-16,106.53,140);player.velocity=Vector3.ZERO;player.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position);await frames(20);var goals:Array[Vector3]=[]
 for side in[-1.,1.]:
  for point:Vector3 in[Vector3(19,106.5,140),Vector3(28.5,106.5,139.5),Vector3(19,106.5,140),Vector3(19,106.5,143.8),Vector3(21.6,106.5,143.8),Vector3(24.4,106.5,143.8),Vector3(27.2,106.5,143.8),Vector3(19,106.5,143.8),Vector3(19,106.5,150.8),Vector3(25.5,106.5,150.8),Vector3(19,106.5,150.8),Vector3(16,106.5,145)]:goals.append(Vector3(side*point.x,point.y,point.z))
  if side<0:goals.append(Vector3(0,106.5,145));goals.append(Vector3(16,106.5,145));goals.append(Vector3(16,106.5,140))
 var legs:Array=[]
 for goal:Vector3 in goals:
  var leg:Dictionary=await walk_to(player,goal);legs.append(leg)
  if not leg.reached or not leg.floor_contact:break
 player.set_physics_process(false);player.global_position=Vector3(0,0,0);player.force_update_transform();await frames(2);var stances:Array=[]
 for side in[-1.,1.]:
  for point:Vector3 in[Vector3(28.5,106.5,139.5),Vector3(21.6,106.5,143.8),Vector3(24.4,106.5,143.8),Vector3(27.2,106.5,143.8),Vector3(25.5,106.5,150.8)]:
   var at:=Vector3(side*point.x,point.y,point.z);var h:=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02);stances.append({"at":str(at),"capsule_clear":capsule_clear(space,at),"floor":not h.is_empty()and absf(h.position.y-106.5)<.003})
 var originals_unchanged:=true
 for mesh in preserved:
  if not mesh.global_transform.is_equal_approx(preserved[mesh].pose)or mesh.mesh!=preserved[mesh].mesh:originals_unchanged=false
 var lights:Array=[];var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 for light:Light3D in group.find_children("*","Light3D",true,false):lights.append({"name":str(light.name),"registered_once":budget.sources.count(light)==1})
 var ok:bool=group.get_meta("default_main_adoption")and feet.size()>20 and feet.all(func(a):return a.supported)and legs.size()==goals.size()and legs.all(func(a):return a.reached and a.floor_contact)and stances.all(func(a):return a.capsule_clear and a.floor)and originals_unchanged and lights.size()==2 and lights.all(func(a):return a.registered_once)
 FileAccess.open(D+"INSTALLED_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS"if ok else"FAIL","authoring_meshes":320,"runtime_batches":70,"old_contact_inventory":contacts,"retained_floor_foot_pins":feet,"actual_controller_legs":legs,"required_controller_legs":goals.size(),"work_stances":stances,"original_foyer_sitting_mesh_count":preserved.size(),"original_foyer_sitting_poses_resources_unchanged":originals_unchanged,"light_registration":lights,"new_floor_room_ids_or_capacity":0,"species_occupied_use_stock_pressure_save_or_final_art_accepted":false},"  "));authored.queue_free();print("PASS_FITTED_HORIZON_CURRENT_SHIP"if ok else"FAIL_FITTED_HORIZON_CURRENT_SHIP");quit(0 if ok else 1)
