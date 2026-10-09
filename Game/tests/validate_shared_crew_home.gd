extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for i in range(12):await physics_frame
	paused=true
	var ship:Node3D=main.get_node("World360/Astraea")
	var home:Node3D=ship.get_node("ShipSpace/Districts/SharedCrewHome_WIP")
	var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/SHARED_CREW_HOME.json"))
	for path in d.source_pins:
		assert(FileAccess.get_sha256("res://"+str(path).trim_prefix("Game/"))==d.source_pins[path])
	assert(home.get_meta("physical_rest_places")==2 and home.get_meta("registered_berths_added")==0)
	assert(not home.get_meta("population_migration_applied"))
	var state:=ship.get_world_3d().direct_space_state
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var points:Array[Vector3]=[Vector3(-41,12,-423),Vector3(-41,12,-421),Vector3(-36.8,12,-421),Vector3(-36.8,12,-425),Vector3(-36.8,12,-428),Vector3(-39,12,-431),Vector3(-39,12,-435),Vector3(-35,12,-433.2),Vector3(-35,12,-429.8),Vector3(-32.6,12,-430),Vector3(-32.6,12,-434)]
	for p in points:
		var ray:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.15,p-Vector3.UP*.35)
		ray.exclude=[actor.get_rid()]
		var hit:=state.intersect_ray(ray)
		assert(not hit.is_empty() and absf(hit.position.y-12)<.02)
		assert(not home.is_ancestor_of(hit.collider),"No duplicate home floor")
		var query:=PhysicsShapeQueryParameters3D.new()
		var capsule:=CapsuleShape3D.new()
		capsule.height=2.2
		capsule.radius=.3
		query.shape=capsule
		query.transform=Transform3D(Basis.IDENTITY,p+Vector3.UP*1.12)
		query.exclude=[actor.get_rid()]
		query.margin=.001
		assert(state.intersect_shape(query,16).is_empty(),"Blocked home point "+str(p))
	for key in ["A","B"]:
		var place:Node3D=home.get_node("PersonalPlace"+key)
		var p:Vector3=place.to_global(Vector3(0,.565,-.9))
		var hit:=state.intersect_ray(PhysicsRayQueryParameters3D.create(p+Vector3.UP*.3,p-Vector3.UP*.1))
		assert(not hit.is_empty() and home.is_ancestor_of(hit.collider),"Missing actual rest surface")
	var result={"status":"PASS","physical_rest_places":2,"floor_and_stationary_clearance_points":points.size(),"retained_source_pins":d.source_pins.size(),"new_floor_owners":0,"population_migration_applied":false,"scope":"Actual main construction, source preservation, bounded clearances and physical rest surfaces. Full traversal, curtain/drawer operation, wet systems, species suitability and visual acceptance unverified."}
	FileAccess.open("res://artifacts/shared_crew_home.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("SHARED_CREW_HOME ",JSON.stringify(result))
	quit()
