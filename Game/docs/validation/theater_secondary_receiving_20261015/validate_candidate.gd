extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/theater_secondary_receiving_20261015/"
var count:=0
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip",D+"CANDIDATE_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func require(ok:bool,label:String)->bool:
 count+=1
 if not ok:push_error(label);quit(1)
 return ok
func at_contact(space:PhysicsDirectSpaceState3D,point:Vector3,needle:String)->bool:
 for axis:Vector3 in[Vector3.RIGHT,Vector3.UP,Vector3.FORWARD]:
  for sign_value in[-1.,1.]:
   var q:=PhysicsRayQueryParameters3D.create(point-axis*.24*sign_value,point+axis*.24*sign_value)
   for i in range(20):
    var hit:Dictionary=space.intersect_ray(q)
    if hit.is_empty():break
    if str(hit.collider.get_path()).contains(needle):return true
    var ex:Array[RID]=q.exclude;ex.append(hit.collider.get_rid());q.exclude=ex
 return false
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(30)
 var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state;var venue:Node3D=ship.get_node("ShipSpace/Districts/GrandLanternTheater_ConnectedStaticStage_WIP");var motion:Node3D=venue.get_node("TheaterUnpoweredDoorLiftAssemblies");var door_poses:Dictionary={}
 for door:Node3D in motion.get_children():
  if door.has_meta("operation_enabled")and not door.get_meta("operation_enabled"):door_poses[door]=door.transform
 var witnesses:Array=[]
 for y in[69.5,78.,84.]:
  for x in[-33.,-30.,-25.,-20.,-15.,-10.,-4.5]:
   for z in[-173.8,-172.7,-171.7,-170.3,-169.6]:
    var point:=Vector3(x,y,z);witnesses.append(point)
    if not require(ray(space,point+Vector3.UP*.01,point-Vector3.UP*.01).is_empty(),"Missing-only source floor preimage "+str(point)):return
 var before:int=ship.get_node("ShipSystems/LocalShadowSourceBudget").sources.size();var package:Node3D=load("res://scripts/theater_secondary_receiving_20261015/package.gd").build(ship);await frames(4)
 for point:Vector3 in witnesses:
  var hit:Dictionary=ray(space,point+Vector3.UP*.01,point-Vector3.UP*.01)
  if not require(not hit.is_empty()and package.is_ancestor_of(hit.collider)and absf(hit.position.y-point.y)<.002,"Actual new floor "+str(point)):return
 var joined:=0
 for y in[69.5,78.,84.]:
  for x in[-35.3,-3.9]:
   for z in([-172.5,-171.,-169.5]if x==-35.3 else[-173.5,-171.7,-169.9]):
    var point:=Vector3(x,y-.11,z)
    if not require(at_contact(space,point,"/TheaterSecondaryReceiving20261015/"),"Actual new floor/lap join "+str(point)):return
    var needle:String="/CompiledStructuralFloors_NotFinishedRooms/"if x==-3.9 or y==69.5 else"/TheaterSourceArchitecture/"
    if not require(at_contact(space,point,needle),"Actual retained receiving contact "+str(point)):return
    joined+=1
 var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");var stream:Node=ship.get_node("ShipSystems/RemainingBatchStreaming");var legs:Array=[]
 for y in[69.5,78.,84.]:
  actor.global_position=Vector3(0,y+.03,-171.7);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);residency.prepare_position(actor.global_position);stream.prepare_position(actor.global_position);await frames(25)
  if not require(actor.is_on_floor(),"Original axial route start "+str(y)):return
  for x in[-3.2,-6.,-15.,-25.,-33.,-25.,-15.,-6.,-3.2,0.]:
   var leg:Dictionary=await walk_to(actor,Vector3(x,y,-171.7));legs.append({"y":y,"leg":leg})
   if not require(leg.reached and leg.floor_contact,"Original controller secondary exterior approach "+str([x,y])):return
 for node in door_poses:
  if not require(node.transform==door_poses[node]and not node.get_meta("operation_enabled"),"Source held doors remain unchanged"):return
 if not require(ship.get_node("ShipSystems/LocalShadowSourceBudget").sources.size()==before+9,"Exactly9 retained coffer lights registered once"):return
 FileAccess.open(D+"CANDIDATE_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_THREE_SECONDARY_THEATER_RECEIVING_CANDIDATE","checks":count,"floor_samples":witnesses.size(),"actual_end_receiving_contacts":joined,"legs":legs,"doors_operating":false,"capacity_or_primary_beam_load_accepted":false,"whole_build_complete":false},"  "));print("PASS_SECONDARY_THEATER_RECEIVING checks=",count);quit(0)
