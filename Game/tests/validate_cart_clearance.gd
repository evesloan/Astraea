extends SceneTree
var samples:=0
func _initialize() -> void:call_deferred("run")
func check_pose(ship:Node3D,cart:RigidBody3D,position:Vector3,yaw:float,excluded:Array[RID]) -> void:
	var body_transform:=Transform3D(Basis(Vector3.UP,yaw),position)
	for child in cart.get_children():
		if not child is CollisionShape3D:continue
		var query:=PhysicsShapeQueryParameters3D.new()
		query.shape=child.shape
		query.transform=body_transform*child.transform
		query.margin=.001
		query.exclude=excluded
		var hits:=ship.get_world_3d().direct_space_state.intersect_shape(query,32)
		assert(hits.is_empty(),"Cart geometry clashes at %s yaw %.2f part %s"%[str(position),yaw,child.name])
	var load_shape:=BoxShape3D.new()
	load_shape.size=Vector3(.65,.26,.96)
	var load_query:=PhysicsShapeQueryParameters3D.new()
	load_query.shape=load_shape
	load_query.transform=body_transform*Transform3D(Basis.IDENTITY,Vector3(0,1.05,0))
	load_query.exclude=excluded
	assert(ship.get_world_3d().direct_space_state.intersect_shape(load_query).is_empty(),"Upper-tray load clearance")
	samples+=1
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(40):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var cart:=ship.find_child("CustodialCart",true,false)as RigidBody3D
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var excluded:Array[RID]=[cart.get_rid(),actor.get_rid()]
	for product in cart.products:excluded.append(product.get_rid())
	for z in [-42.0,-49.4]:
		for i in range(31):check_pose(ship,cart,Vector3(84,84.03,z),PI*.5*i/30.0,excluded)
		for i in range(56):check_pose(ship,cart,Vector3(84-i*.1,84.03,z),PI/2,excluded)
	for i in range(61):check_pose(ship,cart,Vector3(-48-i*.5,27.03,0),PI/2,excluded)
	print("CART CLEARANCE PASS:",samples,"compound cart and upper-load pose samples across both suite entries, street turns and D06 Canopy arrival. Geometric clearance only; physical turning and inter-deck travel remain unverified.")
	main.queue_free()
	await process_frame
	quit()
