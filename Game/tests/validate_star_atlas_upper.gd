extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for i in range(120):await physics_frame
	paused=true
	var ship:Node3D=main.get_node("World360/Astraea")
	var districts:Node3D=ship.get_node("ShipSpace/Districts")
	var upper:Node3D=districts.get_node("D15_D17_StarAtlasUpper_WIP")
	assert(upper.get_meta("source_part_count")==514 and upper.get_meta("D15_cover_reused") and upper.get_meta("new_guest_units")==0)
	var lower:Node3D=districts.get_node("D12_D14_StarAtlas_WIP")
	assert(lower.get_node("StarAtlasPassengerLift").floor_heights==[78.0,84.0,88.5])
	var home_root:Node3D=districts.get_node("StarAtlasRoomCandidates")
	var retained_homes:=0
	for entry in ship.get_node("ShipSystems/ReceivedRoomResidency").entries:
		if entry.parent==home_root:
			assert(is_instance_valid(entry.room))
			retained_homes+=1
	assert(retained_homes==85,"Count registered homes, including temporarily detached residents")
	var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_UPPER_COMMONS.json"))
	for path in d.source_pins:assert(FileAccess.get_sha256("res://"+str(path).trim_prefix("Game/"))==d.source_pins[path])
	var excluded:Array[RID]=[]
	for body in ship.find_children("*","CharacterBody3D",true,false):excluded.append(body.get_rid())
	for body in ship.find_children("*","RigidBody3D",true,false):excluded.append(body.get_rid())
	var physics:=ship.get_world_3d().direct_space_state
	var points:Array[Dictionary]=[]
	for y in [93.0,97.5,102.0]:
		for x in [-65.5,-61.0,-55.0,-50.0]:points.append({"p":Vector3(x,y,0),"stair":false})
		points.append({"p":Vector3(-76,y,-8),"stair":false})
	for z in [-15.0,-24.0,-31.0,15.0,24.0,29.0]:points.append({"p":Vector3(-84,97.5,z),"stair":false})
	for y in [93.0,97.5]:
		points.append({"p":Vector3(-70.8,y+1.125,6.54),"stair":true})
		points.append({"p":Vector3(-69.3,y+2.25,10.2),"stair":false})
		points.append({"p":Vector3(-67.8,y+3.375,6.54),"stair":true})
	var errors:Array=[]
	for item in points:
		var p:Vector3=item.p
		var ray:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.2,p-Vector3.UP*.35);ray.exclude=excluded
		var hit:=physics.intersect_ray(ray)
		if hit.is_empty() or absf(hit.position.y-p.y)>.035:errors.append({"kind":"floor","point":str(p),"hit":str(hit.get("position","none"))})
		var query:=PhysicsShapeQueryParameters3D.new();var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8
		query.shape=capsule;query.exclude=excluded;query.margin=.001;query.transform.origin=p+Vector3.UP*(1.0 if item.stair else .925)
		var collisions:=physics.intersect_shape(query,16)
		if not collisions.is_empty():
			var names:Array=[]
			for col in collisions:names.append(str(col.collider.get_path()))
			errors.append({"kind":"clearance","point":str(p),"colliders":names})
	var report={"status":"PASS" if errors.is_empty() else "FAIL","parts":514,"new_guest_units":0,"retained_homes":85,"lower_lift_stops":3,"source_pins":d.source_pins.size(),"floor_and_clearance_points":points.size(),"errors":errors,"scope":"Actual main installation, retained source pins and bounded public-ring/home-link/stair witnesses. Detailed traversal, final visual review, full furnishing and service completion remain unfinished."}
	FileAccess.open("res://artifacts/star_atlas_upper.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("STAR_ATLAS_UPPER ",JSON.stringify(report));quit(0 if errors.is_empty() else 1)
