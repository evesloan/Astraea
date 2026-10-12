extends SceneTree
var checks:=0
func _initialize()->void:call_deferred("run")
func door_static_clearance(door:Node3D)->void:
	var excluded:Array[RID]=[]
	for body in door.find_children("*","CollisionObject3D",true,false):excluded.append(body.get_rid())
	for leaf in door.leaves:
		for collision in leaf.find_children("*","CollisionShape3D",true,false):
			var query:=PhysicsShapeQueryParameters3D.new();query.shape=collision.shape;query.transform=collision.global_transform;query.exclude=excluded
			for hit in door.get_world_3d().direct_space_state.intersect_shape(query,64):assert(not hit.collider is StaticBody3D,"Retained wide door must clear new enclosure and source receiver")
			checks+=1
func walk(actor:CharacterBody3D,target:Vector3)->void:
	var key:=InputEventKey.new();key.keycode=KEY_W;key.physical_keycode=KEY_W;key.pressed=true;Input.parse_input_event(key.duplicate());Input.flush_buffered_events()
	var reached:=false
	for frame in range(1000):
		var d:=target-actor.global_position
		if Vector2(d.x,d.z).length()<.1:reached=true;break
		actor.rotation.y=atan2(-d.x,-d.z);await physics_frame
		assert(abs(actor.global_position.y-97.5)<.12);checks+=1
	key.pressed=false;Input.parse_input_event(key.duplicate());Input.flush_buffered_events()
	for frame in range(15):await physics_frame
	assert(reached and actor.is_on_floor(),"Actual retained receiver/source childcare path must remain supported and clear")
func run()->void:
	var world:=Node3D.new();world.set_meta("group2_isolated_source_fixture",true);root.add_child(world)
	var retained:Node3D=(load("res://assets/models/FAMILY_TERRACE_ARCHITECTURE_lift_r003.glb")as PackedScene).instantiate();world.add_child(retained)
	load("res://scripts/static_contact_cache.gd").attach_group(retained,retained.find_children("*","MeshInstance3D",true,false))
	var before:Dictionary={}
	for mesh in retained.find_children("*","MeshInstance3D",true,false):before[mesh]=mesh.global_transform
	var section:Node3D=load("res://scripts/group2_family_childcare/package.gd").build_source_fixture(world)
	for mesh in before:assert(mesh.global_transform.is_equal_approx(before[mesh]));checks+=1
	var door:=section.get_node("CareEntry")as Node3D
	var actor:CharacterBody3D=load("res://scripts/player.gd").new();world.add_child(actor)
	var plate:=door.find_child("DATUM_call_button",true,false)as Node3D;assert(plate!=null)
	actor.position=Vector3(plate.global_position.x,97.55,plate.global_position.z+1.2);actor.spawn_position=actor.position
	for frame in range(20):await physics_frame
	assert(actor.is_on_floor())
	var delta:=plate.global_position-actor.camera.global_position;actor.rotation.y=atan2(-delta.x,-delta.z);actor.pitch=atan2(delta.y,Vector2(delta.x,delta.z).length());actor.camera.rotation.x=actor.pitch
	assert(actor.target_from_view()==door)
	var focus:=InputEventMouseButton.new();focus.button_index=MOUSE_BUTTON_RIGHT;focus.pressed=true;Input.parse_input_event(focus.duplicate())
	var key:=InputEventKey.new();key.keycode=KEY_E;key.physical_keycode=KEY_E;key.pressed=true;Input.parse_input_event(key.duplicate())
	for frame in range(85):await physics_frame;door_static_clearance(door)
	assert(door.open_fraction>.999);key.pressed=false;Input.parse_input_event(key.duplicate());focus.pressed=false;Input.parse_input_event(focus.duplicate())
	await walk(actor,Vector3(86,97.5,362.5))
	for pt in [Vector3(86,97.5,359.0),Vector3(86,97.5,357.9),Vector3(83.6,97.5,357.9),Vector3(88.3,97.5,357.9),Vector3(86,97.5,359.0),Vector3(86,97.5,362.5)]:await walk(actor,pt)
	await walk(actor,Vector3(86,97.5,359.0))
	var budget:Node=load("res://scripts/lighting_budget.gd").new();world.add_child(budget);budget.configure(section,actor)
	var active:=0
	for light in section.find_children("*","OmniLight3D",true,false):
		if light.visible and light.shadow_enabled:active+=1
	assert(active>0 and active<=8)
	await walk(actor,Vector3(86,97.5,362.5))
	await walk(actor,Vector3(plate.global_position.x,97.5,plate.global_position.z+1.2))
	delta=plate.global_position-actor.camera.global_position;actor.rotation.y=atan2(-delta.x,-delta.z);actor.pitch=atan2(delta.y,Vector2(delta.x,delta.z).length());actor.camera.rotation.x=actor.pitch
	assert(actor.target_from_view()==door);focus.pressed=true;Input.parse_input_event(focus.duplicate());key.pressed=true;Input.parse_input_event(key.duplicate())
	for frame in range(85):await physics_frame;door_static_clearance(door)
	assert(door.open_fraction<.001);key.pressed=false;Input.parse_input_event(key.duplicate());focus.pressed=false;Input.parse_input_event(focus.duplicate())
	var file:=FileAccess.open("res://artifacts/group2_family_childcare.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"pass":true,"checks":checks,"all_retained_receiver_mesh_poses_unchanged":true,"original_player_entry_and_internal_aisles":true,"RMB_E_exact_source_wide_door":true,"temporary_floor_fixture_added":false,"admission_child_body_capacity_structural_or_final_acceptance":false},"\t")+"\n")
	print("GROUP2 FAMILY CHILDCARE PASS actual retained receiver and original player; programme/admission held");quit()
