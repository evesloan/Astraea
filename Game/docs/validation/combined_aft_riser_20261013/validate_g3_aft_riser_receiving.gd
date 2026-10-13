extends "res://tests/validate_d04_port_forward_commons_service.gd"
var nchecks:=0
var failures:Array=[]
var observations:Array=[]
const OUT="/workspace/astraea-integration-cutoff-20261013/G3_AFT_RISER_RECEIVING_RUNTIME.json"
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
 for p in ["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/G3_AFT_RISER_CANDIDATE_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(p,true))
 call_deferred("run")
func save_result()->void:
 FileAccess.open(OUT,FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_EXACT_AFT_RISER_PHYSICAL_RECEIVING"if failures.is_empty()else"HOLD","checks":nchecks,"failures":failures,"observations":observations,"models":4,"native_floor_m2":1766.9119999999991,"affected_native_floor_parts":34,"floor_triangle_witnesses":204,"new_registered_berths":0,"working_lifts_or_doors":0,"identity_mapping_created":false,"scope":"Exact native aft riser source and floor/fixture receiving;34 declared part preimage setup cases and2 independent original-player D03 lobby setups. No operating lift/gate,whole network,person/berth/save/species/structural/final-art acceptance."},"  "))
func require(ok:bool,label:String)->bool:
 nchecks+=1
 if not ok:failures.append(label);save_result();push_error(label);quit(1)
 return ok
func frames(n:int)->void:
 for i in range(n):await physics_frame
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(30)
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");var stream:Node=ship.get_node("ShipSystems/RemainingBatchStreaming");var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 var source:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_remaining_risers_20261011/AFT_PAIR.json"));var floors:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-integration-cutoff-20261013/g3_aft_riser_preflight/AFT_PAIR_MISSING_ONLY_FLOORS.json"));var mappings:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-integration-cutoff-20261013/G3_AFT_RISER_LENS_MAPPING.json"))
 var space:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state;var witnesses:Array=[];actor.set_controls_enabled(false)
 for part in floors.parts:
  var at:=Vector3(0,part.y[1],0);var points:Array=[]
  for t in part.triangles:points.append(Vector3((t[0][0]+t[1][0]+t[2][0])/3.,part.y[1],(t[0][1]+t[1][1]+t[2][1])/3.))
  actor.global_position=points[0]+Vector3.UP*.03;actor.velocity=Vector3.ZERO;residency.prepare_position(actor.global_position);stream.prepare_position(actor.global_position);await frames(2)
  for point:Vector3 in points:
   var hit:Dictionary=ray(space,point+Vector3.UP*.02,point-Vector3.UP*.02)
   if not require(hit.is_empty(),"Exact aft missing native floor preimage "+str(part.name)+" "+str(hit.collider.get_path()if not hit.is_empty()else "none")):return
   witnesses.append(point)
 var old_sources:int=budget.sources.size();var aft:Node3D=load("res://scripts/group3_remaining_risers_20261011/aft_pair.gd").build(ship);await frames(4)
 if not require(not aft.get_meta("operating_lifts_admitted")and not aft.get_meta("authoritative_identity_mapping")and aft.get_meta("registered_berths_added")==0,"No fabricated operating lifts/identities/capacity"):return
 for file in source.model_pins:
  if not require(FileAccess.get_sha256("res://assets/models/group3_remaining_risers_20261011/"+str(file))==str(source.model_pins[file]),"Exact native aft source "+str(file)):return
 for point:Vector3 in witnesses:
  var hit:Dictionary=ray(space,point+Vector3.UP*.02,point-Vector3.UP*.02)
  if not require(not hit.is_empty()and aft.is_ancestor_of(hit.collider)and absf(hit.position.y-point.y)<.002,"Actual source-owned aft native floor witness "+str(point)):return
 if not require(budget.sources.size()==old_sources+34,"Exactly34 native aft light sources registered once"):return
 for site in source.sites:
  for i in range(17):
   if not require(float(site.controller_binding.floor_heights[i])==ship.deck_y[i],"Original17 deck datums preserved "+str(site.reservation_id)+" "+str(i)):return
  if not require(aft.get_node_or_null(str(site.reservation_id))==null,"Unassigned operating lift backend not invented"):return
  for fixture in site.fixtures:
   var light:Light3D=aft.get_node(str(fixture.name)+"_PhysicalSource");var name:=""
   for mapping in mappings.mappings:
    if str(mapping.fixture)==str(fixture.name):name=str(mapping.node).validate_node_name()
   var lens:MeshInstance3D=aft.get_node(str(site.architecture_file).trim_suffix(".glb")).find_child(name,true,false)
   if not require(lens!=null and (lens.global_transform*lens.get_aabb()).grow(.025).has_point(light.global_position),"Exact original aft fixture receiver "+str(fixture.name)):return
   if not require(budget.sources.count(light)==1,"Single source registration "+str(fixture.name)):return
  var x:float=-21 if float(site.center_xz[0])<0 else 21
  actor.global_position=Vector3(x,12.03,487);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);residency.prepare_position(actor.global_position);stream.prepare_position(actor.global_position);await frames(25)
  if not require(actor.is_on_floor()and absf(actor.global_position.y-12)<.12,"Supported original-player aft lobby start "+str(site.reservation_id)):return
  for z in [489.,487.]:
   var leg:Dictionary=await walk_to(actor,Vector3(x,12,z));observations.append({"site":site.reservation_id,"leg":leg})
   if not require(leg.reached and leg.floor_contact,"Original-controller aft native lobby leg "+str(site.reservation_id)):return
 if not require(ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms").get_child_count()==303,"No duplicate compiler owners"):return
 save_result();print("G3_AFT_RISER_PHYSICAL_RECEIVING_PASS checks=",nchecks);quit(0)
