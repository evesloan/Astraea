extends "res://tests/validate_crown_access.gd"
func run()->void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
	for frame in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	assert(ship.find_child("BridgePlatform_WIP",true,false)!=null)
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/BRIDGE_PLATFORM_RUNTIME.json"))
	assert(data.doors.is_empty(),"Stage1 has no private enclosure across the original route")
	actor.set_physics_process(false);actor.position=Vector3(0,106.6,-190);actor.velocity=Vector3.ZERO
	# The original path stays physically open while the replacement is proven.
	await walk_route(actor,[Vector2(0,-111),Vector2(5.5,-111),Vector2(5.5,-77),Vector2(-44,-77),Vector2(-44,-177),Vector2(0,-177),Vector2(0,-190)])
	# Then walk the public bypass forward to the existing core without taking the future bridge floor.
	await walk_route(actor,[Vector2(0,-177),Vector2(-44,-177),Vector2(-44,-77),Vector2(5.5,-77),Vector2(5.5,-111),Vector2(0,-111)])
	# Both new floor wings remain physically accessible from the retained spine.
	await walk_route(actor,[Vector2(0,-140),Vector2(20,-140),Vector2(30,-150),Vector2(20,-166),Vector2(0,-166),Vector2(-20,-166),Vector2(-30,-150),Vector2(-20,-140),Vector2(0,-140)])
	assert(absf(actor.position.y-106.5)<.12)
	var excluded:Array[RID]=[]
	for body in ship.find_children("*","CollisionObject3D",true,false):
		if body is RigidBody3D or body is CharacterBody3D:excluded.append(body.get_rid())
	var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8
	var count:=0
	for segment in [[Vector2(0,-177),Vector2(-44,-177)],[Vector2(-44,-177),Vector2(-44,-82)]]:
		var a:Vector2=segment[0];var b:Vector2=segment[1];var direction:Vector2=(b-a).normalized();var normal:=Vector2(-direction.y,direction.x)
		for i in range(ceili(a.distance_to(b))+1):
			for offset in [-2.7,0.0,2.7]:
				var p:Vector2=a.lerp(b,float(i)/ceili(a.distance_to(b)))+normal*offset
				var query:=PhysicsShapeQueryParameters3D.new();query.shape=shape;query.margin=.001;query.exclude=excluded;query.transform.origin=Vector3(p.x,107.42,p.y)
				assert(ship.get_world_3d().direct_space_state.intersect_shape(query,32).is_empty(),"Six-metre public width has a standing-body obstruction at %s"%p)
				var ray:=PhysicsRayQueryParameters3D.create(Vector3(p.x,106.75,p.y),Vector3(p.x,106.2,p.y));ray.exclude=excluded
				var hit:=ship.get_world_3d().direct_space_state.intersect_ray(ray)
				assert(not hit.is_empty() and hit.normal.y>.99 and absf(hit.position.y-106.5)<.005,"Public width lacks actual same-level floor")
				count+=1
	print("BRIDGE PLATFORM ROUTES PASS: original centreline remains open; continuous bidirectional public bypass, core approach and both guarded wings walked;",count," supported six-metre-width capsule probes. Private bridge enclosure, traffic and final art remain unfinished.")
	main.queue_free();await process_frame;quit()
