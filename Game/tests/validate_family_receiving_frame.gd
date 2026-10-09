extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for i in range(120):await physics_frame
	paused=true
	var ship:Node3D=main.get_node("World360/Astraea")
	var house:Node3D=ship.get_node("ShipSpace/Districts/FamilyTerraceReceivingCandidate")
	var frame:Node3D=house.get_node("FamilyCourtReceivingFrame")
	assert(frame.get_meta("source_part_count")==437 and not frame.get_meta("full_base_hold_closed"))
	assert(house.get_meta("open_construction_hold") =="FT_BASE_RECEIVING_HOLD")
	assert(house.get_meta("installed_guest_units")==82 and house.get_node("RetainedLandscapeAndSeating").get_child_count()==157)
	var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/FAMILY_RECEIVING_FRAME.json"))
	for path in d.source_pins:assert(FileAccess.get_sha256("res://"+str(path).trim_prefix("Game/"))==d.source_pins[path])
	var excluded:Array[RID]=[]
	for body in ship.find_children("*","CharacterBody3D",true,false):excluded.append(body.get_rid())
	var physics:=ship.get_world_3d().direct_space_state
	var points:Array[Vector3]=[]
	for contact in d.contact_interfaces:
		for y in [78.0,84.0]:points.append(Vector3(3.4,y,float(contact.station_z)))
	points.append(Vector3(90.3,84,378.9))
	for p in points:
		var ray:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.15,p-Vector3.UP*.3);ray.exclude=excluded
		var hit:=physics.intersect_ray(ray)
		assert(not hit.is_empty() and absf(hit.position.y-p.y)<.025,"Receiving work changed supported floor "+str(p))
		var query:=PhysicsShapeQueryParameters3D.new();var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8
		query.shape=capsule;query.exclude=excluded;query.margin=.001;query.transform.origin=p+Vector3.UP*.925
		assert(physics.intersect_shape(query,16).is_empty(),"Receiving frame obstructs passage "+str(p))
	var report={"status":"PASS","frame_parts":437,"geometric_source_reaction_feet":27,"axial_and_cabin_clearance_points":points.size(),"retained_source_pins":d.source_pins.size(),"retained_homes":82,"retained_landscape":157,"whole_base_hold_closed":false,"held_reactions":d.held_reactions,"scope":"Actual main installation, source preservation and bounded floor/clearance tests. Geometric receiving contacts do not establish primary hull load path or capacity. Inner Celestial receiving, full traversal and final visual review remain unfinished."}
	FileAccess.open("res://artifacts/family_receiving_frame.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print("FAMILY_RECEIVING_FRAME ",JSON.stringify(report));quit()
