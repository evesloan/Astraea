extends SceneTree
const P:="res://quiet_grove_bank_20261022/"
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
	var host:Node3D=load("res://scripts/quiet_grove_bank_integration_20261022/fixture_host.gd").new();root.add_child(host)
	var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
	var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
	var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
	actor=load("res://scripts/player.gd").new();actor.position=Vector3(10000,10000,10000);actors.add_child(actor);actor.set_physics_process(false)
	var house:Node3D=load("res://scripts/quiet_grove_receiving.gd").build(host)
	var before_meshes:=house.find_children("*","MeshInstance3D",true,false).size()
	var manager:Node=load("res://scripts/night_garden_residency_20261022/manager.gd").new();host.add_child(manager);manager.setup(host);manager.set_physics_process(false);host.private_detail_residency=manager
	await host._construction_step("quiet_grove_adoption.gd")
	var prior:Node3D=districts.get_node("QuietGrove17Specialty20261022")
	var old_doors:={}
	for door in prior.find_children("*","Node3D",true,false):
		if door.get("persistent_id")!=null:old_doors[door.get_instance_id()]=str(door.persistent_id)
	var district:Node3D=districts.get_node("QuietGroveD15Specialty20261022")
	var preserved:={}
	for mesh:MeshInstance3D in house.find_children("*","MeshInstance3D",true,false):
		if mesh.get_meta("extras",{}).has("source_plan_sha256"):preserved[mesh.get_instance_id()]={"mesh":mesh.mesh,"transform":mesh.global_transform,"contacts":mesh.find_children("*","StaticBody3D",true,false).map(func(n):return n.get_instance_id())}
	var finish:Node3D=load("res://quiet_court_finish_20261022/adapter.gd").build(host)
	for id in preserved:
		var mesh:MeshInstance3D=instance_from_id(id);var row:Dictionary=preserved[id]
		check(mesh!=null and mesh.mesh==row.mesh and mesh.global_transform==row.transform and mesh.find_children("*","StaticBody3D",true,false).map(func(n):return n.get_instance_id())==row.contacts,"Original court geometry, transform and contact owner preserved")
	check(finish.get_meta("placements")==149 and finish.get_meta("receiving_beds")==33,"149 plantings on33 retained beds; no new circulation collision")
	check(finish.get_meta("existing_fixtures_retuned")==79,"79 original fixtures reused")
	for id in old_doors:
		var door=instance_from_id(id);check(door!=null and str(door.persistent_id)==old_doors[id],"Original17-room door object and ID preserved")
	var package:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PACKAGE.json"))
	check(district.get_meta("view_bank_reserved_rests")==59,"59 unchanged reserved rest IDs; no new capacity")
	check(district.get_meta("fixed_enclosure_parts_corrected")==217,"All217 fixed enclosure parts match corrected native bounds")
	check(manager.entries.size()==47,"47 rooms registered in existing residency owner")
	check(house.find_children("*","MeshInstance3D",true,false).size()-finish.find_children("*","MeshInstance3D",true,false).size()==before_meshes-19,"Only11 previous plus8 D15 guard batches replaced; floors and other guards remain")
	for frame in range(100):await physics_frame
	for room in package.rooms:
		if int(room.allocation.source_envelope_index) not in [105,409]:continue
		var id:String=str(room.allocation.proposed_runtime_id);var home:Node3D=(district if str(room.allocation.deck)=="D15" else prior).get_node(id)
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
	var receipt:={"status":"PASS" if failed==0 else "FAIL","checks":checks,"routes":routes,"scope":"bounded current court with two representative existing guest thresholds; no full ship launch","main_integrated":false,"full_startup":false,"visual_accepted":false}
	var f:=FileAccess.open("res://quiet_court_finish_20261022/evidence/CHECK.json",FileAccess.WRITE);f.store_string(JSON.stringify(receipt,"\t")+"\n");f.close();print("QUIET_GROVE_CHECK ",checks.size()," failures=",failed);quit(1 if failed else 0)
