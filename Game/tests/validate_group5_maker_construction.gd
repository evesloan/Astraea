extends "res://tests/validate_group5_large_venue_doors.gd"
func run()->void:
	var spec:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group5/MAKER_CONSTRUCTION.json"))
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(20):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var manager:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
	var owner:Node3D=load("res://scripts/group5_large_venue_lighting.gd")._owner(ship,"D09_directory_05")
	var installed:Node3D=owner.get_node_or_null("Group5MakerConstruction")
	var originals:Dictionary={}
	for mesh:MeshInstance3D in owner.find_children("*","MeshInstance3D",true,false):
		if installed==null or not installed.is_ancestor_of(mesh):originals[mesh.get_instance_id()]=[mesh.mesh.get_instance_id(),mesh.transform]
	var startup:bool=ship.get_meta("group5_maker_construction_attached",false)
	var builder=load("res://scripts/group5_maker_construction.gd");var construction:Node3D=builder.build(ship)
	record("idempotent_original_owner",builder.build(ship)==construction)
	var preserved:=0
	for mesh:MeshInstance3D in owner.find_children("*","MeshInstance3D",true,false):
		if originals.has(mesh.get_instance_id()):
			var prior:Array=originals[mesh.get_instance_id()];record("original_maker_mesh_"+str(mesh.get_instance_id()),mesh.mesh.get_instance_id()==prior[0] and mesh.transform.is_equal_approx(prior[1]));preserved+=1
	record("all108_original_maker_meshes",preserved==108)
	var door:Node3D=construction.get_node(str(spec.door.door_name))
	actor.set_controls_enabled(true);actor.global_position=vec(spec.door.public_approach_world_xyz);actor.velocity=Vector3.ZERO;manager.prepare_position(actor.global_position)
	for i in range(15):await physics_frame
	var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget");var optical:Array=[]
	for row in spec.fixtures:
		var light:OmniLight3D=construction.get_node(str(row.name));var query:=PhysicsRayQueryParameters3D.create(light.global_position,light.global_position+Vector3.UP*.05)
		var hit:=ship.get_world_3d().direct_space_state.intersect_ray(query)
		record("physical_lens_"+str(row.name),not hit.is_empty() and absf(hit.position.y-(light.global_position.y+.03))<.00005)
	for at in [Vector3(-58.5,52.53,0),Vector3(-71,52.53,-9),Vector3(-89.7,52.53,-15)]:
		actor.global_position=at;manager.prepare_position(at)
		for i in range(3):await physics_frame
		budget.refresh();var reaches:=0;var active:=0
		for light:Light3D in budget.sources:
			if not is_instance_valid(light) or not light.is_inside_tree():continue
			if light.visible and light.shadow_enabled:active+=1
			if construction.is_ancestor_of(light):
				record("no_maker_wall_leak_"+str(at)+str(light.name),not light.visible or light.shadow_enabled)
				if light.visible and light.shadow_enabled and light.global_position.distance_to(at+Vector3.UP*1.5)<light.omni_range and budget._clear_sample(light.global_position,at+Vector3.UP*1.5):reaches+=1
		record("maker_reached_light_"+str(at),reaches>0 and active<=8 and budget.shadow_source_budget==8);optical.append({"world_xyz":str(at),"active_sources_reaching_viewer":reaches,"total_active_shadow_sources":active})
	actor.global_position=vec(spec.door.public_approach_world_xyz);actor.velocity=Vector3.ZERO
	for i in range(15):await physics_frame
	var ok:=true
	for at in [vec(spec.door.public_foyer_world_xyz),vec(spec.door.public_stance_world_xyz)]:
		if not await leg(actor,at,"continuous original receiving floor and recessed public control"):ok=false;break
	if ok and not await operate(actor,door,"PublicControl",true):ok=false
	for at in [vec(spec.door.public_foyer_world_xyz),vec(spec.door.interior_world_xyz),vec(spec.door.interior_stance_world_xyz)]:
		if not ok:break
		if not await leg(actor,at,"continuous original recessed foyer and opened threshold"):ok=false
	if ok:
		var witness:=CharacterBody3D.new();var col:=CollisionShape3D.new();var cap:=CapsuleShape3D.new();cap.radius=.3;cap.height=1.8;col.shape=cap;col.position=Vector3.UP*.9;witness.add_child(col);ship.get_node("ShipSpace/PersistentActors").add_child(witness);witness.global_position=door.to_global(Vector3(0,.02,0))
		for i in range(3):await physics_frame
		await aim(actor,door.get_node("InteriorControl").to_global(Vector3(0,0,.055)));record("normal_maker_guard_target",actor.interaction_target==door);await key_e()
		for i in range(5):await physics_frame
		record("occupied_maker_character_guard",door.obstructed and door.desired_open and door.fraction==1);guards+=1;witness.queue_free()
		for i in range(3):await physics_frame
	if ok and not await operate(actor,door,"InteriorControl",false):ok=false
	if ok and not await operate(actor,door,"InteriorControl",true):ok=false
	var path:Array=[vec(spec.door.interior_world_xyz),Vector3(-71,52.53,0),Vector3(-71,52.53,-9),Vector3(-87,52.53,-9),Vector3(-88,52.53,-17),Vector3(-88,52.53,-22),Vector3(-91,52.53,-22),Vector3(-88,52.53,-22),Vector3(-89.7,52.53,-15),Vector3(-88,52.53,-17),Vector3(-87,52.53,-9),Vector3(-71,52.53,-9),Vector3(-71,52.53,0),vec(spec.door.interior_world_xyz),vec(spec.door.public_foyer_world_xyz),vec(spec.door.public_stance_world_xyz)]
	for at:Vector3 in path:
		if not ok:break
		if not await leg(actor,at,"continuous original gallery,stock/wrapping inspection and original return"):ok=false
	if ok and not await operate(actor,door,"PublicControl",false):ok=false
	for at in [vec(spec.door.public_foyer_world_xyz),vec(spec.door.public_approach_world_xyz)]:
		if not ok:break
		if not await leg(actor,at,"closed-default foyer back to actual original spine connection"):ok=false
	physical_key(false);record("complete_maker_source_route",ok and legs.size()==23 and operations.size()==4 and guards==1)
	var cached:=false
	if ok:
		# Cached state is a separate explicit fixture after the walking route.
		actor.global_position=vec(spec.door.public_stance_world_xyz);manager.prepare_position(actor.global_position)
		for i in range(3):await physics_frame
		door.interact(actor)
		for i in range(85):await physics_frame
		var id:=door.get_instance_id();actor.global_position=Vector3(1000,1000,1000);manager.refresh(9)
		record("actual_maker_cached_detach",not owner.is_inside_tree());manager.prepare_position(vec(spec.door.public_stance_world_xyz))
		for i in range(3):await physics_frame
		cached=owner.is_inside_tree() and door.get_instance_id()==id and door.desired_open and door.fraction==1;record("same_open_maker_cached_return",cached)
	var out:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks.size(),"errors":errors,"startup_attached":startup,"original_meshes_preserved":preserved,"physical_sources":9,"optical_samples":optical,"continuous_original_controller_legs":legs,"normal_RMB_E_operations":operations,"occupied_guard_fixtures":guards,"cached_open_return":cached,"teleports_inside_walking_route":0,"scope":"Literal current source and original gallery/stock/wrapping approaches,normal controller and recessed door,physical source lenses and affected optical admission;original correction-native,child/species use,inventory/refill,economy,save/role/pressure,engineering,Game/CRT/hardware/final-art and whole-group acceptance remain held"}
	FileAccess.open("res://artifacts/group5_maker_construction_integrated001.json",FileAccess.WRITE).store_string(JSON.stringify(out,"  "))
	print("GROUP5_MAKER_CONSTRUCTION ",JSON.stringify({"status":out.status,"checks":checks.size(),"legs":legs.size(),"operations":operations.size(),"guards":guards,"cached":cached,"errors":errors}));quit(0 if errors.is_empty() else 1)
