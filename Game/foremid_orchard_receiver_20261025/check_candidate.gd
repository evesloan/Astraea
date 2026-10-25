extends SceneTree
var world:Node3D
var count:=0
func _initialize()->void:call_deferred("run")
func raw(path:String,offset:Vector3)->Node3D:
 var doc:=GLTFDocument.new();var state:=GLTFState.new()
 assert(doc.append_from_file(ProjectSettings.globalize_path(path),state)==OK)
 var node:Node3D=doc.generate_scene(state);world.add_child(node);node.position=offset
 for mesh:MeshInstance3D in node.find_children("*","MeshInstance3D",true,false):mesh.create_trimesh_collision()
 return node
func require(ok:bool,label:String)->void:
 assert(ok,label);count+=1
func query(center:Vector3,size:Vector3)->Array:
 var shape:=BoxShape3D.new();shape.size=size
 var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform.origin=center;q.margin=0
 return world.get_world_3d().direct_space_state.intersect_shape(q,128)
func run()->void:
 world=Node3D.new();root.add_child(world)
 var c:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://foremid_orchard_receiver_20261025/RECEIVER_r003.json"))
 for p:String in c.source_pins:require(FileAccess.get_sha256("res://"+p.trim_prefix("Game/"))==c.source_pins[p],"Immutable source pin: "+p)
 var candidate:=raw("res://foremid_orchard_receiver_20261025/ForemidOrchardReceiver_r003.glb",Vector3.ZERO)
 raw("res://source_derivatives/group4_completion_20261011/AST-TRM-G4-020_foremid_north_candidate.glb",Vector3.ZERO)
 raw("res://assets/models/AST-RTL-009.glb",Vector3(4,52.5,-250))
 require(candidate.find_children("*","MeshInstance3D",true,false).size()==90,"Every candidate member survives")
 for i in 3:await physics_frame
 for p:Dictionary in c.parts:
  if not str(p.name).begins_with("UpWest_") and not str(p.name).begins_with("UpEast_"):continue
  var center:=Vector3((p.lo[0]+p.hi[0])/2,p.hi[1],(p.lo[2]+p.hi[2])/2)
  var ray:=PhysicsRayQueryParameters3D.create(center+Vector3.UP*.03,center-Vector3.UP*.03)
  var hit:=world.get_world_3d().direct_space_state.intersect_ray(ray)
  require(not hit.is_empty() and abs(hit.position.y-center.y)<.002,"Real tread contact: "+str(p.name))
 # 4m clear bridge air, including retained source contacts. The existing route
 # slab itself is not loaded here; its seam remains a separate installed gate.
 require(query(Vector3(-5.9,63.005,-235.2),Vector3(3.78,4,4)).is_empty(),"Four metre receiving air envelope")
 var entry:=query(Vector3(-13.29,57.1,-256.4),Vector3(.20,1.8,2.4))
 var blockers:Array[String]=[]
 for h:Dictionary in entry:blockers.append(str(h.collider.get_parent().name))
 require(not blockers.is_empty(),"Retained guard must remain present until fitted successor")
 var report:Dictionary={"checks":count,"candidate_only":true,"tread_contacts":28,"receiving_air_m":4,"blocked_old_guard_members":blockers,"installed":false,"operation_admitted":false,"limits":"Subset source geometry only; no full vehicle sweep, third lift stop, whole-world neighbors, structural engineering, actual camera or scenic acceptance."}
 print("ORCHARD_RECEIVER_RESULT ",JSON.stringify(report))
 world.queue_free();await process_frame;quit(0)
