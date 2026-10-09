extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for i in range(12):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var manager:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
	var actor:Node3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var before:int=int(manager.get_meta("startup_live_nodes",get_node_count()))
	var floors:int=ship.find_children("*","OccluderInstance3D",true,false).size()
	manager.refresh(9.0)
	var after:int=get_node_count()
	assert(after<before)
	assert(ship.find_children("*","OccluderInstance3D",true,false).size()==floors)
	var stats:Dictionary=manager.statistics()
	assert(stats.registered_rooms==561)
	var target:Dictionary={}
	for e in manager.entries:
		if not e.attached:
			target=e
			break
	assert(not target.is_empty())
	var identity:int=target.room.get_instance_id()
	var child_count:int=target.room.get_child_count()
	manager.prepare_position(target.bounds.get_center())
	assert(target.attached and target.room.is_inside_tree())
	assert(target.room.get_instance_id()==identity and target.room.get_child_count()==child_count)
	var bottle:=RigidBody3D.new()
	bottle.name="ResidencyContactWitness"
	bottle.freeze=true
	ship.get_node("ShipSpace/PersistentActors").add_child(bottle)
	bottle.global_position=target.bounds.get_center()
	manager.refresh(20.0)
	assert(target.attached)
	bottle.free()
	# Retention hysteresis: recently prepared far room survives a brief hidden interval.
	manager.refresh(.2)
	assert(target.attached)
	for i in range(3):await physics_frame
	# Find a demonstrated hit on actual cached collision geometry before testing restore.
	# Source meshes may start with tiny/degenerate or hidden/internal triangles.
	var state:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state
	var witness:Dictionary=_collision_witness(target.room,state)
	if not _require(not witness.is_empty(),"No baseline room collision witness"):return
	var query:PhysicsRayQueryParameters3D=witness.query
	var expected:RID=witness.rid
	paused=true
	if not _require(state.intersect_ray(query).get("rid")==expected,"Baseline collision missing when paused"):return
	target.parent.remove_child(target.room)
	target.attached=false
	if not _require(state.intersect_ray(query).get("rid")!=expected,"Detached collider remains queryable"):return
	manager.prepare_position(target.bounds.get_center())
	var restored:bool=state.intersect_ray(query).get("rid")==expected
	paused=false
	if not _require(restored,"Restored room collision unavailable in the same paused call"):return
	assert(target.room.get_instance_id()==identity and target.room.get_child_count()==child_count)
	# Signal-driven visibility reattachment does not wait for the0.2second poll.
	target.parent.remove_child(target.room)
	target.attached=false
	target.witness.screen_entered.emit()
	await process_frame
	assert(target.attached and target.room.is_inside_tree())
	# Deferred interiors release geometry while preserving room and moving-door state.
	var deferred:Dictionary={}
	for entry in manager.entries:
		if str(entry.parent.name)=="StarAtlasRoomCandidates":
			deferred=entry
			break
	assert(not deferred.is_empty())
	manager.prepare_position(deferred.bounds.get_center())
	var central:Node3D=deferred.room
	var central_id:int=central.get_instance_id()
	var door:Node3D=central.get_node("EntryDoor")
	var door_id:int=door.get_instance_id()
	door.open_fraction=.37
	var old_visual:Node3D=central.get_meta("resident_visual")
	var old_visual_id:int=old_visual.get_instance_id()
	manager.refresh(9.0)
	assert(not deferred.attached and not central.has_meta("resident_visual"))
	assert(not is_instance_valid(old_visual))
	paused=true
	manager.prepare_position(deferred.bounds.get_center())
	assert(central.get_instance_id()==central_id and door.get_instance_id()==door_id)
	assert(is_equal_approx(door.open_fraction,.37))
	assert(central.get_meta("resident_visual").get_instance_id()!=old_visual_id)
	var floor_point:Vector3=central.to_global(Vector3(0,0,-1))
	var floor_hit:Dictionary=state.intersect_ray(PhysicsRayQueryParameters3D.create(floor_point+Vector3.UP*.15,floor_point-Vector3.UP*.4))
	assert(not floor_hit.is_empty() and absf(floor_hit.position.y-floor_point.y)<.04)
	assert(ship.find_children("*","OccluderInstance3D",true,false).size()==floors)
	paused=false
	var result:Dictionary={"status":"PASS","deferred_geometry_recreated":true,"deferred_door_identity_and_state_preserved":true,"deferred_arrival_immediate_collision":true,"initial_live_nodes":before,"after_hidden_room_detachment":after,"reduction":before-after,"steady_state":stats,"same_node_identity_after_restore":true,"remote_loose_body_pins_room":true,"paused_arrival_immediate_collision":true,"visibility_signal_restore":true,"independent_occluders_retained":floors,"scope":"Headless near/hidden residency, same cached source identity, grace and arrival preparation. Received-section cache and prototype resources are retained; immutable home instances are released/recreated. Graphical notifier behavior and target FPS unverified."}
	FileAccess.open("res://artifacts/received_room_residency.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("RECEIVED_ROOM_RESIDENCY ",JSON.stringify(result))
	quit()

func _require(condition:bool,message:String)->bool:
	if not condition:
		push_error(message)
		quit(1)
	return condition

func _collision_witness(room:Node3D,state:PhysicsDirectSpaceState3D)->Dictionary:
	for collider:CollisionShape3D in room.find_children("*","CollisionShape3D",true,false):
		if collider.disabled or not collider.shape is ConcavePolygonShape3D:continue
		var body:StaticBody3D=collider.get_parent() as StaticBody3D
		if body==null:continue
		var faces:PackedVector3Array=collider.shape.get_faces()
		for offset in range(0,faces.size()-2,3):
			var a:Vector3=collider.global_transform*faces[offset]
			var b:Vector3=collider.global_transform*faces[offset+1]
			var c:Vector3=collider.global_transform*faces[offset+2]
			var normal:Vector3=(b-a).cross(c-a)
			if normal.length_squared()<0.0001:continue
			normal=normal.normalized()
			var center:Vector3=(a+b+c)/3.0
			var query:=PhysicsRayQueryParameters3D.create(center+normal*.1,center-normal*.1)
			query.hit_back_faces=true
			var hit:Dictionary=state.intersect_ray(query)
			if hit.get("rid")==body.get_rid():
				print("RESIDENCY_COLLISION_WITNESS ",collider.get_path()," triangle=",offset/3," position=",hit.position)
				return {"query":query,"rid":body.get_rid()}
	return {}
