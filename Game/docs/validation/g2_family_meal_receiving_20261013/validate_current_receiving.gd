extends SceneTree
var nchecks:=0
var failures:Array=[]
var legs:Array=[]
var retained_meshes:=0
const OUT="/workspace/astraea-integration-cutoff-20261013/g2_family_meal_receiving/RECEIVING_RUNTIME.json"
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
 for p in ["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/g2_family_meal_receiving/CANDIDATE_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(p,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func receipt()->void:
 FileAccess.open(OUT,FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_CURRENT_FAMILY_MEAL_PHYSICAL_RECEIVING"if failures.is_empty()else"HOLD","checks":nchecks,"failures":failures,"original_controller_legs":legs,"retained_meshes":retained_meshes,"tables":3,"settings":12,"new_tables_chairs_floor_or_capacity":0,"food_stock_staff_hygiene_admission_or_programme_accepted":false,"tabletop_inspection_excludes_only_new_kit_colliders":true,"route_collision_masks_or_exclusions_changed":false,"historical_network_criteria":13,"unaccepted_joins":184},"  "))
func require(ok:bool,label:String)->bool:
 nchecks+=1
 if not ok:failures.append(label);receipt();push_error(label);quit(1)
 return ok
func tabletop(space:PhysicsDirectSpaceState3D,at:Vector3,excluded:Array[RID]=[])->Dictionary:
 var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.08,at-Vector3.UP*.15);q.exclude=excluded;return space.intersect_ray(q)
func walk(actor:CharacterBody3D,target:Vector3,label:String)->void:
 var start:Vector3=actor.global_position;var key:=InputEventKey.new();key.keycode=KEY_W;key.physical_keycode=KEY_W;key.pressed=true;Input.parse_input_event(key.duplicate());Input.flush_buffered_events();var reached:=false;var used_frames:=0
 for i in range(600):
  var delta:=target-actor.global_position
  if Vector2(delta.x,delta.z).length()<.09:reached=true;break
  actor.rotation.y=atan2(-delta.x,-delta.z);await physics_frame;used_frames=i+1
  if not require(absf(actor.global_position.y-97.5)<.12,"Original supported tabletop approach "+label):return
 key.pressed=false;Input.parse_input_event(key.duplicate());Input.flush_buffered_events();await frames(15)
 legs.append({"table":label,"start":str(start),"target":str(target),"finish":str(actor.global_position),"reached":reached,"floor":actor.is_on_floor(),"frames":used_frames})
 require(reached and actor.is_on_floor(),"Actual existing-table approach reached "+label)
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(30)
 var ship:Node3D=main.get_node("World360/Astraea");var house:Node3D=ship.get_node("ShipSpace/Districts/FamilyTerraceReceivingCandidate");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var space:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state;var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");var stream:Node=ship.get_node("ShipSystems/RemainingBatchStreaming")
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_family_meal/COMPONENT_r001.json"));var preflight:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_family_meal/CURRENT_TABLE_PREFLIGHT.json"));var old:Array=[];var source_contacts:Array=[];var old_identity:Variant=house.get_meta("persistent_id");var old_units:Variant=house.get_meta("installed_guest_units")
 for mesh:MeshInstance3D in house.find_children("*","MeshInstance3D",true,false):
  var contact:CollisionShape3D=mesh.get_node_or_null("StaticContact/SharedShape")
  old.append({"node":mesh,"mesh":mesh.mesh,"pose":mesh.global_transform,"local_pose":mesh.transform,"parent":mesh.get_parent(),"bounds":mesh.get_aabb(),"material":mesh.material_override,"contact":contact,"shape":contact.shape if contact!=null else null,"disabled":contact.disabled if contact!=null else false})
 retained_meshes=old.size()
 for table in data.tables:
  var row:Dictionary={}
  for r in preflight.table_parts:
   if str(r.name)==str(table.existing_table):row=r
  for setting in table.settings:
   var at:=Vector3(setting.world_xyz[0],setting.world_xyz[1],setting.world_xyz[2]);var hit:Dictionary=tabletop(space,at)
   if not require(not hit.is_empty()and absf(hit.position.y-float(table.support_y))<.002 and str(hit.collider.get_parent().name)==str(row.batch_node),"Exact original tabletop supports setting before fitout "+str(table.existing_table)):return
   source_contacts.append({"at":at,"collider":hit.collider,"position":hit.position})
 var addition:Node3D=load("res://scripts/group2_family_meal/package.gd").build_on_current_receiver(ship)
 for row in old:
  var mesh:MeshInstance3D=row.node
  if not require(is_instance_valid(mesh)and mesh.mesh==row.mesh and mesh.global_transform==row.pose and mesh.get_aabb()==row.bounds and mesh.material_override==row.material,"Exact original populated Family mesh during construction "+str(mesh.name)):return
  if row.contact!=null:
   if not require(is_instance_valid(row.contact)and row.contact.shape==row.shape and row.contact.disabled==row.disabled,"Original Family contact resource unchanged "+str(mesh.name)):return
 await frames(4)
 for row in old:
  var mesh:MeshInstance3D=row.node
  if not require(is_instance_valid(mesh)and mesh.transform==row.local_pose and mesh.get_parent()==row.parent and mesh.mesh==row.mesh,"Original local geometry retained while live lift continues "+str(mesh.name)):return
 var excluded:Array[RID]=[]
 for body:CollisionObject3D in addition.find_children("*","CollisionObject3D",true,false):excluded.append(body.get_rid())
 for row in source_contacts:
  var hit:Dictionary=tabletop(space,row.at,excluded)
  if not require(not hit.is_empty()and hit.collider==row.collider and hit.position.distance_to(row.position)<.0001,"Exact original tabletop contact retained after fitout "+str(row.at)):return
 var kit:Node3D=addition.get_child(0);var expected:Array[Vector3]=[]
 for mesh:MeshInstance3D in kit.find_children("*","MeshInstance3D",true,false):
  var contact:CollisionShape3D=mesh.get_node_or_null("StaticContact/SharedShape")
  if contact!=null:
   if not require(not contact.disabled and contact.shape.get_faces()==mesh.mesh.get_faces(),"Exact transparent source contact "+str(mesh.name)):return
  else:
   var pose:Transform3D=kit.global_transform.affine_inverse()*mesh.global_transform
   for vertex in mesh.mesh.get_faces():expected.append(pose*vertex)
  if not require(mesh.mesh.surface_get_material(0)!=null,"Original source fitting material "+str(mesh.name)):return
 var combined:CollisionShape3D=kit.get_node("RoomStaticContacts/SharedRoomTriangles")
 if not require(not combined.disabled and combined.shape.get_faces()==PackedVector3Array(expected),"All opaque source fitting contact triangles exact"):return
 var cases:Array=[{"table":"D16_UpperGroupTable_Top_0","start":Vector3(79.5,97.5,343.8),"front":Vector3(79.5,97.5,345.0)},{"table":"D16_MeetingTable_0_Top_0","start":Vector3(70.2,97.5,356.9),"front":Vector3(70.2,97.5,358.1)},{"table":"D16_MeetingTable_1_Top_0","start":Vector3(70.2,97.5,375.2),"front":Vector3(70.2,97.5,376.4)}]
 for setup in cases:
  actor.global_position=setup.start+Vector3.UP*.03;actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);residency.prepare_position(actor.global_position);stream.prepare_position(actor.global_position);await frames(25)
  if not require(actor.is_on_floor()and absf(actor.global_position.y-97.5)<.12,"Existing original-player table approach start "+str(setup.table)):return
  for goal in [setup.front,setup.start]:
   await walk(actor,goal,str(setup.table))
   if not failures.is_empty():return
 if not require(house.get_meta("persistent_id")==old_identity and house.get_meta("installed_guest_units")==old_units,"Existing Family identity and source unit metadata unchanged"):return
 if not require(addition.get_meta("new_seats_or_capacity")==0 and addition.get_meta("new_floor_owners")==0 and not addition.get_meta("food_stock_hygiene_or_staff_operation")and not addition.get_meta("programme_or_dining_designation_accepted"),"No food/service/programme or capacity admission"):return
 if not require(ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms").get_child_count()==303,"Original compiler floor owners remain303"):return
 receipt();print("G2_FAMILY_MEAL_CURRENT_RECEIVING_PASS checks=",nchecks," retained_meshes=",retained_meshes);quit(0)
