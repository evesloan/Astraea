extends SceneTree
var BASELINE: String = get_script().resource_path.get_base_dir().path_join("baseline_private_detail.gd")
const CANDIDATE := "res://scripts/startup_residency_20261020/private_detail_residency.gd"
func _initialize() -> void: call_deferred("run")
func digest(bytes: PackedByteArray) -> String:
	var h := HashingContext.new()
	h.start(HashingContext.HASH_SHA256)
	h.update(bytes)
	return h.finish().hex_encode()
func signature(value: Variant, depth: int = 0) -> Variant:
	if value == null: return null
	if value is Texture2D:
		var img: Image = value.get_image()
		return {"type":value.get_class(),"path":value.resource_path,"pixels":digest(img.get_data()) if img != null else "none"}
	if value is Shader: return {"shader":value.code}
	if value is Resource:
		assert(depth < 8, "Unexpected material resource cycle")
		var props: Dictionary = {"class":value.get_class()}
		for property in value.get_property_list():
			var key: String = property.name
			if int(property.usage) & PROPERTY_USAGE_STORAGE and key not in ["resource_name","resource_path","resource_local_to_scene"]:
				props[key] = signature(value.get(key), depth + 1)
		return props
	if value is Array:
		var a: Array = []
		for v in value: a.append(signature(v, depth + 1))
		return a
	if value is Dictionary:
		var d: Dictionary = {}
		for k in value: d[str(k)] = signature(value[k], depth + 1)
		return d
	return var_to_str(value)
func fingerprint(node: Node3D) -> Dictionary:
	var meshes: Dictionary = {}
	var contacts: Dictionary = {}
	for m: MeshInstance3D in node.find_children("*", "MeshInstance3D", true, false):
		if m.mesh == null: continue
		var materials: Array = []
		for s in m.mesh.get_surface_count(): materials.append(signature(m.get_active_material(s)))
		meshes[str(node.get_path_to(m))] = {"faces":digest(m.mesh.get_faces().to_byte_array()),"pose":var_to_str(m.global_transform),"materials":materials,"layers":m.layers,"shadow":m.cast_shadow,"visible":m.visible}
	for c: CollisionShape3D in node.find_children("*", "CollisionShape3D", true, false):
		contacts[str(node.get_path_to(c))] = {"faces":digest(c.shape.get_faces().to_byte_array()),"pose":var_to_str(c.global_transform),"margin":c.shape.margin,"disabled":c.disabled,"layer":c.get_parent().collision_layer,"mask":c.get_parent().collision_mask}
	return {"meshes":meshes,"contacts":contacts}
func run() -> void:
	var index: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/startup_residency_20261020/private_shells.json")).rooms
	var record: Dictionary = {}
	for row: Dictionary in index.values():
		if str(row.room_id) == "AST-UNIT-D13-f1b81969c5730258": record = row
	assert(not record.is_empty())
	var cache: Script = load("res://scripts/static_contact_cache.gd")
	var initial_live: int = cache.live_shape_count()
	var reference: Dictionary = {}
	var results: Array = []
	for script_path in [BASELINE, CANDIDATE]:
		var manager: Node = load(script_path).new()
		root.add_child(manager)
		manager.set_physics_process(false)
		for cycle in range(3):
			var home := Node3D.new()
			home.name = str(record.room_id)
			home.transform = Transform3D(Basis(Vector3.UP, 0.17), Vector3(20,52,-5))
			root.add_child(home)
			var entry := {"home":weakref(home),"record":record,"detail":null,"hidden":0.0,"bounds":AABB()}
			manager.entries.clear()
			manager.entries.append(entry)
			var before: int = cache.contacts_created
			var started := Time.get_ticks_usec()
			manager.prepare_position(Vector3.ZERO)
			var elapsed_us := Time.get_ticks_usec() - started
			assert(is_instance_valid(entry.detail))
			var current := fingerprint(entry.detail)
			if reference.is_empty(): reference = current
			assert(current == reference, "Final material/geometry/contact/identity mismatch")
			var created: int = cache.contacts_created - before
			manager._release_entry(entry)
			assert(entry.detail == null)
			assert(cache.live_shape_count() == initial_live, "Live collision shape retained after release")
			results.append({"candidate":script_path==CANDIDATE,"cycle":cycle,"contacts_created":created,"activation_us":elapsed_us,"live_shapes_after_release":cache.live_shape_count()})
			home.free()
		manager.free()
	for i in range(3): assert(results[i+3].contacts_created < results[i].contacts_created)
	var result := {"status":"PASS","room_id":record.room_id,"model_file":record.model_file,"cycles_each":3,"identical_final_geometry_materials_contacts":true,"live_shapes_returned":true,"baseline_signature_sha256":digest(var_to_bytes(reference)),"results":results,"scheduler_visibility_flags_changed":false,"headless_cloud_timings_not_fps":true,"full_ship_tested":false,"crash_resolved":false}
	var file := FileAccess.open(OS.get_environment("ASTRAEA_CONTACT_CHECK_OUTPUT"),FileAccess.WRITE)
	file.store_string(JSON.stringify(result,"  ")+"\n")
	file.close()
	print("PRIVATE_SINGLE_PASS ",JSON.stringify(result))
	quit(0)
