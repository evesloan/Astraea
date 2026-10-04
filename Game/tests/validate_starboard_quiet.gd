extends "res://tests/validate_living_gifts.gd"
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(50):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var nook:Node3D=ship.find_child("D17QuietReadingAlcove",true,false)
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	assert(nook!=null)
	for part in nook.find_children("*","MeshInstance3D",true,false):
		var bounds:AABB=part.global_transform*part.get_aabb()
		assert(bounds.position.x>=63.60 and bounds.end.x<=66.81 and bounds.position.z>=3.24 and bounds.end.z<=6.76 and bounds.end.y<105.201,"Quiet alcove exceeds verified footprint or roof clearance")
	for x in [63.75,65.0,66.65]:
		var query:=PhysicsRayQueryParameters3D.create(Vector3(x,105.202,5),Vector3(x,105.27,5))
		assert(ship.get_world_3d().direct_space_state.intersect_ray(query).is_empty(),"Oval vault must clear existing ceiling and ribs")
	var corners:=0
	for side in [-1,1]:
		for level in range(4):
			for row in range(2):
				var name_suffix:="%s_%s_%s"%[side,level,row]
				var marker:Node3D=nook.find_child("DATUM_book_"+name_suffix,true,false)
				var stock:Node3D=ship.find_child("D17QuietBook_"+name_suffix,true,false)
				for dx in [-.08,.08]:
					for dz in [-.23,.23]:
						var p:Vector3=marker.global_position+Vector3(dz,0,dx)
						var query:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.015,p-Vector3.UP*.015)
						var hit:=ship.get_world_3d().direct_space_state.intersect_ray(query)
						assert(not hit.is_empty() and "QUIET_BookShelf_" in str(hit.collider.get_path()),"Quiet book group lacks shelf support")
				for part in stock.find_children("*","MeshInstance3D",true,false):
					var aabb:AABB=part.get_aabb()
					for i in range(8):
						var p:Vector3=part.global_transform*aabb.get_endpoint(i)
						var query:=PhysicsRayQueryParameters3D.create(marker.global_position+Vector3.UP*.14,p)
						var hit:=ship.get_world_3d().direct_space_state.intersect_ray(query)
						assert(hit.is_empty() or hit.position.distance_to(p)<.009,"Quiet book envelope clips enclosure: %s at %s"%[name_suffix,hit])
						corners+=1
	for i in range(2):
		var seat:Node3D=nook.find_child("DATUM_seat_"+str(i),true,false)
		var query:=PhysicsRayQueryParameters3D.create(seat.global_position+Vector3.UP*.02,seat.global_position-Vector3.UP*.02)
		var hit:=ship.get_world_3d().direct_space_state.intersect_ray(query)
		assert(not hit.is_empty() and "QUIET_SeatCushion" in str(hit.collider.get_path()))
	actor.set_physics_process(false)
	actor.position=Vector3(68.4,102.1,5)
	actor.velocity=Vector3.ZERO
	for i in range(2):
		var approach:Node3D=nook.find_child("DATUM_approach_"+str(i),true,false)
		await walk(actor,Vector2(approach.global_position.x,approach.global_position.z))
		await walk(actor,Vector2(68.4,5))
	assert(abs(actor.position.y-102)<.12,"Level-entry retreat must preserve deck elevation")
	var approach:Node3D=nook.find_child("DATUM_approach_1",true,false)
	await walk(actor,Vector2(approach.global_position.x,approach.global_position.z))
	var control:Node3D=ship.find_child("D17QuietReadingLightSwitch",true,false)
	actor.camera.look_at(control.global_position,Vector3.UP)
	assert(actor.target_from_view()==control and control.diffuser_materials.size()>0,"Quiet light control must be reachable from actual approach")
	control.interact(actor)
	assert(not control.powered and not control.source.visible)
	control.interact(actor)
	print("STARBOARD QUIET PASS: actual level-entry approaches, two cushion contacts,64book support rays,",corners,"book envelope corners, three vault clearance probes and reachable shared light control. Seated animation, species fit, full cart entry and final art pending.")
	main.queue_free()
	await process_frame
	quit()
