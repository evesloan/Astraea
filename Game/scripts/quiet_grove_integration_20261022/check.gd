extends SceneTree
const P:="res://quiet_grove_specialty_20261022/"
var checks:Array=[]
var routes:Array=[]
var actor:CharacterBody3D
func _initialize()->void:call_deferred("run")
func check(ok:bool,label:String)->void:
	checks.append({"pass":ok,"label":label})
	if not ok:push_error(label)
func key(down:bool)->void:
	var e:=InputEventKey.new();e.physical_keycode=KEY_W;e.pressed=down;Input.parse_input_event(e)
func walk(target:Vector3)->bool:
	for frame in range(240):
		var delta:=target-actor.global_position;delta.y=0
		if delta.length()<.12:
			key(false)
			for settle in range(8):await physics_frame
			return actor.is_on_floor() and absf(actor.global_position.y-target.y)<.12
		actor.rotation.y=atan2(-delta.x,-delta.z);key(true);await physics_frame
	key(false);return false
func run()->void:
	var host:Node3D=load("res://scripts/quiet_grove_integration_20261022/fixture_host.gd").new();root.add_child(host)
	var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
	var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
	var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
	actor=load("res://scripts/player.gd").new();actor.position=Vector3(10000,10000,10000);actors.add_child(actor);actor.set_physics_process(false)
	var house:Node3D=load("res://scripts/quiet_grove_receiving.gd").build(host)
	var before_meshes:=house.find_children("*","MeshInstance3D",true,false).size()
	var manager:Node=load("res://scripts/night_garden_residency_20261022/manager.gd").new();host.add_child(manager);manager.setup(host);manager.set_physics_process(false);host.private_detail_residency=manager
	await host._construction_step("quiet_grove_adoption.gd")
	var district:Node3D=districts.get_node("QuietGrove17Specialty20261022")
	var package:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PACKAGE_R002.json"))
	check(district.get_meta("reserved_rests")==19,"19 unchanged reserved rest IDs; no new capacity")
	check(manager.entries.size()==17,"17 rooms registered in existing residency owner")
	check(house.find_children("*","MeshInstance3D",true,false).size()==before_meshes-11,"Only11 exact guard batches replaced; house floors and other guards remain")
	for frame in range(100):await physics_frame
	for room in package.rooms:
		var id:String=str(room.allocation.proposed_runtime_id);var home:Node3D=district.get_node(id)
		check(home.get_meta("rest_slot_ids")==room.allocation.proposed_rest_slot_ids,id+" reserved identity")
		var record:Dictionary=manager.index[room.model_file];var entry:Dictionary=manager.entries.filter(func(e):return str(e.record.model_file)==str(room.model_file))[0]
		manager._load_entry(entry)
		check(is_instance_valid(entry.detail),id+" actual private detail loaded")
		var door_row:Dictionary=room.doors.filter(func(d):return str(d.controller)=="guest_entry_door.gd")[0]
		var door:Node3D=home.get_node(str(door_row.name))
		check(door.open_fraction>.99,id+" unchanged controller opens fully")
		var y:float=room.allocation.floor_y;var z:float=door_row.position[2];var outboard:bool=room.allocation.allocation_x[0]>45
		actor.position=Vector3(44,y+.04,z);actor.velocity=Vector3.ZERO;actor.set_physics_process(true)
		for settle in range(15):await physics_frame
		var target:=Vector3(47.4 if outboard else 40.6,y,z)
		var entered:bool=await walk(target);check(entered,id+" street-to-room controller contact")
		var exited:bool=await walk(Vector3(44,y,z));check(exited,id+" room-to-street controller contact")
		routes.append({"allocation":room.allocation.source_envelope_index,"entered":entered,"exited":exited,"actual":str(actor.position)})
		actor.set_physics_process(false);actor.position=Vector3(10000,10000,10000);manager._release_entry(entry)
		check(not is_instance_valid(entry.detail),id+" immutable detail releases; shell doors lights retained")
	var failed:=checks.filter(func(c):return not c.pass).size()
	var receipt:={"status":"PASS" if failed==0 else "FAIL","checks":checks,"routes":routes,"scope":"bounded actual house receiving and17 new rooms; no full ship launch","main_integrated":true,"full_startup":false,"visual_accepted":false}
	var f:=FileAccess.open("res://docs/validation/quiet_grove_integration_20261022/CHECK.json",FileAccess.WRITE);f.store_string(JSON.stringify(receipt,"\t")+"\n");f.close();print("QUIET_GROVE_CHECK ",checks.size()," failures=",failed);quit(1 if failed else 0)
