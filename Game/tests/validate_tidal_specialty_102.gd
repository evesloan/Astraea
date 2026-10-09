extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	var ship:Node3D=main.get_node("World360/Astraea")
	var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	for i in range(120):await physics_frame
	paused=true
	var districts:Node3D=ship.get_node("ShipSpace/Districts")
	var room:Node3D
	for entry in ship.get_node("ShipSystems/ReceivedRoomResidency").entries:
		if str(entry.room.name)=="AST-UNIT-D13-b93f57e92db46ca1":
			room=entry.room
			if room.get_parent()==null:entry.parent.add_child(room)
	assert(room!=null)
	ship.get_node("ShipSystems/ReceivedRoomResidency").enabled=false
	paused=false
	for i in range(4):await physics_frame
	paused=true
	assert(room.get_meta("census_source_index")==102 and room.get_meta("source_rest_slots").size()==1 and not room.get_meta("finished"))
	var retained:=0
	for entry in ship.get_node("ShipSystems/ReceivedRoomResidency").entries:
		if str(entry.parent.name)=="TidalRoomCandidates":retained+=1
	assert(retained==85)
	var support:Node3D=room.get_node("QuietCocoonSupport")
	var physics:=ship.get_world_3d().direct_space_state
	var excluded:Array[RID]=[]
	for body in ship.find_children("*","CharacterBody3D",true,false):excluded.append(body.get_rid())
	for body in ship.find_children("*","RigidBody3D",true,false):excluded.append(body.get_rid())
	var errors:Array=[]
	var points:Array[Vector3]=[Vector3(-44.5,84,-298.4),Vector3(-45.8,84,-298.4),Vector3(-46.2,84,-298.4),Vector3(-47.5,84,-298.4),Vector3(-49,84,-298.4),Vector3(-51,84,-298.4),Vector3(-52.8,84,-298.4),Vector3(-52.8,84,-300.05),Vector3(-55,84,-297.25),Vector3(-48.875,84,-299.5),Vector3(-48.875,84,-300.35)]
	for p in points:
		var ray:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.2,p-Vector3.UP*.35);ray.exclude=excluded
		var hit:=physics.intersect_ray(ray)
		if hit.is_empty() or absf(hit.position.y-p.y)>.035:errors.append({"kind":"floor","point":str(p),"hit":str(hit.get("position","none"))})
		var q:=PhysicsShapeQueryParameters3D.new();var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8;q.shape=capsule;q.exclude=excluded;q.margin=.001;q.transform.origin=p+Vector3.UP*.925
		for collision in physics.intersect_shape(q,16):errors.append({"kind":"clearance","point":str(p),"collider":str(collision.collider.get_path())})
	var contact:Vector3=support.to_global(Vector3(0,.6096875,0))
	var ray:=PhysicsRayQueryParameters3D.create(contact+Vector3.UP*.12,contact-Vector3.UP*.12);ray.exclude=excluded
	var hit:=physics.intersect_ray(ray)
	if hit.is_empty() or absf(hit.position.y-contact.y)>.025:errors.append({"kind":"support","point":str(contact),"hit":str(hit.get("position","none"))})
	for name in ["EntryDoor","WashDoor"]:
		var door:Node3D=room.get_node(name);assert(door.has_method("interact") and not door.persistent_id.is_empty())
	var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/TIDAL_SPECIALTY_102.json"))
	assert(FileAccess.get_sha256("res://assets/models/AST-RES-TIDAL_lift_fit_r003.glb")==d.frontage.source_sha256)
	var result={"status":"PASS" if errors.is_empty() else "FAIL","source_index":102,"retained_ordinary_homes":retained,"specialty_reservations_instantiated":1,"rest_places":1,"bounded_floor_capsule_points":points.size(),"support_surface_probe":1,"errors":errors,"limits":"No actual species/pose, full cart traversal, acoustic/environment simulation or final visual acceptance"}
	FileAccess.open("res://artifacts/tidal_specialty_102.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print("TIDAL_SPECIALTY_102 ",JSON.stringify(result));quit(0 if errors.is_empty() else 1)
