extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for i in range(12):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var manager:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
	manager.enabled=false
	var actor:Node3D=ship.get_node("ShipSpace/PersistentActors/Player")
	paused=true
	var shopping:Node3D=ship.get_node("ShipSpace/Districts/ShoppingPromenadeChunks")
	assert(manager.entries.size()==738)
	assert(shopping.get_meta("new_shops")==99 and shopping.get_meta("unresolved_address_joins")==84)
	assert(ship.get_node("ShipSpace/Districts/D09_R070_KindCurios_WIP").get_meta("historical_room_id")=="R070")
	assert(FileAccess.get_sha256("res://assets/models/AST-RTL-005.glb")=="dda0ea75fa8d2363ac4f61292018271f2032b896d0669eccc097d58017e45497")
	var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/SHOPPING_PROMENADE.json"))
	var state:=ship.get_world_3d().direct_space_state
	var errors:Array=[]
	var floor_checks:=0
	var threshold_checks:=0
	var mapped:=0
	var unmapped:=0
	for row in d.chunks:
		var p:=Vector3(row.position[0],row.position[1],row.position[2])
		actor.global_position=p
		manager.prepare_position(p)
		manager.refresh(9.0)
		var chunk:Node3D=shopping.get_node(str(row.chunk_id))
		assert(chunk.has_meta("resident_visual"))
		if row.has("front_sign_x"):
			if chunk.has_meta("stable_room_id"):mapped+=1
			else:unmapped+=1
		var probes:Array[Vector3]=[]
		if row.has("front_sign_x"):
			for uv in [[0.0,-5.0],[0.0,-3.2],[-3.5,4.5]]:probes.append(Vector3(p.x-float(row.front_sign_x)*uv[1],52.5,p.z+uv[0]))
		else:
			for floor_row in d.floor_proposals:
				if floor_row.chunk_id!=row.chunk_id:continue
				var t:Array=floor_row.triangles_xz[0]
				probes.append(Vector3((t[0][0]+t[1][0]+t[2][0])/3.0,52.5,(t[0][1]+t[1][1]+t[2][1])/3.0))
		for point in probes:
			var hit:=state.intersect_ray(PhysicsRayQueryParameters3D.create(point+Vector3.UP*.15,point-Vector3.UP*.6))
			if hit.is_empty() or absf(hit.position.y-52.5)>.04:errors.append({"chunk":row.chunk_id,"kind":"floor","point":str(point)})
			floor_checks+=1
		if row.has("door_world"):
			var door:=Vector3(row.door_world[0],52.5,row.door_world[2])
			var shape:=CapsuleShape3D.new()
			shape.radius=.3
			shape.height=2.2
			var query:=PhysicsShapeQueryParameters3D.new()
			query.shape=shape
			query.transform=Transform3D(Basis.IDENTITY,door+Vector3.UP*1.102)
			query.margin=0
			query.exclude=[actor.get_rid()]
			var hits:=state.intersect_shape(query,8)
			if not hits.is_empty():errors.append({"chunk":row.chunk_id,"kind":"public_threshold","collider":str(hits[0].collider.get_path())})
			threshold_checks+=1
	assert(mapped==15 and unmapped==84)
	assert(ship.get_node("ShipSpace/ShoppingPromenadeOwnedFloors").get_child_count()==204)
	var result:Dictionary={"status":"PASS" if errors.is_empty() else "FAIL","new_shops":99,"chunks":177,"floor_checks":floor_checks,"public_threshold_checks":threshold_checks,"proven_new_room_ids":mapped,"unresolved_room_ids":unmapped,"retained_R070_unchanged":true,"source_lights":d.lights.size(),"errors":errors,"scope":"Actual main registration, floor contacts, stationary public thresholds and identity protection. Commerce, shared staff riser joins, hull acceptance, visual quality, full traversal and GPU FPS remain unfinished."}
	FileAccess.open("res://artifacts/shopping_default_adoption.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("SHOPPING_DEFAULT_ADOPTION ",JSON.stringify(result))
	quit(0 if errors.is_empty() else 1)
