extends SceneTree
func _initialize() -> void: call_deferred("run")
func bodies(node: Node) -> Array[RID]:
	var result: Array[RID] = []
	for body in node.find_children("*","StaticBody3D",true,false): result.append(body.get_rid())
	return result
func run() -> void:
	var main := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(30): await physics_frame
	var ship: Node3D = main.get_node("World360/Astraea")
	var player: CharacterBody3D = ship.get_node("ShipSpace/PersistentActors/Player")
	var state := ship.get_world_3d().direct_space_state
	var contents := ship.get_node("ShipSpace/Districts/D09_StarboardTerrace_AuthoredFootprint_WIP/SalonActivityFurnishings_WIP")
	assert(contents.find_children("StudyChair_*","Node3D",false,false).size()==4)
	for p in [Vector3(60.2,52.6,-31.8),Vector3(64,52.6,-18.5),Vector3(65.5,52.6,-20.8)]: assert(ship.arrive_at(p,0),"Activity approaches need actual floor and player clearance")
	var counter := contents.get_node("GuestRefreshmentCounter")
	var appliance := contents.get_node("TwinSpoutStation_StaticOnly")
	var probe := PhysicsRayQueryParameters3D.create(appliance.global_position+Vector3.UP*.03,appliance.global_position-Vector3.UP*.03)
	probe.exclude = bodies(appliance)
	var hit := state.intersect_ray(probe)
	assert(not hit.is_empty() and counter.is_ancestor_of(hit.collider) and absf(hit.position.y-53.4)<.01,"Beverage station support must meet the real host worktop")
	var fixture := contents.get_node("SharedStudyTaskFixture")
	var mount: Node3D = fixture.find_child("POINT_mount_contact",true,false)
	var query := PhysicsRayQueryParameters3D.create(mount.global_position+Vector3.UP*.025,mount.global_position-Vector3.UP*.025)
	query.exclude = bodies(fixture)
	var support := state.intersect_ray(query)
	assert(not support.is_empty() and absf(support.position.y-mount.global_position.y)<.006,"Study fixture must meet its authored receiver")
	for folio in contents.find_children("OpenReadingFolio_*","Node3D",false,false):
		var ray := PhysicsRayQueryParameters3D.create(folio.global_position+Vector3.UP*.02,folio.global_position-Vector3.UP*.02)
		ray.exclude = bodies(folio)
		var contact := state.intersect_ray(ray)
		assert(not contact.is_empty() and absf(contact.position.y-folio.global_position.y)<.005,"Reading folio must rest on the tabletop")
	var light: SpotLight3D = contents.get_node("StudyTableOpticalSource")
	var optical := PhysicsRayQueryParameters3D.create(light.global_position,light.global_position+Vector3.DOWN*.20)
	assert(state.intersect_ray(optical).is_empty(),"Task light must exit the real diffuser unobstructed")
	print("SALON CONTENT PASS: four proposed study chairs; three clear activity approaches; beverage/fixture/folio support contacts; task-light optical exit. Static furnishings, not serving, seating AI or pickup behavior.")
	quit()
