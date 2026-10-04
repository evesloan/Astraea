extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var main := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(30): await physics_frame
	var ship: Node3D = main.get_node("World360/Astraea")
	var player: CharacterBody3D = ship.get_node("ShipSpace/PersistentActors/Player")
	var state := ship.get_world_3d().direct_space_state
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/atrium_garden.json"))
	assert(ship.arrive_at(Vector3(0,6.1,-51),PI))
	var probes := 0
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.3
	capsule.height = 1.8
	for route in data.approach_centerlines:
		for i in range(route.size()-1):
			var a := Vector3(route[i][0],6.05,route[i][1])
			var b := Vector3(route[i+1][0],6.05,route[i+1][1])
			var steps := int(ceil(a.distance_to(b)/0.4))
			for step in range(steps+1):
				var at := a.lerp(b,float(step)/steps)
				var ray := PhysicsRayQueryParameters3D.create(at+Vector3.UP*.4,at-Vector3.UP*.4)
				ray.exclude = [player.get_rid()]
				var hit := state.intersect_ray(ray)
				assert(not hit.is_empty() and absf(hit.position.y-6)<.02,"Garden path must remain level at D02")
				var query := PhysicsShapeQueryParameters3D.new()
				query.shape = capsule
				query.transform.origin = at+Vector3.UP*.9
				query.exclude = [player.get_rid()]
				assert(state.intersect_shape(query).is_empty(),"Garden approach body clearance")
				probes += 1
	var garden := ship.get_node("ShipSpace/Districts/D02_OffsetGardenCourt_WIP")
	for lamp in garden.find_children("PathLantern_*","Node3D",false,false):
		var datum: Node3D = lamp.find_child("DATUM_light",true,false)
		assert(datum != null)
		var optical_ray := PhysicsRayQueryParameters3D.create(datum.global_position,datum.global_position+Vector3.DOWN)
		optical_ray.exclude = [player.get_rid()]
		assert(state.intersect_ray(optical_ray).is_empty(),"Lamp optical datum must clear its own stem and hood")
		for offset in [Vector3(.35,0,0),Vector3(-.35,0,0),Vector3(0,0,.35),Vector3(0,0,-.35)]:
			var at: Vector3 = lamp.global_position+offset
			var support := state.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.25,at-Vector3.UP*.15))
			assert(not support.is_empty() and absf(support.position.y-6)<.02,"Lantern foot must remain on dry court: "+str(lamp.name)+" at "+str(at)+" hit "+str(support))
	for tree_name in ["CANOPY_A","CANOPY_B"]:
		var tree := garden.get_node(tree_name)
		for mesh in tree.find_children("*","MeshInstance3D",true,false):
			for index in range(8):
				var p: Vector3 = mesh.global_transform * mesh.get_aabb().get_endpoint(index)
				assert(p.y < 27 and absf(p.x)<26 and absf(p.z)<42,"Canopies stay below D06 and inside reserved lower void")
	for frame in range(20): await physics_frame
	assert(player.is_on_floor() and absf(player.position.y-6)<.1)
	print("GARDEN PASS: four level approaches; ",probes," support/body-clearance probes; two canopies fit lower atrium. No cart, swimming or final visual acceptance.")
	quit()
