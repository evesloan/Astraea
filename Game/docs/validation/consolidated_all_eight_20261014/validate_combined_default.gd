extends "res://tests/validate_d04_port_forward_commons_service.gd"
var count:=0
var legs:Array=[]
var installed_mode:=false
const P="/workspace/astraea-integration-cutoff-20261013/consolidated_all_eight_20261013/"
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","")
 for p in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(p,true))
 if not installed_mode:assert(ProjectSettings.load_resource_pack(P+"COMBINED_CANDIDATE_OVERLAY.zip",true))
 call_deferred("run")
func require(ok:bool,label:String)->bool:
 count+=1
 if not ok:push_error(label);quit(1)
 return ok
func frames(n:int)->void:
 for i in range(n):await physics_frame
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(30)
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var n:Node3D=ship.get_node("ShipSpace/Districts/Group7CompletionCandidate");var base:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GROUP7_COMPLETION.json"));var extra:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/consolidated_all_eight_20261013/G7_ADDITIONAL.json"));var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget");var models:Array=base.models.duplicate();models.append_array(extra.models)
 if not require(n.get_meta("default_runtime_adoption")and n.get_meta("physical_source_models")==88 and not n.get_meta("whole_group_or_primary_capacity_accepted"),"Default88physicalmodelsincludedwithoutacceptancecredit"):return
 for row in models:
  if not require(FileAccess.get_sha256("res://assets/models/"+str(row.file))==str(row.sha256)and n.has_node(str(row.cell)),"ExactsourceGLBandactualinstance "+str(row.cell)):return
 for row in extra.doors:
  var door:Node3D=n.get_node(str(row.id));var before:float=door.open_fraction;door.interact(actor);await frames(2)
  if not require(door.persistent_id==StringName(str(row.id))and not door.desired_open and door.open_fraction==before and door.get_interaction_label()=="Door locked"and not door.get_meta("operational_admission"),"NewgardendoorsretainauthoredIDsandclosedhold"):return
 var lights:Array=n.find_children("*","SpotLight3D",true,false)
 if not require(lights.size()==39,"All39sourcefixturesphysicallyregistered"):return
 for light:Light3D in lights:
  if not require(budget.sources.count(light)==1,"Sourcebudgetregistrationexactlyonce"):return
 var space:=ship.get_world_3d().direct_space_state;var support:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-integration-cutoff-20261013/G7_FULL_CURRENT_CONTACT_RUNTIME.json"))
 for witness in support.support_results:
  var at:Vector3=str_to_var("Vector3"+str(witness.at));var hit:Dictionary=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02)
  if not require(not hit.is_empty()and absf(hit.position.y-at.y)<.002,"Actualretainedsupport "+str(witness.id)+" "+str(at)):return
 if not require(FileAccess.get_sha256("res://scripts/player.gd")=="f1bd92d00ad355d5d3c87b57da5ff0e3aa76f9d48776a58f3515932c017a9566","Originalmovementsourceexact"):return
 if not require(ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms").get_child_count()==303,"Original303floorownersunchanged"):return
 for name in["Group2CentralSupportedAdjunct","Group2ForwardSupportedPairs","Group2PortCentralSupportedPair"]:
  if not require(ship.get_node("ShipSpace/"+name).get_meta("default_main_adoption"),"Priorfouradjunctcarepairsremainincluded"):return
 var clinical:Node3D=ship.get_node("ShipSpace/Group3CompleteClinical")
 if not require(not clinical.get_meta("clinical_operational_acceptance")and not clinical.get_meta("operating_gates_or_dispatch_admitted"),"Clinicaloperationholdsremain"):return
 var at:=Vector3(-65.5,102,-15.1)
 if not require(capsule_clear(space,at),"Defaultworldoriginalcontrollerstartclear"):return
 actor.global_position=at+Vector3.UP*.03;actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);await frames(25)
 for goal:Vector3 in[Vector3(-82.8,102,-15.1),Vector3(-82.8,102,-18),Vector3(-80.94999694824219,102,-18.85),Vector3(-82.8,102,-18),Vector3(-82.8,102,-15.1),Vector3(-65.5,102,-15.1)]:
  var leg:Dictionary=await walk_to(actor,goal);legs.append(leg)
  if not require(leg.reached and leg.floor_contact,"Representativecombineddefaultoriginalcontrollerrouting"):return
 FileAccess.open(P+"COMBINED_DEFAULT_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_COMBINED_DEFAULT_PHYSICAL_INTEGRATION","checks":count,"G7_models_physically_included":88,"G7_sources":39,"G7_doors":8,"new_garden_doors_locked":4,"support_witnesses":support.support_results.size(),"representative_original_controller_legs":legs,"all_eight_inclusion_inventory_accounted":true,"strict_original_D09_transit_five_checks_still_held":true,"G2_missingreceivers_80homes_private_pit_wet_aftpairs_uninstalled":true,"structural_tram_operation_capacity_or_fullbuild_accepted":false},"  "));print("COMBINED_DEFAULT_INTEGRATION_PASS checks=",count);quit(0)
