extends SceneTree
var errors:Array=[]
var samples:Array=[]
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(20):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var manager:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
	var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	var helper=load("res://scripts/group5_large_venue_lighting.gd")
	var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group5/LARGE_VENUE_LIGHTING.json"))
	var doors:Array=load("res://scripts/group5_large_venue_doors.gd").build(ship)
	actor.set_controls_enabled(false);actor.set_physics_process(false);manager.enabled=false;budget.set_process(false)
	for row in definition.venues:
		var owner:Node3D=helper._owner(ship,str(row.programme_key))
		var sources:Node3D=owner.get_node("Group5SourceLighting")
		var sign_x:float=1.0 if float(row.translation_xyz[0])>0 else -1.0
		for local in [Vector3(sign_x*3,.03,34),Vector3(sign_x*14,.03,34),Vector3(sign_x*36,.03,34)]:
			actor.global_position=owner.position+local;manager.prepare_position(actor.global_position)
			for i in range(3):await physics_frame
			budget.refresh()
			var global_count:=0;var reaching:=0
			for light in budget.sources:
				if is_instance_valid(light) and light.is_inside_tree() and light.visible and light.shadow_enabled:global_count+=1
			for light:OmniLight3D in sources.get_children():
				if light.visible and not light.shadow_enabled:errors.append(str(row.programme_key)+" unshadowed source leak")
				if not light.visible or not light.shadow_enabled:continue
				for offset in [Vector3(0,1.5,0),Vector3(0,.4,0),Vector3(.65,1,0),Vector3(-.65,1,0)]:
					var target:Vector3=actor.global_position+offset
					if light.global_position.distance_to(target)<light.omni_range and budget._clear_sample(light.global_position,target):reaching+=1;break
			if global_count>8:errors.append(str(row.programme_key)+" shared budget exceeded")
			if reaching<1:errors.append(str(row.programme_key)+str(local)+" changed-door optical sample unlit")
			samples.append({"programme_key":row.programme_key,"at":[actor.global_position.x,actor.global_position.y,actor.global_position.z],"global_shadow_sources":global_count,"active_venue_sources_reaching_viewer":reaching})
	var out:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","errors":errors,"samples":samples,"new_doors":doors.size(),"scope":"Affected15 explicit optical placements with all five new foyer doors in exact proposed startup;actual active source range/visibility and unchanged eight-source budget only;no pixel,CRT,brightness calibration or hardware acceptance."}
	FileAccess.open("res://artifacts/group5_large_venue_door_optics.json",FileAccess.WRITE).store_string(JSON.stringify(out,"  "))
	print("GROUP5_LARGE_VENUE_DOOR_OPTICS ",JSON.stringify(out));quit(0 if errors.is_empty() else 1)
