extends SceneTree
# Isolated visual evidence only. Run with a display and Compatibility renderer:
# godot --rendering-method gl_compatibility --path Game --script res://scripts/startup_residency_20261020/compare_visual.gd -- manifest.json output_prefix
# No gameplay scene, source asset edits, or collision generation.
var failed := false

func _initialize() -> void:
	call_deferred("run")

func fail(message: String) -> void:
	push_error(message)
	failed = true

func xyz(v: Vector3) -> Array:
	return [v.x, v.y, v.z]

func bounds_of(model: Node3D) -> AABB:
	var result := AABB()
	var first := true
	var nodes: Array[Node] = model.find_children("*", "MeshInstance3D", true, false)
	if model is MeshInstance3D:
		nodes.push_front(model)
	for mesh: MeshInstance3D in nodes:
		if mesh.mesh == null:
			continue
		var box: AABB = mesh.global_transform * mesh.get_aabb()
		result = box if first else result.merge(box)
		first = false
	if first:
		fail("No source mesh bounds")
	return result

func load_model(path: String) -> Node3D:
	var packed: PackedScene = load(path) as PackedScene
	if packed == null:
		fail("Cannot load model: " + path)
		return null
	var model: Node3D = packed.instantiate() as Node3D
	if model == null:
		fail("Model root must be Node3D: " + path)
	return model

func apply_source_policy(model: Node3D, policy: Dictionary) -> void:
	if policy.is_empty():
		return
	var nodes: Array[Node] = model.find_children("*", "MeshInstance3D", true, false)
	if model is MeshInstance3D:
		nodes.push_front(model)
	for mesh: MeshInstance3D in nodes:
		if not policy.has(str(mesh.name)):
			fail("Source mesh absent from collision/material policy: " + str(mesh.name))
			continue
		var spec: Dictionary = policy[str(mesh.name)]
		if str(spec.get("role", "")) == "hospitality_glass":
			var material := ShaderMaterial.new()
			material.shader = load("res://shaders/hospitality_glass.gdshader") as Shader
			mesh.material_override = material
		if str(spec.get("category", "")) == "light_source":
			mesh.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF

func run() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 2:
		fail("Expected bake manifest path and output prefix after --")
		quit(1)
		return
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if not parsed is Dictionary:
		fail("Invalid bake manifest JSON")
		quit(1)
		return
	var manifest: Dictionary = parsed
	var prefix: String = args[1]
	var report_path: String = prefix + "_cameras.json"
	var labels: Array[String] = ["exterior", "interior_a", "interior_b"]
	for variant in ["source", "baked"]:
		for label in labels:
			if FileAccess.file_exists(prefix + "_" + variant + "_" + label + ".png"):
				fail("Refusing to overwrite previous image evidence")
	if FileAccess.file_exists(report_path):
		fail("Refusing to overwrite previous camera report")
	var source_path: String = str(manifest.get("model_file", ""))
	if not source_path.begins_with("res://"):
		source_path = "res://assets/models/" + source_path
	var baked_path: String = str(manifest.get("visual_path", manifest.get("output_scene", "")))
	if FileAccess.get_sha256(source_path) != str(manifest.get("input_sha256", "")):
		fail("Source hash differs from bake manifest")
	if FileAccess.get_sha256(baked_path) != str(manifest.get("visual_sha256", "")):
		fail("Baked visual hash differs from bake manifest")
	if failed:
		quit(1)
		return
	var parent_dir: String = ProjectSettings.globalize_path(prefix.get_base_dir())
	if DirAccess.make_dir_recursive_absolute(parent_dir) != OK:
		fail("Cannot create output directory")
		quit(1)
		return
	root.size = Vector2i(640, 360)
	root.content_scale_size = Vector2i(640, 360)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_VIEWPORT
	root.msaa_3d = Viewport.MSAA_DISABLED
	root.screen_space_aa = Viewport.SCREEN_SPACE_AA_DISABLED
	var stage := Node3D.new()
	stage.name = "IsolatedComparison"
	root.add_child(stage)
	var world := WorldEnvironment.new()
	var environment := Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color(0.18, 0.18, 0.18)
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color.WHITE
	environment.ambient_light_energy = 0.7
	environment.reflected_light_source = Environment.REFLECTION_SOURCE_DISABLED
	environment.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	world.environment = environment
	stage.add_child(world)
	var fill := DirectionalLight3D.new()
	fill.name = "IdenticalUnshadowedFill"
	fill.rotation_degrees = Vector3(-55.0, -30.0, 0.0)
	fill.light_color = Color.WHITE
	fill.light_energy = 0.5
	fill.shadow_enabled = false
	stage.add_child(fill)
	var camera := Camera3D.new()
	camera.fov = 70.0
	camera.near = 0.05
	stage.add_child(camera)
	camera.current = true
	var poses: Array[Dictionary] = []
	var results: Array[Dictionary] = []
	for variant in ["source", "baked"]:
		var path: String = source_path if variant == "source" else baked_path
		var model: Node3D = load_model(path)
		if model == null:
			break
		stage.add_child(model)
		if variant == "source":
			apply_source_policy(model, manifest.get("source_collision_policy", {}))
		if failed:
			model.free()
			break
		var box: AABB = bounds_of(model)
		if variant == "source":
			var center: Vector3 = box.get_center()
			var radius: float = maxf(box.size.length() * 0.5, 1.0)
			var exterior: Vector3 = center + Vector3(1.0, 0.7, 1.0).normalized() * radius / sin(deg_to_rad(camera.fov * 0.5)) * 1.2
			var eye_y: float = box.position.y + 1.6
			var first: Vector3 = Vector3(center.x - box.size.x * 0.2, eye_y, center.z - box.size.z * 0.2)
			var second: Vector3 = Vector3(center.x + box.size.x * 0.2, eye_y, center.z + box.size.z * 0.2)
			poses = [{"name": "exterior", "position": exterior, "target": center}, {"name": "interior_a", "position": first, "target": first + Vector3(0.3, 0.0, 1.0)}, {"name": "interior_b", "position": second, "target": second + Vector3(-0.3, 0.0, -1.0)}]
			camera.far = maxf(radius * 8.0, 1000.0)
		for pose: Dictionary in poses:
			camera.position = pose.position
			camera.look_at(pose.target, Vector3.UP)
			await process_frame
			await process_frame
			await RenderingServer.frame_post_draw
			var screenshot: Image = root.get_texture().get_image()
			var image_path: String = prefix + "_" + str(variant) + "_" + str(pose.name) + ".png"
			if screenshot == null or screenshot.is_empty() or screenshot.save_png(image_path) != OK:
				fail("Could not save viewport image: " + image_path)
				break
			results.append({"variant": variant, "camera": pose.name, "png": image_path, "sha256": FileAccess.get_sha256(image_path), "bounds_min": xyz(box.position), "bounds_max": xyz(box.end)})
			print("VISUAL_COMPARISON_PNG " + image_path)
		model.free()
		await process_frame
		await process_frame
		if failed:
			break
	var camera_rows: Array[Dictionary] = []
	for pose: Dictionary in poses:
		camera_rows.append({"name": pose.name, "position": xyz(pose.position), "target": xyz(pose.target), "up": [0, 1, 0], "fov_degrees": camera.fov, "near": camera.near, "far": camera.far})
	var report := {"schema": "astraea.isolated_visual_comparison.v1", "manifest": args[0], "source": source_path, "baked": baked_path, "viewport": [640, 360], "rendering_method": RenderingServer.get_current_rendering_method(), "ambient_energy": 0.7, "directional_fill_energy": 0.5, "directional_fill_shadows": false, "source_light_defaults_preserved": true, "cameras": camera_rows, "images": results, "status": "CAPTURE_FAILED" if failed else "CAPTURED_REQUIRES_PIXEL_REVIEW", "caveat": "Bounds-derived interior viewpoints are geometric samples, not certified walkable locations. Capture alone is not visual equivalence acceptance."}
	var report_file := FileAccess.open(report_path, FileAccess.WRITE)
	if report_file == null:
		fail("Could not write camera report")
	else:
		report_file.store_string(JSON.stringify(report, "\t") + "\n")
		report_file.close()
		print("VISUAL_COMPARISON_REPORT " + report_path)
	stage.free()
	quit(1 if failed else 0)
