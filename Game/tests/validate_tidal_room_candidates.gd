extends SceneTree

# Entry and exact retained rest-anchor fit in the current ship. Direct door-pose
# setup here is not an ordinary-input interaction or whole-room traversal test.
func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var main: Node = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	var ship := main.get_node("World360/Astraea") as Node3D
	for frame in range(12): await physics_frame
	load("res://scripts/tidal_garden_receiving.gd").build(ship)
	var units: Node3D = load("res://scripts/tidal_room_candidates.gd").build(ship)
	for room in units.get_children():
		var entry := room.get_node("EntryDoor")
		entry.desired_open = true
		entry.open_fraction = 1.0
		entry._apply_pose()
	for frame in range(6): await physics_frame
	var definition: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/TIDAL_UNIT_CANDIDATES.json"))
	var excluded: Array[RID] = []
	for actor in main.find_children("*","CharacterBody3D",true,false): excluded.append(actor.get_rid())
	for body in main.find_children("*","RigidBody3D",true,false): excluded.append(body.get_rid())
	var physics := ship.get_world_3d().direct_space_state
	var capsule := CapsuleShape3D.new()
	capsule.radius = .3
	capsule.height = 1.8
	var errors: Array = []
	var samples := 0
	var anchors := 0
	for unit in definition.units:
		var room := units.get_node(NodePath(str(unit.rebuild_identity))) as Node3D
		for binding in unit.anchor_bindings:
			var marker := room.find_child("SOURCE_"+str(binding.prototype_marker_name),true,false) as Node3D
			assert(marker != null)
			var p: Array = binding.source_xyz
			var expected := room.to_global(Vector3(p[0],p[2],-p[1]))
			if marker.global_position.distance_to(expected)>.002:
				errors.append({"unit":unit.rebuild_identity,"kind":"rest_anchor_mismatch","marker":binding.prototype_marker_name})
			anchors += 1
		for i in range(13):
			var p := room.to_global(Vector3(0,0,1.25-float(i)*.25))
			var ray := PhysicsRayQueryParameters3D.create(p+Vector3.UP*.2,p-Vector3.UP*.35)
			ray.exclude = excluded
			var support := physics.intersect_ray(ray)
			samples += 1
			if support.is_empty() or absf(support.position.y-float(unit.floor_y))>.15:
				errors.append({"unit":unit.rebuild_identity,"kind":"entry_support","xyz":[p.x,p.y,p.z]})
				continue
			var query := PhysicsShapeQueryParameters3D.new()
			query.shape = capsule
			query.transform.origin = Vector3(p.x,support.position.y+.925,p.z)
			query.exclude = excluded
			for hit in physics.intersect_shape(query,32):
				errors.append({"unit":unit.rebuild_identity,"kind":"entry_clearance","xyz":[p.x,p.y,p.z],"collider":str(hit.collider.get_path())})
	var shared: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/TIDAL_GARDEN_RECEIVING_CANDIDATE.json"))
	var routes: Array = shared.routes.duplicate(true)
	routes.append({"id":"Retained_Horizon_Entry","points":[[-6,78,-432],[-19,78,-432]]})
	var route_samples := 0
	for route in routes:
		var points: Array = route.points
		for segment in range(points.size()-1):
			var a := Vector3(points[segment][0],points[segment][1],points[segment][2])
			var b := Vector3(points[segment+1][0],points[segment+1][1],points[segment+1][2])
			var count := int(ceil(a.distance_to(b)/.5))+1
			for i in range(count):
				var p := a.lerp(b,float(i)/maxf(1.0,float(count-1)))
				var ray := PhysicsRayQueryParameters3D.create(p+Vector3.UP*.15,p-Vector3.UP*.4)
				ray.exclude = excluded
				var support := physics.intersect_ray(ray)
				route_samples += 1
				if support.is_empty() or absf(support.position.y-p.y)>.025:
					errors.append({"route":route.id,"kind":"shared_route_support","xyz":[p.x,p.y,p.z]})
				var query := PhysicsShapeQueryParameters3D.new()
				query.shape = capsule
				query.transform.origin = p+Vector3.UP*.925
				query.exclude = excluded
				for hit in physics.intersect_shape(query,32):
					errors.append({"route":route.id,"kind":"shared_route_clearance","xyz":[p.x,p.y,p.z],"collider":str(hit.collider.get_path())})
	assert(anchors==221)
	assert(ship.find_child("D13_13017_TwinSuite_WIP",true,false)!=null)
	assert(ship.find_child("D13_13041_TwinSuite_WIP",true,false)!=null)
	var result := {"status":"PASS" if errors.is_empty() else "FAIL","candidate_units":85,"source_rest_anchors":anchors,"entry_samples":samples,"shared_route_samples":route_samples,"retained_landscape_and_seating_instances":81,"errors":errors,"default_scene_enabled":false,"scope":"All85 retained Tidal source placements in actual default ship plus candidates; exact rest anchors, open-pose entry support/capsule fit and shared routes with source landscaping/seating. No full-room, ordinary-input, cart/species, privacy, visual or occupied-capacity acceptance."}
	var file := FileAccess.open("res://artifacts/tidal_room_candidates.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(result,"  "))
	print("TIDAL_ROOM_CANDIDATES ",result.status," units=85 anchors=",anchors," entry_samples=",samples," failures=",errors.size())
	quit(0 if errors.is_empty() else 1)
