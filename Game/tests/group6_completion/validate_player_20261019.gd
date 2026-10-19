extends "res://tests/group6_completion/validate_water_care.gd"
var output_name:="LOCAL"
var active_residency:Node
func run()->void:
	var host:=LocalHost.new();root.add_child(host)
	var floor_data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/received_structural_meshes.json"));var regions:Array=[]
	for r in floor_data.regions:
		if str(r.id).begins_with("D08_directory_02_") or str(r.id).begins_with("D08_directory_03_"):regions.append(r)
	var floors:Node3D=load("res://scripts/structural_floor_builder.gd").build_regions(host,host.stone,host.ivory,regions,{},"ExactRetainedThermalCompilerFloors");record("four_original_floor_owners",floors.get_child_count()==4)
	var actor:CharacterBody3D=load("res://scripts/group6_completion/player_water_seat_20261019.gd").new();host.add_child(actor)
	var entries:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_completion/THERMAL_ENTRY_CONTRACT.json"));var supports:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_completion/THERMAL_SUPPORT_CONTRACT.json"));var rooms:Array=[]
	for i in range(2):
		var entry:Dictionary=entries.rooms[i];var room:Node3D=load("res://"+str(entry.current_room_runtime).trim_prefix("Game/")).instantiate();room.name=str(entry.programme_key);room.set_meta("programme_key",str(entry.programme_key));host.add_child(room)
		for mesh:MeshInstance3D in room.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
		load("res://scripts/group6_completion/thermal_entries.gd").build(room);var addition:Node3D=load("res://scripts/group6_completion/thermal_support.gd").build(room);record(str(entry.programme_key)+"_support_build",addition!=null);rooms.append(room)

	for i in range(3):await physics_frame
	await exercise(host,rooms,actor)

func exercise(host:Node3D,rooms:Array,actor:CharacterBody3D)->void:
	for room:Node3D in rooms:
		for seat:Area3D in room.get_node("Group6ThermalSupport").find_children("*PlayerControl","Area3D",true,false):
			if active_residency!=null:active_residency.prepare_position(vec(seat.station.operator_xyz))
			actor.global_position=seat.exit_world_position();actor.velocity=Vector3.ZERO
			for j in range(5):await physics_frame
			var id:String=str(seat.get_meta("persistent_id"))
			actor.set_controls_enabled(false)
			record(id+"_disabled_input_rejects_mount",not actor.try_mount_parked_seat(seat))
			actor.set_controls_enabled(true)
			actor.held_interaction=Node.new();host.add_child(actor.held_interaction)
			record(id+"_hands_full_rejects_mount",not actor.try_mount_parked_seat(seat))
			actor.held_interaction.free();actor.held_interaction=null
			await aim(actor,seat.global_position+Vector3.UP*.4)
			record(id+"_source_seat_focus",actor.interaction_target==seat)
			await key_e()
			record(id+"_mount_with_E",actor.seated and seat.occupant==actor)
			if not actor.seated:continue
			var blocker:=StaticBody3D.new();var collision:=CollisionShape3D.new();var box:=BoxShape3D.new();box.size=Vector3(.7,1.8,.7);collision.shape=box;blocker.add_child(collision);host.add_child(blocker);blocker.global_position=seat.exit_world_position()+Vector3.UP*.9
			for j in range(3):await physics_frame
			record(id+"_blocked_exit_holds",not actor.try_leave_parked_seat() and actor.seated and seat.occupant==actor)
			blocker.queue_free()
			for j in range(3):await physics_frame
			var other:CharacterBody3D=load("res://scripts/group6_completion/player_water_seat_20261019.gd").new();host.add_child(other);other.global_position=seat.exit_world_position()
			record(id+"_exclusive_occupant",not other.try_mount_parked_seat(seat))
			other.queue_free()
			for j in range(3):await physics_frame
			var seated_at:Vector3=actor.global_position
			actor.set_controls_enabled(false)
			for j in range(20):await physics_frame
			record(id+"_menu_keeps_seated",actor.seated and actor.global_position.distance_to(seated_at)<.001 and actor.velocity==Vector3.ZERO)
			actor.set_controls_enabled(true)
			await aim(actor,actor.global_position+Vector3(0,1.05,2))
			record(id+"_seated_focus_priority",actor.interaction_target==seat)
			await key_e()
			record(id+"_leave_with_E",not actor.seated)
			record(id+"_restores_standing",not actor.seated and is_equal_approx(actor.body_collider.shape.height,1.8) and seat.occupant==null)
			for j in range(10):await physics_frame
			record(id+"_supported_exit",actor.is_on_floor())
			if host.has_method("arrive_at"):
				record(id+"_remount_for_travel",actor.try_mount_parked_seat(seat))
				record(id+"_verified_arrival",host.arrive_at(actor.spawn_position,0.0))
				record(id+"_arrival_releases_seat",not actor.seated and seat.occupant==null and is_equal_approx(actor.body_collider.shape.height,1.8))
			if actor.seated:break
	for fixture in [[Vector3(89.5,44.4,216),"wading"],[Vector3(78,44.4,216),"dry"],[Vector3(95,44.4,216),"dry"],[Vector3(89.5,40,216),"dry"],[Vector3(89.5,50,216),"dry"]]:
		actor.global_position=fixture[0];actor.update_water_state();record("river_"+str(fixture[0]),actor.water_state==fixture[1] and not actor.head_under_water)
	var result:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks,"errors":errors,"scope":"Fixed four source thermal station seating and river state only; occupied hoists, swimming, float mount, save and final visual acceptance remain open."}
	FileAccess.open("res://docs/validation/group6_player_20261019/"+output_name+".json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("GROUP6 PLAYER ",result.status," ",errors);quit(0 if errors.is_empty() else 1)
