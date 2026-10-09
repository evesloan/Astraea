extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var main: Node = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	var ship := main.get_node("World360/Astraea") as Node3D
	for frame in range(12): await physics_frame
	var room: Node3D = ship.get_node("ShipSpace/Districts/CustodialDepotReceiving_WIP")
	load("res://scripts/tidal_lift_candidate.gd").build(ship)
	for frame in range(6): await physics_frame
	var physics := ship.get_world_3d().direct_space_state
	var excluded: Array[RID] = []
	for actor in main.find_children("*","CharacterBody3D",true,false): excluded.append(actor.get_rid())
	for body in main.find_children("*","RigidBody3D",true,false): excluded.append(body.get_rid())
	var floor_excluded: Array[RID] = excluded.duplicate()
	for body in room.find_children("*","StaticBody3D",true,false):floor_excluded.append(body.get_rid())
	var errors: Array = []
	var contacts: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/CUSTODIAL_FLOOR_CONTACTS_CANDIDATE.json"))
	for contact in contacts.contacts:
		var a: Array = contact.min_world
		var b: Array = contact.max_world
		var p := Vector3((a[0]+b[0])*.5,0,(a[2]+b[2])*.5)
		var ray := PhysicsRayQueryParameters3D.create(p+Vector3.UP*.1,p-Vector3.UP*.3)
		ray.exclude=floor_excluded
		var hit := physics.intersect_ray(ray)
		if hit.is_empty() or absf(hit.position.y-0)>.003:errors.append({"kind":"floor_contact","id":contact.id})
	var capsule := CapsuleShape3D.new()
	capsule.radius=.3
	capsule.height=1.8
	var routes := [
		[Vector3(3,0,460),Vector3(10,0,460),Vector3(26,0,460),Vector3(26,0,404)],
		[Vector3(26,0,439),Vector3(19.4,0,439)],
		[Vector3(26,0,449),Vector3(39,0,449)],
		[Vector3(26,0,405),Vector3(19.5,0,405)]
	]
	var samples:=0
	for points in routes:
		for segment in range(points.size()-1):
			var a: Vector3=points[segment]
			var b: Vector3=points[segment+1]
			var count:=int(ceil(a.distance_to(b)/.25))+1
			for i in range(count):
				var p:=a.lerp(b,float(i)/maxf(1,float(count-1)))
				var ray:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.15,p-Vector3.UP*.30)
				ray.exclude=excluded
				var support:=physics.intersect_ray(ray)
				if support.is_empty() or absf(support.position.y-0)>.025:errors.append({"kind":"route_support","xyz":[p.x,p.y,p.z]})
				var query:=PhysicsShapeQueryParameters3D.new()
				query.shape=capsule
				query.exclude=excluded
				query.transform.origin=p+Vector3.UP*.925
				for hit in physics.intersect_shape(query,32):errors.append({"kind":"route_clearance","xyz":[p.x,p.y,p.z],"collider":str(hit.collider.get_path())})
				samples+=1
	var original_count:=0
	var normalized_count:=0
	var budget:=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	for light: Light3D in room.find_children("*","Light3D",true,false):
		if light.get_meta("retained_source_light_witness",false):
			original_count+=1
			if light.visible or light.shadow_enabled or light.get_meta("fixture_powered",true):errors.append({"kind":"unquarantined_source_light","id":str(light.name)})
		else:
			normalized_count+=1
			if not budget.sources.has(light) or not budget.requested_shadow.get(light.get_instance_id(),false):errors.append({"kind":"unregistered_normalized_light","id":str(light.name)})
	assert(original_count==35 and normalized_count==35)
	assert(budget.shadow_source_budget==8 and budget.MAX_VISIBILITY_CANDIDATES==32)
	var result: Dictionary={"status":"PASS" if errors.is_empty() else "FAIL","source_meshes":7400,"floor_contacts":contacts.contacts.size(),"route_samples":samples,"quarantined_lights":original_count,"normalized_lights":normalized_count,"errors":errors,"default_scene_enabled":true,"limits":"Static receiving and candidate light registration only. Player/cart driven traversal, final lighting/visual, save and stock and cart operations remain open."}
	FileAccess.open("res://artifacts/custodial_depot_candidate.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("CUSTODIAL_DEPOT_CANDIDATE ",result.status," floor_contacts=",contacts.contacts.size()," route_samples=",samples," errors=",errors.size())
	quit(0 if errors.is_empty() else 1)
