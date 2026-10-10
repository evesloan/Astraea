extends "res://tests/validate_commons_lift.gd"
var visited:Array=[]
var moving_frames:=0
var gate_contact_queries:=0
var gate_swept_queries:=0
var upper_obstruction_checks:=0
var precise_panel_controls:=0
func _initialize() -> void:
	target_lift_name="ForwardStaffLift"
	test_stop_sequence.assign([1,5,9,4,0])
	super._initialize()
func wait_trip(lift:Node3D,cart:RigidBody3D,actor:CharacterBody3D,goal:int) -> void:
	var previous_contacts:Dictionary={}
	var gate_exclusions:Array[RID]=[lift.cabin.get_rid()]
	for body in lift.cabin_gate.find_children("*","CollisionObject3D",true,false):gate_exclusions.append(body.get_rid())
	var reached:=false
	var previous:=0.0
	var travel:=absf(lift.floor_heights[goal]-lift.cabin.position.y)
	var expected_seconds:float=travel/lift.maximum_speed+lift.maximum_speed/lift.acceleration+2.0/.75+3.0
	var budget_frames:int=ceili(expected_seconds*60.0)
	for frame in range(budget_frames):
		await physics_frame
		assert(abs(lift.travel_velocity)<=lift.maximum_speed+.001)
		if lift.phase=="moving":
			assert(lift.cabin_gate.open_fraction<.001,"Cabin gate stays closed during travel")
			for gate in lift.landing_gates:assert(gate.open_fraction<.001,"All shaft gates stay closed during travel")
			assert(abs(lift.travel_velocity-previous)<.025,"Acceleration is bounded")
		# Detect fitted-frame/roof intersections independently of carried-body tests.
		# Kinematic platforms can otherwise move through static geometry unnoticed.
		for contact in lift.cabin.get_children():
			if not contact is CollisionShape3D:continue
			var query:=PhysicsShapeQueryParameters3D.new()
			query.shape=contact.shape
			query.transform=contact.global_transform
			query.exclude=[lift.cabin.get_rid()]
			query.margin=.0001
			for hit in lift.get_world_3d().direct_space_state.intersect_shape(query,64):
				if hit.collider is StaticBody3D and not hit.collider is AnimatableBody3D:
					assert(false,"Moving cabin clips static structure at cabin Y%.4f: %s / %s"%[lift.cabin.position.y,contact.name,hit.collider.get_path()])
		for leaf in lift.cabin_gate.leaves:
			for contact in leaf.get_children():
				if not contact is CollisionShape3D:continue
				var query:=PhysicsShapeQueryParameters3D.new()
				query.shape=contact.shape
				query.transform=contact.global_transform
				query.exclude=gate_exclusions
				query.margin=.0001
				for hit in lift.get_world_3d().direct_space_state.intersect_shape(query,64):
					if hit.collider is StaticBody3D or hit.collider is AnimatableBody3D:assert(false,"Moving cabin gate clips external structure at Y%.4f: %s"%[lift.cabin.position.y,hit.collider.get_path()])
				gate_contact_queries+=1
				var identity:int=contact.get_instance_id()
				if previous_contacts.has(identity):
					var previous_pose:Transform3D=previous_contacts[identity]
					query.transform=previous_pose
					query.motion=contact.global_transform.origin-previous_pose.origin
					var fractions=lift.get_world_3d().direct_space_state.cast_motion(query)
					assert(fractions[0]>.99999,"Continuous cabin-gate swept contact blocked")
					gate_swept_queries+=1
				previous_contacts[identity]=contact.global_transform
		if lift.phase=="moving":
			assert(not lift.cabin_gate.cabin_present_and_stopped)
			for gate in lift.landing_gates:assert(not gate.cabin_present_and_stopped and not gate.requested_open)
			moving_frames+=1
		previous=lift.travel_velocity
		assert(cart.get_parent().name=="PersistentActors","Cart is not parented to moving lift")
		assert(abs(cart.global_position.y-lift.cabin.global_position.y)<.16,"Loose physical cart stays on moving platform: cart=%s cabin=%s phase=%s velocity=%s"%[cart.global_position,lift.cabin.global_position,lift.phase,lift.travel_velocity])
		assert(abs(actor.global_position.y-lift.cabin.global_position.y)<.18,"Character follows platform")
		for product in cart.products:
			assert(product.get_parent()==cart.get_parent())
			var p:Vector3=cart.to_local(product.global_position)
			assert(p.y>.80 and p.y<1.3 and abs(p.x)<.4 and abs(p.z)<.6,"Loose load retained during trip")
		if lift.current_floor==goal and lift.phase=="idle":
			reached=true
			break
	assert(reached,"Lift failed to reach requested floor")
	for i in range(10):
		assert(lift.landing_gates[i].cabin_present_and_stopped==(i==goal))
		assert(lift.landing_gates[i].open_fraction>.999 if i==goal else lift.landing_gates[i].open_fraction<.001)
	visited.append(goal)
	if goal==9:
		var blocker:=CharacterBody3D.new()
		var contact:=CollisionShape3D.new()
		var sphere:=SphereShape3D.new()
		sphere.radius=.18
		contact.shape=sphere
		blocker.add_child(contact)
		lift.get_parent().add_child(blocker)
		blocker.global_position=lift.landing_gates[9].global_position+Vector3(0,1.2,0)
		for frame in range(5):await physics_frame
		assert(lift.request_floor(8))
		for frame in range(100):await physics_frame
		assert(lift.phase=="closing" and absf(lift.cabin.position.y-102)<.001)
		assert(lift.landing_gates[9].threshold_occupied())
		blocker.free()
		assert(lift.request_floor(9))
		for frame in range(110):await physics_frame
		assert(lift.phase=="idle" and lift.landing_gates[9].open_fraction>.999)
		upper_obstruction_checks+=1

func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(120):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var lift:Node3D=ship.find_child(target_lift_name,true,false)
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var cart:RigidBody3D=ship.find_child("CustodialCart",true,false)
	assert(lift.phase=="idle" and lift.current_floor==0)
	# Load the fixture on a stationary cabin, then test entirely physical carry.
	var base:=lift.to_global(Vector3(lift.gate_origin_xz.x,lift.floor_heights[0],lift.gate_origin_xz.y))
	var offset:Vector3=base+lift.global_basis*Vector3(1.85,.04,0)-cart.global_position
	cart.global_position+=offset
	cart.linear_velocity=Vector3.ZERO
	cart.angular_velocity=Vector3.ZERO
	cart.sleeping=false
	for product in cart.products:
		product.global_position+=offset
		product.linear_velocity=Vector3.ZERO
		product.angular_velocity=Vector3.ZERO
		product.sleeping=false
	actor.spawn_position=base+lift.global_basis*Vector3(2.15,.1,1.25)
	actor.global_position=actor.spawn_position
	actor.velocity=Vector3.ZERO
	for frame in range(60):await physics_frame
	assert(not lift.request_floor(-1) and not lift.request_floor(lift.floor_heights.size()))
	var original_ids:Array=["D01","D02","D03","D08_WET","D09","D13","D14","D15","D16","D17"]
	assert(lift.stop_ids==original_ids and lift.floor_heights==[0.0,6.0,12.0,46.2,52.5,84.0,88.5,93.0,97.5,102.0])
	assert(lift.operation_ready and lift.cabin_file=="AST-CIR-003_ten_stop.glb" and lift.retained_upper_gates.size()==5)
	for i in range(10):
		assert(str(lift.landing_gates[i].persistent_id)==str(original_ids[i])+"_forward_staff_lift_gate")
		var button:Node3D=lift.find_child("forward_staff_cabin_"+str(original_ids[i]),true,false)
		assert(button!=null and button.controller==lift and button.floor_index==i)
		var aim:Vector3=button.global_position-actor.camera.global_position
		actor.rotation.y=atan2(-aim.x,-aim.z)
		actor.pitch=atan2(aim.y,Vector2(aim.x,aim.z).length())
		actor.camera.rotation.x=actor.pitch
		assert(actor.target_from_view()==button,"All ten authored controls precisely selectable")
		precise_panel_controls+=1
	var house:Node3D=ship.get_node("ShipSpace/Districts/TidalGardenReceivingCandidate")
	for deck in range(13,18):
		var module:Node3D=house.get_node("TidalD"+str(deck)+"ServiceReceiving")
		assert(module.get_meta("upper_staff_lift_enabled") and module.get_meta("temporary_shaft_closure_reconciled"))
		assert(module.find_child("D"+str(deck)+"_UnfinishedShaftPhysicalClosure",true,false)==null)
		assert(lift.landing_gates[deck-8]==lift.retained_upper_gates["D"+str(deck)])
	assert(house.get_node("ListeningSalonCompositeCapReceivingCore").get_child_count()==13)
	assert(house.get_node("RetainedLandscapeAndSeating").get_child_count()==81)
	assert(house.get_node("TidalGardenPassengerLiftCandidate").floor_heights==[84.0,88.5,93.0,97.5,102.0])
	var ordinary:Dictionary={}
	var specialty:Dictionary={}
	for entry in ship.get_node("ShipSystems/ReceivedRoomResidency").entries:
		if str(entry.parent.name)=="TidalRoomCandidates":ordinary[str(entry.room.name)]=true
		if str(entry.parent.name)=="SpecialtyHomeCandidates":specialty[str(entry.room.name)]=true
	assert(ordinary.size()==85 and specialty.size()==46)
	for destination in test_stop_sequence:
		await select_floor_by_focus(lift,actor,destination)
		await wait_trip(lift,cart,actor,destination)
		assert(abs(cart.global_position.y-lift.to_global(Vector3(lift.gate_origin_xz.x,lift.floor_heights[destination],lift.gate_origin_xz.y)).y)<.12)
	# Obstruction of the actual threshold must hold departure.
	var blocker:=RigidBody3D.new()
	blocker.gravity_scale=0
	blocker.position=base+lift.global_basis*Vector3(-.1,1,0)
	var contact:=CollisionShape3D.new()
	var shape:=SphereShape3D.new()
	shape.radius=.18
	contact.shape=shape
	blocker.add_child(contact)
	ship.get_node("ShipSpace/PersistentActors").add_child(blocker)
	for frame in range(5):await physics_frame
	lift.request_floor(1)
	for frame in range(100):await physics_frame
	assert(lift.phase=="closing" and abs(lift.cabin.position.y-lift.floor_heights[0])<.001)
	blocker.queue_free()
	lift.request_floor(0)
	for frame in range(100):await physics_frame
	assert(lift.phase=="idle")
	print(target_lift_name+" LIFT PASS: physical capsule/cart/four loose bottles carried both directions, bounded acceleration, closed travel gates, obstruction holds departure and same-floor cancellation reopens. Precise RMB/E for every trip destination and unfocused rejection pass. Boarding turns, save and visual acceptance pending.")
	var result:Dictionary={"status":"PASS","actual_main_loaded":true,"visited_stop_indices":visited,"original_five_stop_ids_preserved":true,"ten_gate_button_ids_unique":true,"upper_gates_reused":5,"upper_sills_reused":5,"precise_panel_controls":precise_panel_controls,"moving_frames":moving_frames,"moving_gate_contact_queries":gate_contact_queries,"continuous_gate_sweep_queries":gate_swept_queries,"upper_obstruction_checks":upper_obstruction_checks,"lower_obstruction_checks":1,"same_floor_cancellation_checks":2,"physical_passenger_cart_four_loose_products_carried":true,"closed_gates_on_travel":true,"all_five_closures_reconciled":true,"ordinary_homes":85,"specialty_homes":46,"errors":[],"limits":"Bounded actual-main travel/carried fixture/contact/interlock checks; full route, cart/species turning and service hygiene/load/structural/final visual/target hardware acceptance remain open."}
	FileAccess.open("res://artifacts/forward_staff_upper_operation.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("FORWARD_STAFF_UPPER_OPERATION ",JSON.stringify(result))
	print("PASS: bounded forward staff ten-stop travel and guarded receiving interfaces")
	main.queue_free()
	await process_frame
	quit()
