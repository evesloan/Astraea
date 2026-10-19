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
 var records:Array=[]
 for mesh:MeshInstance3D in ship.find_children("*","MeshInstance3D",true,false):
  var b:AABB=mesh.global_transform*mesh.get_aabb()
  if b.intersects(AABB(Vector3(59,97.2,-73),Vector3(29,10,135))):
   records.append({"path":str(mesh.get_path()),"min":[b.position.x,b.position.y,b.position.z],"max":[b.end.x,b.end.y,b.end.z],"visible":mesh.visible})
 var space:=ship.get_world_3d().direct_space_state
 var samples:Array=[]
 for z in [-71.4,-64.2,-57.0,-49.8,-42.6,-35.8,32.2,39.4,46.6,53.8,60.6]:
  samples.append({"xz":[85.82,z],"bearing":hit(space,Vector3(85.82,97.55,z),Vector3(85.82,97.2,z),actor.get_rid()),"upper_clear":hit(space,Vector3(85.82,101.8,z),Vector3(85.82,97.55,z),actor.get_rid())})
 FileAccess.open("/workspace/d17-starboard-integration/SURVEY.json",FileAccess.WRITE).store_string(JSON.stringify({"meshes":records,"bearing_samples":samples},"  "))
 print("D17_STARBOARD_SURVEY_COMPLETE ",records.size());quit()
