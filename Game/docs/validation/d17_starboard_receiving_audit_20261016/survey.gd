extends SceneTree
func _initialize()->void:call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func hit(space:PhysicsDirectSpaceState3D,a:Vector3,b:Vector3,rid:RID)->Dictionary:
 var q:=PhysicsRayQueryParameters3D.create(a,b);q.exclude=[rid];var h:=space.intersect_ray(q)
 return {}if h.is_empty()else {"at":[h.position.x,h.position.y,h.position.z],"owner":str(h.collider.get_path())}
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(60)
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false);actor.global_position=Vector3(80,102.03,0)
 ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position);ship.get_node("ShipSystems/RemainingBatchStreaming").prepare_position(actor.global_position);await frames(8)
 var space:=ship.get_world_3d().direct_space_state;var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D17_LUXURY_HOUSES_PROPOSAL.json"));var rows:Array=[]
 for r in p.replanned_standard_units:
  if r.house!="starboard_central_upper_house":continue
  var samples:Array=[];var a:Array=r.source_allocation.x;var b:Array=r.source_allocation.z
  actor.global_position=Vector3((float(a[0])+float(a[1]))/2,102.03,(float(b[0])+float(b[1]))/2);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position);ship.get_node("ShipSystems/RemainingBatchStreaming").prepare_position(actor.global_position);await frames(3)
  for x in [float(a[0])+.4,(float(a[0])+float(a[1]))/2,float(a[1])-.4]:
   for z in [float(b[0])+.4,(float(b[0])+float(b[1]))/2,float(b[1])-.4]:
    samples.append({"xz":[x,z],"D17_floor":hit(space,Vector3(x,102.05,z),Vector3(x,101.7,z),actor.get_rid()),"D16_floor":hit(space,Vector3(x,97.55,z),Vector3(x,97.2,z),actor.get_rid()),"first_lower_surface":hit(space,Vector3(x,101.75,z),Vector3(x,90,z),actor.get_rid())})
  rows.append({"source_envelope_index":r.source_envelope_index,"source_allocation":r.source_allocation,"historical_stable_id":r.historical_stable_id,"historical_proposed_boundary":r.proposed_floor_boundary,"samples":samples})
 var receipt:Dictionary={"commit":"5f7b87cb45a85187ad99086fba1d9543633f073d","scope":"Read-only current-main point survey, no route, load, absence-of-all-geometry or construction acceptance","rooms":rows,"starboard_adjunct_installed":ship.find_child("Group2CentralSupportedAdjunct",true,false)!=null,"tidal_D15_installed":ship.find_child("TidalD15ServiceReceiving",true,false)!=null,"tidal_D17_installed":ship.find_child("TidalD17ServiceReceiving",true,false)!=null,"actual_forward_staff_lift_stops":ship.find_child("ForwardStaffLift",true,false).floor_heights,"actual_forward_staff_lift_operation_ready":ship.find_child("ForwardStaffLift",true,false).operation_ready,"room_residency_prepared_at_each_original_allocation":true}
 FileAccess.open("/workspace/d17-receiving-audit/CURRENT_MAIN_SURVEY.json",FileAccess.WRITE).store_string(JSON.stringify(receipt,"  "));print("D17_RECEIVING_SURVEY_COMPLETE ",rows.size()," source allocations");quit()
