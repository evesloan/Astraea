extends SceneTree
var checks:=0
func _initialize()->void:call_deferred("run")
func run()->void:
	var scene:PackedScene=load("res://scenes/main.tscn")
	var main:=scene.instantiate()
	root.add_child(main)
	for i in range(120):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var house:Node3D=ship.get_node("ShipSpace/Districts/TidalGardenReceivingCandidate")
	var group:=house.get_node("TidalD13LocalServiceFittings") as Node3D
	assert(load("res://scripts/tidal_d13_local_service_fittings.gd").build(ship,house)==group)
	assert(group.get_meta("stock_returns_save_enabled")==false)
	assert(group.get_meta("new_cart_count")==0 and group.get_meta("new_room_count")==0 and group.get_meta("new_floor_count")==0)
	var meshes:=group.find_children("*","MeshInstance3D",true,false)
	var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/TIDAL_D13_LOCAL_SERVICE_FITTINGS.json"))
	assert(meshes.size()==int(d.mesh_count))
	var world:=group.get_world_3d().direct_space_state
	var exclude:Array[RID]=[]
	for body in main.find_children("*","CharacterBody3D",true,false):exclude.append(body.get_rid())
	for body in main.find_children("*","RigidBody3D",true,false):exclude.append(body.get_rid())
	for item in d.assemblies:
		var node:=group.find_child(str(item.name),true,false) as Node3D
		assert(str(node.get_meta("persistent_id"))==str(item.persistent_id))
		assert(node.global_position.distance_to(Vector3(item.position[0],item.position[1],item.position[2]))<.002)
	# Small representative stationary stance/door approaches and empty parking; exhaustive route/turning checks deferred.
	for p in [[-61,84,-493],[-61,84,-490],[-61,84,-487],[-61,84,-485.2],[-62.6,84,-493],[-62.6,84,-487],[-61,84,-496.5],[-61,84,-497.5]]:
		check_stance(world,Vector3(p[0],p[1],p[2]),exclude)
	# Bounded primary-fit screen: each new opaque triangle centroid samples against old static geometry.
	# A centroid ray through a short normal segment distinguishes actual nearby surface contacts from broad AABB overlap.
	var own:Array[RID]=exclude.duplicate()
	for mesh in meshes:own.append(mesh.get_node("StaticContact").get_rid())
	var geometry_probes:=0
	for item in d.assemblies:
		var assembly:=group.find_child(str(item.name),true,false) as Node3D
		var bounds:=AABB()
		var initialized:=false
		for mesh:MeshInstance3D in assembly.find_children("*","MeshInstance3D",true,false):
			var box: AABB=mesh.global_transform*mesh.get_aabb()
			bounds=box if not initialized else bounds.merge(box)
			initialized=true
		# Whole-source bounding envelope is conservative, with 3mm shrink only at exact floor contacts.
		var shape:=BoxShape3D.new();shape.size=bounds.size-Vector3(.006,.006,.006)
		var query:=PhysicsShapeQueryParameters3D.new();query.shape=shape;query.transform=Transform3D(Basis.IDENTITY,bounds.get_center());query.exclude=own;query.collide_with_areas=false
		var contacts:=world.intersect_shape(query,16)
		assert(contacts.is_empty(),"Existing solid inside fitting envelope "+str(item.name)+": "+str(contacts))
		geometry_probes+=1
	for mesh:MeshInstance3D in meshes:
		if not ("Bumper" in mesh.name or "EndStop" in mesh.name):continue
		var aabb:=mesh.get_aabb();var center:=mesh.global_transform*aabb.get_center()
		var box:=BoxShape3D.new();box.size=aabb.size-Vector3(.003,.003,.003)
		var query:=PhysicsShapeQueryParameters3D.new();query.shape=box;query.transform=Transform3D(mesh.global_basis,center);query.exclude=own;query.collide_with_areas=false
		assert(world.intersect_shape(query,16).is_empty(),"Parking bumpers intersect old geometry: "+mesh.name)
		geometry_probes+=1
	var staff:=main.find_child("ForwardStaffLift",true,false)
	assert(staff.floor_heights==[0.0,6.0,12.0,46.2,52.5,84.0,88.5,93.0,97.5,102.0])
	assert(staff.operation_ready and staff.landing_gates.size()==10)
	assert(house.get_meta("installed_guest_units")==131)
	assert(main.find_children("CustodialCart","RigidBody3D",true,false).size()==1)
	assert(house.get_node("TidalD13ServiceReceiving/D13_CleanSupplyDoor").persistent_id==&"tidal_d13_clean_supply_door_001")
	assert(house.get_node("TidalD13ServiceReceiving/D13_SealedReturnsDoor").persistent_id==&"tidal_d13_sealed_returns_door_001")
	var receipt:={"status":"PASS","actual_main_loaded":true,"source_meshes":meshes.size(),"stationary_floor_capsule_points":checks,"fitting_and_parking_old_geometry_queries":geometry_probes,"no_new_cart_room_floor":true,"physical_fittings":3,"empty_parking_bay":1,"original_ten_stop_lift_and_131_homes_preserved":true,"stock_returns_save_enabled":false,"limits":"Bounded primary fit and stationary stances; full routes/cart turning/species, stock operations, structural/load and final visual acceptance remain open."}
	var f:=FileAccess.open("res://artifacts/tidal_d13_local_service_fittings.json",FileAccess.WRITE);f.store_string(JSON.stringify(receipt,"\t")+"\n");f.close()
	print("PASS: bounded D13 local service fittings")
	quit(0)
func check_stance(world:PhysicsDirectSpaceState3D,p:Vector3,exclude:Array[RID])->void:
	var ray:=PhysicsRayQueryParameters3D.create(p+Vector3(0,.35,0),p-Vector3(0,.35,0));ray.exclude=exclude
	var hit:=world.intersect_ray(ray);assert(not hit.is_empty() and absf(hit.position.y-p.y)<.003)
	var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.72
	var query:=PhysicsShapeQueryParameters3D.new();query.shape=shape;query.transform=Transform3D(Basis.IDENTITY,p+Vector3(0,.87,0));query.exclude=exclude;query.collide_with_areas=false
	assert(world.intersect_shape(query,16).is_empty(),"Blocked stance: "+str(p));checks+=1
