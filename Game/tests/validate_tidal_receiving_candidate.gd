extends SceneTree

# Candidate is evaluated inside the actual default ship and its existing contacts.
# No default-scene installation, guest-unit acceptance or visual finish is implied.
func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	OS.set_environment("ASTRAEA_TIDAL_CANDIDATE_ISOLATION", "1")
	var main: Node = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	var ship := main.get_node("World360/Astraea") as Node3D
	for frame in range(12): await physics_frame
	var house: Node3D = load("res://scripts/tidal_garden_receiving.gd").build(ship)
	for frame in range(4): await physics_frame
	var definition: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/TIDAL_GARDEN_RECEIVING_CANDIDATE.json"))
	var excluded: Array[RID] = []
	for actor in main.find_children("*", "CharacterBody3D", true, false): excluded.append(actor.get_rid())
	for body in main.find_children("*", "RigidBody3D", true, false): excluded.append(body.get_rid())
	var physics := ship.get_world_3d().direct_space_state
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.3
	capsule.height = 1.8
	var results: Array = []
	var failures := 0
	var samples := 0
	var routes: Array = definition.routes.duplicate(true)
	routes.append({"id":"Retained_Horizon_Entry","points":[[-6,78,-432],[-19,78,-432]]})
	for route in routes:
		var errors: Array = []
		var points: Array = route.points
		for segment in range(points.size() - 1):
			var a := Vector3(points[segment][0], points[segment][1], points[segment][2])
			var b := Vector3(points[segment+1][0], points[segment+1][1], points[segment+1][2])
			var count := int(ceil(a.distance_to(b) / 0.5)) + 1
			for i in range(count):
				var p := a.lerp(b, float(i) / maxf(1.0, float(count-1)))
				samples += 1
				var ray := PhysicsRayQueryParameters3D.create(p + Vector3.UP * 0.15, p - Vector3.UP * 0.4)
				ray.exclude = excluded
				var hit := physics.intersect_ray(ray)
				if hit.is_empty() or absf(hit.position.y-p.y) > 0.025:
					errors.append({"type":"support", "xyz":[p.x,p.y,p.z]})
				var query := PhysicsShapeQueryParameters3D.new()
				query.shape = capsule
				query.transform.origin = p + Vector3.UP * 0.925
				query.exclude = excluded
				for obstruction in physics.intersect_shape(query, 32):
					errors.append({"type":"clearance", "xyz":[p.x,p.y,p.z], "collider":str(obstruction.collider.get_path())})
		if not errors.is_empty(): failures += 1
		results.append({"route":route.id, "errors":errors})
	var result := {"status":"PASS" if failures == 0 else "FAIL", "scope":"Retained Tidal architecture candidate in actual default ship; static planned route support/capsule only. Interiors, support transfer, operating lift, full traversal, carts, species and visual review remain open.", "failed_routes":failures, "samples":samples, "source_meshes":definition.mesh_count, "collision_batches":house.get_meta("source_contact_count"), "installed_guest_units":0, "routes":results}
	var file := FileAccess.open("res://artifacts/tidal_receiving_candidate.json", FileAccess.WRITE)
	file.store_string(JSON.stringify(result,"  "))
	print("TIDAL_RECEIVING_CANDIDATE ", result.status, " failed_routes=", failures, " samples=", samples)
	quit(0 if failures == 0 else 1)
