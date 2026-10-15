extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/arrivals_upper_staff_receiving_20261015/"
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/DINING_SERVICE_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ORCHARD_RECEIVING_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/SYNTHESIS_EXTERNAL_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/D09_RETAIL_SERVICE_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/AQUATIC_EXTERNAL_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ARRIVALS_STAFF_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/THREAD_SUCCESSOR_ADOPTION_OVERLAY.zip",D+"CANDIDATE_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func opaque_between(ship:Node3D,a:Vector3,b:Vector3) -> bool:
    var excluded:Array[RID]=[]
    for iteration in range(32):
        var ray:=PhysicsRayQueryParameters3D.create(a,b)
        ray.exclude=excluded
        var hit:=ship.get_world_3d().direct_space_state.intersect_ray(ray)
        if hit.is_empty():return false
        var owner:Node=hit.collider.get_parent()
        if owner is MeshInstance3D and owner.material_override is ShaderMaterial:
            excluded.append(hit.rid)
            continue
        return true
    return false
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(90);var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.set_physics_process(false);player.global_position=Vector3(-57,6.03,-442);player.force_update_transform();var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");residency.prepare_position(player.global_position);ship.get_node("ShipSystems/RemainingBatchStreaming").prepare_position(player.global_position);await frames(4);player.global_position=Vector3(0,0,0);player.force_update_transform();await frames(3)
 var space:=ship.get_world_3d().direct_space_state;var group:Node3D=ship.get_node("ShipSpace/ArrivalsUpperStaffReceiving20261015");var r:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/arrivals_upper_staff_receiving_20261015/NATIVE_VERIFICATION.json"));var source:Node3D=ship.get_node("ShipSpace/Districts/D01_D02_ArrivalsFusion_Integrated_WIP/ArrivalsAuthoredArchitecture");var before:Dictionary={}
 for mesh:MeshInstance3D in source.find_children("*","MeshInstance3D",true,false):before[mesh]={"pose":mesh.global_transform,"mesh":mesh.mesh}
 var excluded:Array[RID]=[]
 for body:CollisionObject3D in group.find_children("*","CollisionObject3D",true,false):excluded.append(body.get_rid())
 var doc:=GLTFDocument.new();var state:=GLTFState.new();assert(doc.append_from_file(D+"AUTHORING_COMPONENTS_r001.glb",state)==OK);var authored:Node3D=doc.generate_scene(state);authored.visible=false;root.add_child(authored);var contacts:Array=[];var unexplained:Array=[]
 for row in r.bounds:
  if str(row.name).ends_with("_Lens"):continue
  var mesh:MeshInstance3D=authored.find_child(str(row.name).validate_node_name(),true,false);assert(mesh!=null);var shape:=mesh.mesh.create_convex_shape(true,false);shape.margin=0.;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.margin=0.;q.transform=mesh.global_transform;q.exclude=excluded
  for hit in space.intersect_shape(q,256):
   var path:=str(hit.collider.get_path());var classification:=""
   if "EmbeddedTie"in str(row.name)and (("StaffEmbedded"in str(row.name)and "/D02_port_forward_staff_floor_0/"in path)or("ArrivalsEmbedded"in str(row.name)and "/D01_arrivals_ground/"in path)):classification="embedded_exact_existing_floor_bearing"
   elif "HOME_BATCH_"in path and str(row.name)in["ARRUS_StaffPortalHeader","ARRUS_StaffGatewayNorthJamb","ARRUS_StaffGatewaySouthJamb","ARRUS_StaffGatewayHeadReveal"]:classification="measured_opposing_gateway_edge_bearing_in_exact_staff_wall"
   elif "/D02_port_forward_staff_floor_0/"in path and str(row.name)=="ARRUS_ReceivingFloor":classification="contiguous_retained_floor_seam_with_fifty_micron_new_edge_relief"
   elif "/ARR_WestServiceEnclosure_-465.85/"in path and (str(row.name).begins_with("ARRUS_NorthSide_")or str(row.name).begins_with("ARRUS_SouthSide_")):classification="measured_new_side_panel_end_joint_in_exact_retained_arrivals_wall"
   elif "/ARR_WestServiceEnclosure_-465.85/"in path and str(row.name)in["ARRUS_SourceJoinedCanopy"]:classification="positive_header_end_bearing_in_exact_retained_wall"
   contacts.append({"part":row.name,"owner":path,"classification":classification})
   if classification.is_empty():unexplained.append(contacts[-1])
 var floors:Array=[];var preimages:Array=[]
 for x in[-55.1,-54.6,-54.1]:
  for z in[-443.7,-442.,-440.3]:
   var at:=Vector3(x,6,z);var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.025,at-Vector3.UP*.025);q.exclude=excluded;var old:=space.intersect_ray(q)
   if not old.is_empty():preimages.append({"at":str(at),"owner":str(old.collider.get_path())})
   var hit:=ray(space,at+Vector3.UP*.04,at-Vector3.UP*.04);floors.append({"at":str(at),"supported":not hit.is_empty()and absf(hit.position.y-6)<.003,"owner":str(hit.collider.get_path())if not hit.is_empty()else""})
 var bearings:Array=[]
 for row in r.source_bearings:
  var at:=vec(row.point);var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.02,at-Vector3.UP*.02);q.exclude=excluded;var hit:=space.intersect_ray(q);bearings.append({"part":row.name,"expected_source":row.source_region,"actual_source":str(hit.collider.get_path())if not hit.is_empty()else"","supported":not hit.is_empty()and absf(hit.position.y-6)<.003 and str(row.source_region)in str(hit.collider.get_path())})
 var stances:Array=[]
 for at:Vector3 in[Vector3(-57,6.03,-442),Vector3(-55,6.03,-442),Vector3(-54.2,6.03,-442),Vector3(-52,6.03,-442),Vector3(-50,6.03,-442)]:stances.append({"at":str(at),"clear":capsule_clear(space,at)})
 var upper:Array=[]
 for x in[-57.,-55.5,-54.6,-53.5,-52.,-50.]:
  var at:=Vector3(x,6,-442);var hit:=ray(space,at+Vector3.UP*.08,at-Vector3.UP*.08);upper.append({"at":str(at),"source_floor":str(hit.collider.get_path())if not hit.is_empty()else"","clear":capsule_clear(space,at+Vector3.UP*.03)})
 player.global_position=Vector3(-57,6.03,-442);player.velocity=Vector3.ZERO;player.set_physics_process(true);player.set_controls_enabled(true);residency.prepare_position(player.global_position);await frames(20);var legs:Array=[]
 for at:Vector3 in[Vector3(-54.6,6,-442),Vector3(-52,6,-442),Vector3(-50,6,-442),Vector3(-52,6,-442),Vector3(-54.6,6,-442),Vector3(-57,6,-442)]:
  legs.append(await walk_to(player,at))
  if not legs[-1].reached:break
 var preserved:=true
 for mesh in before:
  if not is_instance_valid(mesh)or not mesh.global_transform.is_equal_approx(before[mesh].pose)or mesh.mesh!=before[mesh].mesh:preserved=false
 var lights:Array=[];var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 for light:Light3D in group.find_children("*","Light3D",true,false):lights.append({"name":str(light.name),"registered_once":budget.sources.count(light)==1})
 var privacy:Array=[];var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D01_D02_arrivals_fusion.json"))
 for label in definition.guest_viewpoints:
  var a:=vec(definition.guest_viewpoints[label]);var targets:Array=definition.concealed_service_view_targets.duplicate(true);targets.append([-54.6,1.65,-442]);targets.append([-54.6,7.65,-442])
  for target in targets:privacy.append({"guest":str(label),"target":str(vec(target)),"opaque_screen_preserved":opaque_between(ship,a,vec(target))})
 var ok:bool=privacy.all(func(a):return a.opaque_screen_preserved)and unexplained.is_empty()and preimages.is_empty()and floors.all(func(a):return a.supported)and bearings.size()==6 and bearings.all(func(a):return a.supported)and stances.all(func(a):return a.clear)and legs.size()==6 and legs.all(func(a):return a.reached and a.floor_contact)and preserved and lights.size()==1 and lights.all(func(a):return a.registered_once)
 FileAccess.open(D+"CANDIDATE_RUNTIME304.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS"if ok else"FAIL","source_contacts":contacts,"unexplained_contacts":unexplained,"old_floor_preimages":preimages,"new_floor_samples":floors,"source_bearings":bearings,"clear_operator_stances":stances,"actual_original_controller_legs":legs,"teleports_within_continuous_route":0,"original_arrivals_meshes_poses_resources_preserved":preserved,"original_arrivals_mesh_count":before.size(),"lights":lights,"upper_d02_readonly_floor_survey":upper,"guest_view_concealment":privacy,"new_room_ids_capacity_or_lift_stops":0,"primary_load_stock_species_save_final_art_accepted":false},"  "));print("PASS_ARRIVALS_STAFF_RECEIVING_CURRENT_MAIN"if ok else"FAIL_ARRIVALS_STAFF_RECEIVING_CURRENT_MAIN");authored.queue_free();quit(0 if ok else 1)
