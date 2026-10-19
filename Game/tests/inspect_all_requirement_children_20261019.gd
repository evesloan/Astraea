extends SceneTree
# Read-only, all mesh children including metadata-free geometry; does not force residency.
var seen:Dictionary={}
var rows:Array=[]
func _initialize()->void:call_deferred("run")
func scan(n:Node,p:String)->void:
 if seen.has(n.get_instance_id()):return
 seen[n.get_instance_id()]=true
 if n is MeshInstance3D or n is MultiMeshInstance3D:
  var r:Dictionary={"path":p,"class":n.get_class(),"attached":n.is_inside_tree()}
  if n is MultiMeshInstance3D:r["instances"]=n.multimesh.instance_count if n.multimesh else 0
  if not n.scene_file_path.is_empty():r["scene_source"]=n.scene_file_path
  rows.append(r)
 for c in n.get_children():scan(c,p+"/"+str(c.name))
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(60):await physics_frame
 var ship:Node=main.get_node("World360/Astraea")
 assert(ship.get_node("ReceivedSectionInstallation").get_meta("installation_ready",false))
 scan(ship,"")
 var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
 for e in residency.entries:scan(e.room,str(ship.get_path_to(e.parent))+"/"+str(e.room.name))
 var d:Dictionary={"base_commit":"042c4bb2f2d0e6ac11ac0eee8ac6738e48d163b6","scope":"Every actual MeshInstance3D and MultiMeshInstance3D in current main and cached rooms; deferred uninstantiated visuals not forced or classified absent.","visited_nodes":seen.size(),"rows":rows,"residency":residency.statistics()}
 FileAccess.open("/workspace/full-requirement-reconciliation-20261019/ALL_CHILD_MESHES.json",FileAccess.WRITE).store_string(JSON.stringify(d))
 print("ALL_REQUIREMENT_CHILDREN visited=",seen.size()," mesh_nodes=",rows.size())
 quit()
