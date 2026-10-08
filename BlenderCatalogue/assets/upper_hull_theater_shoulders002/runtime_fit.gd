extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
 for i in range(30):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea")
 var source:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/scratch/375c2e438292/upper_hull_theater_full_shoulders002/EXACT_MITER_VERTICES.json"))
 var excluded:Array[RID]=[]
 var owned:Node=ship.get_node("ShipSpace/Districts/TheaterWestUpperHull_Skin_WIP")
 for body in owned.find_children("*","StaticBody3D",true,false):excluded.append(body.get_rid())
 var contacts:Array=[]
 for index in range(source.outer_triangles.size()):
  var ids:Array=source.outer_triangles[index]
  var points:=PackedVector3Array()
  for table in [source.outer_vertices_world,source.inner_vertices_world]:
   for i in ids:
    var p:Array=table[int(i)];points.append(Vector3(p[0],p[1],p[2]))
  var shape:=ConvexPolygonShape3D.new();shape.points=points
  var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.exclude=excluded;q.collision_mask=1
  for hit in ship.get_world_3d().direct_space_state.intersect_shape(q,256):contacts.append({"facet":index,"collider":str(hit.collider.get_path())})
 var out:Dictionary={"checked_actual_source_facet_prisms":source.outer_triangles.size(),"excluded_only_existing_owned_skin_bodies":excluded.size(),"contacts":contacts,"candidate_installed":false,"source_inner_miter_max_normal":source.normal_skin_max_at_miter}
 var f:=FileAccess.open("/workspace/scratch/375c2e438292/upper_hull_theater_full_shoulders002/RUNTIME_FIT.json",FileAccess.WRITE);f.store_string(JSON.stringify(out,"  "))
 if contacts.is_empty():print("FULL THEATER SHOULDER PHYSICS FIT PASS")
 else:print("FULL THEATER SHOULDER CONTACT HOLD: ",JSON.stringify(contacts))
 main.queue_free();await process_frame;quit(0 if contacts.is_empty()else 1)
