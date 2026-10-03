extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var cache = load("res://scripts/static_contact_cache.gd")
	var mesh: Mesh = BoxMesh.new()
	var a := MeshInstance3D.new()
	var b := MeshInstance3D.new()
	a.mesh = mesh
	b.mesh = mesh
	root.add_child(a)
	root.add_child(b)
	cache.attach(a)
	cache.attach(b)
	assert(a.get_node("StaticContact/SharedShape").shape == b.get_node("StaticContact/SharedShape").shape)
	assert(cache.live_shape_count()==1 and cache.shapes_reused==1)
	a.queue_free()
	b.queue_free()
	mesh = null
	await process_frame
	await process_frame
	assert(cache.live_shape_count()==0,"Collision cache must not pin unloaded geometry")
	print("CACHE PASS: identical mesh instances share contact shape; unloaded contacts are released")
	quit(0)
