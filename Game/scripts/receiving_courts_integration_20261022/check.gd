extends SceneTree
const P:="res://night_garden_receiving_courts_20261022/"
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
	var host:Node3D=load("res://scripts/receiving_courts_integration_20261022/fixture_host.gd").new();root.add_child(host)
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
	host.stone=host.surface("warm_stone",Color.WHITE);host.ivory=host.surface("ivory_enamel",Color.WHITE);host.metal=host.surface("champagne_metal",Color.WHITE)
	load("res://scripts/central_house_connections.gd").build(host)
	await host._construction_step("central_homes/night_garden_residency_20261022")
	check(districts.has_node("NightGardenReceivingCourts20261022"),"Actual inherited main hook installs one court assembly")
	check(districts.get_node("NightGardenReceivingCourts20261022").scene_file_path==P+"runtime/ReceivingCourts_r003.scn","Same route-tested court scene")
	var street:=district.get_node("ConnectedStreetsAndPortalSuccessors")
	check(street.has_node("NightGardenD15CourtEntrances_r004") and not street.has_node("NightGardenD15ConnectedReceiving_r003"),"One exact public entrance successor; no duplicate owner")
	check(street.get_node("NightGardenD15CourtEntrances_r004").scene_file_path==P+"runtime/CourtEntrances_r004_policy.scn","Same policy-preserving route-tested entrance scene")
	check(manager.entries.size()==30 and district.get_meta("reserved_rest_count")==40,"30 rooms and 40 reserved rests preserved")
	check(districts.get_node("NightGardenReceivingCourts20261022").find_children("*","SpotLight3D",true,false).size()==14,"Exactly 14 new source fixtures; no duplication")
	check(host.atrium_interiors_verified,"Previous inner/outer suite integration guards retained")
	var failed:=0
	for row in checks:
		if not row.pass:failed+=1
	var output:=FileAccess.open("res://docs/validation/receiving_courts_integration_20261022/CHECK.json",FileAccess.WRITE)
	output.store_string(JSON.stringify({"checks":checks,"failures":failed,"whole_ship_launched":false,"final_acceptance":false},"\t")+"\n");output.close()
	print("RECEIVING_MAIN_HOOK_CHECKS ",checks.size()," failures=",failed);quit(0 if failed==0 else 1)
