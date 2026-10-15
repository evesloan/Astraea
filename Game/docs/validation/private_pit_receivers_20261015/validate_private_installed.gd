extends "res://tests/validate_d04_port_forward_commons_service.gd"
const P="/workspace/astraea-integration-cutoff-20261013/approved_combined_receivers_20261014/private_pit_receivers/"
var count:=0
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func require(ok:bool,label:String)->bool:
 count+=1
 if not ok:push_error(label);quit(1)
 return ok
func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func find_contact(space:PhysicsDirectSpaceState3D,point:Vector3,needle:String)->bool:
 for direction:Vector3 in[Vector3.RIGHT,Vector3.UP,Vector3.FORWARD]:
  for sign_value in[-1.,1.]:
   var q:=PhysicsRayQueryParameters3D.create(point+direction*.24*sign_value,point-direction*.24*sign_value)
   for attempt in range(16):
    var hit:Dictionary=space.intersect_ray(q)
    if hit.is_empty():break
    if str(hit.collider.get_path()).contains(needle):return true
    var excludes:Array[RID]=q.exclude;excludes.append(hit.collider.get_rid());q.exclude=excludes
 return false
func relative_pose(node:Node3D,model:Node3D)->Transform3D:
 var pose:Transform3D=node.transform;var parent:Node3D=node.get_parent()
 while parent!=model:pose=parent.transform*pose;parent=parent.get_parent()
 return model.transform*pose
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(30)
 var ship:Node3D=main.get_node("World360/Astraea");var manager:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");var space:=ship.get_world_3d().direct_space_state
 if not require(ship.get_node("ShipSpace/PrivatePitReceivingFrames").get_meta("default_main_adoption"),"Private receivers fitted by default"):return
 var rooms:Dictionary={}
 for entry in manager.entries:
  if entry.room.has_meta("retained_group2_home"):rooms[str(entry.room.get_meta("group2_source_key"))]=entry.room
 if not require(rooms.size()==80,"All80 source homes registered after private physical dependencies"):return
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"EXACT_PIT_RECEIVER_PLAN.json"));var floor_samples:=0;var joins:=0
 for suite in plan.suites:
  var centroid:=Vector3.ZERO
  for point in suite.floor_outline_xz:centroid+=Vector3(point[0],suite.floor_top_y,point[1])/4.
  var hit:Dictionary=ray(space,centroid+Vector3.UP*.02,centroid-Vector3.UP*.02)
  if not require(not hit.is_empty()and absf(hit.position.y-suite.floor_top_y)<.002 and str(hit.collider.get_path()).contains("RetainedPitReceiver_"+str(suite.key)),"Exact retained pit slab contact "+str(suite.key)):return
  floor_samples+=1
  for witness in suite.installed_rim_connection_witnesses:
   var point:Vector3=v(witness.surface_station)
   if not require(find_contact(space,point,"/ApprovedSixHouseReceiving/"),"Actual existing rim frame atnew carrier join "+str(suite.key)):return
   if not require(find_contact(space,point,"/PrivatePitReceivingFrames/NewUnderfloorCarriers/"),"Actual new carrier reaches installed rim "+str(suite.key)):return
   joins+=1
 var source_data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/received_homes_20261015/HOMES.json"));var homes:Dictionary={}
 for row in source_data.homes:homes[str(row.key)]=row
 var patches:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_pit_perimeters/PLAN_r003.json"));var results:Array=[];var poses:=0
 var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 for key in["787","792","794","795","797"]:
  var room:Node3D=rooms[key];manager.prepare_position(v(homes[key].source_arrival_stance_world));await frames(3)
  var section:Node3D=room.get_meta("resident_visual");var visual:Node3D=section.get_node("RetainedSource");var lift:Node3D=section.get_node("PrivateVertical_"+key)
  if not require(section.get_meta("private_pit_and_perimeter_fitted")and section.has_node("FullPitPerimeter_"+key),"Private scene and full perimeter physically fitted "+key):return
  if not require(not lift.operation_ready and lift.phase=="held_receivers_and_private_access"and not lift.get_meta("production_identity_adopted"),"Original private operating and identity holds preserved "+key):return
  if not require(lift.landing_gates.size()==2 and not lift.cabin_gate.cabin_present_and_stopped,"Two landing gates and one held cabin gate "+key):return
  var before:Vector3=lift.cabin.global_position;await frames(15)
  if not require(lift.cabin.global_position.distance_to(before)<.001,"Parked source cabin remains stationary "+key):return
  var row:Dictionary={}
  for candidate in patches.suites:
   if str(int(candidate.source_index))==key:row=candidate
  var original:Node3D=(load("res://assets/group2_completion/"+key+".glb")as PackedScene).instantiate()
  for name in row.furniture_pose_patch.exact_mesh_names:
   var node_name:String=str(name).validate_node_name();var current:Node3D=visual.find_child(node_name,true,false);var prior:Node3D=original.find_child(node_name,true,false)
   if not require(current!=null and prior!=null,"Exact source pose target "+key+":"+node_name):original.free();return
   var expected:Transform3D=relative_pose(prior,original);var delta:Array=row.furniture_pose_patch.per_mesh_world_delta.get(node_name,[0,.45,0]);expected.origin+=v(delta)
   if not require(current.global_transform.origin.distance_to(expected.origin)<.002 and current.global_basis.is_equal_approx(expected.basis),"Exact retained furniture translation "+key+":"+node_name):original.free();return
   poses+=1
  original.free()
  for light:Light3D in section.find_children("*","Light3D",true,false):
   if not require(budget.sources.count(light)==1,"Every source/private cabin fixture registered once "+key):return
  var start:Vector3=v(homes[key].source_arrival_stance_world)
  if not require(capsule_clear(space,start),"Private source arrival stance clear "+key):return
  actor.global_position=start+Vector3.UP*.03;actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);await frames(20)
  var contract:Dictionary=section.get_meta("source_contract");var fitting:Dictionary={}
  for item in contract.imports:
   if item.catalogue_id=="AST-DOR-002":fitting=item;break
  var inward:Vector3=(start-v(fitting.world_xyz)).normalized();var goal:Vector3=start+inward*.8;goal.y=102
  var leg:Dictionary=await walk_to(actor,goal)
  if not require(leg.reached and leg.floor_contact,"Original controller private source arrival "+key):return
  results.append({"key":key,"pose_targets":row.furniture_pose_patch.exact_mesh_names.size(),"cabin_stationary":true,"operation_ready":false,"leg":leg})
 FileAccess.open(P+"PRIVATE_INSTALLED_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_ALL80_PRIVATE_PIT_AND_PERIMETER_DEFAULT_INSTALLED","checks":count,"registered_homes":80,"private_cabins":5,"held_gates":15,"retained_pit_floor_samples":floor_samples,"actual_rim_carrier_joins":joins,"exact_furniture_pose_targets":poses,"original_controller_legs":results,"capacity_or_operational_admission":false,"whole_build_accepted":false},"  "))
 print("PASS_PRIVATE_PIT_CANDIDATE checks=",count);quit(0)
