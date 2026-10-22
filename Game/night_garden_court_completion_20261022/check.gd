extends SceneTree
const P:="res://night_garden_court_completion_20261022/"
var checks:Array=[]
var routes:Array=[]
var actor:CharacterBody3D
func _initialize()->void:call_deferred("run")
func check(ok:bool,label:String)->void:
	checks.append({"pass":ok,"label":label})
	if not ok:push_error(label)
func raw(file:String)->Node3D:
	var doc:=GLTFDocument.new();var state:=GLTFState.new();assert(doc.append_from_file("res://assets/models/"+file,state)==OK);return doc.generate_scene(state)
func key(down:bool)->void:
	var event:=InputEventKey.new();event.physical_keycode=KEY_W;event.pressed=down;Input.parse_input_event(event)
func walk(target:Vector3)->bool:
	for frame in range(1100):
		var delta:=target-actor.global_position;delta.y=0
		if delta.length()<.13:
			key(false)
			for settle in range(8):await physics_frame
			routes.append({"target":str(target),"actual":str(actor.global_position)})
			return actor.is_on_floor() and absf(actor.global_position.y-target.y)<.10
		actor.rotation.y=atan2(-delta.x,-delta.z);key(true);await physics_frame
	key(false);routes.append({"target":str(target),"actual":str(actor.global_position),"timeout":true});return false
func run()->void:
	var host:Node3D=load("res://scripts/atrium_interior_integration_20261022/fixture_host.gd").new();root.add_child(host)
	var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
	var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
	var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
	actor=load("res://scripts/player.gd").new();actor.name="Player";actor.position=Vector3(10000,10000,10000);actors.add_child(actor);actor.set_physics_process(false)
	var lower:=Node3D.new();lower.name="D13_D14_StarboardCommons_WIP";districts.add_child(lower)
	var upper:=Node3D.new();upper.name="D15_D17_StarboardHouseUpper_WIP";lower.add_child(upper)
	var wrapper:=Node3D.new();wrapper.name="StarboardHouseUpperArchitecture";upper.add_child(wrapper);wrapper.position=Vector3(63,84,0)
	var commons:=raw("AST-COM-003.glb");wrapper.add_child(commons)
	for mesh:MeshInstance3D in commons.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
	var manager:Node=load("res://scripts/night_garden_residency_20261022/manager.gd").new();host.add_child(manager);manager.setup(host);manager.set_physics_process(false);host.private_detail_residency=manager
	var district:Node3D=load("res://scripts/night_garden_residency_20261022/district.gd").build(host)
	await host._construction_step("central_homes/night_garden_residency_20261022")
	var regions:Array=[]
	var structural:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
	for row in structural.regions:
		if str(row.id)in ["D13_atrium_circulation","D14_atrium_circulation","D15_atrium_circulation","D16_atrium_circulation","D13_window_terrace"]:regions.append(row)
	load("res://scripts/structural_floor_builder.gd").build_regions(space,host.surface("warm_stone",Color.WHITE),host.surface("ivory_enamel",Color.WHITE),regions)
	load("res://night_garden_receiving_courts_20261022/adapter.gd").build(host)
	var courts:Node3D=load(P+"adapter.gd").finish(host)
	check(courts.get_meta("compiled_finish_records").size()==5,"Five exact compiler owners retain geometry and contacts")
	check(courts.find_children("*","SpotLight3D",true,false).size()==28,"28 fixture lights replace 14 without duplication")
	check(manager.entries.size()==30,"All 30 room registrations preserved")
	check(district.get_meta("reserved_rest_count")==40,"All 40 reserved rests preserved")
	check(courts.get_meta("new_room_ids")==0,"No new capacity or room identity")
	check(not district.has_node("OuterViewGalleries20261022"),"Rejected gallery remains absent")
	for sign in [-1.0,1.0]:
		actor.position=Vector3(84,93.03,sign*35.5);actor.velocity=Vector3.ZERO;actor.set_physics_process(true)
		for settle in range(12):await physics_frame
		for target in [Vector3(56.1,93,sign*35.5),Vector3(56.1,93,sign*49),Vector3(58.15,93,sign*49),Vector3(58.15,97.5,sign*78),Vector3(56.1,97.5,sign*78),Vector3(56.1,97.5,sign*88),Vector3(56.1,97.5,sign*78),Vector3(58.15,97.5,sign*78),Vector3(58.15,93,sign*49),Vector3(56.1,93,sign*49),Vector3(56.1,93,sign*35.5),Vector3(84,93,sign*35.5)]:
			var passed:=await walk(target)
			check(passed,"Existing controller connected court route "+str(sign)+" / "+str(target))
			if not passed:
				var failure:=FileAccess.open(P+"evidence/CHECK_FAILED_ROUTE.json",FileAccess.WRITE);failure.store_string(JSON.stringify({"checks":checks,"routes":routes},"\t"));failure.close();quit(1);return
		actor.set_physics_process(false)
	actor.position=Vector3(70.25,93,-42)
	await physics_frame;await physics_frame
	var budget:Node=load(P+"lighting_budget.gd").new();host.add_child(budget);budget.configure(host,actor)
	check(budget.shadow_source_budget==8,"Eight-source limit preserved")
	check(budget._clear_sample(Vector3(68.5,94.6,-42),Vector3(70.25,94.6,-42)),"Known privacy pane transmits visibility from resident side")
	check(not budget._clear_sample(Vector3(68.5,94.6,-45.5),Vector3(70.25,94.6,-45.5)),"Opaque room framing still blocks visibility")
	actor.position=Vector3(68.5,93,-42)
	check(not budget._clear_sample(Vector3(70.25,94.6,-42),Vector3(68.5,94.6,-42)),"Privacy pane remains opaque from public side")
	actor.position=Vector3(70.25,93,-42);budget.refresh()
	var active_courts:=0
	for light in budget.previously_active:
		if courts.is_ancestor_of(light):active_courts+=1
	check(active_courts>0 and budget.previously_active.size()<=8,"Physical court fixtures illuminate resident outlook within unchanged budget")
	var wash:SpotLight3D=courts.find_child("Fore_RetainedSoffitWash_-42",true,false)
	check(wash!=null and budget._has_visible_sample(wash),"Nearest soffit washer has a real unblocked trim receiver")
	check(wash!=null and wash.visible,"Nearest soffit washer is admitted within the eight-source budget")
	var failures:=0
	for row in checks:
		if not row.pass:failures+=1
	var out:=FileAccess.open(P+"evidence/CHECK.json",FileAccess.WRITE);out.store_string(JSON.stringify({"checks":checks,"routes":routes,"failures":failures,"full_ship_launched":false,"visual_accepted":false,"active_court_sources":active_courts},"\t")+"\n");out.close()
	print("RECEIVING_CHECKS ",checks.size()," failures=",failures);quit(0 if failures==0 else 1)
