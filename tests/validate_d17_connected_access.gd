extends SceneTree
# Grand Pool additive adoption: all 250 retained rows independently match Git
# 16bf7ee and GRAND_POOL_PRE_ADOPTION_MESHES.json. Admit only these eight rows;
# retain every original numeric pin and actual render/contact geometry check.
const GRAND_POOL_FLOORS_JSON := """{"D08_grand_pool_base":{"deck":"D08","floor_y":44.0,"layout_numeric9_sha256":"f1d8276afbfc7810084879c390f40fb7401bc02b87a380a185d5094576e2827a","record_numeric9_sha256":"90bbdfee89300f0243aa75283b84e4633b9d49dc9c63eaf43c8fbbe7be204ea0","structural_area_m2":3128.0,"thickness":0.24},"D08_grand_pool_core_tongue":{"deck":"D08","floor_y":44.0,"layout_numeric9_sha256":"9dcbabeb9cf36404cd237f4e7dc3162b3b9c8d9866461d677e3cec616506c875","record_numeric9_sha256":"7ffba714b21a0aaa289238e2cd8246aecb6e6707c9f6e3f98b972a2be55a9804","structural_area_m2":1.2,"thickness":0.24},"D08_grand_pool_upper_staff":{"deck":"D08","floor_y":46.2,"layout_numeric9_sha256":"d58987acbca8d0eb8a5daaae8161a66b545cbaba00c6b4e2f7b0c85ec7e70bf4","record_numeric9_sha256":"483405dde91a65d4da07b0d114698eedcf33c294a2562b33426cdc2f7882fc2e","structural_area_m2":340.56,"thickness":0.24},"D08_grand_pool_wet":{"deck":"D08","floor_y":46.2,"layout_numeric9_sha256":"8203147f585fdbdf1603b3fe1ca4100847a7bab578670b98a2a8a59b8cc07aba","record_numeric9_sha256":"6dd8b47fee4f8c5b369d2bc3f62f358b52c18e3d61b164dde7de36ab0d5b6fc9","structural_area_m2":1849.862,"thickness":0.24},"D09_orchard_market_core_tongue":{"deck":"D09","floor_y":52.5,"layout_numeric9_sha256":"01cfd5b37bf5fc98d1de0d76777b9ac20c0338aaf728d557e6f3f7a051e14123","record_numeric9_sha256":"a903df9c096479bcafdc0ea720935a1504a0988ef17267ce967da45d0ab67bd9","structural_area_m2":1.2,"thickness":0.24},"D09_orchard_market_gallery":{"deck":"D09","floor_y":52.5,"layout_numeric9_sha256":"e6568210fea1b369c73d679230394ed53334bba7591643d20025560dfef05cf4","record_numeric9_sha256":"ae3ffbdb65ed498c6c324b94673280342fe4aa2e15ffe601c5ef6891f453a5f5","structural_area_m2":1551.43,"thickness":0.24},"D09_orchard_market_upper_staff":{"deck":"D09","floor_y":52.5,"layout_numeric9_sha256":"f08f94244c9b0bece254439105ab902bbd86f1d81cd5730e490d18fcc321374d","record_numeric9_sha256":"40d20051cd63322c5037194898a1d3ab2a849654daf0c0cc1134955211c51977","structural_area_m2":340.56,"thickness":0.24},"D10_shared_table_reserved_cap":{"deck":"D10","floor_y":61.0,"layout_numeric9_sha256":"5d53a425ba67115d340fadb56053f7d3da18781c708d15e9b580d8fa40ca7ae9","record_numeric9_sha256":"65594524b8366ab9dd9d6733d982484bab52fd9e5a23546e72dce64b27081627","structural_area_m2":3128.0,"thickness":0.24}}"""
const COMPILED_SHA := "646ee5875fd230be13f6553f36ae6dc05322b5848d42f5c725841dc9aee08a3a"
const LAYOUT_SHA := "d260d6c55397c822603fe88ea702fff2515eec13a1259ba607b57b85a1ffdc73"
var walked_frames := 0
func _initialize() -> void:
	call_deferred("run")

func canonical(value: Variant) -> String:
	if value is Dictionary:
		var keys: Array = value.keys()
		keys.sort()
		var fields := PackedStringArray()
		for key in keys:
			fields.append(JSON.stringify(str(key))+":"+canonical(value[key]))
		return "{"+",".join(fields)+"}"
	if value is Array:
		var fields := PackedStringArray()
		for item in value:
			fields.append(canonical(item))
		return "["+",".join(fields)+"]"
	if value is float or value is int:
		return "%.9f" % float(value)
	return JSON.stringify(value)


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
	var engineering_floors: Dictionary = load("res://tests/secondary_engineering_additive_guard.gd").validate(compiled)
	assert(FileAccess.get_sha256("res://data/generated/structural_meshes.json") == COMPILED_SHA, "Retained 258 records plus the exact three engineering additions are required")
	assert(FileAccess.get_sha256("res://data/spatial_layout.json") == LAYOUT_SHA, "Reviewed additive layout identity changed")
	var pool_floors: Dictionary = JSON.parse_string(GRAND_POOL_FLOORS_JSON)
	assert(compiled.regions.size() == 261 and engineering_floors.size() == 3 and pool_floors.size() == 8)
	var seen: Dictionary = {}
	var pool_seen: Dictionary = {}
	for region in compiled.regions:
		var id := str(region.id)
		assert(not seen.has(id), "Duplicate floor identity: " + id)
		seen[id] = true
		if pool_floors.has(id):
			var expected: Dictionary = pool_floors[id]
			assert(canonical(region).sha256_text() == str(expected.record_numeric9_sha256), "Approved pool-market compiled record changed: " + id)
			assert(str(region.deck) == str(expected.deck) and absf(float(region.floor_y) - float(expected.floor_y)) < .001 and absf(float(region.thickness) - float(expected.thickness)) < .001, "Approved pool-market slab deck/datum/thickness changed: " + id)
			assert(absf(float(region.structural_area_m2) - float(expected.structural_area_m2)) < .001, "Approved pool-market slab area changed: " + id)
			pool_seen[id] = true
	assert(seen.size() == 261 and pool_seen.size() == 8, "Exactly eight pool-market and three engineering additions must accompany all 250 prior owners")
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
