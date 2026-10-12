extends SceneTree
var checks := 0
func _initialize() -> void: call_deferred("run")
func walk(actor: CharacterBody3D,target: Vector3) -> void:
	var key := InputEventKey.new();key.keycode=KEY_W;key.physical_keycode=KEY_W;key.pressed=true
	Input.parse_input_event(key.duplicate());Input.flush_buffered_events()
	var reached := false
	for frame in range(1000):
		var delta := target-actor.global_position
		if Vector2(delta.x,delta.z).length()<.1:reached=true;break
		actor.rotation.y=atan2(-delta.x,-delta.z)
		await physics_frame
		assert(actor.global_position.y>-.05 and actor.global_position.y<1.65,"Scoped source floor/ramp remains bounded")
		checks += 1
	key.pressed=false;Input.parse_input_event(key.duplicate());Input.flush_buffered_events()
	for frame in range(15):await physics_frame
	assert(reached,"Source construction route blocked: actor=%s target=%s"%[actor.global_position,target])
	assert(actor.is_on_floor() and abs(actor.global_position.y-target.y)<.09)
	checks += 2
func floor_fixture(world: Node3D) -> void:
	var floor := StaticBody3D.new();var contact := CollisionShape3D.new();var shape := BoxShape3D.new()
	shape.size=Vector3(36,.24,30);contact.shape=shape;contact.position.y=-.12;floor.add_child(contact);world.add_child(floor)
func input_e(pressed: bool) -> void:
	var key := InputEventKey.new();key.keycode=KEY_E;key.physical_keycode=KEY_E;key.pressed=pressed
	Input.parse_input_event(key.duplicate());Input.flush_buffered_events()
func aim(actor: CharacterBody3D,door: Node3D) -> void:
	var handle: Vector3=door.leaves[0].to_global(Vector3(.925,1.1,.060))
	var delta: Vector3=handle-actor.camera.global_position
	actor.rotation.y=atan2(-delta.x,-delta.z)
	actor.pitch=atan2(delta.y,Vector2(delta.x,delta.z).length());actor.camera.rotation.x=actor.pitch
	assert(actor.target_from_view()==door,"Original view ray selects actual changing handle")
func door_static_clearance(door: Node3D) -> void:
	var excluded: Array[RID]=[]
	for body in door.find_children("*","CollisionObject3D",true,false):excluded.append(body.get_rid())
	for leaf in door.leaves:
		for collision in leaf.find_children("*","CollisionShape3D",true,false):
			var query := PhysicsShapeQueryParameters3D.new();query.shape=collision.shape
			query.transform=collision.global_transform;query.exclude=excluded
			for hit in door.get_world_3d().direct_space_state.intersect_shape(query,64):
				assert(not hit.collider is StaticBody3D,"New source wall/furnishing must clear retained door swing")
			checks+=1
func run() -> void:
	var world := Node3D.new();world.set_meta("group2_isolated_source_fixture",true);root.add_child(world)
	floor_fixture(world)
	var results: Array=[]
	for kit in ["TIDAL","QUIET"]:
		var section: Node3D=load("res://scripts/group2_vip_pavilions/package.gd").build_source_fixture(world,kit)
		assert(not section.get_meta("production_adoption"))
		var actor: CharacterBody3D=load("res://scripts/player.gd").new();world.add_child(actor)
		actor.position=Vector3(-16.4,.05,-5.05);actor.spawn_position=actor.position
		for frame in range(20):await physics_frame
		# Physical original controller crosses the toe, entire18m rise, top landing and wet east viewing edge.
		for point in [Vector3(-14.7,.025,-5.05),Vector3(-6,.75,-5.05),Vector3(3.5,1.5,-5.05),
		 Vector3(13.5,1.5,-5.05),Vector3(13.5,1.5,-6.8)]:await walk(actor,point)
		var budget: Node=load("res://scripts/lighting_budget.gd").new();section.add_child(budget)
		budget.configure(section,actor)
		var active := 0
		for light in section.find_children("*","OmniLight3D",true,false):
			if light.visible and light.shadow_enabled:active += 1
		assert(active>0 and active<=8,"Actual fixture visibility uses original eight-source budget")
		budget.free()
		for point in [Vector3(13.5,1.5,-5.05),Vector3(3.5,1.5,-5.05),Vector3(-6,.75,-5.05),
		 Vector3(-14.7,.025,-5.05),Vector3(-16.4,0,-5.05)]:await walk(actor,point)
		# Existing public dry lane is represented only by the isolated floor fixture.
		for point in [Vector3(-16.4,0,0),Vector3(16.4,0,0),Vector3(16.4,0,3.3),Vector3(-16.4,0,3.3)]:await walk(actor,point)
		actor.free();await physics_frame
		for name in ["Privacy0","Privacy1"]:
			var door := section.get_node(name) as Node3D
			assert(door.open_fraction<.001)
			var visitor: CharacterBody3D=load("res://scripts/player.gd").new();world.add_child(visitor)
			var handle: Vector3=door.leaves[0].to_global(Vector3(.925,1.1,.060))
			visitor.position=Vector3(handle.x,.05,handle.z+1.2);visitor.spawn_position=visitor.position
			for frame in range(20):await physics_frame
			aim(visitor,door)
			var focus := InputEventMouseButton.new();focus.button_index=MOUSE_BUTTON_RIGHT;focus.pressed=true
			Input.parse_input_event(focus.duplicate());input_e(true)
			for frame in range(80):await physics_frame;door_static_clearance(door)
			input_e(false)
			assert(door.open_fraction>.999)
			aim(visitor,door);input_e(true)
			for frame in range(80):await physics_frame;door_static_clearance(door)
			input_e(false);focus.pressed=false;Input.parse_input_event(focus.duplicate())
			assert(door.open_fraction<.001)
			visitor.free();await physics_frame
			checks+=3
		assert(section.find_children("*","OmniLight3D",true,false).size()==7)
		results.append({"kit":kit,"original_player_full_ramp_up_down":true,"public_lane_walk":true,
		 "two_retained_privacy_mechanisms_RMB_E_open_close":true,"full_door_sweep_new_static_clearance":true,
		 "original_eight_shadow_budget":true,"placement_accepted":false})
		section.free();await physics_frame
		print("VIP SOURCE kit "+kit+" passed")
	var file:=FileAccess.open("res://artifacts/group2_vip_pavilions.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"pass":true,"checks":checks,"results":results,"scope":"Unplaced kits, original source controller; shared receiving not installed",
	 "actual_shared_roof_bearing_access_swimming_cart_species_final_art_accepted":false},"\t")+"\n")
	print("GROUP2 VIP SOURCE PASS; placement remains held")
	quit()
