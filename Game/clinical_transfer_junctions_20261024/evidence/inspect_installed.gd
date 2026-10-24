extends SceneTree
func _initialize()->void:call_deferred("run")
func a(p:Vector3)->Array:return[p.x,p.y,p.z]
func run()->void:
 var main:Node=load("res://scenes/main_clinical_return_links_integrated_20261024.tscn").instantiate();root.add_child(main);var ship:Node3D=main.get_node("World360/Astraea")
 while not ship.get_meta("runtime_ready",false):await process_frame
 for i in range(5):await physics_frame
 paused=true
 var manager:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
 for entry:Dictionary in manager.entries:
  if str(entry.room.name).begins_with("D05_directory_")and not entry.attached:manager._attach_visible_room(entry)
 for i in range(3):await physics_frame
 var space:=ship.get_world_3d().direct_space_state;var rows:Array=[];var owners:={};var excluded:Array[RID]=[]
 for body:CollisionObject3D in ship.get_node("ShipSpace/PersistentActors").find_children("*","CollisionObject3D",true,false):excluded.append(body.get_rid())
 var samples:Array=[]
 for z in range(14,39):samples.append(["D06 clean offset",Vector3(102.6,21,z),Vector3(3.6,3.2,.2)])
 for z in range(22,31):samples.append(["D06 receiver turn",Vector3(94,21,z),Vector3(3.6,3.1,.2)])
 for x in range(94,112):samples.append(["D06 transverse",Vector3(x,21,22),Vector3(.2,3.1,3.6)])
 for z in range(-413,-389):
  for x in [-63.4,-57.0]:samples.append(["D01 junction",Vector3(x,21,z),Vector3(3.6,3.2,.2)])
 for z in [-402,-394,-390]:
  for x in range(-65,-47):samples.append(["D01 transverse",Vector3(x,21,z),Vector3(.2,3.2,3.6)])
 for s:Array in samples:
  var point:Vector3=s[1];var box:=BoxShape3D.new();box.size=s[2];var query:=PhysicsShapeQueryParameters3D.new();query.shape=box;query.margin=.001;query.transform.origin=point+Vector3.UP*1.62;query.exclude=excluded;var hits:=space.intersect_shape(query,32);var blockers:Array=[]
  for hit:Dictionary in hits:
   var node:Node=hit.collider;var name:String=str(node.get_path());blockers.append(name)
   if not owners.has(name):
    var mesh:Node=node.get_parent();var bounds:Variant=null
    if mesh is MeshInstance3D:bounds=mesh.global_transform*mesh.get_aabb()
    owners[name]={"class":node.get_class(),"mesh_parent":str(mesh.name),"bounds":[a(bounds.position),a(bounds.end)]if bounds!=null else[],"mesh_path":str(ship.get_path_to(mesh)),"faces":mesh.mesh.get_faces().size()/3 if mesh is MeshInstance3D else -1}
  var ray:=PhysicsRayQueryParameters3D.create(point+Vector3.UP*.15,point-Vector3.UP*.5);ray.exclude=excluded;var floor:Dictionary=space.intersect_ray(ray)
  rows.append({"zone":s[0],"point":a(point),"blockers":blockers,"floor":str(floor.collider.get_path())if not floor.is_empty()else"","floor_y":floor.position.y if not floor.is_empty()else null})
 var result:={"scope":"Actual selected ship; 3.6m width/3.2m height envelope at candidate outer corridors. Design survey, not route acceptance.","samples":rows,"owners":owners}
 FileAccess.open("res://clinical_transfer_junctions_20261024/evidence/INSTALLED_NEIGHBORS.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  ")+"\n")
 print("TRANSFER_NEIGHBOR_SURVEY ",rows.size()," samples ",owners.size()," contact owners");main.free();await process_frame;quit(0)
