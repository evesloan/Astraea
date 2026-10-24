extends SceneTree
const P:="res://night_garden_lower_receiving_20261024/"
var failures:Array=[]
var checks:=0
func _initialize()->void:call_deferred("run")
func check(ok:bool,label:String)->void:
 checks+=1
 if not ok:failures.append(label);push_error(label)
func run()->void:
 var main:Node=load("res://scenes/main_night_garden_lower_integrated_20261024.tscn").instantiate();root.add_child(main)
 var ship:Node3D=main.get_node("World360/Astraea")
 while not ship.get_meta("runtime_ready",false):await process_frame
 for frame in range(8):await physics_frame
 paused=true
 var district:=ship.get_node("ShipSpace/Districts/NightGardenLower17_20261024")
 var package:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://night_garden_lower_bank_20261022/PACKAGE.json"))
 var index:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://night_garden_lower_bank_20261022/evidence/INDEX.json")).rooms
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"RECEIVING.json"))
 var manager:Node=ship.private_detail_residency
 check(district.get_meta("source_rooms")==17 and district.get_meta("new_capacity")==0 and district.get_meta("new_private_floors")==0,"Only17 retained allocations, zero duplicate private floors/capacity")
 var ordinary:=ship.get_node("ShipSpace/Districts/NightGardenRoomCandidates")
 var received_count:=0
 for entry:Dictionary in ship.get_node("ShipSystems/ReceivedRoomResidency").entries:
  if entry.parent==ordinary:received_count+=1
 check(received_count==80,"All80 original ordinary-home registrations retained")
 var original_d15:=ship.get_node("ShipSpace/Districts/NightGardenD15SpecialtyReceiving20261020")
 var original_d15_count:=0
 for entry:Dictionary in manager.entries:
  var home:Node=entry.home.get_ref()
  if home!=null and home.get_parent()==original_d15:original_d15_count+=1
 check(original_d15_count==30,"OriginalNightGarden30 registrations retained")
 var state:=ship.get_world_3d().direct_space_state
 var excluded:Array[RID]=[]
 for body in ship.find_children("*","CharacterBody3D",true,false):excluded.append(body.get_rid())
 for body in ship.find_children("*","RigidBody3D",true,false):excluded.append(body.get_rid())
 var points:Array[Vector3]=[];var threshold_points:Array[Vector3]=[]
 for region:Dictionary in plan.regions:
  var z0:float=region.rings[0][0][1];var z1:float=region.rings[0][2][1];var y:float=region.floor_y
  # Continuous new street and both sides of its original/new join.
  var steps:=ceili(absf(z1-z0)/1.0)
  for i in range(steps+1):points.append(Vector3(84,y,lerpf(z0+.5,z1-.5,float(i)/steps)))
  var join:float=z1 if z1<0 else z0
  for delta in [-.1,.1]:points.append(Vector3(84,y,join+delta))
 var rests:={};var doors:={};var records:Array=[];var windows:=0;var expected_windows:=0
 for room:Dictionary in package.rooms:
  expected_windows+=room.parts.filter(func(part):return part.get("category","")=="window").size()
  var home:Node3D=district.get_node(room.allocation.proposed_runtime_id)
  var entries:Array=manager.entries.filter(func(e):return e.home.get_ref()==home)
  check(entries.size()==1 and entries[0].record==index[room.model_file],"Exact manager record "+str(room.allocation.source_envelope_index))
  check(home.get_meta("rest_slot_ids")==room.allocation.proposed_rest_slot_ids and not home.get_meta("species_ready"),"Retained rest IDs and operating hold")
  for id:String in home.get_meta("rest_slot_ids"):check(not rests.has(id),"Unique rest "+id);rests[id]=true
  for data:Dictionary in room.doors:
   var door:=home.get_node(data.name)
   check(str(door.persistent_id)==data.persistent_id and not doors.has(data.persistent_id),"Exact unique door "+data.persistent_id);doors[data.persistent_id]=true
  var a:Dictionary=room.allocation;var z:float=(a.allocation_z[0]+a.allocation_z[1])*.5;var y:float=a.floor_y;var front:float=a.historical_door_marker_xz[0];var direction:=1.0 if front>84 else -1.0
  for x in [84.0,front-direction*.35,front,front+direction*.55]:
   var point:=Vector3(x,y,z);points.append(point);threshold_points.append(point)
  var shell:Node3D=home.get_children().filter(func(c):return c.scene_file_path==str(index[room.model_file].shell_path))[0]
  var floor:MeshInstance3D=home.get_node(home.get_meta("retained_floor_owner"))
  check(absf((floor.global_transform*floor.get_aabb()).end.y-y)<.0002,"Original room-floor top unchanged")
  for mesh:MeshInstance3D in shell.find_children("*","MeshInstance3D",true,false):
   if mesh.get_meta("extras",{}).get("construction_role","")!="window":continue
   windows+=1
   var material:=mesh.material_override as ShaderMaterial
   var plane:float=(mesh.global_transform*mesh.get_aabb()).get_center().x
   var center:float=(a.allocation_x[0]+a.allocation_x[1])*.5
   check(material!=null and material.shader.resource_path=="res://night_garden_view_galleries_20261022/private_view.gdshader" and absf(float(material.get_shader_parameter("plane_x"))-plane)<.0001 and float(material.get_shader_parameter("interior_sign"))==signf(center-plane),"Actual outward-opaque private pane orientation")
  records.append({"id":int(a.source_envelope_index),"room_id":home.name,"floor_owner":home.get_meta("retained_floor_owner"),"door_source_open_pose_unchanged":true})
 for point:Vector3 in points:
  var query:=PhysicsRayQueryParameters3D.create(point+Vector3.UP*.15,point-Vector3.UP*.35);query.exclude=excluded
  var hit:=state.intersect_ray(query)
  check(not hit.is_empty() and absf(hit.position.y-point.y)<.015,"Connected floor at "+str(point)+" hit="+str(hit.get("position","none")))
  var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8
  var sweep:=PhysicsShapeQueryParameters3D.new();sweep.shape=shape;sweep.margin=.001;sweep.exclude=excluded;sweep.transform.origin=point+Vector3.UP*.925
  var hits:=state.intersect_shape(sweep,8);var names:Array=[]
  for h in hits:names.append(str(h.collider.get_path()))
  check(hits.is_empty(),"Connected public/entry clearance at "+str(point)+" "+str(names))
 check(rests.size()==19 and doors.size()==53 and windows==expected_windows,"19 rests, 53 doors and every source-authored privacy pane")
 var budget:=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 check(budget.shadow_source_budget==8 and budget.previously_active.size()<=8,"Existing light budget unchanged")
 # One near/far detail transition in each deck through the unchanged manager.
 # The already-passed17-room isolated cycle suite is not repeated.
 for number in [100,380]:
  var room:Dictionary=package.rooms.filter(func(r):return int(r.allocation.source_envelope_index)==number)[0]
  var home:=district.get_node(room.allocation.proposed_runtime_id)
  var entry:Dictionary=manager.entries.filter(func(e):return e.home.get_ref()==home)[0]
  manager._load_entry(entry);check(is_instance_valid(entry.detail),"Connected detail loads "+str(number));manager._release_entry(entry)
  check(not is_instance_valid(entry.detail)and home.has_node(home.get_meta("retained_floor_owner")),"Shell/floor stays after detail release "+str(number))
 var result:={"status":"PASS"if failures.is_empty()else"FAIL","checks":checks,"rooms":17,"reserved_rests":19,"door_ids":53,"privacy_panes":windows,"new_capacity":0,"new_private_floors":0,"street_area_m2":273.06,"floor_clearance_points":points.size(),"threshold_points":threshold_points.size(),"original_ordinary_homes":received_count,"original_d15_rooms":original_d15_count,"records":records,"failures":failures,"actual_main_runtime_ready":true,"primary_structure_accepted":false,"final_visual_accepted":false,"full_gameplay_performance_accepted":false,"scope":"Actual complete current ship; changed street joins/entry thresholds, source identity, private-pane orientation, persistent floor and representative detail lifecycle. No standalone fixture, hull cuts, repeated cart tests or claimed whole-ship acceptance."}
 FileAccess.open(P+"evidence/INTEGRATION.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  ")+"\n");print("NIGHT_GARDEN_LOWER_INTEGRATION ",JSON.stringify(result))
 main.free();await process_frame;quit(0 if failures.is_empty()else 1)
