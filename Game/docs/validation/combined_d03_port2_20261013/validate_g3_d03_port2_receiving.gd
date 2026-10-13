extends "res://tests/validate_d04_port_forward_commons_service.gd"
var nchecks:=0
var failures:Array=[]
var observations:Array=[]
var retained_cells:=0
const OUT="/workspace/astraea-integration-cutoff-20261013/G3_D03_PORT2_RECEIVING_RUNTIME.json"
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
 for p in ["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/G3_D03_PORT2_CANDIDATE_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(p,true))
 call_deferred("run")
func receipt()->void:
 FileAccess.open(OUT,FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_EXACT_D03_PORT2_CURRENT_RECEIVING"if failures.is_empty()else"HOLD","checks":nchecks,"failures":failures,"observations":observations,"models":4,"native_floor_m2":148.2159999999999,"exact_current_wall_cells_replaced":4,"unrelated_live_cells_preserved":retained_cells,"fixtures":4,"working_lifts_or_gates":0,"new_registered_berths":0,"scope":"Exact four current source-wall cells replaced onlyby pinned owner derivative;unrelated currentcells/contactresources/poses remain unchanged;source floor/fixture andoriginal-controller corridor receiving only. Closed source leaves are not working gates;no lift,clinicalprotocol,whole network,species/engineering/save/final-art acceptance."},"  "))
func require(ok:bool,label:String)->bool:
 nchecks+=1
 if not ok:failures.append(label);receipt();push_error(label);quit(1)
 return ok
func frames(n:int)->void:
 for i in range(n):await physics_frame
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(30)
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget");var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");var stream:Node=ship.get_node("ShipSystems/RemainingBatchStreaming")
 var source:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_d03_port2_20261011/CONNECTION.json"));var floors:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-integration-cutoff-20261013/g3_d03_port2_preflight/D03_PORT2_MISSING_FLOOR.json"));var bounds:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_d03_port2_20261011/CURRENT_CELL_PREFLIGHT.json"));var mapping:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-integration-cutoff-20261013/G3_D03_PORT2_LENS_MAPPING.json"))
 if not require(ship.get_node_or_null("ShipSpace/"+str(source.required_existing_port2_package))!=null,"Verified port2 receiving prerequisite installed"):return
 if not require(FileAccess.get_sha256("res://assets/models/AST-STF-009_pool_market_home_equipment.glb")==source.current_spine_sha256,"Exact current original spine source file"):return
 var lower:Node3D=ship.get_node("ShipSpace/Districts/LowerStaffNetwork_WIP/LowerStaffEnclosure");var unchanged:Array=[]
 for mesh:MeshInstance3D in lower.find_children("*","MeshInstance3D",true,false):
  if str(mesh.name)in source.exact_current_meshes_to_replace:continue
  var contact:CollisionShape3D=mesh.get_node_or_null("StaticContact/SharedShape")
  unchanged.append({"node":mesh,"id":mesh.get_instance_id(),"mesh_id":mesh.mesh.get_instance_id(),"pose":mesh.global_transform,"bounds":mesh.get_aabb(),"contact":contact,"shape":contact.shape if contact!=null else null,"disabled":contact.disabled if contact!=null else false})
 retained_cells=unchanged.size()
 for row in bounds.mesh_preimages:
  var mesh:MeshInstance3D=lower.find_child(str(row.name),true,false);var box:AABB=mesh.global_transform*mesh.get_aabb()
  if not require(box.position.distance_to(Vector3(row.min[0],row.min[1],row.min[2]))<.0001 and box.end.distance_to(Vector3(row.max[0],row.max[1],row.max[2]))<.0001,"Actual exact current wall preimage "+str(row.name)):return
 var witnesses:Array=[]
 for part in floors.parts:
  for t in part.triangles:witnesses.append(Vector3((t[0][0]+t[1][0]+t[2][0])/3.,12.,(t[0][1]+t[1][1]+t[2][1])/3.))
 actor.global_position=Vector3(-31,12.03,-293);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(false);residency.prepare_position(actor.global_position);stream.prepare_position(actor.global_position);await frames(2)
 var space:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state
 for at:Vector3 in witnesses:
  var hit:Dictionary=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02)
  if not require(hit.is_empty(),"Exact missing-only connection floor preimage "+str(at)):return
 var before:Dictionary=ray(space,Vector3(-56,13.4,-293),Vector3(-54.9,13.4,-293))
 if not require(not before.is_empty()and str(before.collider.get_parent().name)in source.exact_current_meshes_to_replace,"Original exact current spine wall blocks proposed opening"):return
 var addition:Node3D=load("res://scripts/group3_d03_port2_20261011/physical_package.gd").build(ship,{},true);await frames(4)
 if not require(addition.get_meta("owner_current_spine_patch_applied")and not addition.get_meta("operating_doors_admitted")and addition.get_meta("registered_berths_added")==0,"Exact owner wall derivative without fabricated gate operation"):return
 for file in source.model_pins:
  if not require(FileAccess.get_sha256("res://assets/models/group3_d03_port2_20261011/"+str(file))==str(source.model_pins[file]),"Exact connection source "+str(file)):return
 for name in source.exact_current_meshes_to_replace:
  if not require(lower.find_child(str(name),true,false)==null,"Exactly declared source cell replaced "+str(name)):return
 for row in unchanged:
  var mesh:MeshInstance3D=row.node
  if not require(is_instance_valid(mesh)and mesh.get_instance_id()==row.id and mesh.mesh.get_instance_id()==row.mesh_id and mesh.global_transform==row.pose and mesh.get_aabb()==row.bounds,"Unrelated current live cell remains exact "+str(mesh.name)):return
  if row.contact!=null:
   if not require(is_instance_valid(row.contact)and row.contact.shape==row.shape and row.contact.disabled==row.disabled,"Unrelated current contact shape preserved "+str(mesh.name)):return
 if not require(ray(space,Vector3(-56,13.4,-293),Vector3(-54.9,13.4,-293)).is_empty(),"Exact wall derivative clears original source opening before closed gate plane"):return
 for at:Vector3 in witnesses:
  var hit:Dictionary=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02)
  if not require(not hit.is_empty()and addition.is_ancestor_of(hit.collider)and absf(hit.position.y-12)<.002,"Actual source-owned connection floor "+str(at)):return
 if not require(addition.find_children("*","OmniLight3D",true,false).size()==4,"Exactlyfour owned source fixtures"):return
 for fixture in source.fixtures:
  var light:Light3D=addition.get_node(str(fixture.name)+"_PhysicalSource");var bind:Dictionary={}
  for row in mapping.mappings:
   if str(row.fixture)==str(fixture.name):bind=row
  var lens:MeshInstance3D=addition.get_node(str(bind.model).trim_suffix(".glb")).find_child(str(bind.node).validate_node_name(),true,false)
  if not require(lens!=null and (lens.global_transform*lens.get_aabb()).grow(.025).has_point(light.global_position)and budget.sources.count(light)==1,"Exact singly registered connection fixture "+str(fixture.name)):return
 for q in source.door_bindings:
  if not require(addition.get_node_or_null(str(q.name))==null,"Unassigned gate backend remains absent "+str(q.name)):return
 actor.global_position=Vector3(-31,12.03,-293);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);await frames(25)
 if not require(actor.is_on_floor()and absf(actor.global_position.y-12)<.12,"Actual supported original-controller connection corridor stance"):return
 for x in [-41.,-50.,-41.,-31.]:
  var leg:Dictionary=await walk_to(actor,Vector3(x,12,-293));observations.append(leg)
  if not require(leg.reached and leg.floor_contact,"Original-controller supported connection corridor leg"):return
 if not require(ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms").get_child_count()==303,"Original compiler owners remain unchanged"):return
 receipt();print("G3_D03_PORT2_CURRENT_RECEIVING_PASS checks=",nchecks," retained_cells=",retained_cells);quit(0)
