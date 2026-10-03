extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var main := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(25): await physics_frame
	var ship: Node3D=main.get_node("World360/Astraea")
	var state=ship.get_world_3d().direct_space_state
	for name in ["bath_vanity","bath_wc","bath_shower"]:
		var fixture:=ship.find_child(name,true,false) as Node3D
		assert(fixture!=null)
		var position_marker:=fixture.find_child("DATUM_standing",true,false) as Node3D
		assert(ship.arrive_at(position_marker.global_position+Vector3.UP*.1,0),"Fixture needs a usable body approach: "+name)
		for mesh in fixture.find_children("*","MeshInstance3D",true,false):
			for corner in range(8):
				var p:Vector3=mesh.global_transform*mesh.get_aabb().get_endpoint(corner)
				assert(p.x>=77.95 and p.x<=81.84 and p.z>=-41.31 and p.z<=-38.49 and p.y>=83.99 and p.y<86.60,"Fixture must stay inside the existing bathroom volume")
	var vanity:=ship.find_child("bath_vanity",true,false) as Node3D
	var drain:=vanity.find_child("DATUM_drain",true,false) as Node3D
	var hit:=state.intersect_ray(PhysicsRayQueryParameters3D.create(drain.global_position+Vector3.UP*.22,drain.global_position-Vector3.UP*.03))
	assert(not hit.is_empty() and absf(hit.position.y-drain.global_position.y)<.01,"Basin must remain genuinely hollow to its authored bottom")
	var shower:=ship.find_child("bath_shower",true,false) as Node3D
	for reverse in [false,true]:
		var a:=shower.to_global(Vector3(-.75,1,0))
		var b:=shower.to_global(Vector3(-.45,1,0))
		hit=state.intersect_ray(PhysicsRayQueryParameters3D.create(b if reverse else a,a if reverse else b))
		assert(not hit.is_empty() and str(hit.collider.get_parent().name).contains("bath_glass"),"Shower screen blocks from both sides")
	print("GUEST WASH PASS: three usable fixture approaches, bathroom/headroom fit, hollow basin and two-sided shower screen. Water, flushing, mirror reflections, lids and species use are not implemented.")
	main.queue_free()
	await process_frame
	quit()
