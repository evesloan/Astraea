extends SceneTree
# Focused source-backed integration gate, not ordinary-input or visual acceptance.
func _initialize() -> void:call_deferred("run")
func walk(actor:CharacterBody3D,destination:Vector2,expected_y:float) -> void:
	var reached:=false
	for frame in range(1800):
		var delta:=Vector3(destination.x-actor.position.x,0,destination.y-actor.position.z)
		if delta.length()<.10:
			reached=true
			break
		var motion:=delta.normalized()*3.1
		actor.velocity.x=motion.x
		actor.velocity.z=motion.z
		actor.velocity.y=-.1 if actor.is_on_floor()else actor.velocity.y-9.8/60
		actor.move_and_slide()
		await physics_frame
		assert(absf(actor.position.y-expected_y)<.25,"Fitted activity route must remain on its own supported deck")
	if not reached:
		for i in range(actor.get_slide_collision_count()):print("FITTED ROUTE BLOCKER ",actor.get_slide_collision(i).get_collider().get_path())
	assert(reached,"Fitted route stalled at %s toward %s"%[actor.position,destination])
func support(ship:Node3D,object:Node3D,point:Vector3,expected:Node=null,tolerance:float=.012) -> void:
	var query:=PhysicsRayQueryParameters3D.create(point+Vector3.UP*.025,point-Vector3.UP*.035)
	var excluded:Array[RID]=[]
	for body in object.find_children("*","StaticBody3D",true,false):excluded.append(body.get_rid())
	query.exclude=excluded
	var hit:=ship.get_world_3d().direct_space_state.intersect_ray(query)
	assert(not hit.is_empty(),"Missing support beneath "+str(object.get_path()))
	assert(absf(hit.position.y-point.y)<tolerance,"Support height mismatch "+str(object.get_path()))
	if expected!=null:assert(expected.is_ancestor_of(hit.collider),"Wrong supporting object "+str(object.get_path()))
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(30):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var district:Node3D=ship.find_child("D12_D14_StarAtlas_WIP",true,false)
	var fitted:Node3D=district.get_node("StarAtlasFittedInteriors_Candidate")
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/star_atlas_fitted_interiors.json"))
	assert(data.models.size()==105 and data.clusters.size()==24)
	assert(fitted.get_meta("capacity_change")==0)
	for item in data.models:
		var object:Node3D=fitted.get_node(NodePath(item.id))
		assert(object.get_meta("catalogue_file")==item.file)
		if item.role in ["mounted","static_stock"]:
			var receiver:Node3D=object.find_child("POINT_mount_contact",true,false)
			var p:Vector3=receiver.global_position if receiver!=null else object.global_position
			support(ship,object,p,fitted.get_node(NodePath(item.support)))
	for descriptor in data.fixtures:
		var light:SpotLight3D=fitted.get_node(NodePath(descriptor.id+"_OpticalSource"))
		assert(light.spot_range<=3.0)
		var ray:=PhysicsRayQueryParameters3D.create(light.global_position,light.global_position-light.global_basis.z*.15)
		assert(ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Source trapped in its fixture "+descriptor.id)
	var groups:=0
	for batch in fitted.find_children("FittedCollectionStock_*","MultiMeshInstance3D",false,false):
		groups+=batch.multimesh.instance_count
		for index in range(batch.multimesh.instance_count):
			var p:Vector3=batch.global_transform*batch.multimesh.get_instance_transform(index).origin
			support(ship,batch,p)
	assert(groups==data.stock_profiles.size()*21,"Every new seven-tier collection bay must carry its authored supported stock")
	for label in fitted.find_children("IntegratedCollectionLabel","Label3D",true,false):
		var from:Vector3=label.global_position+label.global_basis.z*.015
		var to:Vector3=label.global_position-label.global_basis.z*.025
		var hit:=ship.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(from,to))
		assert(not hit.is_empty() and label.get_parent().is_ancestor_of(hit.collider),"Integrated label must have its own physical source backing")
	actor.set_physics_process(false)
	for cluster in data.clusters:
		var y:float=cluster.origin[1]
		var start:Vector3=Vector3(-50,y+.1,0)
		assert(ship.arrive_at(start,0),"Every deck's normal arrival interface needs floor and capsule clearance")
		actor.velocity=Vector3.ZERO
		var points:Array[Vector2]=[Vector2(-50,0)]
		for p in cluster.approach_route:points.append(Vector2(p[0],p[1]))
		for point in points:await walk(actor,point,y)
		points.reverse()
		for point in points:await walk(actor,point,y)
		print("FITTED BRANCH ROUND TRIP ",cluster.id)
	print("STAR ATLAS FITTED PASS:24 source-defined activity branches, supported static contents/fixtures and real integrated-label backing. Scripted capsule movement only; ordinary input, loaded cart, visuals and target hardware remain separate gates.")
	main.queue_free()
	await process_frame
	quit()
