extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
	for frame in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var space:=ship.get_world_3d().direct_space_state
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/BRIDGE_PLATFORM_RUNTIME.json"))
	assert(data.windows.size()==24)
	var contacts:=0;var exterior_axes:=0
	for window in data.windows:
		var b:Array=window.world_aabb
		var centre:=Vector3((b[0]+b[1])*.5,(b[2]+b[3])*.5,(b[4]+b[5])*.5)
		var normal:=Vector3(window.outward_normal[0],window.outward_normal[1],window.outward_normal[2])
		for y in [107.3,108.4,110.1]:
			centre.y=y
			for sign in [-1.0,1.0]:
				var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(centre+normal*sign*.4,centre-normal*sign*.4))
				assert(not hit.is_empty() and "glass" in str(hit.collider.get_path()).to_lower(),"Each pane must retain real closed glass contacts: "+str(window.id))
				var mesh:=hit.collider.get_parent()as MeshInstance3D
				assert(mesh!=null and mesh.material_override is ShaderMaterial and mesh.material_override.shader.resource_path=="res://shaders/hospitality_glass.gdshader")
				contacts+=1
		if str(window.side) in ["port","fore"]:
			centre.y=108.4
			assert(space.intersect_ray(PhysicsRayQueryParameters3D.create(centre+normal*.4,centre+normal*700)).is_empty(),"Designated current exterior view is blocked: "+str(window.id))
			exterior_axes+=1
	assert(contacts==144 and exterior_axes>0)
	print("BRIDGE BYPASS WINDOWS PASS:24 physical panes,144 bidirectional contacts with visible glass shader and",exterior_axes," current outward axes. Aft panes honestly face the bridge frame; moving views, future neighbouring structures and final composition remain separate review gates.")
	main.queue_free();await process_frame;quit()
