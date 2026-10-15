extends "res://tests/validate_d04_port_forward_commons_service.gd"
const P="/workspace/astraea-integration-cutoff-20261013/approved_combined_receivers_20261014/home_installation/"
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
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(30)
 var ship:Node3D=main.get_node("World360/Astraea");var manager:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");var group:Node3D=ship.get_node("ShipSpace/Districts/ApprovedGroup2Homes")
 if not require(group.get_meta("default_main_adoption"),"Source homes included by default"):return
 var rooms:Dictionary={}
 for entry in manager.entries:
  if entry.room.has_meta("retained_group2_home"):rooms[str(entry.room.get_meta("group2_source_key"))]=entry.room
 if not require(rooms.size()==75 and group.get_meta("source_homes_registered")==75,"75 source homes registered with ordinary residency"):return
 for key in["787","792","794","795","797"]:
  if not require(not rooms.has(key),"Multilevel dependency gate retained "+key):return
 var manifest:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/received_homes_20261015/HOMES.json"));var by_key:Dictionary={}
 for row in manifest.homes:
  by_key[str(row.key)]=row
  if row.selected_for_first_source_home_package:
   if not require(FileAccess.get_sha256("res://assets/group2_completion/"+str(row.key)+".glb")==str(row.source_sha256),"Exact immutable model "+str(row.key)):return
 if not require(FileAccess.get_sha256("res://scripts/received_room_residency.gd")=="98a86d0de5209bb1bfa55dcd3bcfb9a344a14f03e7a16d5e7e9360ce761a1074","Original residency implementation preserved"):return
 var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget");var results:Array=[]
 for key in["876","879","829","832","878","875"]:
  var row:Dictionary=by_key[key];var room:Node3D=rooms[key];manager.prepare_position(v(row.entry_world));await frames(3)
  if not require(room.is_inside_tree()and room.has_meta("resident_visual"),"Normal arrival prepares source home "+key):return
  var section:Node3D=room.get_meta("resident_visual");var visual:Node3D=section.get_node("RetainedSource")
  if not require(visual.find_children("*","MeshInstance3D",true,false).size()>0 and section.get_meta("capacity_migrated")==false,"Real source geometry present without capacity migration "+key):return
  if not require(section.get_meta("fixture_registration_count")==1,"Source fixture registration once "+key):return
  var sources:Array=section.find_children("*","Light3D",true,false)
  for light:Light3D in sources:
   if light.get_meta("group2_fixture",false):
    if not require(budget.sources.count(light)==1,"Bounded source light registered once "+key):return
  var doors:Array=[]
  for node in section.get_children():
   if node.get_script()==load("res://scripts/group2_completion/fitted_entry.gd"):
    var fraction:float=node.open_fraction;node.interact(actor)
    if not require(node.access_refused and not node.desired_open and node.open_fraction==fraction,"Source entry retains positive consent hold "+key):return
    doors.append({"id":str(node.persistent_id),"fraction":fraction})
  if not require(not doors.is_empty(),"Exact source entry controller fitted "+key):return
  var start:Vector3=v(row.source_arrival_stance_world);var space:=ship.get_world_3d().direct_space_state
  if not require(capsule_clear(space,start),"Source entry clear for original controller "+key):return
  actor.global_position=start+Vector3.UP*.03;actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);await frames(20)
  var contract:Dictionary=section.get_meta("source_contract");var entry_fitting:Dictionary={}
  for fitting in contract.imports:
   if fitting.catalogue_id=="AST-DOR-002":entry_fitting=fitting;break
  var inward:Vector3=(start-v(entry_fitting.world_xyz)).normalized();var goal:Vector3=start+inward*1.1;goal.y=102
  var leg:Dictionary=await walk_to(actor,goal)
  if not require(leg.reached and leg.floor_contact,"Original controller source entry approach "+key):return
  var old_id:int=section.get_instance_id();var registrations:int=budget.sources.size()
  load("res://scripts/received_homes_20261015/source_dispatch.gd").release(room)
  load("res://scripts/received_homes_20261015/source_dispatch.gd").ensure(room);await frames(2)
  if not require(room.get_meta("resident_visual").get_instance_id()==old_id and budget.sources.size()==registrations,"Source section identity and registrations survive residency cycle "+key):return
  results.append({"key":key,"source_mesh_nodes":row.mesh_nodes,"entry_doors":doors,"source_lights":sources.size(),"leg":leg,"same_source_section_after_cycle":true})
 if not require(budget.shadow_source_budget==8 and budget.MAX_VISIBILITY_CANDIDATES==32,"Original global lighting budgets retained"):return
 if not require(ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms").get_child_count()==303,"Original floor ownership retained"):return
 FileAccess.open(P+"HOME_INSTALLED_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_SIX_DISTRICT_DEFAULT_RETAINED_HOMES","checks":count,"registered_homes":75,"private_multilevel_held":5,"district_cases":results,"original_controller_legs":results.size(),"source_residency_original_unchanged":true,"capacity_registry_or_private_admission_credit":false,"full_build_or_final_visual_accepted":false},"  "))
 print("PASS_SIX_DISTRICT_SOURCE_HOMES checks=",count);quit(0)
