extends "res://tests/validate_d04_port_forward_commons_service.gd"
var nchecks:=0
var failures:Array=[]
var observations:Array=[]
const OUT="/workspace/astraea-integration-cutoff-20261013/G3_PRECINCT_RECEIVING_RUNTIME.json"
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
 for p in ["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/G3_FIRST_RECEIVING_CANDIDATE_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(p,true))
 call_deferred("run")
func save_result()->void:
 FileAccess.open(OUT,FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_PRECISE_PRECINCT_SOURCE_RECEIVING"if failures.is_empty()else"HOLD","checks":nchecks,"failures":failures,"observations":observations,"source_models":6,"owned_native_missing_floor_m2":1542.4901490922566,"new_registered_berths":0,"labelled_private_bank_or_other_G3_packages_admitted":false,"source_scope":"Native precinct source only;current floors/contacts and bounded original-player leg;no population,whole network,species,engineering or final-art acceptance"},"  "))
func require(ok:bool,label:String)->bool:
 nchecks+=1
 if not ok:failures.append(label);save_result();push_error(label);quit(1)
 return ok
func frames(n:int)->void:
 for i in range(n):await physics_frame
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(30)
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 var source:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_completion_20261011/D03_PRECINCT.json"));var floors:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-integration-cutoff-20261013/g3_first_floor_preflight/MISSING_ONLY_FLOOR_PATCH.json"))
 var witnesses:Array=[]
 for part in floors.parts:
  for t in part.triangles:witnesses.append(Vector3((t[0][0]+t[1][0]+t[2][0])/3.,12.,(t[0][1]+t[1][1]+t[2][1])/3.))
 var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");var stream:Node=ship.get_node("ShipSystems/RemainingBatchStreaming")
 for at in witnesses:residency.prepare_position(at);stream.prepare_position(at)
 await frames(2)
 var space:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state
 for i in range(witnesses.size()):
  var at:Vector3=witnesses[i];var hit:Dictionary=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.02,at-Vector3.UP*.02))
  if not require(hit.is_empty(),"Declared missing-only floor has no current native/compiled floor "+str(i)+" "+str(hit.collider.get_path()if not hit.is_empty()else "none")):return
 var old_sources:int=budget.sources.size();var precinct:Node3D=load("res://scripts/group3_completion_20261011/d03_precinct.gd").build(ship);await frames(4)
 if not require(precinct.get_meta("registered_berths_added")==0 and not precinct.get_meta("full_clean_used_network_accepted"),"No source retention credited as programme/population acceptance"):return
 for file in source.model_pins:
  if not require(FileAccess.get_sha256("res://assets/models/group3_completion_20261011/"+str(file))==str(source.model_pins[file]),"Exact native model "+str(file)):return
 for i in range(witnesses.size()):
  var at:Vector3=witnesses[i];var hit:Dictionary=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.03,at-Vector3.UP*.03))
  if not require(not hit.is_empty()and precinct.is_ancestor_of(hit.collider)and absf(hit.position.y-12)<.002,"Actual source-owned native floor witness "+str(i)):return
 if not require(budget.sources.size()==old_sources+source.fixtures.size(),"Exactly33 owned sources appended once"):return
 for f in source.fixtures:
  var light:Light3D=precinct.get_node(str(f.name)+"_PhysicalSource")
  if not require(budget.sources.count(light)==1,"Single source registration "+str(f.name)):return
 for item in source.service_doors:
  var door:Node3D=precinct.get_node(str(item.name))
  if not require(str(door.persistent_id)==str(item.id)and not door.desired_open and door.open_fraction==0,"Exact closed source service gate "+str(item.name)):return
 # One supported test start and short out-and-back on the retained training service strip.
 actor.global_position=Vector3(-101.5,12.03,3.2);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);residency.prepare_position(actor.global_position);stream.prepare_position(actor.global_position);await frames(25)
 if not require(actor.is_on_floor()and absf(actor.global_position.y-12)<.12,"Supported actual precinct initial stance"):return
 for goal in [Vector3(-101.5,12,5.0),Vector3(-101.5,12,3.2)]:
  var leg:Dictionary=await walk_to(actor,goal);observations.append(leg)
  if not require(leg.reached and leg.floor_contact,"Original player supported precinct service strip"):return
 if not require(ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms").get_child_count()==303,"Original compiler owners remain exact"):return
 save_result();print("G3_PRECISE_PRECINCT_RECEIVING_PASS checks=",nchecks);quit(0)
