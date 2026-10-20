extends SceneTree
# Bake explicit editable nodes, not an @tool generator. Runtime lift stays separate.
func _initialize() -> void:
	call_deferred("run")
func own(node: Node, scene_root: Node) -> void:
	for child in node.get_children():
		child.owner = scene_root
		own(child,scene_root)
func run() -> void:
	var scene := Node3D.new()
	scene.name = "Royalty790_UpperCandidate"
	scene.set_meta("source_index",790)
	scene.set_meta("status","Candidate only: replace AST-RES-006 once, not additive double-instance")
	scene.set_meta("canonical_placement","World-coordinate source. Position zero; rotation zero; scale one.")
	scene.set_meta("lower_floor_owner","Existing ship floor compiler. Not duplicated in this scene.")
	root.add_child(scene)
	var groups := {}
	for label in ["RetainedArchitecture","UpperGallery","FittedStair","PitlessReceiver","Fixtures","SupportingFrame"]:
		var group := Node3D.new()
		group.name = label
		scene.add_child(group)
		groups[label] = group
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	assert(doc.append_from_file("res://royalty_790_completion_20261020/exports/ROYALTY790_upper_candidate_r002.glb",state)==OK)
	var source := doc.generate_scene(state) as Node3D
	scene.add_child(source)
	for child in source.get_children():
		var label := "RetainedArchitecture"
		var n := String(child.name)
		if n.begins_with("RG_"):
			label = "UpperGallery"
			if "Stair" in n or "MidLanding" in n or "OpeningTrimmer" in n: label = "FittedStair"
			elif "Shaft" in n or "Boarding" in n: label = "PitlessReceiver"
			elif "Lamp" in n: label = "Fixtures"
			elif "Pier" in n or "Rib" in n: label = "SupportingFrame"
		elif n.begins_with("DATUM_RG"): label = "Fixtures"
		child.reparent(groups[label],true)
	source.queue_free()
	await process_frame
	for child in scene.find_children("*","MeshInstance3D",true,false):
		if String(child.name).begins_with("RG_StairFlight_") or String(child.name).begins_with("RG_StairNosing_"): continue
		load("res://scripts/static_contact_cache.gd").attach(child)
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://royalty_790_completion_20261020/evidence/BUILD_RECEIPT.json"))
	for row in data.collision_ramps:
		var body := StaticBody3D.new()
		body.name = row.name + "_WalkingContact"
		var shape := ConvexPolygonShape3D.new()
		var points := PackedVector3Array()
		for p in row.vertices: points.append(Vector3(p[0],p[1],p[2]))
		shape.points = points
		shape.margin = 0.001
		var collision := CollisionShape3D.new()
		collision.shape = shape
		body.add_child(collision)
		groups.FittedStair.add_child(body)
	# Reference-only parked cabin makes the physical fit inspectable in the editor.
	# It has no controller or collision and must be removed when using package.gd.
	var cabin := (load("res://assets/models/AST-CIR-003.glb") as PackedScene).instantiate()
	cabin.name = "ReferenceOnly_ParkedCabin_NoOperation"
	cabin.position = Vector3(101.75,102.2,45.65)
	cabin.rotation.y = PI
	cabin.set_meta("reference_only",true)
	cabin.set_meta("runtime_owner","package.gd uses unchanged moving_lift.gd instead")
	groups.PitlessReceiver.add_child(cabin)
	for marker in scene.find_children("DATUM_*light*","Node3D",true,false):
		var light := OmniLight3D.new()
		light.name = "FixtureLight"
		marker.add_child(light)
		light.omni_range = 5.0
		light.light_energy = 0.65
		light.light_color = Color(1.0,0.91,0.78)
	own(scene,scene)
	var packed := PackedScene.new()
	assert(packed.pack(scene)==OK)
	var path := "res://royalty_790_completion_20261020/Royalty790_UpperCandidate.tscn"
	assert(ResourceSaver.save(packed,path)==OK)
	var reloaded := load(path) as PackedScene
	assert(reloaded != null)
	var reopened := reloaded.instantiate()
	assert(reopened.find_child("RG_UpperGalleryFloor",true,false)!=null)
	assert(reopened.find_child("StairRamp_0_WalkingContact",true,false)!=null)
	var receipt := {"status":"PASS","entry_scene":path,"named_meshes":scene.find_children("*","MeshInstance3D",true,false).size(),"explicit_editable_nodes":true,"generator_required_to_open":false,"runtime_lift_operation":false,"source_original_unchanged":true,"canonical_transform":"Identity","scope":"Editor organization and saved PackedScene reload only"}
	var f := FileAccess.open("res://royalty_790_completion_20261020/evidence/EDITOR_SCENE_CHECK.json",FileAccess.WRITE)
	f.store_string(JSON.stringify(receipt,"\t")+"\n")
	print("ROYALTY_EDITOR_SCENE_PASS ",receipt.named_meshes)
	reopened.free()
	quit()
