extends "res://tests/validate_d04_port_forward_commons_service.gd"
var nchecks:=0
var failures:Array=[]
var observations:Array=[]
const OUT="/workspace/astraea-integration-cutoff-20261013/G3_LABELLED_BANK_RECEIVING_RUNTIME.json"
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
 for p in ["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/G3_LABELLED_BANK_CANDIDATE_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(p,true))
 call_deferred("run")
func save_result()->void:
 FileAccess.open(OUT,FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_EXACT_LABELLED_BANK_PHYSICAL_RECEIVING"if failures.is_empty()else"HOLD","checks":nchecks,"failures":failures,"observations":observations,"models":3,"native_missing_floor_m2":2589.124004486059,"unassigned_rest_surfaces":32,"new_registered_berths":0,"private_external_admission":false,"source_scope":"Physical source receiving only;unknown external permission refused;inside egress API preserved. No person/berth/save/species/migration/full network/final-art acceptance."},"  "))
func require(ok:bool,label:String)->bool:
 nchecks+=1
 if not ok:failures.append(label);save_result();push_error(label);quit(1)
 return ok
func frames(n:int)->void:
 for i in range(n):await physics_frame
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(30)
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 var source:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_completion_20261011/LABELLED_BANK.json"));var floors:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-integration-cutoff-20261013/g3_first_floor_preflight/BANK_MISSING_ONLY_FLOOR.json"))
 var witnesses:Array=[]
 for part in floors.parts:
  for t in part.triangles:witnesses.append(Vector3((t[0][0]+t[1][0]+t[2][0])/3.,12.,(t[0][1]+t[1][1]+t[2][1])/3.))
 var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");var stream:Node=ship.get_node("ShipSystems/RemainingBatchStreaming")
 for at in witnesses:residency.prepare_position(at);stream.prepare_position(at)
 await frames(2)
 var space:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state
 for i in range(witnesses.size()):
  var at:Vector3=witnesses[i];var hit:Dictionary=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.02,at-Vector3.UP*.02))
  if not require(hit.is_empty(),"Bank missing floor preimage "+str(i)+" "+str(hit.collider.get_path()if not hit.is_empty()else "none")):return
 var old_sources:int=budget.sources.size();var bank:Node3D=load("res://scripts/group3_completion_20261011/labelled_bank.gd").build(ship);await frames(4)
 if not require(bank.get_meta("registered_berths_added")==0 and not bank.get_meta("private_entry_admitted")and not bank.get_meta("C036_migration_applied"),"No invented private admission or capacity"):return
 for file in source.model_pins:
  if not require(FileAccess.get_sha256("res://assets/models/group3_completion_20261011/"+str(file))==str(source.model_pins[file]),"Exact bank native source "+str(file)):return
 for i in range(witnesses.size()):
  var at:Vector3=witnesses[i];var hit:Dictionary=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.03,at-Vector3.UP*.03))
  if not require(not hit.is_empty()and bank.is_ancestor_of(hit.collider)and absf(hit.position.y-12)<.002,"Supported bank floor witness "+str(i)):return
 if not require(budget.sources.size()==old_sources+source.fixtures.size(),"Exact48 bank sources appended once"):return
 for q in source.fixtures:
  if not require(budget.sources.count(bank.get_node(str(q.name)+"_PhysicalSource"))==1,"Single bank source "+str(q.name)):return
 for q in source.service_doors:
  var door:Node3D=bank.get_node(str(q.name));actor.global_position=door.to_global(Vector3(0,.03,-2.2));actor.velocity=Vector3.ZERO;residency.prepare_position(actor.global_position);stream.prepare_position(actor.global_position);await frames(20)
  if not require(actor.is_on_floor()and absf(actor.global_position.y-12)<.12,"Actual supported external bank gate stance "+str(q.name)):return
  if not require(str(door.persistent_id)==str(q.id)and not door.desired_open and door.open_fraction==0 and door.to_local(actor.global_position).z<-.25,"Exact closed identity and source street orientation "+str(q.name)):return
  door.interact(actor);await frames(3)
  if not require(door.authorization_denied and not door.desired_open and door.open_fraction==0,"Unknown outside admission physically refused "+str(q.name)):return
 # One disclosed independent actor setup inside first native room;preserves ordinary door backend API and egress.
 var door:Node3D=bank.get_node(str(source.service_doors[0].name));actor.global_position=door.to_global(Vector3(0,.03,2.2));actor.velocity=Vector3.ZERO;await frames(25)
 if not require(actor.is_on_floor()and absf(actor.global_position.y-12)<.12,"Actual supported inside bank egress stance"):return
 door.interact(actor);await frames(80)
 if not require(not door.authorization_denied and door.desired_open and door.open_fraction>.99,"Original backend permits supported inside egress"):return
 door.interact(actor);await frames(80)
 if not require(not door.desired_open and door.open_fraction<.001,"Original door returns to closed private state"):return
 actor.global_position=Vector3(87,12.03,-132);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);residency.prepare_position(actor.global_position);stream.prepare_position(actor.global_position);await frames(25)
 if not require(actor.is_on_floor()and absf(actor.global_position.y-12)<.12,"Actual supported original-player bank street start"):return
 for goal in [Vector3(87,12,-128),Vector3(87,12,-132)]:
  var leg:Dictionary=await walk_to(actor,goal);observations.append(leg)
  if not require(leg.reached and leg.floor_contact,"Original player remains supported on native bank street"):return
 if not require(ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms").get_child_count()==303,"No compiler owner duplication"):return
 save_result();print("G3_LABELLED_BANK_PHYSICAL_RECEIVING_PASS checks=",nchecks);quit(0)
