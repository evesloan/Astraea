extends SceneTree
const D="/workspace/cinema6-evidence/"
func _initialize()->void:call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(60)
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
 actor.set_physics_process(false);actor.global_position=Vector3(16,69.53,464.0)
 ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
 ship.get_node("ShipSystems/RemainingBatchStreaming").prepare_position(actor.global_position)
 await frames(8)
 var cafe:Node3D=ship.get_node("ShipSpace/Districts/ReceivedSections/D11_directory_07")
 var space:=ship.get_world_3d().direct_space_state;var samples:Array=[]
 for z in [458.0,459.0,461.0,461.5,462.5,464.0,465.0,466.0]:
  for x in [2.,4.,6.,8.,10.,11.,12.,16.,32.,36.,40.,52.,56.]:
   var at:=Vector3(x,69.5,z);var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.03,at-Vector3.UP*.1);q.exclude=[actor.get_rid()];var floor:=space.intersect_ray(q)
   var sq:=PhysicsShapeQueryParameters3D.new();var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8;sq.shape=capsule;sq.margin=.001;sq.transform.origin=at+Vector3.UP*.925;sq.exclude=[actor.get_rid()];var contacts:Array=[]
   for h in space.intersect_shape(sq,32):contacts.append(str(h.collider.get_path()))
   samples.append({"at":[x,69.5,z],"floor":str(floor.collider.get_path())if not floor.is_empty()else"","floor_y":float(floor.position.y)if not floor.is_empty()else null,"body_contacts":contacts})
 var meshes:Array=[]
 for mesh:MeshInstance3D in ship.find_children("*","MeshInstance3D",true,false):
  var b:AABB=mesh.global_transform*mesh.get_aabb()
  if b.end.y>=69 and b.position.y<=74 and b.end.z>=458.0 and b.position.z<=467.0 and b.end.x>=0 and b.position.x<=61:
   meshes.append({"path":str(mesh.get_path()),"min":[b.position.x,b.position.y,b.position.z],"max":[b.end.x,b.end.y,b.end.z]})
 var report:Dictionary={"commit":"bb810fab4f1e1db7543d8f64852f9b927b5b54c6","scope":"Unchanged current-main geometry survey; no walking or operational acceptance","cafe_meshes":cafe.find_children("*","MeshInstance3D",true,false).size(),"samples":samples,"nearby_meshes":meshes}
 FileAccess.open(D+"CINEMA6_CURRENT_MAIN_SURVEY.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("CINEMA6_CURRENT_MAIN_SURVEY_COMPLETE ",samples.size()," samples ",meshes.size()," nearby meshes");quit(0)
