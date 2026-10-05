extends "res://tests/validate_crown_access.gd"
# One setup placement, then every approach, threshold and return uses collision movement.
const FLOOR := 106.5
const PUBLIC_ROUTE := [Vector2(0,-520),Vector2(0,-177),Vector2(-44,-177),Vector2(-44,-77),Vector2(45,-77),Vector2(-5.5,-77),Vector2(-5.5,-106),Vector2(-5.5,-77),Vector2(5.5,-77),Vector2(5.5,-111),Vector2(0,-111)]
var bridge_doors:Array[Node3D]=[]
var require_closed := false

func assert_closed() -> void:
	for door in bridge_doors:
		assert(not door.desired_open and door.open_fraction<.001,"Public circulation must not open either controlled bridge door")

func walk(actor:CharacterBody3D,destination:Vector2) -> void:
	var reached:=false
	for frame in range(700):
		var offset:=Vector3(destination.x-actor.position.x,0,destination.y-actor.position.z)
		if offset.length()<.09:reached=true;break
		var movement:=offset.normalized()*3.1
		actor.velocity=Vector3(movement.x,-.1 if actor.is_on_floor() else actor.velocity.y-9.8/60,movement.z)
		actor.move_and_slide();await physics_frame
		assert(absf(actor.position.y-FLOOR)<.12,"Public/bridge walker lost D18 support")
		if require_closed:assert_closed()
	assert(reached,"Bridge walk stalled at %s toward %s"%[actor.position,destination])
	actor.velocity=Vector3.ZERO

func aim_at(actor:CharacterBody3D,point:Vector3) -> void:
	var aim:Vector3=point-actor.camera.global_position
	actor.rotation.y=atan2(-aim.x,-aim.z)
	actor.pitch=atan2(aim.y,Vector2(aim.x,aim.z).length())
	actor.camera.rotation.x=actor.pitch

func select_door(actor:CharacterBody3D,door:Node3D) -> void:
	# Closed centre first, then actual moving contacts for an open/part-open pair.
	var targets:Array[Vector3]=[door.to_global(Vector3(0,1.3,0)),door.to_global(Vector3(-1.30,1.3,0)),door.to_global(Vector3(1.30,1.3,0))]
	for leaf in door.leaves:
		for contact in leaf.get_children():
			if contact is CollisionShape3D:targets.append(contact.global_position)
	for point in targets:
		aim_at(actor,point)
		if actor.target_from_view()==door:return
	assert(false,"No precise reachable bridge-door target from %s: %s"%[actor.position,door.name])

func press(actor:CharacterBody3D,door:Node3D,focused:bool=true) -> void:
	actor.velocity=Vector3.ZERO;actor.set_physics_process(true)
	select_door(actor,door)
	focus(focused);key(KEY_E,true)
	for frame in range(3):await physics_frame
	key(KEY_E,false);focus(false)
	actor.set_physics_process(false);actor.velocity=Vector3.ZERO

func animate(ship:Node3D,door:Node3D,frames:int=100) -> void:
	for frame in range(frames):await physics_frame;assert_door_clear(ship,door)

func go_local(actor:CharacterBody3D,door:Node3D,z:float) -> void:
	var p:=door.to_global(Vector3(0,0,z))
	await walk_route(actor,[Vector2(p.x,p.z)])

func closed_collision(actor:CharacterBody3D,door:Node3D,side:float) -> void:
	assert(not door.desired_open and door.open_fraction<.001)
	var contacted:=false
	for frame in range(90):
		var movement:Vector3=-door.global_basis.z*side*3.1
		actor.velocity=Vector3(movement.x,-.1 if actor.is_on_floor() else actor.velocity.y-9.8/60,movement.z)
		actor.move_and_slide();await physics_frame
		for i in range(actor.get_slide_collision_count()):
			var collider:Node=actor.get_slide_collision(i).get_collider()
			if door.is_ancestor_of(collider):contacted=true
		assert(door.to_local(actor.global_position).z*side>.20,"Closed bridge door allowed capsule passage")
	assert(contacted,"Capsule must physically contact the closed moving leaves")
	actor.velocity=Vector3.ZERO
	await go_local(actor,door,side*2.0)

func exercise_door(ship:Node3D,actor:CharacterBody3D,door:Node3D,first_side:float) -> void:
	for side in [first_side,-first_side]:
		await go_local(actor,door,side*2.0)
		if door.desired_open:
			await press(actor,door);await animate(ship,door)
		await closed_collision(actor,door,side)
		await press(actor,door,false)
		assert(not door.desired_open and door.open_fraction<.001,"Unfocused E must be rejected from both sides")
		await press(actor,door)
		assert(door.desired_open,"RMB/E must operate the selected bridge threshold")
		await animate(ship,door,18)
		assert(door.open_fraction>.05 and door.open_fraction<.95)
		# A second normal input reverses a partially opened pair without a pose reset.
		await press(actor,door);assert(not door.desired_open)
		await animate(ship,door);assert(door.open_fraction<.001)
		await press(actor,door);await animate(ship,door);assert(door.open_fraction>.999)
		await go_local(actor,door,-side*2.0)
	# Occupied-sweep rejection and live interruption use the same real walker.
	await go_local(actor,door,-.65)
	await press(actor,door)
	assert(door.obstructed and door.desired_open,"Occupied bridge sweep must reject closing")
	await animate(ship,door,15);assert(door.open_fraction>.999)
	await go_local(actor,door,-2.0)
	await press(actor,door);assert(not door.desired_open)
	# Enter the sweep before either open leaf reaches the centreline.
	await go_local(actor,door,-1.30)
	assert(door.obstructed and door.open_fraction>.05 and door.open_fraction<.999,"Moving bridge door must pause for an entering actor")
	var paused:float=door.open_fraction
	await animate(ship,door,30)
	assert(is_equal_approx(paused,door.open_fraction),"Occupied animation advanced")
	await go_local(actor,door,-2.0)
	await animate(ship,door);assert(door.open_fraction<.001 and not door.obstructed,"Clear sweep must resume its interrupted closure")
	await go_local(actor,door,-.65)
	await press(actor,door)
	assert(door.obstructed and not door.desired_open,"Occupied inward sweep must also reject opening a closed bridge door")
	await animate(ship,door,15);assert(door.open_fraction<.001)
	await go_local(actor,door,-2.0)
	await press(actor,door);await animate(ship,door)
	await go_local(actor,door,-first_side*2.0)
	print("BRIDGE THRESHOLD PASS: ",door.name," both-side input, collision, reversal, occupancy and pause/resume")

func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
	for frame in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var enclosure:Node3D=ship.find_child("BridgeEnclosure_WIP",true,false)
	assert(enclosure!=null and enclosure.find_child("BridgeEnclosureArchitecture",true,false)!=null)
	var aft:Node3D=enclosure.get_node("BridgeEnclosureDoor_Aft")
	var fore:Node3D=enclosure.get_node("BridgeEnclosureDoor_Fore")
	bridge_doors.assign([aft,fore])
	assert(aft.position.distance_to(Vector3(0,FLOOR,-118.3))<.001 and fore.position.distance_to(Vector3(0,FLOOR,-171.7))<.001)
	assert(aft.global_basis.z.dot(Vector3.BACK)>.999 and fore.global_basis.z.dot(Vector3.FORWARD)>.999)
	assert(aft.persistent_id!=fore.persistent_id)
	for door in bridge_doors:
		assert(door.get_script().resource_path=="res://scripts/service_door.gd" and door.get_meta("catalogue_file")=="AST-STF-008.glb")
	assert_closed()
	actor.set_physics_process(false);actor.position=Vector3(0,FLOOR+.1,-520);actor.velocity=Vector3.ZERO
	require_closed=true
	await walk_route(actor,PUBLIC_ROUTE)
	var reverse:Array=PUBLIC_ROUTE.duplicate();reverse.reverse()
	await walk_route(actor,reverse)
	require_closed=false
	await walk_route(actor,[Vector2(0,-177),Vector2(0,-173.7)])
	await exercise_door(ship,actor,fore,1.0)
	await walk_route(actor,[Vector2(0,-140),Vector2(0,-120.3)])
	await exercise_door(ship,actor,aft,-1.0)
	await walk_route(actor,[Vector2(0,-113.5),Vector2(0,-111),Vector2(5.5,-111),Vector2(5.5,-77)])
	print("BRIDGE ENCLOSURE ACCESS PASS: complete Z-520/public-bypass/fore-street/actual primary lift and core approaches walked both ways with both bridge doors closed; both thresholds physically traversed with precise RMB/E, unfocused rejection, closed collision, reversal and occupied interruption. Scripted capsule only; species fit, roles and final art remain pending.")
	main.queue_free();await process_frame;quit()
