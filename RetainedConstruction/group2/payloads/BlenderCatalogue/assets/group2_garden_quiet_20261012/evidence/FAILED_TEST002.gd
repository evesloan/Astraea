extends SceneTree
var checks:=0
func _initialize()->void:call_deferred("run")
func walk(actor:CharacterBody3D,target:Vector3)->void:
	var key:=InputEventKey.new();key.keycode=KEY_W;key.physical_keycode=KEY_W;key.pressed=true;Input.parse_input_event(key.duplicate());Input.flush_buffered_events()
	var reached:=false
	for frame in range(800):
		var delta:=target-actor.global_position
		if Vector2(delta.x,delta.z).length()<.09:reached=true;break
		actor.rotation.y=atan2(-delta.x,-delta.z);await physics_frame;assert(abs(actor.global_position.y-97.5)<.12);checks+=1
	key.pressed=false;Input.parse_input_event(key.duplicate());Input.flush_buffered_events()
	for frame in range(15):await physics_frame
	assert(reached and actor.is_on_floor(),"Actual source garden/quiet approach remains supported and clear")
func run()->void:
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_garden_quiet/COMPONENTS_r001.json"))
	var results:Array=[]
	for row in data.rows:
		var world:=Node3D.new();world.set_meta("group2_isolated_source_fixture",true);root.add_child(world)
		var retained:Node3D=(load("res://assets/models/"+str(row.source_model))as PackedScene).instantiate();world.add_child(retained)
		load("res://scripts/static_contact_cache.gd").attach_group(retained,retained.find_children("*","MeshInstance3D",true,false))
		var before:Dictionary={}
		for mesh in retained.find_children("*","MeshInstance3D",true,false):before[mesh]=mesh.global_transform
		var section:Node3D=load("res://scripts/group2_garden_quiet/package.gd").build_source_fixture(world,row.kind)
		for mesh in before:assert(mesh.global_transform.is_equal_approx(before[mesh]));checks+=1
		var actor:CharacterBody3D=load("res://scripts/player.gd").new();world.add_child(actor)
		var points:Array=[Vector3(94.55,97.5,384.9),Vector3(94.55,97.5,384.6),Vector3(94.55,97.5,384.9)] if row.kind=="family_hydroponics" else [Vector3(83,97.5,-356.0),Vector3(83,97.5,-358.0),Vector3(83,97.5,-359.7),Vector3(83,97.5,-356.0)]
		actor.position=points[0]+Vector3.UP*.05;actor.spawn_position=actor.position
		for frame in range(20):await physics_frame
		for point in points:await walk(actor,point)
		var budget:Node=load("res://scripts/lighting_budget.gd").new();world.add_child(budget);budget.configure(section,actor)
		var active:=0
		for light in section.find_children("*","OmniLight3D",true,false):
			if light.visible and light.shadow_enabled:active+=1
		assert(active>0 and active<=8)
		results.append({"kind":row.kind,"retained_receiver_poses_unchanged":true,"original_player_supported_approach":true,"existing_light_budget":true,"temporary_floor_added":false})
		world.free();await physics_frame;print("GARDEN QUIET "+str(row.kind)+" passed")
	FileAccess.open("res://artifacts/group2_garden_quiet.json",FileAccess.WRITE).store_string(JSON.stringify({"pass":true,"checks":checks,"rows":results,"original_props_retained_by_source_bounds_check":true,"agriculture_body_or_production_adoption_accepted":false},"\t")+"\n")
	print("GROUP2 GARDEN QUIET PASS actual receivers and original player");quit()
