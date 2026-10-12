extends "res://tests/group6_completion/validate_local.gd"
func run()->void:
	var host:=LocalHost.new();root.add_child(host)
	var annex:Node3D=load("res://scripts/aquatic_annex_receiving.gd").build(host,host)
	load("res://scripts/group6_completion/completion.gd").build(annex,host)
	var actor:CharacterBody3D=load("res://scripts/player.gd").new();actor.spawn_position=Vector3(64,44.5,192.92);host.add_child(actor);actor.global_position=actor.spawn_position;actor.set_controls_enabled(true)
	for i in range(20):await physics_frame
	var frames:Array=[];actor.rotation.y=0;physical_key(true)
	for frame in range(40):
		await physics_frame
		var contacts:Array=[]
		for j in range(actor.get_slide_collision_count()):
			var c:=actor.get_slide_collision(j)
			contacts.append({"normal":str(c.get_normal()),"position":str(c.get_position()),"depth":c.get_depth(),"face":c.get_collider_shape(),"owner":str(c.get_collider().get_parent().name)})
		frames.append({"frame":frame,"position":str(actor.position),"velocity":str(actor.velocity),"floor":actor.is_on_floor(),"normal":str(actor.get_floor_normal()),"contacts":contacts})
	physical_key(false)
	FileAccess.open("res://docs/group6_completion/RECOVERY_CONTACT_DIAGNOSTIC.json",FileAccess.WRITE).store_string(JSON.stringify({"floor_max_angle":actor.floor_max_angle,"snap":actor.floor_snap_length,"safe_margin":actor.safe_margin,"frames":frames},"  "))
	quit()
