extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
	for frame in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var environment:Environment=ship.get_node("WorldEnvironment").environment
	assert(environment.background_mode==Environment.BG_SKY and environment.sky!=null)
	assert(environment.sky.sky_material is ShaderMaterial)
	assert(environment.sky.sky_material.shader.resource_path=="res://shaders/astraea_space.gdshader")
	assert(environment.sky.sky_material.get_shader_parameter("use_radiance_cache")==false,"Keep the visually verified direct path until cached sampling is proven")
	assert(environment.sky.process_mode==Sky.PROCESS_MODE_QUALITY and environment.sky.radiance_size==Sky.RADIANCE_SIZE_256)
	assert(environment.sky_rotation==Vector3.ZERO and is_zero_approx(environment.sky_custom_fov))
	assert(environment.ambient_light_source==Environment.AMBIENT_SOURCE_SKY and is_zero_approx(environment.ambient_light_sky_contribution))
	assert(environment.ambient_light_color.is_equal_approx(Color(.75,.81,.86)) and is_equal_approx(environment.ambient_light_energy,.2))
	assert(environment.reflected_light_source==Environment.REFLECTION_SOURCE_DISABLED)
	var space:=ship.get_world_3d().direct_space_state
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/CENTRAL_CROWN_RUNTIME.json"))
	var panes:=0;var contacts:=0
	for window in data.windows:
		var side:float=1 if window.side=="starboard"else -1
		for i in range(window.mullions_z.size()-1):
			var z:float=(window.mullions_z[i]+window.mullions_z[i+1])*.5
			panes+=1
			for y in [107.2,108.1,110.2]:
				var centre:float=lerpf(35.1,35.95,(y-106.95)/(110.55-106.95))
				for outward in [true,false]:
					var start:=Vector3(side*(30 if outward else 38),y,z)
					var finish:=Vector3(side*(38 if outward else 30),y,z)
					var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(start,finish))
					assert(not hit.is_empty(),"Every framed window retains physical glass")
					assert("crown_tinted_glass" in str(hit.collider.get_path()),"Window ray hit an opaque wall/frame instead of its pane")
					assert(absf(absf(hit.position.x)-centre)<.04,"Glass contact follows the authored outward cant")
					var mesh:=hit.collider.get_parent()as MeshInstance3D
					assert(mesh!=null and mesh.material_override is ShaderMaterial,"Runtime glazing keeps the visible glass shader")
					assert(mesh.material_override.shader.resource_path=="res://shaders/hospitality_glass.gdshader")
					contacts+=1
			var view_ray:=PhysicsRayQueryParameters3D.create(Vector3(side*36.1,108.1,z),Vector3(side*130,108.1,z))
			assert(space.intersect_ray(view_ray).is_empty(),"Selected horizontal window view is blocked by current ship geometry")
	assert(panes==16 and contacts==96)
	print("CROWN WINDOWS PASS:16 physical canted panes,96 inside/outside contact rays and16 unobstructed horizontal view axes beyond the present hull width. Visible glass shader is retained. Celestial composition, adjacent future pavilions and final visual quality remain separate review gates.")
	main.queue_free();await process_frame;quit()
