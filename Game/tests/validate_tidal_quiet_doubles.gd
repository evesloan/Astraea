extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	var ship:Node3D=main.get_node("World360/Astraea")
	for i in range(120):await physics_frame
	var registry:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");registry.enabled=false
	var rooms:Array[Node3D]=[];var retained:=0
	for entry in registry.entries:
		if str(entry.parent.name)=="TidalRoomCandidates":retained+=1
		if str(entry.parent.name)=="SpecialtyHomeCandidates":
			if entry.room.get_parent()==null:entry.parent.add_child(entry.room)
			rooms.append(entry.room)
	assert(retained==85 and rooms.size()==46)
	for i in range(4):await physics_frame
	var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var errors:Array=[];var doors:Array[Node3D]=[];var identities:Dictionary={}
	for room in rooms:
		assert(not identities.has(str(room.name)));identities[str(room.name)]=true
		assert(room.get_meta("source_rest_slots").size() in [1,2] and not room.get_meta("finished"))
		for name in ["EntryDoor","WashDoor"]:
			var door:Node3D=room.get_node(name);doors.append(door);door.interact(player)
	for i in range(90):await physics_frame
	for door in doors:
		if door.open_fraction>.001:errors.append({"kind":"door_close","door":str(door.get_path()),"fraction":door.open_fraction})
		door.interact(player)
	for i in range(90):await physics_frame
	for door in doors:
		if door.open_fraction<.999:errors.append({"kind":"door_open","door":str(door.get_path()),"fraction":door.open_fraction})
	paused=true
	var excluded:Array[RID]=[]
	for body in ship.find_children("*","CharacterBody3D",true,false):excluded.append(body.get_rid())
	for body in ship.find_children("*","RigidBody3D",true,false):excluded.append(body.get_rid())
	var physics:=ship.get_world_3d().direct_space_state;var points:=0;var supports:=0
	var rest_ids:Dictionary={}
	for room in rooms:
		var entry:Node3D=room.get_node("EntryDoor");var wash:Node3D=room.get_node("WashDoor")
		var aquatic:=str(room.get_meta("habitat_profile"))=="new_aquatic_rest_candidate"
		var low_nest:=str(room.get_meta("habitat_profile"))=="new_low_nesting_candidate"
		var floor_y:float=entry.position.y
		var side:=1.0 if entry.position.x<-44 else -1.0
		var witnesses:Array[Vector3]=[entry.position+Vector3(side,0,0),entry.position,entry.position-Vector3(side*1.5,0,0)]
		var supports_here:Array=[]
		for child in room.get_children():
			if child.has_node("ReservedRestPlace"):supports_here.append(child)
		assert(supports_here.size()==room.get_meta("source_rest_slots").size())
		for cocoon:Node3D in supports_here:
			witnesses.append(cocoon.to_global(Vector3(0,0,-2.4) if low_nest else (Vector3(0,0,-2.6) if aquatic else Vector3(0,0,-2.15))))
			if aquatic:witnesses.append(cocoon.to_global(Vector3(2.05,0,-.47)))
			if low_nest:witnesses.append(cocoon.to_global(Vector3(2.05,0,.72)))
			var rest:Marker3D=cocoon.get_node("ReservedRestPlace");var id:String=str(rest.get_meta("rest_slot_id"));assert(not rest_ids.has(id) and id in room.get_meta("source_rest_slots"));rest_ids[id]=true
			if aquatic:
				for mesh in cocoon.find_children("*","MeshInstance3D",true,false):
					if str(mesh.get_meta("extras",{}).get("collision_policy","")) in ["NO_SOLID_COLLISION","no_collision_detail"]:assert(mesh.find_children("*","StaticBody3D",true,false).is_empty())
			var contact:Vector3=rest.global_position;supports+=1
			var ray:=PhysicsRayQueryParameters3D.create(contact+Vector3.UP*.12,contact-Vector3.UP*.12);ray.exclude=excluded
			var hit:=physics.intersect_ray(ray)
			if hit.is_empty() or absf(hit.position.y-contact.y)>.025:errors.append({"kind":"support","room":str(room.name),"hit":str(hit.get("position","none"))})
		if int(room.get_meta("census_source_index"))==394:
			witnesses.append(wash.position+Vector3(0,0,.7));witnesses.append(wash.position);witnesses.append(wash.position-Vector3(0,0,.7))
		for p in witnesses:
			p.y=floor_y;points+=1
			var ray:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.2,p-Vector3.UP*.35);ray.exclude=excluded
			var hit:=physics.intersect_ray(ray)
			if hit.is_empty() or absf(hit.position.y-p.y)>.035:errors.append({"kind":"floor","room":str(room.name),"point":str(p),"hit":str(hit.get("position","none"))})
			var q:=PhysicsShapeQueryParameters3D.new();var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8;q.shape=capsule;q.exclude=excluded;q.margin=.001;q.transform.origin=p+Vector3.UP*.925
			for collision in physics.intersect_shape(q,16):errors.append({"kind":"clearance","room":str(room.name),"point":str(p),"collider":str(collision.collider.get_path())})
	assert(rest_ids.size()==57)
	var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/TIDAL_SPECIALTY_D13_BATCH.json"));assert(FileAccess.get_sha256("res://assets/models/AST-RES-TIDAL_lift_fit_r003.glb")==d.frontage.source_sha256)
	var result={"status":"PASS" if errors.is_empty() else "FAIL","retained_ordinary_homes":retained,"specialty_reservations":rooms.size(),"rest_places":57,"bounded_floor_capsule_points":points,"support_probes":supports,"door_cycles":doors.size(),"errors":errors,"limits":"Controller calls and bounded actual-main contacts; no full cart traversal, species/body pose, acoustic/environment simulation or final in-engine visual acceptance"}
	FileAccess.open("res://artifacts/tidal_quiet_doubles.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print("TIDAL_QUIET_DOUBLES ",JSON.stringify(result));quit(0 if errors.is_empty() else 1)
