extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	OS.set_environment("ASTRAEA_FORCE_ALL_RECEIVED_ROOMS","")
	var main:Node=load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for i in range(12):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	assert(bool(ship.get_meta("central_residential_streets_installed",false)))
	var manager:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
	manager.enabled=false
	var districts:Node3D=ship.get_node("ShipSpace/Districts")
	assert(districts.get_node("D13_13017_TwinSuite_WIP")!=null)
	assert(districts.get_node("D13_13041_TwinSuite_WIP")!=null)
	var identities:Dictionary={}
	for prior_root in ["TidalRoomCandidates","QuietGroveRoomCandidates","FamilyTerraceRoomCandidates","SunsetRoomCandidates"]:
		for entry in manager.entries:
			if entry.parent==districts.get_node(prior_root):identities[str(entry.room.name)]=true
	var anchors:=0
	var checks:=0
	var errors:Array=[]
	var world:=ship.get_world_3d().direct_space_state
	for root_name in ["StarAtlasRoomCandidates","NightGardenRoomCandidates"]:
		var homes:Node3D=districts.get_node(root_name)
		var entries:Array=manager.entries.filter(func(e):return e.parent==homes)
		assert(entries.size()==(85 if root_name=="StarAtlasRoomCandidates" else 80))
		assert(homes.get_meta("default_scene_enabled"))
		for entry in entries:
			manager.prepare_position(entry.bounds.get_center())
			var room:Node3D=entry.room
			assert(not identities.has(str(room.name)))
			identities[str(room.name)]=true
			anchors+=room.get_meta("source_rest_slots").size()
			assert(room.get_node("EntryDoor")!=null and room.get_node("BathroomDoor")!=null)
			for local_z in [-1.0,1.0]:
				var p:=room.to_global(Vector3(0,0,local_z))
				var hit:=world.intersect_ray(PhysicsRayQueryParameters3D.create(p+Vector3.UP*.15,p-Vector3.UP*.4))
				if hit.is_empty() or absf(hit.position.y-p.y)>.04:errors.append({"room":str(room.name),"kind":"interior_floor" if local_z<0 else "street_floor","expected":str(p),"hit":str(hit.get("position","none"))})
				checks+=1
			manager.refresh(9.0)
	var prior_checks:=0
	for prior_root in ["TidalRoomCandidates","QuietGroveRoomCandidates","FamilyTerraceRoomCandidates","SunsetRoomCandidates"]:
		for entry in manager.entries:
			if entry.parent!=districts.get_node(prior_root):continue
			manager.prepare_position(entry.bounds.get_center())
			var room:Node3D=entry.room
			for local_z in [-1.0,1.0]:
				var p:=room.to_global(Vector3(0,0,local_z))
				var hit:=world.intersect_ray(PhysicsRayQueryParameters3D.create(p+Vector3.UP*.15,p-Vector3.UP*.4))
				if hit.is_empty() or absf(hit.position.y-p.y)>.04:errors.append({"room":str(room.name),"kind":"prior_home_contact_regression","point":str(p)})
				prior_checks+=1
			manager.refresh(9.0)
	for y in [84.0,88.5,97.5]:
		for x in [-50.0,50.0]:
			for z in [-32.0,30.0]:
				var p:=Vector3(x,y,z)
				var hit:=world.intersect_ray(PhysicsRayQueryParameters3D.create(p+Vector3.UP*.15,p-Vector3.UP*.4))
				if hit.is_empty() or absf(hit.position.y-y)>.04:errors.append({"kind":"crosslink_floor","point":str(p)})
	# Only three obsolete pilot construction-guard seams, not exhaustive traversal.
	for pair in [[Vector3(84,84.55,-52.8),Vector3(84,84.55,-53.2)],[Vector3(81.75,84.55,-32),Vector3(82.15,84.55,-32)],[Vector3(85.85,84.55,-49.4),Vector3(86.25,84.55,-49.4)],[Vector3(85.85,84.55,-42),Vector3(86.25,84.55,-42)]]:
		var hit:=world.intersect_ray(PhysicsRayQueryParameters3D.create(pair[0],pair[1]))
		if not hit.is_empty():errors.append({"kind":"pilot_guard_seam","from":str(pair[0]),"collider":str(hit.collider.get_path())})
	assert(anchors==431)
	assert(ship.get_node("ShipSystems/ReceivedRoomResidency").entries.size()==561)
	var result:Dictionary={"status":"PASS" if errors.is_empty() else "FAIL","installed_source_units":165,"rest_anchors":anchors,"prior_home_contact_checks":prior_checks,"entrance_pair_checks":checks,"crosslink_floor_checks":12,"pilot_guard_seam_checks":4,"preserved_existing_pilots":2,"unique_with_existing_homes":true,"errors":errors,"scope":"Actual main registration and bounded floor/contact checks. Receiving frames, gardens, lifts, service links, privacy, occupancy, visual and full traversal acceptance unfinished."}
	FileAccess.open("res://artifacts/central_homes_default_adoption.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("CENTRAL_HOMES_DEFAULT_ADOPTION ",JSON.stringify(result))
	quit(0 if errors.is_empty() else 1)
