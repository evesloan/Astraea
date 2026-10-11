extends SceneTree
func _initialize():call_deferred("run")
func run():
 var main=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship=main.get_node("World360/Astraea");var space=ship.get_world_3d().direct_space_state;var rows=[]
 var ats=[]
 for z in [-100.6,-95,-85,-75,-71.6,-63.2,-53,-43.2,-32,-15,0,15,32,43.2,57.6,70,78]:ats.append(Vector3(-104,16.5,z))
 for x in [-101,-98,-94,-90,-86,-82,-78,-74,-70,-66]:ats.append(Vector3(x,16.5,-100.6))
 for a in ats:
  var cap=CapsuleShape3D.new();cap.height=1.8;cap.radius=.3;cap.margin=.001;var q=PhysicsShapeQueryParameters3D.new();q.shape=cap;q.transform=Transform3D(Basis.IDENTITY,a+Vector3.UP*.925);var hits=space.intersect_shape(q,64)
  var ray=PhysicsRayQueryParameters3D.create(a-Vector3.UP*.25,a-Vector3.UP*30);ray.hit_back_faces=true;var h=space.intersect_ray(ray)
  rows.append({"at":[a.x,a.y,a.z],"blockers":hits.map(func(x):return str(x.collider.get_path())),"support":{}if h.is_empty()else{"at":[h.position.x,h.position.y,h.position.z],"owner":str(h.collider.get_path())}})
 FileAccess.open("res://../BlenderCatalogue/assets/d04_port_central_west_staff_circuit_20261011/PERIMETER_PREFLIGHT.json",FileAccess.WRITE).store_string(JSON.stringify(rows,"  "));print("Perimeter preflight complete");quit()
