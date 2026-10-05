extends "res://tests/validate_living_gifts.gd"
var contract_path:String
func run()->void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
	for frame in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(contract_path))
	var z:float=data.origin[2]
	assert(data.floor_y.size()==17 and data.stairs.size()==16)
	actor.set_physics_process(false);actor.position=Vector3(1.75,.1,z+1.6);actor.velocity=Vector3.ZERO
	for i in range(16):
		for point in [Vector2(1.75,z+3.5),Vector2(1.75,z+13),Vector2(-1.75,z+13),Vector2(-1.75,z+1.6)]:await walk(actor,point)
		assert(absf(actor.position.y-float(data.floor_y[i+1]))<.12)
		await walk(actor,Vector2(1.75,z+1.6))
	for i in range(15,-1,-1):
		await walk(actor,Vector2(-1.75,z+1.6))
		for point in [Vector2(-1.75,z+13),Vector2(1.75,z+13),Vector2(1.75,z+1.6)]:await walk(actor,point)
		assert(absf(actor.position.y-float(data.floor_y[i]))<.12)
	for y in data.floor_y:
		actor.position=Vector3(0,float(y)+.1,z-14);actor.velocity=Vector3.ZERO
		for point in [Vector2(0,z-11),Vector2(5.5,z-11),Vector2(5.5,z+18),Vector2(0,z+18),Vector2(0,z+24)]:await walk(actor,point)
		assert(absf(actor.position.y-float(y))<.12)
		for side in [-1,1]:
			var ray:=PhysicsRayQueryParameters3D.create(Vector3(side*7.5,float(y)+1.5,z),Vector3(side*8.1,float(y)+1.5,z))
			assert(not ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Unsupported lateral exits stay closed")
	print(data.id," STAIRS PASS:16 real switchbacks both ways,17 supported bypasses and intact sidewalls. Destination branches, species and final art unfinished.")
	quit()
