extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
 for i in range(30):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea")
 var box:=AABB(Vector3(-118.5,74.5,-250),Vector3(.8,13,90))
 var hits:Array=[]
 var count:=0
 for mesh in ship.find_children("*","MeshInstance3D",true,false):
  if mesh.mesh==null:continue
  count+=1
  if not box.intersects(mesh.global_transform*mesh.get_aabb()):continue
  var triangles:=0
  var faces:PackedVector3Array=mesh.mesh.get_faces()
  for j in range(0,faces.size(),3):
   var a:Vector3=mesh.global_transform*faces[j]
   var t:=AABB(a,Vector3.ZERO)
   t=t.expand(mesh.global_transform*faces[j+1]);t=t.expand(mesh.global_transform*faces[j+2])
   if box.intersects(t):triangles+=1
  if triangles>0:hits.append({"path":str(mesh.get_path()),"triangle_aabb_candidates":triangles,"visible":mesh.is_visible_in_tree()})
 var q:=PhysicsShapeQueryParameters3D.new();var shape:=BoxShape3D.new();shape.size=box.size;q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,box.get_center());q.collision_mask=1
 var contacts:Array=[]
 for h in ship.get_world_3d().direct_space_state.intersect_shape(q,256):contacts.append(str(h.collider.get_path()))
 var mm_hits:Array=[]
 for mm in ship.find_children("*","MultiMeshInstance3D",true,false):
  if mm.multimesh==null:continue
  for j in range(mm.multimesh.instance_count):
   if box.intersects(mm.global_transform*mm.multimesh.get_instance_transform(j)*mm.multimesh.mesh.get_aabb()):mm_hits.append({"path":str(mm.get_path()),"instance":j})
 var out:Dictionary={"checked_meshes":count,"mesh_triangle_candidates":hits,"physics_contacts":contacts,"multimesh_aabb_candidates":mm_hits,"new_geometry_installed":false}
 var f:=FileAccess.open("/workspace/scratch/375c2e438292/upper_hull_theater_source_20261008/RUNTIME_CENSUS.json",FileAccess.WRITE);f.store_string(JSON.stringify(out,"  ")+"\n")
 print("UPPER HULL CENSUS COMPLETE: ",JSON.stringify(out))
 main.queue_free();await process_frame;quit()
