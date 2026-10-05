extends SceneTree
var walked_frames := 0
func _initialize() -> void:
	call_deferred("run")

func walk(actor: CharacterBody3D, target: Vector2) -> void:
	var reached := false
	for frame in range(900):
		var delta := Vector3(target.x - actor.position.x, 0, target.y - actor.position.z)
		if delta.length() < .09:
			reached = true
			break
		var v := delta.normalized() * 3.1
		actor.velocity = Vector3(v.x, -.1 if actor.is_on_floor() else actor.velocity.y - 9.8 / 60, v.z)
		actor.move_and_slide()
		await physics_frame
		walked_frames += 1
		assert(abs(actor.position.y - 102) < .18, "D17 walk left its intended floor")
	if not reached:
		for index in range(actor.get_slide_collision_count()):
			print("D17 WALK BLOCK: ", actor.get_slide_collision(index).get_collider().get_path())
	assert(reached, "D17 walk stalled at %s toward %s" % [actor.position, target])

func run() -> void:
	assert(FileAccess.get_sha256("res://assets/models/AST-RES-006.glb") == "5375179c3d89b92a4f950b7fad0a0936aafdeca37797aa388264f9bdf6d8e664")
	assert(FileAccess.get_sha256("res://assets/models/AST-COM-003.glb") == "6b559b69c13d0ea2e5cb16e42791aec6af495c377fcfbf074ebfb36f7e57ff18")
	var main: Node = (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(90): await physics_frame
	var ship: Node3D = main.get_node("World360/Astraea")
	var space := ship.get_world_3d().direct_space_state
	var built: Node3D = ship.find_child("D17ConnectedHouse_WIP", true, false)
	assert(built != null and built.get_meta("source_guest_index") == 790)
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D17_CONNECTED_HOUSE_RUNTIME.json"))
	assert(data.units_preserved.size() == 16 and data.exported_walkable_floor_meshes == 0)
	var architecture: Node3D = built.find_child("D17ConnectedArchitecture", true, false)
	var floor_exclusions: Array[RID] = []
	for body in architecture.find_children("*", "StaticBody3D", true, false): floor_exclusions.append(body.get_rid())
	var compiled: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
	assert(compiled.regions.size() == 250)
	var floor_rays := 0
	for region in compiled.regions:
		if region.id != "D17_connected_house_floor_00": continue
		assert(abs(float(region.structural_area_m2) - 605.2) < .00001)
		for triangle in region.triangles:
			for weights in [Vector3(.34,.33,.33),Vector3(.6,.2,.2),Vector3(.2,.6,.2),Vector3(.2,.2,.6)]:
				var x: float = triangle[0][0]*weights.x + triangle[1][0]*weights.y + triangle[2][0]*weights.z
				var z: float = triangle[0][1]*weights.x + triangle[1][1]*weights.y + triangle[2][1]*weights.z
				var q := PhysicsRayQueryParameters3D.create(Vector3(x,102.2,z),Vector3(x,101.8,z),1)
				q.exclude = floor_exclusions
				var hit := space.intersect_ray(q)
				assert(not hit.is_empty() and abs(hit.position.y-102) < .002)
				assert("D17_connected_house_floor_00" in str(hit.collider.get_path()), "Compiler must be the actual new slab owner")
				floor_rays += 1
	assert(floor_rays == 92)
	assert(space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(80,103.2,12),Vector3(80,103.2,16),1)).is_empty(), "Aft portal must be open")
	var fore := space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(80,103.2,-12),Vector3(80,103.2,-14),1))
	assert(not fore.is_empty() and "HC_ProfileWall_D17" in str(fore.collider.get_path()), "Fore wall must remain physically closed")
	var guard_rays := 0
	var all_guards: Array = data.guards.duplicate()
	all_guards.append_array(data.portal_guard_returns)
	for guard in all_guards:
		var a := Vector2(guard.a_xz[0], guard.a_xz[1])
		var b := Vector2(guard.b_xz[0], guard.b_xz[1])
		var n := Vector2(-(b-a).y,(b-a).x).normalized() * .24
		for fraction in [.05,.5,.95]:
			var p := a.lerp(b,fraction)
			for y in [102.15,102.7,103.05]:
				var hit := space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(p.x+n.x,y,p.y+n.y),Vector3(p.x-n.x,y,p.y-n.y),1))
				assert(not hit.is_empty() and "D17ConnectedArchitecture" in str(hit.collider.get_path()), "Source guard gap at " + str(p))
				guard_rays += 1
	for fixture in data.fixtures:
		var marker: Node3D = architecture.find_child(fixture.name,true,false)
		assert(marker != null)
		assert(space.intersect_ray(PhysicsRayQueryParameters3D.create(marker.global_position,marker.global_position+Vector3.DOWN*.06,1)).is_empty(), "Fixture light exit blocked")
	var actor: CharacterBody3D = ship.get_node("ShipSpace/PersistentActors/Player")
	actor.set_physics_process(false)
	actor.position = Vector3(50.5,102.1,0)
	actor.velocity = Vector3.ZERO
	var route: Array[Vector2] = [Vector2(54,0),Vector2(59,-11.8),Vector2(65,-11.8),Vector2(75,-11),Vector2(86,-8),Vector2(89,0),Vector2(84.5,0),Vector2(84.5,9),Vector2(80,10),Vector2(80,12),Vector2(80,18),Vector2(80,21.5),Vector2(82,25),Vector2(88,25),Vector2(92,25.9),Vector2(92.4,30),Vector2(95,32.4),Vector2(101,33),Vector2(107,36),Vector2(113,40)]
	for point in route: await walk(actor,point)
	route.reverse()
	for point in route: await walk(actor,point)
	await walk(actor,Vector2(50.5,0))
	print("D17 CONNECTED ACCESS PASS: ",floor_rays," compiler-owned floor rays; ",guard_rays," guard rays; fore closure, aft opening,9 fixture exits and physical round-trip walk. Frames:",walked_frames,". Loaded cart and in-ship visuals remain separate checks.")
	main.queue_free()
	await process_frame
	quit()
