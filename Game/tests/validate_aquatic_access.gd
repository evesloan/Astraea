extends "res://tests/validate_cart_clearance.gd"
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(60):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var lift:Node3D=ship.find_child("AquaticPassengerLift",true,false)
	var cart:RigidBody3D=ship.find_child("CustodialCart",true,false)
	var excluded:Array[RID]=[]
	for body in ship.find_children("*","CollisionObject3D",true,false):
		if not body is StaticBody3D or body is AnimatableBody3D:excluded.append(body.get_rid())
	# Full moving cabin contact geometry must clear all fixed construction.
	var sweep_samples:=0
	for i in range(171):
		var pose:Transform3D=lift.cabin.global_transform
		pose.origin.y=44.0+i*.1
		for part in lift.cabin.get_children():
			if not part is CollisionShape3D:continue
			var query:=PhysicsShapeQueryParameters3D.new()
			query.shape=part.shape
			query.transform=pose*part.transform
			query.margin=0.001
			query.exclude=excluded
			var hits:=ship.get_world_3d().direct_space_state.intersect_shape(query,16)
			for hit in hits:print("SWEEP CONTACT:",hit.collider.get_path()," part:",part.name," y:",pose.origin.y)
			assert(hits.is_empty(),"Aquatic cabin contacts fixed structure: %s at %.2f"%[part.name,pose.origin.y])
			sweep_samples+=1
	var ceiling:Node3D=ship.find_child("AquaticAuthoredCeiling",true,false)
	for part in ceiling.find_children("*","MeshInstance3D",true,false):
		var bounds:AABB=part.global_transform*part.get_aabb()
		assert(bounds.end.y<=69.101,"Ceiling must not enter Cinema5 volume")
	for i in range(4):
		var marker:=ceiling.find_child("DATUM_ceiling_light_"+str(i),true,false)as Node3D
		var ray:=PhysicsRayQueryParameters3D.create(marker.global_position,marker.global_position+Vector3.DOWN*.2)
		assert(ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Ceiling source exit obstructed")
		var mount:=marker.global_position+Vector3(.48,0,0)
		ray=PhysicsRayQueryParameters3D.create(mount,Vector3(mount.x,67.6,mount.z))
		var hit:=ship.get_world_3d().direct_space_state.intersect_ray(ray)
		assert(not hit.is_empty() and abs(hit.position.y-67.4)<.01,"Ceiling luminaire lacks its fitted overhead mounting surface")
	var compiled:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
	var cover_area:=0.0
	for region in compiled.regions:
		if String(region.id).begins_with("D11_aquatic_"):
			assert(abs(region.floor_y-69.5)<.001 and abs(region.thickness-.4)<.001)
			cover_area+=region.structural_area_m2
	assert(abs(cover_area-3128.0)<.01,"Both protected cover ownership pieces must be present")
	var edge_data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D09_D10_aquatic_edges.json"))
	var guard_samples:=0
	for deck in edge_data.decks:
		var ring:Array=deck.boundary
		for i in range(ring.size()):
			var a:=Vector2(ring[i][0],ring[i][1])
			var b:=Vector2(ring[(i+1)%ring.size()][0],ring[(i+1)%ring.size()][1])
			var t:Vector2=(b-a).normalized()
			var n:=Vector2(-t.y,t.x)
			for fraction in [.08,.3,.5,.7,.92]:
				var p:Vector2=a.lerp(b,fraction)
				var ray:=PhysicsRayQueryParameters3D.create(Vector3(p.x+n.x*.4,deck.floor_y+.7,p.y+n.y*.4),Vector3(p.x-n.x*.4,deck.floor_y+.7,p.y-n.y*.4))
				ray.hit_back_faces=true
				var hit:=ship.get_world_3d().direct_space_state.intersect_ray(ray)
				assert(not hit.is_empty() and "AquaticAuthoredBalconyEdges" in String(hit.collider.get_path()),"Missing physical aquatic guard")
				guard_samples+=1
		for fixture in deck.lights:
			var a:Array=fixture.source_xyz
			var b:Array=fixture.receiver_xyz
			var ray:=PhysicsRayQueryParameters3D.create(Vector3(a[0],a[1],a[2]),Vector3(b[0],b[1],b[2]))
			var optical_hit:=ship.get_world_3d().direct_space_state.intersect_ray(ray)
			if not optical_hit.is_empty():print("BALCONY OPTICAL BLOCK:",deck.deck," ",a," to ",b," ",optical_hit.collider.get_path()," at ",optical_hit.position)
			assert(optical_hit.is_empty(),"Balcony fixture cannot reach its authored lower-floor receiver")
	# Compound loaded-cart clearance, including the aft bypass around the existing column.
	for floor_y in [44.0,52.5,61.0]:
		for i in range(66):check_pose(ship,cart,Vector3(9.8,floor_y+.03,223.2+i*.25),0,excluded)
		for i in range(31):check_pose(ship,cart,Vector3(9.8,floor_y+.03,239.5),PI*.5*i/30,excluded)
		for i in range(42):check_pose(ship,cart,Vector3(9.8+i*.24,floor_y+.03,239.5),PI/2,excluded)
		for i in range(31):check_pose(ship,cart,Vector3(20,floor_y+.03,239.5),PI*.5*i/30,excluded)
		for i in range(23):check_pose(ship,cart,Vector3(20,floor_y+.03,239.5+i*.25),0,excluded)
	print("AQUATIC ACCESS PASS:",sweep_samples,"full cabin-shape sweep samples;",samples,"compound cart and upper-load approach poses;",guard_samples,"guard contacts and eight lower receivers; four ceiling fixture mounts/exits and protected cover ownership. Geometric clearance only; driven boarding turns and final art remain pending.")
	main.queue_free()
	await process_frame
	quit()
