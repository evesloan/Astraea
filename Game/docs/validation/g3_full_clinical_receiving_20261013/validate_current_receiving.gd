extends "res://tests/validate_d04_port_forward_commons_service.gd"
var nchecks:=0
var failures:Array=[]
var legs:Array=[]
var loaded_originals:Array=[]
var preserved_meshes:=0
const OUT="/workspace/astraea-integration-cutoff-20261013/g3_full_clinical_receiving/RECEIVING_RUNTIME.json"
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
 for path in ["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/g3_full_clinical_receiving/CANDIDATE_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func receipt()->void:
 FileAccess.open(OUT,FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_CURRENT_FULL_CLINICAL_PHYSICAL_RECEIVING"if failures.is_empty()else"HOLD","checks":nchecks,"failures":failures,"original_controller_legs":legs,"preserved_prior_and_medical_meshes":preserved_meshes,"loaded_original_D05_programmes":loaded_originals,"temporary_medical_residency_frozen_for_conservative_source_check":true,"new_models_instantiated":3,"new_floor_m2":16089.193863999986,"native_floor_witnesses":247,"new_fixture_sources":193,"original_port2_fore_sources_preserved":60,"static_closed_gate_instances":36,"gate_dispatch_ids_or_sealed_predicates_supplied":false,"medical_receiver_panels_inventory_sterility_egress_or_clinical_admission":false,"protected_pool_junction_and_two_royalty_spans":true,"whole_starboard_return_route_accepted":false,"historical_network_criteria":13,"unaccepted_joins":184,"capacity_credit":0},"  "))
func require(ok:bool,label:String)->bool:
 nchecks+=1
 if not ok:failures.append(label);receipt();push_error(label);quit(1)
 return ok
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(30)
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget");var stream:Node3D=ship.get_node("ShipSystems/RemainingBatchStreaming");var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_clinical_full_20261011/CLINICAL.json"));var floor:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-integration-cutoff-20261013/g3_full_clinical_receiving/native/CLINICAL_COMPLETE_MISSING_FLOOR.json"));var mapping:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-integration-cutoff-20261013/g3_full_clinical_receiving/FIXTURE_LENS_MAPPING.json"));var pre:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_clinical_full_20261011/CURRENT_BOUNDED_PREFLIGHT.json"))
 var original_rooms:Array=[]
 # Load only the already registered original medical entries; freeze their temporary test residency so missing source contacts cannot yield false empty preimages.
 stream.set_physics_process(false)
 for item in stream.entries:
  if not str(item.key).begins_with("D05_directory_"):continue
  var room:Node3D=stream.rooms[str(item.key)]
  if not room.get_meta("stream_loaded",false):load("res://scripts/remaining_batch_receiving.gd").install(ship,item,room)
  original_rooms.append(room);loaded_originals.append(str(item.key))
 residency.enabled=false;residency.set_physics_process(false)
 for entry in residency.entries:
  var room:Node3D=entry.room;var key:String=str(room.get_meta("programme_key",""))
  if not key.begins_with("D05_directory_"):continue
  if not entry.attached:entry.parent.add_child(room);entry.attached=true
  load("res://scripts/deferred_home_visual.gd").ensure(room);original_rooms.append(room);loaded_originals.append(key)
 loaded_originals.sort()
 if not require(loaded_originals.size()==10,"All ten original medical source receivers loaded through existing registration"):return
 await frames(5)
 var prior:Node3D=ship.get_node("ShipSpace/Group3Port2ClinicalPhysical");var fore:Node3D=ship.get_node("ShipSpace/Group3ForeStarboardClinical");var bounded:Node3D=prior.get_node("AST-MED-G3-006");var old:Array=[];var old_contacts:Array=[];var old_lights:Array=[]
 for owner:Node3D in [prior,fore]+original_rooms:
  for mesh:MeshInstance3D in owner.find_children("*","MeshInstance3D",true,false):
   if bounded.is_ancestor_of(mesh):continue
   old.append({"node":mesh,"mesh":mesh.mesh,"pose":mesh.global_transform,"local_pose":mesh.transform,"parent":mesh.get_parent(),"bounds":mesh.get_aabb(),"material":mesh.material_override})
  for contact:CollisionShape3D in owner.find_children("*","CollisionShape3D",true,false):
   if bounded.is_ancestor_of(contact):continue
   old_contacts.append({"node":contact,"shape":contact.shape,"pose":contact.transform,"parent":contact.get_parent(),"disabled":contact.disabled})
 for owner:Node3D in [prior,fore]:
  for light:Light3D in owner.find_children("*","Light3D",true,false):old_lights.append({"node":light,"pose":light.global_transform,"range":light.omni_range,"energy":light.light_energy,"color":light.light_color})
 preserved_meshes=old.size()
 if not require(old_lights.size()==60,"All prior26port2 and34fore sources remain instantiated"):return
 for row in pre.mesh_preimages:
  var mesh:MeshInstance3D=bounded.find_child(str(row.name).validate_node_name(),true,false);var b:AABB=mesh.global_transform*mesh.get_aabb()
  if not require(b.position.distance_to(Vector3(row.min[0],row.min[1],row.min[2]))<.0001 and b.end.distance_to(Vector3(row.max[0],row.max[1],row.max[2]))<.0001,"Exact old bounded mesh preimage "+str(row.name)):return
 var space:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state;var witnesses:Array=[]
 for part in floor.parts:
  for t in part.triangles:witnesses.append(Vector3((t[0][0]+t[1][0]+t[2][0])/3.,21.,(t[0][1]+t[1][1]+t[2][1])/3.))
 for at:Vector3 in witnesses:
  var hit:Dictionary=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02)
  if not require(hit.is_empty()or bounded.is_ancestor_of(hit.collider),"Exact new missing-floor receiving preimage "+str(at)):return
 var held_preimages:Array=[]
 for hold in p.held_support_spans:
  var source:Node=ship.get_node_or_null(str(hold.source_contact).trim_prefix("/root/AstraeaPresentation/World360/Astraea/"))if str(hold.source_contact).begins_with("/root/")else ship.get_node_or_null("ShipSpace/Districts/"+str(hold.source_contact))
  if not require(source!=null,"Exact declared held source node exists "+str(hold.name)):return
  var mesh:MeshInstance3D=source if source is MeshInstance3D else source.get_parent()as MeshInstance3D
  if not require(mesh!=null,"Held source owner is the original mesh "+str(hold.name)):return
  var contacts:Array=[]
  for shape:CollisionShape3D in mesh.find_children("*","CollisionShape3D",true,false):contacts.append({"node":shape,"shape":shape.shape,"pose":shape.transform,"parent":shape.get_parent(),"disabled":shape.disabled})
  if not require(not contacts.is_empty(),"Declared original held support contact exists "+str(hold.name)):return
  held_preimages.append({"name":hold.name,"node":mesh,"mesh":mesh.mesh,"pose":mesh.global_transform,"bounds":mesh.get_aabb(),"contacts":contacts})
 var addition:Node3D=load("res://scripts/group3_clinical_full_20261011/physical_package.gd").build(ship);await frames(4)
 if not require(prior.get_node_or_null("AST-MED-G3-006")==null,"Only declared old bounded visual/contact subtree replaced"):return
 for row in old:
  var mesh:MeshInstance3D=row.node
  if not require(is_instance_valid(mesh)and mesh.mesh==row.mesh and mesh.global_transform==row.pose and mesh.transform==row.local_pose and mesh.get_parent()==row.parent and mesh.get_aabb()==row.bounds and mesh.material_override==row.material,"Prior/medical mesh remains exact "+str(mesh.name)):return
 for row in old_contacts:
  var contact:CollisionShape3D=row.node
  if not require(is_instance_valid(contact)and contact.shape==row.shape and contact.transform==row.pose and contact.get_parent()==row.parent and contact.disabled==row.disabled,"Prior/medical original contact exact "+str(contact.name)):return
 for row in old_lights:
  var light:Light3D=row.node
  if not require(is_instance_valid(light)and light.global_transform==row.pose and light.omni_range==row.range and light.light_energy==row.energy and light.light_color==row.color and budget.sources.count(light)==1,"Exact singly registered prior fixture retained "+str(light.name)):return
 for at:Vector3 in witnesses:
  var hit:Dictionary=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02)
  if not require(not hit.is_empty()and addition.get_node("AST-MED-G3-008").is_ancestor_of(hit.collider)and absf(hit.position.y-21)<.002,"Exact source-owned missing clinical floor "+str(at)):return
 if not require(addition.find_children("*","OmniLight3D",true,false).size()==193,"Exactly193new physical sources without prior duplicates"):return
 for row in mapping.mappings:
  var light:Light3D=addition.get_node((str(row.fixture)+"_PhysicalSource").validate_node_name());var lens:MeshInstance3D=addition.get_node(str(row.model).trim_suffix(".glb")).find_child(str(row.node).validate_node_name(),true,false)
  if not require(lens!=null and (lens.global_transform*lens.get_aabb()).grow(.025).has_point(light.global_position)and budget.sources.count(light)==1,"Exact singly registered clinical lens binding "+str(row.fixture)):return
 for d in p.door_bindings:
  if not require(addition.get_node_or_null(str(d.name))==null,"No unsupported clinical operating gate backend "+str(d.name)):return
 for crossing in p.crossings:
  if not require(addition.get_node_or_null(str(crossing.programme_key))==null,"No synthetic sealed-load manager admitted "+str(crossing.programme_key)):return
  for button in crossing.dispatch_buttons:
   if not require(addition.get_node_or_null(str(button.name))==null,"No unsupported dispatch identity "+str(button.name)):return
 for row in held_preimages:
  var mesh:MeshInstance3D=row.node
  if not require(is_instance_valid(mesh)and mesh.mesh==row.mesh and mesh.global_transform==row.pose and mesh.get_aabb()==row.bounds,"Original held pool/royalty support remains exact "+str(row.name)):return
  for contact in row.contacts:
   var shape:CollisionShape3D=contact.node
   if not require(is_instance_valid(shape)and shape.shape==contact.shape and shape.transform==contact.pose and shape.get_parent()==contact.parent and shape.disabled==contact.disabled,"Held source contact resource exact "+str(row.name)):return
 var cases:Array=[{"name":"starboard_clean_fore_segment","start":Vector3(57,21.03,-470),"goals":[Vector3(57,21,-460),Vector3(57,21,-470)]},{"name":"port_clean_mid_segment","start":Vector3(-57,21.03,-240),"goals":[Vector3(-57,21,-230),Vector3(-57,21,-240)]},{"name":"starboard_clean_core_segment","start":Vector3(102,21.03,-40),"goals":[Vector3(102,21,-30),Vector3(102,21,-40)]}]
 for setup in cases:
  actor.global_position=setup.start;actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);await frames(25)
  if not require(actor.is_on_floor()and absf(actor.global_position.y-21)<.12,"Supported source clinical corridor start "+str(setup.name)):return
  for goal in setup.goals:
   var leg:Dictionary=await walk_to(actor,goal);legs.append({"case":setup.name,"leg":leg})
   if not require(leg.reached and leg.floor_contact,"Original-controller bounded clinical corridor "+str(setup.name)):return
 if not require(not addition.get_meta("clinical_operational_acceptance")and not addition.get_meta("operating_gates_or_dispatch_admitted")and addition.get_meta("registered_berths_added")==0,"No clinical/protocol/capacity operation accepted"):return
 receipt();print("FULL_CLINICAL_CURRENT_PHYSICAL_RECEIVING_PASS checks=",nchecks," preserved_meshes=",preserved_meshes);quit(0)
