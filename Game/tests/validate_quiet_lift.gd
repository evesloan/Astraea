extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for i in range(120):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var house:Node3D=ship.get_node("ShipSpace/Districts/QuietGroveReceivingCandidate")
	var lift:Node3D=house.get_node("QuietGrovePassengerLift")
	assert(house.get_meta("installed_guest_units")==83)
	assert(house.get_node("RetainedLandscapeAndSeating").get_child_count()==250)
	assert(house.get_node("LongLibraryCompositeReceivingCore").get_child_count()==143)
	var excluded:Array[RID]=[]
	for body in ship.find_children("*","CharacterBody3D",true,false):excluded.append(body.get_rid())
	for body in ship.find_children("*","RigidBody3D",true,false):excluded.append(body.get_rid())
	var points:=0
	for destination in [0,1,2,3,4,0]:
		assert(lift.request_floor(destination))
		var ticks:=0
		while not (lift.phase=="idle" and lift.current_floor==destination):
			await physics_frame
			ticks+=1
			assert(ticks<2400,"Lift arrival timeout")
			if lift.phase=="moving":
				for gate in lift.landing_gates:assert(gate.open_fraction<.001,"Open shaft gate during travel")
		for i in range(3):await physics_frame
		var physics:=ship.get_world_3d().direct_space_state
		for lateral in [-.6,0.0,.6]:
			for advance in [-1.8,-.3,1.0]:
				var p:Vector3=lift.to_global(Vector3(advance,lift.floor_heights[destination],lateral))
				var ray:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.15,p-Vector3.UP*.3)
				ray.exclude=excluded
				var hit:=physics.intersect_ray(ray)
				assert(not hit.is_empty() and absf(hit.position.y-p.y)<.03,"Landing floor "+str(p))
				var query:=PhysicsShapeQueryParameters3D.new()
				var capsule:=CapsuleShape3D.new()
				capsule.radius=.3;capsule.height=1.8
				query.shape=capsule;query.exclude=excluded;query.margin=.001
				query.transform.origin=p+Vector3.UP*.925
				assert(physics.intersect_shape(query,16).is_empty(),"Blocked boarding "+str(p))
				points+=1
		print("QUIET_LIFT_ARRIVAL ",destination)
	var result={"status":"PASS","stops":5,"arrivals_tested":6,"floor_and_stationary_capsule_checks":points,"closed_gates_during_travel":true,"retained_homes":83,"retained_landscape":250,"retained_library_support":143,"scope":"Actual main installation and bounded boarding checks. Full traversal, cart/species transport, structural engineering and final visual acceptance remain unverified."}
	FileAccess.open("res://artifacts/quiet_lift.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("QUIET_LIFT ",JSON.stringify(result))
	quit()
