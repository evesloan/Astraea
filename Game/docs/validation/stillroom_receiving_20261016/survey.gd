extends SceneTree
const D="/workspace/stillroom-evidence/"
func _initialize()->void:call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(60)
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
 actor.set_physics_process(false);actor.global_position=Vector3(14,78.03,-193)
 ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
 ship.get_node("ShipSystems/RemainingBatchStreaming").prepare_position(actor.global_position)
 await frames(8)
 var cafe:Node3D=ship.get_node("ShipSpace/Districts/StillroomReceiving_WIP")
 var space:=ship.get_world_3d().direct_space_state;var samples:Array=[]
 for z in [-204.,-201.,-198.,-196.,-194.,-193.,-192.,-190.6,-188.,-185.1]:
  for x in [2.,4.,6.,7.8,8.,9.,10.,11.,14.,16.,16.3,18.]:
   var at:=Vector3(x,78.0,z);var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.03,at-Vector3.UP*.1);q.exclude=[actor.get_rid()];var floor:=space.intersect_ray(q)
   var sq:=PhysicsShapeQueryParameters3D.new();var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8;sq.shape=capsule;sq.margin=.001;sq.transform.origin=at+Vector3.UP*.925;sq.exclude=[actor.get_rid()];var contacts:Array=[]
   for h in space.intersect_shape(sq,32):contacts.append(str(h.collider.get_path()))
   samples.append({"at":[x,78.0,z],"floor":str(floor.collider.get_path())if not floor.is_empty()else"","floor_y":float(floor.position.y)if not floor.is_empty()else null,"body_contacts":contacts})
 var meshes:Array=[]
 for mesh:MeshInstance3D in ship.find_children("*","MeshInstance3D",true,false):
  var b:AABB=mesh.global_transform*mesh.get_aabb()
  if b.end.y>=77.5 and b.position.y<=83 and b.end.z>=-204 and b.position.z<=-182 and b.end.x>=0 and b.position.x<=20:
   meshes.append({"path":str(mesh.get_path()),"min":[b.position.x,b.position.y,b.position.z],"max":[b.end.x,b.end.y,b.end.z]})
 var report:Dictionary={"commit":"ab3b5b7d6427d651fb4976c1cb3198e52a2dc15a","scope":"Unchanged current-main geometry survey; no walking or operational acceptance","cafe_meshes":cafe.find_children("*","MeshInstance3D",true,false).size(),"samples":samples,"nearby_meshes":meshes}
 FileAccess.open(D+"STILLROOM_CURRENT_MAIN_SURVEY.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("STILLROOM_CURRENT_MAIN_SURVEY_COMPLETE ",samples.size()," samples ",meshes.size()," nearby meshes");quit(0)
