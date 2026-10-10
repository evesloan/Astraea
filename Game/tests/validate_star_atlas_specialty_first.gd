extends SceneTree
var errors:Array=[]
var rays:=0
func ray(space:PhysicsDirectSpaceState3D,a:Vector3,b:Vector3,label:String,y:float=-999)->void:
	var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(a,b));rays+=1
	if h.is_empty() or (y!=-999 and absf(h.position.y-y)>.025):errors.append({"kind":label,"point":str(a),"hit":str(h.get("position","none"))})
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(90):await physics_frame
	var candidate_root:Node3D=main.get_node("World360/Astraea/ShipSpace/Districts/StarAtlasSpecialtyCandidates")
	var actor:CharacterBody3D=main.get_node("World360/Astraea/ShipSpace/PersistentActors/Player")
	for door:Node3D in candidate_root.find_children("*Door","Node3D",true,false):
		if door.has_method("interact"):door.interact(actor)
	for i in range(100):await physics_frame
	for door:Node3D in candidate_root.find_children("*Door","Node3D",true,false):
		if door.has_method("interact"):assert(door.open_fraction<.001)
	paused=true
	var ship:Node3D=main.get_node("World360/Astraea")
	var homes:Node3D=ship.get_node("ShipSpace/Districts/StarAtlasSpecialtyCandidates")
	assert(load("res://scripts/star_atlas_specialty_first.gd").build(ship)==homes)
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_SPECIALTY_FIRST.json"))
	var space:=ship.get_world_3d().direct_space_state
	for z in [-14.0,-25.0,-38.0,-42.0,-49.4,14.0,25.0,38.0,42.0,49.4]:ray(space,Vector3(-84,93.15,z),Vector3(-84,92.9,z),"street",93)
	for z in [-14.0,14.0]:
		if not space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-84,94,z-1),Vector3(-84,94,z+1))).is_empty():errors.append({"kind":"portal_blocked","z":z})
	var doors:=0;var water:=0
	var roof_contacts:=0
	var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
	for room in p.rooms:
		for entry in residency.entries:
			if str(entry.room.name)==str(room.below_unit.rebuild_identity):
				if not entry.room.is_inside_tree():entry.parent.add_child(entry.room)
				load("res://scripts/deferred_home_visual.gd").ensure(entry.room)
	for i in range(3):await physics_frame
	var exclude:Array[RID]=[]
	for body:StaticBody3D in homes.find_children("*","StaticBody3D",true,false):exclude.append(body.get_rid())
	for room in p.rooms:
		for toe in room.receiving_contacts:
			var t:Vector3=Vector3(toe.position[0],toe.position[1],toe.position[2])
			var q:=PhysicsRayQueryParameters3D.create(t+Vector3.UP*.025,t-Vector3.UP*.025);q.exclude=exclude;q.hit_back_faces=true
			var h:=space.intersect_ray(q);roof_contacts+=1
			if h.is_empty() or absf(h.position.y-t.y)>.003:errors.append({"kind":"source_roof_contact","toe":str(t),"hit":str(h.get("position","none"))})
	for room in p.rooms:
		var home:Node3D=homes.get_node(room.allocation.proposed_runtime_id)
		assert(home.get_meta("rest_slot_ids")==room.allocation.proposed_rest_slot_ids and not home.has_meta("species_assignment"))
		var z:float=(room.allocation.allocation_z[0]+room.allocation.allocation_z[1])*.5
		for x in [-83.2,-81.7,-79.8,-76.0,-71.0]:ray(space,Vector3(x,93.15,z-.6),Vector3(x,92.9,z-.6),"room_floor",93)
		ray(space,Vector3(-70.5,94.95,z),Vector3(-68.6,94.95,z),"window_glass")
		for mesh:MeshInstance3D in home.find_children("*","MeshInstance3D",true,false):
			if "WaterSurface_VisualOnly" in str(mesh.name) or "Ripple" in str(mesh.name):
				water+=1;assert(not bool(mesh.get_meta("extras",{}).runtime_collision))
		ray(space,Vector3(-82.3,94,z),Vector3(-81.3,94,z),"closed_entry_leaf")
		ray(space,Vector3(-78.75,94,z+.4),Vector3(-78.75,94,z+1.2),"closed_privacy_leaf")
		for name in ["EntryDoor","WashDoor"]:
			var door:Node3D=home.get_node(name);assert(not door.persistent_id.is_empty() and door.leaves.size()>0)
			door.open_fraction=1;door._apply_pose();door.open_fraction=0;door._apply_pose();doors+=1
	var retained:=0
	for entry in ship.get_node("ShipSystems/ReceivedRoomResidency").entries:
		if str(entry.parent.name)=="StarAtlasRoomCandidates":retained+=1
	assert(retained==85 and doors==8)
	var report={"status":"PASS" if errors.is_empty() else "FAIL","reservations":4,"remaining":42,"species_assignments":0,"retained_homes":retained,"doors":doors,"source_roof_contact_rays":roof_contacts,"visual_only_water_meshes":water,"rays":rays,"errors":errors,"limits":"Bounded geometric witnesses and reused door poses; load capacity, habitat fit, dynamic traversal, water operation, privacy permission and occupancy remain held."}
	FileAccess.open("res://artifacts/star_atlas_specialty_first.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("PASS: STAR_ATLAS_SPECIALTY_FIRST " if errors.is_empty() else "FAIL: STAR_ATLAS_SPECIALTY_FIRST ",JSON.stringify(report));quit(0 if errors.is_empty() else 1)
