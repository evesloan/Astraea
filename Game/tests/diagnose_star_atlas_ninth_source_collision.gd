extends SceneTree
func _initialize():call_deferred("run")
func run():
 var main=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(90):await physics_frame
 paused=true
 var ship=main.get_node("World360/Astraea");var space=ship.get_world_3d().direct_space_state;var excluded:Array[RID]=[]
 for name in ["StarAtlasSpecialtyNinthCandidates","StarAtlasSpecialtyNinthReceiving"]:
  for body in ship.get_node("ShipSpace/Districts/"+name).find_children("*","StaticBody3D",true,false):excluded.append(body.get_rid())
 var floor=ship.get_node("ShipSpace/CentralResidentialStreetFloors/D13_STAR_ATLAS_MISSING_STREET_0")
 for c in floor.get_children():
  if c is StaticBody3D:
   var shape=c.get_child(0).shape;var lo=Vector3(INF,INF,INF);var hi=Vector3(-INF,-INF,-INF)
   for v in shape.get_faces():lo=lo.min(v);hi=hi.max(v)
   print("SOURCE_COLLIDER ",lo," ",hi," faces ",shape.get_faces().size()," backface ",shape.backface_collision)
 for ray in [[Vector3(-84,83.785,-71.6),Vector3(-84,83.735,-71.6)],[Vector3(-84,83.735,-71.6),Vector3(-84,83.785,-71.6)],[Vector3(-84,84.025,-71.6),Vector3(-84,83.975,-71.6)]]:
  var q=PhysicsRayQueryParameters3D.create(ray[0],ray[1]);q.exclude=excluded;q.hit_back_faces=true;print("DIRECT_SOURCE_RAY ",ray," ",space.intersect_ray(q))
 quit()
