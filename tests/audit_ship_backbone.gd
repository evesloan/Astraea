extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(60):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var contract:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/design_contract.json"))
	var omit:Array[RID]=[]
	for body in ship.find_children("*","CollisionObject3D",true,false):
		if not body is StaticBody3D:omit.append(body.get_rid())
	var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8
	var decks:Array=[]
	for deck in contract.deck_datums:
		var y:float=deck.floor_elevation_m
		var side:float=45 if deck.deck_id in ["D01","D18"]else 49.5
		var route:Array[Vector2]=[Vector2(0,-520),Vector2(0,-111),Vector2(5.5,-111),Vector2(5.5,-72),Vector2(45,-72),Vector2(45,-65.5),Vector2(side,-65.5),Vector2(side,65.5),Vector2(45,65.5),Vector2(45,72),Vector2(0,72),Vector2(0,520)]
		if deck.deck_id!="D18":
			for entry in [Vector2(0,-414),Vector2(5.5,-414),Vector2(5.5,-443),Vector2(0,-443)]:route.insert(1,entry)
		if deck.deck_id in ["D17","D18"]:
			route.remove_at(route.size()-1)
			route.append_array([Vector2(0,108),Vector2(5.5,108),Vector2(5.5,137),Vector2(0,137),Vector2(0,520)])
		var missing:Array=[];var blocked:Array=[];var samples:=0
		for segment in range(route.size()-1):
			var distance:float=route[segment].distance_to(route[segment+1]);var steps:int=maxi(1,ceili(distance/1.0))
			for i in range(steps+1):
				var point:Vector2=route[segment].lerp(route[segment+1],float(i)/steps);var foot:=Vector3(point.x,y+.015,point.y)
				var q:=PhysicsShapeQueryParameters3D.new();q.shape=capsule;q.transform=Transform3D(Basis.IDENTITY,foot+Vector3.UP*.9);q.exclude=omit
				var hits:=ship.get_world_3d().direct_space_state.intersect_shape(q,8)
				if not hits.is_empty():
					var names:Array=[]
					for hit in hits:names.append(str(hit.collider.get_path()))
					blocked.append({"xz":[point.x,point.y],"colliders":names})
				var ray:=PhysicsRayQueryParameters3D.create(foot+Vector3.UP*.08,foot-Vector3.UP*.12);ray.exclude=omit
				var support:=ship.get_world_3d().direct_space_state.intersect_ray(ray)
				if support.is_empty()or absf(support.position.y-y)>.08:missing.append([point.x,point.y])
				samples+=1
		decks.append({"deck":deck.deck_id,"samples":samples,"missing_floor_samples":missing.size(),"blocked_capsule_samples":blocked.size(),"missing_floor_examples":missing.slice(0,16),"blocked_examples":blocked.slice(0,16),"scope":"One nominated spine/bypass/atrium-side circuit; static capsule and floor samples only"})
		print("BACKBONE AUDIT ",deck.deck_id," samples=",samples," unsupported=",missing.size()," blocked=",blocked.size())
	var file:=FileAccess.open("res://artifacts/ship_backbone_audit.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"decks":decks,"scope":"Read-only sampled runtime collision audit. Gaps/blocks are candidates to investigate, not automatic construction changes. Dynamic gates, cart envelope, guests, force-driven walking and all alternative routes remain separate checks."},"  "))
	file.close()
	var total:=0
	for deck in decks:
		total+=int(deck.samples)
		assert(deck.missing_floor_samples==0,"Backbone floor support regression")
		assert(deck.blocked_capsule_samples==0,"Backbone capsule clearance regression")
	print("SHIP BACKBONE PASS:",total," static capsule/support samples across18 deck spine/bypass/atrium-side circuits. Not cart turns, dynamic traffic, destination fit or normal-play traversal acceptance.")
	main.queue_free();await process_frame;quit()
