extends SceneTree
var samples:=0
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

func _initialize() -> void:call_deferred("run")
func walk(actor:CharacterBody3D,destination:Vector2) -> void:
	var reached:=false
	for frame in range(700):
		var delta:=Vector3(destination.x-actor.position.x,0,destination.y-actor.position.z)
		if delta.length()<.09:
			reached=true
			break
		var movement:=delta.normalized()*3.1
		actor.velocity.x=movement.x
		actor.velocity.z=movement.z
		actor.velocity.y=-.1 if actor.is_on_floor()else actor.velocity.y-9.8/60
		actor.move_and_slide()
		await physics_frame
	if not reached:
		for i in range(actor.get_slide_collision_count()):
			var c:=actor.get_slide_collision(i)
			print("BLOCKER ",c.get_collider().get_path()," normal ",c.get_normal())
	assert(reached,"Commons route stalled at %s toward %s"%[actor.position,destination])
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(20):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var district:=ship.find_child("D09_R070_KindCurios_WIP",true,false)
	assert(district.get_meta("historical_room_id")=="R070")
	var room:=district.get_node("KindCuriosAuthoredRoom")
	for key in ["column_light_-1","column_light_1","ceiling_light_0","ceiling_light_1","ceiling_light_2"]:
		var marker:=room.find_child("DATUM_"+key,true,false)as Node3D
		var ray:=PhysicsRayQueryParameters3D.create(marker.global_position,marker.global_position-Vector3.UP*.12)
		assert(ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"R070 real source must exit its fixture")
	for part in room.find_children("CUR_VisualFloorBorder*","MeshInstance3D",true,false):assert(part.get_node_or_null("StaticContact")==null)
	var supported_goods:=0
	for item in district.get_children():
		if not item.has_meta("display_item_id"):continue
		var excluded_goods:Array[RID]=[]
		for body in item.find_children("*","StaticBody3D",true,false):excluded_goods.append(body.get_rid())
		var ray:=PhysicsRayQueryParameters3D.create(item.global_position+Vector3.UP*.01,item.global_position-Vector3.UP*.025)
		ray.exclude=excluded_goods
		var hit:=ship.get_world_3d().direct_space_state.intersect_ray(ray)
		assert(not hit.is_empty() and absf(hit.position.y-item.global_position.y)<.01,"Merchandise support meets actual shelf/plinth")
		supported_goods+=1
	assert(supported_goods==10)
	var cart:=ship.find_child("CustodialCart",true,false)as RigidBody3D
	var excluded:Array[RID]=[cart.get_rid(),actor.get_rid()]
	for product in cart.products:excluded.append(product.get_rid())
	var route:=[Vector2(52,216),Vector2(60,222.5),Vector2(84,223),Vector2(84,236),Vector2(77,236),Vector2(72,236),Vector2(70,236)]
	for i in range(route.size()-1):
		var a:Vector2=route[i]
		var b:Vector2=route[i+1]
		var delta:=b-a
		var yaw:=atan2(-delta.x,-delta.y)
		for step in range(21):
			var p:=a.lerp(b,step/20.0)
			check_pose(ship,cart,Vector3(p.x,52.53,p.y),yaw,excluded)
	for p in [Vector2(60,222.5),Vector2(84,223),Vector2(84,236),Vector2(72,236)]:
		for step in range(25):check_pose(ship,cart,Vector3(p.x,52.53,p.y),step*TAU/24.0,excluded)
	actor.set_physics_process(false)
	actor.position=Vector3(52,52.6,216)
	actor.velocity=Vector3.ZERO
	for destination in [Vector2(60,222.5),Vector2(84,223),Vector2(84,236),Vector2(77,236),Vector2(72,236),Vector2(70,236)]:await walk(actor,destination)
	assert(abs(actor.position.y-52.5)<.12)
	for destination in [Vector2(72,236),Vector2(77,236),Vector2(84,236),Vector2(84,223),Vector2(60,222.5),Vector2(52,216)]:await walk(actor,destination)
	assert(abs(actor.position.y-52.5)<.12)
	print("RETAIL CURIOS PASS: actual R070 stable identity, connected capsule entry/return,226 loaded-cart geometric poses, five source exits,10 supported merchandise placements and single floor ownership. Merchandise interaction, physical loaded-cart turning, guests and final visual acceptance pending.")
	main.queue_free()
	await process_frame
	quit()
