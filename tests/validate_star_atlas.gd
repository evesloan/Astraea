extends SceneTree
func _initialize() -> void:call_deferred("run")
func walk(actor:CharacterBody3D,destination:Vector2) -> void:
	var reached:=false
	for frame in range(900):
		var delta:=Vector3(destination.x-actor.position.x,0,destination.y-actor.position.z)
		if delta.length()<.09:
			reached=true
			break
		var motion:=delta.normalized()*3.1
		actor.velocity.x=motion.x
		actor.velocity.z=motion.z
		actor.velocity.y=-.1 if actor.is_on_floor()else actor.velocity.y-9.8/60
		actor.move_and_slide()
		await physics_frame
	if not reached:
		for i in range(actor.get_slide_collision_count()):print("STAR ATLAS BLOCKER ",actor.get_slide_collision(i).get_collider().get_path())
	assert(reached,"Star Atlas route stalled at %s toward %s"%[actor.position,destination])
func check_gallery_guards(ship:Node3D) -> int:
	var contract:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D12_D14_star_atlas.json"))
	var count:=0
	for region in contract.floor_regions:
		if not "_gallery_" in region.id:continue
		var y:float=contract.floor_y[region.deck]
		var stair:Dictionary=contract.first_stair if region.deck=="D13" else contract.second_stair
		var rings:Array=[region.boundary]
		rings.append_array(region.holes)
		for ring in rings:
			for i in range(ring.size()):
				var a:=Vector2(ring[i][0],ring[i][1])
				var b:=Vector2(ring[(i+1)%ring.size()][0],ring[(i+1)%ring.size()][1])
				var normal:Vector2=(b-a).normalized().orthogonal()
				for t in [.2,.5,.8]:
					var p:Vector2=a.lerp(b,t)
					if absf(p.x+48)<.01:continue # Real atrium connector mouth.
					if absf(p.y-stair.start_z)<.015 and p.x>=stair.upper_flight_x[0]-.04 and p.x<=stair.upper_flight_x[1]+.04:continue
					var shaft:Dictionary=contract.lift.floor_hole_xz
					if p.x>=shaft.x[0]-.02 and p.x<=shaft.x[1]+.02 and p.y>=shaft.z[0]-.02 and p.y<=shaft.z[1]+.02:continue # Separate shaft and controlled gates.
					var from:=Vector3(p.x+normal.x*.35,y+.65,p.y+normal.y*.35)
					var to:=Vector3(p.x-normal.x*.35,y+.65,p.y-normal.y*.35)
					var query:=PhysicsRayQueryParameters3D.create(from,to)
					query.hit_back_faces=true
					var hit:=ship.get_world_3d().direct_space_state.intersect_ray(query)
					assert(not hit.is_empty(),"Missing gallery guard at %s %s"%[region.deck,p])
					count+=1
	return count
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(30):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var district:=ship.find_child("D12_D14_StarAtlas_WIP",true,false)
	assert(district!=null and district.get_meta("historical_library_id")=="D12_stargazing4")
	var guard_samples:=check_gallery_guards(ship)
	assert(guard_samples>50)
	print("STAR ATLAS GUARD CONTACT SAMPLES: ",guard_samples)
	var architecture:=district.get_node("StarAtlasAuthoredArchitecture")
	for i in range(10):
		var marker:=architecture.find_child("DATUM_light_"+str(i),true,false)as Node3D
		var ray:=PhysicsRayQueryParameters3D.create(marker.global_position,marker.global_position-Vector3.UP*.12)
		assert(ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Library fixture exit must be outside its source")
	var roof:=ship.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-84,92.70,1),Vector3(-84,93.10,1)))
	assert(not roof.is_empty() and absf(roof.position.y-92.76)<.015,"Protected D15 cover remains opaque")
	var pan:=ship.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-66.5,77.4,-10.2),Vector3(-66.5,77.81,-10.2)))
	assert(not pan.is_empty() and absf(pan.position.y-77.76)<.015,"Lift pit remains sealed within D12 slab, above performers' commons")
	var lift=district.get_node("StarAtlasPassengerLift")
	assert(lift.floor_heights==[78.0,84.0,88.5])
	for deck in [12,13,14]:assert(lift.find_child("star_atlas_cabin_D"+str(deck),true,false)!=null)
	for part in architecture.find_children("LIB_finish*","MeshInstance3D",true,false):
		assert(part.get_node_or_null("StaticContact")==null,"Study fabric must not duplicate physical floor")
	var collection:=district.get_node("NorthCollectionStudy_WIP")
	var stocked_groups:=0
	for batch in collection.find_children("LocalCollectionStock_*","MultiMeshInstance3D",false,false):
		assert(batch.multimesh.instance_count>0)
		stocked_groups+=batch.multimesh.instance_count
		for index in range(batch.multimesh.instance_count):
			var base:Vector3=batch.global_transform*batch.multimesh.get_instance_transform(index).origin
			var support:=ship.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(base+Vector3.UP*.02,base-Vector3.UP*.03))
			assert(not support.is_empty() and absf(support.position.y-base.y)<.012,"Each book group must rest on a real shelf")
	assert(stocked_groups==63,"All authored shelf positions must remain stocked")
	var activities:=district.get_node("StarAtlasCommonsActivities_WIP")
	for item in activities.get_children():
		if item.has_meta("supported_book_group"):
			var p:Vector3=item.global_position
			var support:=ship.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(p+Vector3.UP*.02,p-Vector3.UP*.03))
			assert(not support.is_empty() and absf(support.position.y-p.y)<.012,"Window-study stock needs shelf contact")
	var fixture:=activities.get_node("D13WindowStudyFixture")
	var mount:Node3D=fixture.find_child("POINT_mount_contact",true,false)
	var mounting:=PhysicsRayQueryParameters3D.create(mount.global_position+Vector3.UP*.025,mount.global_position-Vector3.UP*.025)
	var excluded:Array[RID]=[]
	for body in fixture.find_children("*","StaticBody3D",true,false):excluded.append(body.get_rid())
	mounting.exclude=excluded
	var mounting_contact:=ship.get_world_3d().direct_space_state.intersect_ray(mounting)
	assert(not mounting_contact.is_empty() and absf(mounting_contact.position.y-mount.global_position.y)<.006,"Single-study fixture must sit on its receiver")
	var source:Node3D=activities.get_node("D13WindowStudyOpticalSource")
	assert(ship.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(source.global_position,source.global_position+Vector3.DOWN*.20)).is_empty(),"Window-study light must leave its diffuser")
	for p in [Vector3(-67.1,84.1,-4.8),Vector3(-88.5,88.6,10.6),Vector3(-91.4,88.6,9)]:assert(ship.arrive_at(p,0),"Upper activity approach must have floor and capsule clearance")
	var arrival:=district.get_node("StarAtlasLibraryArrival_WIP")
	var counter:=arrival.get_node("LibraryReferenceCounter")
	for side in ["west","lower","east"]:
		for role in ["guest_approach","rear_approach"]:
			var point:Node3D=counter.find_child("DATUM_"+side+"_"+role,true,false)
			assert(point!=null and ship.arrive_at(point.global_position+Vector3.UP*.1,0),"Counter approaches must meet actual floor/body clearance")
	var knee:=PhysicsShapeQueryParameters3D.new()
	var knee_shape:=BoxShape3D.new()
	knee_shape.size=Vector3(.7,.60,.45)
	knee.shape=knee_shape
	knee.transform=counter.global_transform*Transform3D(Basis.IDENTITY,Vector3(0,.34,0))
	for hit in ship.get_world_3d().direct_space_state.intersect_shape(knee,32):
		assert(not hit.collider is StaticBody3D,"Lower reference counter knee recess must remain hollow")
	for folio in arrival.find_children("CounterReferenceFolio_*","Node3D",false,false):
		var query:=PhysicsRayQueryParameters3D.create(folio.global_position+Vector3.UP*.02,folio.global_position-Vector3.UP*.025)
		var folio_excluded:Array[RID]=[]
		for body in folio.find_children("*","StaticBody3D",true,false):folio_excluded.append(body.get_rid())
		query.exclude=folio_excluded
		var support:=ship.get_world_3d().direct_space_state.intersect_ray(query)
		assert(not support.is_empty() and counter.is_ancestor_of(support.collider) and absf(support.position.y-folio.global_position.y)<.006,"Arrival reference books must sit on counter tops")
	for task_fixture in arrival.find_children("CounterTaskFixture_*","Node3D",false,false):
		var receiver:Node3D=task_fixture.find_child("POINT_mount_contact",true,false)
		var query:=PhysicsRayQueryParameters3D.create(receiver.global_position+Vector3.UP*.025,receiver.global_position-Vector3.UP*.025)
		var fixture_excluded:Array[RID]=[]
		for body in task_fixture.find_children("*","StaticBody3D",true,false):fixture_excluded.append(body.get_rid())
		query.exclude=fixture_excluded
		var support:=ship.get_world_3d().direct_space_state.intersect_ray(query)
		assert(not support.is_empty() and counter.is_ancestor_of(support.collider) and absf(support.position.y-receiver.global_position.y)<.006,"Counter task fixture must rest on its authored top")
	for task_source in arrival.find_children("CounterTaskSource_*","SpotLight3D",false,false):
		assert(ship.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(task_source.global_position,task_source.global_position+Vector3.DOWN*.15)).is_empty(),"Counter task source must leave its diffuser")
	var reading_source:Node3D=arrival.get_node("AtriumReadingLampSource")
	assert(ship.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(reading_source.global_position,reading_source.global_position-reading_source.global_basis.z*.20)).is_empty(),"Reading lamp must emit outside its actual hood")
	for p in [Vector3(-54.7,78.1,6.25),Vector3(-59,78.1,10.5),Vector3(-57,78.1,17.25),Vector3(-53.5,78.1,17.25)]:assert(ship.arrive_at(p,0),"Library catalogue and reading approaches need room clearance")
	actor.set_physics_process(false)
	actor.position=Vector3(-50,78.1,0)
	actor.velocity=Vector3.ZERO
	var route:Array[Vector2]=[Vector2(-60,0),Vector2(-77,-8),Vector2(-87,-15),Vector2(-94.5,-15),Vector2(-94.5,-9.4),Vector2(-94.5,-.5),Vector2(-91,-.5),Vector2(-91,-9.5),Vector2(-85,-11.5),Vector2(-79,-11.5),Vector2(-72.2,-6),Vector2(-63,0),Vector2(-72.2,0),Vector2(-72.2,12.5),Vector2(-69,12.5),Vector2(-69,5),Vector2(-65.5,5),Vector2(-65.5,12.5),Vector2(-83,12.5),Vector2(-72.2,12.5),Vector2(-72.2,0),Vector2(-63,0),Vector2(-72.2,0),Vector2(-72.2,-10.2),Vector2(-70,-10.2)]
	for i in range(route.size()):
		await walk(actor,route[i])
		if i==7:assert(absf(actor.position.y-84)<.12,"First library stair reaches D13")
		if i==17:assert(absf(actor.position.y-88.5)<.12,"Second library stair reaches D14")
	assert(absf(actor.position.y-88.5)<.12)
	route.reverse()
	for p in route:await walk(actor,p)
	await walk(actor,Vector2(-50,0))
	assert(absf(actor.position.y-78)<.12,"Both actual stairs return to the lower library")
	for point in [Vector2(-60,0),Vector2(-77,-8),Vector2(-87,-15),Vector2(-89.5,-21.5),Vector2(-87,-25.3),Vector2(-83,-25.3),Vector2(-79,-24),Vector2(-79,-18),Vector2(-87,-15)]:await walk(actor,point)
	for point in [Vector2(-65,-2),Vector2(-63,3.5),Vector2(-60,3.5),Vector2(-59,7.5),Vector2(-59,10.5),Vector2(-57,10.5),Vector2(-57,17.25),Vector2(-57,20.5),Vector2(-53.5,20.5),Vector2(-53.5,17.25)]:await walk(actor,point)
	print("STAR ATLAS WALK FINISHED AT PHYSICS FRAME: ",Engine.get_physics_frames())
	print("STAR ATLAS PASS: actual bidirectional three-level walking circuit, ten light exits, protected D15 cap, sealed D12 lift pan, three distinct controls, supported local book stock and first collection study approaches. Loaded lift, detailed guards, wider furnishing and final art require separate checks.")
	main.queue_free()
	await process_frame
	quit()
