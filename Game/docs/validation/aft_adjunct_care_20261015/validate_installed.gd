extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/approved_combined_receivers_20261014/aft_adjunct_care/"
var count:=0
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func require(ok:bool,label:String)->bool:
 count+=1
 if not ok:push_error(label);quit(1)
 return ok
func frames(n:int)->void:
 for i in range(n):await physics_frame
func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(30)
 var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"SOURCE_STAGE.json"));var supported:=0
 for row in data.rows:
  var boundary:Array=row.boundary;var lo:Vector2=Vector2(boundary[0][0],boundary[0][1]);var hi:=lo
  for point in boundary:lo=lo.min(Vector2(point[0],point[1]));hi=hi.max(Vector2(point[0],point[1]))
  for x in range(int(lo.x)+1,int(hi.x),2):
   for z in range(int(lo.y)+1,int(hi.y),2):
    var hit:Dictionary=ray(space,Vector3(x,102.01,z),Vector3(x,101.99,z))
    if not require(not hit.is_empty()and str(hit.collider.get_path()).contains("/ApprovedSixHouseReceiving/")and absf(hit.position.y-102)<.002,"Exact installed source floor "+row.key+" "+str([x,z])):return
    supported+=1
 var fitted:Node3D=ship.get_node("ShipSpace/AftRetainedAdjunctCare");await frames(3)
 if not require(fitted.get_meta("default_main_adoption"),"Aft source pairs present by default"):return
 var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var results:Array=[];var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 for row in data.rows:
  var section:Node3D=fitted.get_node("Group2_"+str(row.key))
  if not require(section.get_node("RetainedSource").find_child("CareStoneSurface",true,false)!=null,"Exact source care counter "+row.key):return
  for light:Light3D in section.find_children("*","Light3D",true,false):
   if not require(budget.sources.count(light)==1,"Source light registered once "+row.key):return
  for view in row.source_views:
   var point:Vector3=v(view.camera_world_xyz)-Vector3.UP*float(view.height_above_local_floor)
   if not require(capsule_clear(space,point),"Exact source view standing capsule clear "+row.key+":"+view.name):return
  var start:Vector3=v(row.source_views[0].camera_world_xyz)-Vector3.UP*float(row.source_views[0].height_above_local_floor)
  actor.global_position=start+Vector3.UP*.03;actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);await frames(20)
  var inward:Vector3=v(row.source_views[0].target_world_xyz)-start;inward.y=0;var goal:Vector3=start+inward.normalized()*.8;var leg:Dictionary=await walk_to(actor,goal)
  if not require(leg.reached and leg.floor_contact,"Original controller source arrival "+row.key):return
  results.append({"key":row.key,"leg":leg})
 FileAccess.open(D+"INSTALLED_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_AFT_SOURCE_ADJUNCT_CARE_DEFAULT_INSTALLED","checks":count,"floor_witnesses":supported,"adjuncts":2,"care_kits":2,"legs":results,"whole_build_complete":false},"  "))
 print("PASS_AFT_SOURCE_ADJUNCT_CARE checks=",count);quit(0)
