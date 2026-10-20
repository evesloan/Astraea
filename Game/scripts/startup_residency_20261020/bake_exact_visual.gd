extends SceneTree
# Offline additive bake. Run in one isolated engine process per model:
# godot --headless --path Game --script res://scripts/startup_residency_20261020/bake_exact_visual.gd -- config.json
# Config: {"model_file":"res://assets/models/example.glb", "output_basename":"example", "keep_mesh_names":[]}
# Optional keep_mesh_paths disambiguates repeated names. Never edits the input.
const CELL := 32.0
const VISUAL_DIR := "res://assets/runtime/startup_residency_20261020/"
const REPORT_DIR := "res://data/architecture/startup_residency_20261020/"
const DRAW_PROPERTIES := ["layers", "cast_shadow", "extra_cull_margin", "gi_mode", "ignore_occlusion_culling", "visibility_range_begin", "visibility_range_end", "visibility_range_begin_margin", "visibility_range_end_margin", "visibility_range_fade_mode", "transparency", "sorting_offset", "sorting_use_aabb_center", "material_overlay"]
var failed := false
var owned_resources: Dictionary = {}
var source_model_path := ""

func stop(message: String) -> void:
	push_error(message)
	failed = true

func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() < 1 or args.size() > 2:
		stop("Expected configuration JSON path and optional model_file after --")
		quit(1)
		return
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if not parsed is Dictionary:
		stop("Invalid configuration JSON")
		quit(1)
		return
	if parsed.has("models"):
		if args.size() != 2:
			stop("models configuration requires a model_file selector as the second argument")
		else:
			var matched := false
			for model in parsed.models:
				if str(model.model_file) == args[1]:
					matched = true
					bake(model)
					break
			if not matched:
				stop("No matching model_file in configuration")
	else:
		bake(parsed)
	quit(1 if failed else 0)

func vec(v: Vector3) -> Array:
	return [v.x, v.y, v.z]

func pose_json(t: Transform3D) -> Dictionary:
	return {"basis_columns": [vec(t.basis.x), vec(t.basis.y), vec(t.basis.z)], "origin": vec(t.origin)}

func box_json(b: AABB) -> Dictionary:
	return {"min": vec(b.position), "max": vec(b.end)}

func relative_pose(node: Node3D, root: Node3D) -> Transform3D:
	# The source scene root's own transform is part of the authored model.
	var result := node.transform
	var cursor := node.get_parent()
	while cursor != null:
		if cursor is Node3D:
			result = cursor.transform * result
		if cursor == root:
			break
		cursor = cursor.get_parent()
	return result

func source_visible(node: Node3D, root: Node3D) -> bool:
	var cursor: Node = node
	while cursor != null:
		if cursor is Node3D and not cursor.visible:
			return false
		if cursor == root:
			break
		cursor = cursor.get_parent()
	return true

func cell_key(point: Vector3) -> String:
	return "%d_%d_%d" % [floori(point.x / CELL), floori(point.y / CELL), floori(point.z / CELL)]

func metadata_json(node: Node) -> Dictionary:
	var result: Dictionary = {}
	for key in node.get_meta_list():
		# Variant strings retain type information without serializing live Objects.
		result[str(key)] = var_to_str(node.get_meta(key))
	return result

func drawing_state(node: MeshInstance3D, root: Node3D) -> Dictionary:
	var result: Dictionary = {"visible": source_visible(node, root)}
	for property in DRAW_PROPERTIES:
		result[property] = node.get(property)
	return result

func drawing_key(state: Dictionary) -> String:
	var parts: Array[String] = []
	for key in state:
		var value = state[key]
		parts.append(str(key) + "=" + (str(value.get_instance_id()) if value is Resource else var_to_str(value)))
	return "|".join(parts)

func copy_drawing(node: MeshInstance3D, state: Dictionary) -> void:
	for key in state:
		node.set(key, state[key])

func own_children(node: Node, owner_node: Node) -> void:
	for child in node.get_children():
		child.owner = owner_node
		own_children(child, owner_node)

func own_value(value):
	if value is Resource:
		return own_resource(value)
	if value is Array:
		var copied: Array = value.duplicate()
		for i in range(copied.size()):
			copied[i] = own_value(copied[i])
		return copied
	if value is Dictionary:
		var copied: Dictionary = value.duplicate()
		for key in copied:
			copied[key] = own_value(copied[key])
		return copied
	return value

func own_resource(resource: Resource) -> Resource:
	if resource == null:
		return null
	if resource is Shader and not resource.resource_path.is_empty() and resource.resource_path.ends_with(".gdshader"):
		return resource # Preserve the named glass shader contract used by lighting rays.
	var identity := resource.get_instance_id()
	if owned_resources.has(identity):
		return owned_resources[identity]
	if resource is Texture2D:
		# Standalone imported textures remain legitimate external references.
		# GLB-owned textures must not refer back to a scene subresource table.
		var reference := resource.resource_path
		if not reference.is_empty() and not reference.contains("::") and reference != source_model_path:
			return resource
		var pixels: Image = resource.get_image()
		if pixels == null or pixels.is_empty():
			stop("Could not detach imported texture: " + reference)
			return null
		if pixels.is_compressed() and pixels.decompress() != OK:
			stop("Could not decompress imported texture: " + reference)
			return null
		var texture := ImageTexture.create_from_image(pixels)
		texture.resource_name = resource.resource_name
		owned_resources[identity] = texture
		return texture
	var copied := resource.duplicate(false)
	if copied == null:
		stop("Could not duplicate imported resource: " + resource.resource_path)
		return null
	copied.resource_path = ""
	owned_resources[identity] = copied
	for property in resource.get_property_list():
		if int(property.usage) & PROPERTY_USAGE_STORAGE == 0:
			continue
		var key := str(property.name)
		if key in ["resource_path", "resource_local_to_scene", "resource_name", "script"]:
			continue
		var value = resource.get(key)
		if value is Resource or value is Array or value is Dictionary:
			copied.set(key, own_value(value))
	if copied is ArrayMesh:
		for surface in range(copied.get_surface_count()):
			copied.surface_set_material(surface, own_resource(resource.surface_get_material(surface)))
	return copied

func fallback_reason(node: MeshInstance3D, transform: Transform3D) -> String:
	var basis := transform.basis
	var lengths := Vector3(basis.x.length(), basis.y.length(), basis.z.length())
	var magnitude := maxf(lengths.x, maxf(lengths.y, lengths.z))
	var epsilon := maxf(0.000001, magnitude * 0.00001)
	if basis.determinant() <= 0.0:
		return "nonpositive_basis_determinant"
	if absf(lengths.x - lengths.y) > epsilon or absf(lengths.x - lengths.z) > epsilon:
		return "nonuniform_scale"
	var unit := basis.orthonormalized()
	if not (basis.x / lengths.x).is_equal_approx(unit.x) or not (basis.y / lengths.y).is_equal_approx(unit.y) or not (basis.z / lengths.z).is_equal_approx(unit.z):
		return "sheared_basis"
	if node.material_overlay != null:
		return "material_overlay"
	if node.transparency != 0.0:
		return "per_instance_transparency"
	for surface in range(node.mesh.get_surface_count()):
		var material := node.get_active_material(surface)
		if material is ShaderMaterial:
			return "shader_local_coordinate_semantics"
		if material is BaseMaterial3D:
			if material.transparency != BaseMaterial3D.TRANSPARENCY_DISABLED or material.albedo_color.a < 0.999:
				return "transparent_object_sorting"
			if material.uv1_triplanar or material.uv2_triplanar:
				return "triplanar_local_coordinate_semantics"
			if material.billboard_mode != BaseMaterial3D.BILLBOARD_DISABLED or material.grow:
				return "vertex_displacement_semantics"
	return ""

func bake(config: Dictionary) -> void:
	var path := str(config.get("model_file", ""))
	if not path.begins_with("res://"):
		path = "res://assets/models/" + path
	source_model_path = path
	var basename := str(config.get("output_basename", path.get_file().get_basename() + "_r002"))
	if basename.is_empty() or basename != basename.validate_filename() or basename.contains("/") or basename.contains("\\"):
		stop("Invalid output_basename")
		return
	var output_path := VISUAL_DIR + basename + ".scn"
	var report_path := REPORT_DIR + basename + ".json"
	if FileAccess.file_exists(output_path) or FileAccess.file_exists(report_path):
		stop("Refusing to overwrite a previous bake: " + basename)
		return
	var input_hash := FileAccess.get_sha256(path)
	if input_hash.is_empty():
		stop("Input is missing: " + path)
		return
	var packed := load(path) as PackedScene
	if packed == null:
		stop("Input is not a PackedScene")
		return
	var source := packed.instantiate() as Node3D
	if source == null:
		stop("Input scene root must be Node3D")
		return
	var output := Node3D.new()
	output.name = basename.validate_node_name()
	var bins: Dictionary = {}
	var collisions: Dictionary = {}
	var transparent_contacts: Array = []
	var rows: Array = []
	var lights: Array = []
	var total_triangles := 0
	var kept_triangles := 0
	var merged_triangles := 0
	var mesh_nodes: Array[Node] = source.find_children("*", "MeshInstance3D", true, false)
	if source is MeshInstance3D:
		mesh_nodes.push_front(source)
	for node: MeshInstance3D in mesh_nodes:
		if node.mesh == null:
			continue
		var policy: Dictionary = config.get("collision_policy", {})
		if not policy.is_empty():
			assert(policy.has(str(node.name)), "Private visual policy missing source mesh")
			var spec: Dictionary = policy[str(node.name)]
			if str(spec.get("role", "")) == "hospitality_glass":
				var glass_material := ShaderMaterial.new()
				glass_material.shader = load("res://shaders/hospitality_glass.gdshader")
				node.material_override = glass_material
			if str(spec.get("category", "")) == "light_source":
				node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		var source_path := str(source.get_path_to(node))
		var transform := source.transform if node == source else relative_pose(node, source)
		var state := drawing_state(node, source)
		var row := {"source_path": source_path, "source_name": str(node.name), "transform": pose_json(transform), "metadata": metadata_json(node), "batches": [], "triangles": 0}
		var keep: bool = str(node.name) in config.get("keep_mesh_names", []) or source_path in config.get("keep_mesh_paths", []) or (not policy.is_empty() and str(policy[str(node.name)].get("category", "")) == "light_source")
		if node.skin != null or node.mesh.get_blend_shape_count() > 0:
			stop("Skinned/blend-shaped mesh requires an explicit implementation: " + source_path)
			break
		if absf(transform.basis.determinant()) < 0.00000001:
			stop("Singular source transform: " + source_path)
			break
		var reason := fallback_reason(node, transform)
		if not reason.is_empty():
			keep = true
			row["kept_fallback_reason"] = reason
		var kept: MeshInstance3D = null
		if keep:
			kept = MeshInstance3D.new()
			kept.name = node.name
			# Stable path containers avoid renaming duplicate fixture node names.
			var holder := Node3D.new()
			holder.name = "KeptSource_%06d" % rows.size()
			output.add_child(holder)
			holder.add_child(kept)
			kept.mesh = own_resource(node.mesh) as Mesh
			kept.transform = transform
			copy_drawing(kept, state)
			kept.material_override = own_resource(node.material_override) as Material
			kept.material_overlay = own_resource(node.material_overlay) as Material
			for s in range(node.mesh.get_surface_count()):
				kept.set_surface_override_material(s, own_resource(node.get_surface_override_material(s)) as Material)
			for key in node.get_meta_list():
				kept.set_meta(key, own_value(node.get_meta(key)))
			row.batches.append(str(output.get_path_to(kept)))
		for surface in range(node.mesh.get_surface_count()):
			if not node.mesh is ArrayMesh or (node.mesh as ArrayMesh).surface_get_primitive_type(surface) != Mesh.PRIMITIVE_TRIANGLES:
				stop("Only ArrayMesh triangle surfaces are supported: " + source_path)
				break
			var arrays := node.mesh.surface_get_arrays(surface)
			var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX] if arrays[Mesh.ARRAY_INDEX] != null else PackedInt32Array()
			var count := indices.size() if not indices.is_empty() else vertices.size()
			if count % 3 != 0:
				stop("Incomplete triangle: " + source_path)
				break
			row.triangles += count / 3
			total_triangles += count / 3
			if keep:
				kept_triangles += count / 3
				continue
			for channel in [Mesh.ARRAY_CUSTOM0, Mesh.ARRAY_CUSTOM1, Mesh.ARRAY_CUSTOM2, Mesh.ARRAY_CUSTOM3, Mesh.ARRAY_BONES, Mesh.ARRAY_WEIGHTS]:
				if arrays[channel] != null and not arrays[channel].is_empty():
					stop("Unsupported custom/skinning vertex channel: " + source_path)
			if failed:
				break
			var material := node.get_active_material(surface)
			var common_key := (str(material.get_instance_id()) if material != null else "null") + ":" + drawing_key(state) + ":" + str((node.mesh as ArrayMesh).surface_get_format(surface))
			var chunks: Dictionary = {}
			for start in range(0, count, 3):
				var a := indices[start] if not indices.is_empty() else start
				var b := indices[start + 1] if not indices.is_empty() else start + 1
				var c := indices[start + 2] if not indices.is_empty() else start + 2
				var cell := cell_key(transform * ((vertices[a] + vertices[b] + vertices[c]) / 3.0))
				if not chunks.has(cell):
					chunks[cell] = PackedInt32Array()
				var chunk: PackedInt32Array = chunks[cell]
				chunk.append(a)
				chunk.append(b)
				chunk.append(c)
				chunks[cell] = chunk
			for cell in chunks:
				var key: String = str(cell) + ":" + common_key
				if not bins.has(key):
					var tool := SurfaceTool.new()
					tool.begin(Mesh.PRIMITIVE_TRIANGLES)
					tool.set_material(own_resource(material) as Material)
					bins[key] = {"tool": tool, "state": state, "name": "ExactBatch_%06d" % bins.size(), "triangles": 0}
				var batch: Dictionary = bins[key]
				var slice: Array = arrays.duplicate()
				slice[Mesh.ARRAY_INDEX] = chunks[cell]
				var temporary := ArrayMesh.new()
				temporary.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, slice)
				# append_from copies vertex buffers, not only referenced vertices.
				# Deindex first so a spatial slice cannot copy the whole source
				# vertex buffer once for every cell it touches.
				var compact := SurfaceTool.new()
				compact.create_from(temporary, 0)
				compact.deindex()
				var compact_mesh := compact.commit()
				batch.tool.append_from(compact_mesh, 0, transform)
				batch.triangles += chunks[cell].size() / 3
				merged_triangles += chunks[cell].size() / 3
				if not batch.name in row.batches:
					row.batches.append(batch.name)
		if failed:
			break
		# Match ship._static_contacts: local visible, not ancestor visibility.
		# Exclude descendants of StaticBody3D because the original recursion skips them.
		var blocked := false
		var ancestor := node.get_parent()
		while ancestor != null:
			if ancestor is StaticBody3D:
				blocked = true
			if ancestor == source:
				break
			ancestor = ancestor.get_parent()
		var transparent_contact := false
		if kept != null and node.mesh.get_surface_count() > 0:
			var first_material := node.get_active_material(0)
			transparent_contact = (first_material is StandardMaterial3D and first_material.transparency != BaseMaterial3D.TRANSPARENCY_DISABLED) or (first_material is ShaderMaterial and first_material.shader != null and "glass" in first_material.shader.resource_path)
		var collide: bool = bool(policy[str(node.name)].collide) if not policy.is_empty() else (node.visible and not str(node.name).begins_with("ALC_VisualFloor") and not blocked)
		if collide and transparent_contact:
			# Retain per-mesh glass ancestry used by the unchanged lighting visibility rays.
			var glass_body := StaticBody3D.new()
			glass_body.name = "StaticContact"
			var glass_collider := CollisionShape3D.new()
			glass_collider.name = "SharedShape"
			var glass_shape := ConcavePolygonShape3D.new()
			glass_shape.set_faces(node.mesh.get_faces())
			glass_collider.shape = glass_shape
			glass_body.add_child(glass_collider)
			kept.add_child(glass_body)
			transparent_contacts.append({"source_path":source_path,"output_mesh_path":str(output.get_path_to(kept)),"triangles":node.mesh.get_faces().size()/3})
		if collide and not transparent_contact:
			var bounds: AABB = transform * node.get_aabb()
			var cell := cell_key(bounds.get_center())
			if not collisions.has(cell):
				collisions[cell] = {"faces": PackedVector3Array(), "bounds": bounds, "sources": []}
			var collision: Dictionary = collisions[cell]
			var faces: PackedVector3Array = collision.faces
			# Preserve legacy mesh-local snapping BEFORE transforming to output root.
			var original_faces := node.mesh.get_faces()
			for vertex in original_faces:
				faces.append(transform * vertex)
			collision.faces = faces
			collision.bounds = collision.bounds.merge(bounds)
			collision.sources.append(source_path)
		rows.append(row)
	if failed:
		source.free()
		output.free()
		return
	for key in bins:
		var batch: Dictionary = bins[key]
		var visual := MeshInstance3D.new()
		visual.name = batch.name
		visual.mesh = batch.tool.commit()
		var output_arrays := visual.mesh.surface_get_arrays(0)
		var output_indices: PackedInt32Array = output_arrays[Mesh.ARRAY_INDEX] if output_arrays[Mesh.ARRAY_INDEX] != null else PackedInt32Array()
		var output_vertices: PackedVector3Array = output_arrays[Mesh.ARRAY_VERTEX]
		var output_count := output_indices.size() if not output_indices.is_empty() else output_vertices.size()
		if output_count != int(batch.triangles) * 3:
			stop("Committed batch triangle count mismatch: " + str(batch.name))
		copy_drawing(visual, batch.state)
		output.add_child(visual)
	var light_nodes: Array[Node] = source.find_children("*", "Light3D", true, false)
	if source is Light3D:
		light_nodes.push_front(source)
	for light: Light3D in light_nodes:
		var copied := light.duplicate(0) as Light3D
		for child in copied.get_children():
			child.free()
		var holder := Node3D.new()
		holder.name = "SourceLight_%06d" % lights.size()
		output.add_child(holder)
		holder.add_child(copied)
		copied.transform = source.transform if light == source else relative_pose(light, source)
		copied.visible = source_visible(light, source)
		for property in copied.get_property_list():
			if int(property.usage) & PROPERTY_USAGE_STORAGE != 0 and copied.get(property.name) is Resource:
				copied.set(property.name, own_resource(copied.get(property.name)))
		lights.append({"source_path": str(source.get_path_to(light)), "output_path": str(output.get_path_to(copied)), "source_name": str(light.name), "transform": pose_json(copied.transform), "metadata": metadata_json(light)})
	if failed or total_triangles != kept_triangles + merged_triangles:
		stop("Triangle accounting mismatch")
		source.free()
		output.free()
		return
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(VISUAL_DIR))
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(REPORT_DIR))
	var collision_rows: Array = []
	# Check ALL destinations before writing any artifact.
	for cell in collisions:
		if FileAccess.file_exists(VISUAL_DIR + basename + "_collision_" + str(cell) + ".res"):
			stop("Collision destination already exists")
	if failed:
		source.free()
		output.free()
		return
	for cell in collisions:
		var collision: Dictionary = collisions[cell]
		var shape := ConcavePolygonShape3D.new()
		shape.set_faces(collision.faces)
		var shape_path := VISUAL_DIR + basename + "_collision_" + str(cell) + ".res"
		if ResourceSaver.save(shape, shape_path) != OK:
			stop("Could not save collision resource: " + shape_path)
			break
		collision_rows.append({"id": cell, "cell": cell, "bounds_min": vec(collision.bounds.position), "bounds_max": vec(collision.bounds.end), "path": shape_path, "sha256": FileAccess.get_sha256(shape_path), "aabb": box_json(collision.bounds), "triangles": collision.faces.size() / 3, "source_paths": collision.sources})
	if not failed:
		own_children(output, output)
		var scene := PackedScene.new()
		if scene.pack(output) != OK or ResourceSaver.save(scene, output_path) != OK:
			stop("Could not save bundled output scene")
	if not failed:
		var report := {"schema": "astraea.startup_exact_visual.v1", "model_file": path, "input_sha256": input_hash, "output_scene": output_path, "visual_path": output_path, "visual_sha256": FileAccess.get_sha256(output_path), "output_sha256": FileAccess.get_sha256(output_path), "cell_size_m": CELL, "input_triangles": total_triangles, "output_triangles": kept_triangles + merged_triangles, "kept_triangles": kept_triangles, "merged_triangles": merged_triangles, "source_to_batch": rows, "lights": lights, "collision_cells": collision_rows, "retained_transparent_contacts": transparent_contacts, "source_collision_policy":config.get("collision_policy",{}), "collision_policy": "ship._static_contacts; mesh-local get_faces before transform; default ConcavePolygonShape3D margin", "resource_persistence": "pathless owned meshes and materials; GLB textures detached as ImageTexture; default ResourceSaver flags", "validation": "offline bake only; runtime visual, contact and importer validation still required"}
		var report_file := FileAccess.open(report_path, FileAccess.WRITE)
		if report_file == null:
			stop("Could not save report")
		else:
			report_file.store_string(JSON.stringify(report, "\t") + "\n")
			report_file.close()
			print("EXACT_BAKE_REPORT " + report_path)
	source.free()
	output.free()
