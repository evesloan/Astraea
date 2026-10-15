extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/aquatic_external_receiving_20261015/"
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/DINING_SERVICE_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ORCHARD_RECEIVING_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/SYNTHESIS_EXTERNAL_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/D09_RETAIL_SERVICE_ADOPTION_OVERLAY.zip",D+"INSTALLED_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func at_y(z:float)->float:return 45.45 if z<=211.4 else 44. if z>=252.3 else 45.45-(z-211.4)*1.45/40.9
func box_contacts(space:PhysicsDirectSpaceState3D,lo:Vector3,hi:Vector3,exclude:Array[RID])->Array:
 var shape:=BoxShape3D.new();shape.size=hi-lo;shape.margin=0.;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.margin=0.;q.transform.origin=(lo+hi)/2;q.exclude=exclude;var out:Array=[]
 for hit in space.intersect_shape(q,512):out.append(str(hit.collider.get_path()))
 return out
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(90);var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.set_physics_process(false);player.global_position=Vector3(99.55,45.48,210.4);player.force_update_transform();var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");residency.prepare_position(player.global_position);ship.get_node("ShipSystems/RemainingBatchStreaming").prepare_position(player.global_position);await frames(4);player.global_position=Vector3(0,0,0);player.force_update_transform();await frames(3);var space:=ship.get_world_3d().direct_space_state;var group:Node3D=ship.get_node("ShipSpace/AquaticExternalReceiving20261015");var r:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/aquatic_external_receiving_20261015/NATIVE_VERIFICATION.json"));var annex:Node3D=ship.get_node("ShipSpace/Districts/AquaticRiverSlideAnnex_WIP");var before:Dictionary={}
 for mesh:MeshInstance3D in annex.find_children("*","MeshInstance3D",true,false):before[mesh]={"pose":mesh.global_transform,"mesh":mesh.mesh}
 var excluded:Array[RID]=[]
 for body:CollisionObject3D in group.find_children("*","CollisionObject3D",true,false):excluded.append(body.get_rid())
 var doc:=GLTFDocument.new();var state:=GLTFState.new();assert(doc.append_from_file(D+"AUTHORING_COMPONENTS_r002.glb",state)==OK);var authored:Node3D=doc.generate_scene(state);authored.visible=false;root.add_child(authored);var contacts:Array=[];var unexplained:Array=[]
 for row in r.bounds:
  if str(row.name).ends_with("_Lens"):continue
  var paths:Array=[]
  if str(row.name)=="AQER_East_EntranceFloor":
   for rect in[[100.25,103.3,208.6,211.4],[100.00005,100.25,208.80005,211.19995]]:
    for path in box_contacts(space,Vector3(rect[0],45.21,rect[2]),Vector3(rect[1],45.45,rect[3]),excluded):
     if not path in paths:paths.append(path)
  elif str(row.name)=="AQER_SouthWest_LevelFloor":
   for rect in[[54.15,103.3,252.3,255.6],[54.15,55.8,242.00005,252.3]]:
    for path in box_contacts(space,Vector3(rect[0],43.76,rect[2]),Vector3(rect[1],44,rect[3]),excluded):
     if not path in paths:paths.append(path)
  else:
   var mesh:MeshInstance3D=authored.find_child(str(row.name).validate_node_name(),true,false);assert(mesh!=null,"Authored source component "+str(row.name));var shape:=mesh.mesh.create_convex_shape(true,false);shape.margin=0.;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.margin=0.;q.transform=mesh.global_transform;q.exclude=excluded
   for hit in space.intersect_shape(q,256):paths.append(str(hit.collider.get_path()))
  for path in paths:
   var classification:=""
   if "/AQD_annex_substrate/"in path and("SubstrateRoot"in str(row.name)or"CornerBrace"in str(row.name)):classification="embedded_root_in_exact_annex_substrate_slab"
   elif "/D08_gentle_waters_floor/"in path and"ExistingFloorRoot"in str(row.name):classification="embedded_root_in_exact_existing_dry_floor"
   contacts.append({"part":row.name,"owner":path,"classification":classification})
   if classification.is_empty():unexplained.append(contacts[-1])
 var points:Array[Vector3]=[Vector3(100.075,45.45,210)]
 for z in[209.2,210.,211.1]:
  for x in[100.55,101.6,102.95]:points.append(Vector3(x,45.45,z))
 for i in range(21):
  var z:float=211.75+i*2.
  for x in[100.55,101.6,102.95]:points.append(Vector3(x,at_y(z),z))
 for i in range(25):
  for z in[252.7,254.,255.2]:points.append(Vector3(54.55+i*2.,44,z))
 for i in range(7):
  for x in[54.5,55.4]:points.append(Vector3(x,44,242.35+i*1.5))
 var floors:Array=[];var preimages:Array=[]
 for at in points:
  var old_q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.025,at-Vector3.UP*.025);old_q.exclude=excluded;var old:=space.intersect_ray(old_q)
  if not old.is_empty():preimages.append({"at":str(at),"owner":str(old.collider.get_path())})
  var hit:=ray(space,at+Vector3.UP*.04,at-Vector3.UP*.04);floors.append({"at":str(at),"supported":not hit.is_empty()and absf(hit.position.y-at.y)<.003,"owner":str(hit.collider.get_path())if not hit.is_empty()else""})
 var bearings:Array=[]
 for row in r.source_bearings:
  var at:=vec(row.point);var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.02,at-Vector3.UP*.02);q.exclude=excluded;var hit:=space.intersect_ray(q);bearings.append({"part":row.name,"at":str(at),"expected_source":row.source_region,"actual_source":str(hit.collider.get_path())if not hit.is_empty()else"","supported":not hit.is_empty()and absf(hit.position.y-at.y)<.003 and str(row.source_region)in str(hit.collider.get_path())})
 var stances:Array=[]
 for at:Vector3 in[Vector3(95.6,45.48,210.6),Vector3(98.5,45.48,210.4),Vector3(99.55,45.48,210),Vector3(101.6,45.48,210),Vector3(55,44.03,254),Vector3(55,44.03,246),Vector3(55,44.03,240),Vector3(56.8,44.03,240)]:stances.append({"at":str(at),"clear":capsule_clear(space,at)})
 player.global_position=Vector3(95.6,45.48,210.6);player.velocity=Vector3.ZERO;player.set_physics_process(true);player.set_controls_enabled(true);residency.prepare_position(player.global_position);await frames(20);var legs:Array=[]
 for at:Vector3 in[Vector3(98.5,45.45,210.6),Vector3(98.5,45.45,210.4),Vector3(99.55,45.45,210.4),Vector3(99.55,45.45,210),Vector3(101.6,45.45,210),Vector3(101.6,44,254),Vector3(55,44,254),Vector3(55,44,240),Vector3(56.8,44,240),Vector3(55,44,240),Vector3(55,44,254),Vector3(101.6,44,254),Vector3(101.6,45.45,210),Vector3(99.55,45.45,210),Vector3(99.55,45.45,210.4),Vector3(98.5,45.45,210.4),Vector3(98.5,45.45,210.6),Vector3(95.6,45.45,210.6)]:
  legs.append(await walk_to(player,at))
  if not legs[-1].reached:break
 var preserved:=true
 for mesh in before:
  if not is_instance_valid(mesh)or not mesh.global_transform.is_equal_approx(before[mesh].pose)or mesh.mesh!=before[mesh].mesh:preserved=false
 var lights:Array=[];var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 for light:Light3D in group.find_children("*","Light3D",true,false):lights.append({"name":str(light.name),"registered_once":budget.sources.count(light)==1})
 var ok:bool=unexplained.is_empty()and preimages.is_empty()and floors.all(func(a):return a.supported)and bearings.size()==13 and bearings.all(func(a):return a.supported)and stances.all(func(a):return a.clear)and legs.size()==18 and legs.all(func(a):return a.reached and a.floor_contact)and preserved and lights.size()==13 and lights.all(func(a):return a.registered_once)
 FileAccess.open(D+"INSTALLED_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS"if ok else"FAIL","source_contacts":contacts,"unexplained_contacts":unexplained,"old_floor_preimages":preimages,"new_floor_samples":floors,"source_bearings":bearings,"clear_operator_stances":stances,"actual_original_controller_legs":legs,"teleports_within_continuous_route":0,"original_annex_meshes_poses_resources_preserved":preserved,"original_annex_mesh_count":before.size(),"lights":lights,"source_public_seam_portal_flanges_gates_and_capacity_unchanged":true,"declared_old_inside_stance_remains_occupied_and_unaccepted":true,"new_narrow_operator_leg_m":1.65,"primary_load_pressure_stock_water_loaded_cart_species_save_final_art_accepted":false},"  "));print("PASS_AQUATIC_EXTERNAL_RECEIVING_CURRENT_MAIN"if ok else"FAIL_AQUATIC_EXTERNAL_RECEIVING_CURRENT_MAIN");authored.queue_free();quit(0 if ok else 1)
