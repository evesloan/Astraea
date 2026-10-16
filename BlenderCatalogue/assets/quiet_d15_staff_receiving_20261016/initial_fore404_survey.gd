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
 var space:=ship.get_world_3d().direct_space_state;var rows:Array=[]
 actor.global_position=Vector3(63,93.03,-404);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position);ship.get_node("ShipSystems/RemainingBatchStreaming").prepare_position(actor.global_position);await frames(3)
 for z in [-408.0,-406.0,-404.0,-402.0,-400.0,-396.0,-392.0,-388.0,-384.0]:
  for x in [54.0,56.0,58.0,60.0,60.5,61.0,62.0,63.0,64.0,65.0,66.0]:
   rows.append({"xz":[x,z],"floor":hit(space,Vector3(x,93.05,z),Vector3(x,92.7,z),actor.get_rid()),"lower":hit(space,Vector3(x,92.7,z),Vector3(x,88.0,z),actor.get_rid())})
 var meshes:Array=[]
 for m:MeshInstance3D in ship.find_children("*","MeshInstance3D",true,false):
  if m.mesh==null:continue
  var b:AABB=m.global_transform*m.get_aabb()
  if b.intersects(AABB(Vector3(54,92.7,-408),Vector3(13,3.7,25))):meshes.append({"path":str(m.get_path()),"min":[b.position.x,b.position.y,b.position.z],"max":[b.end.x,b.end.y,b.end.z]})
 FileAccess.open("/workspace/quiet-d15-receiving/CURRENT_INTERFACE_SURVEY.json",FileAccess.WRITE).store_string(JSON.stringify({"base_commit":"38c69e9f8b9a33e47ada9557de570509d035d32e","samples":rows,"nearby_meshes":meshes,"scope":"Physical Quiet Grove D15 to retained fore-starboard staff landing interface survey; no operation or absence proof"},"  "));print("QUIET_D15_INTERFACE_SURVEY_COMPLETE ",meshes.size());quit()
