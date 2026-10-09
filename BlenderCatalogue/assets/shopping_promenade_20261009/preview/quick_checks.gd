extends SceneTree
# One bounded footprint/court loaded at a time. No movement/route/gameplay pass.
var failures: Array = []
var receipts: Array = []
var node_policy: Dictionary
func _initialize() -> void:
	call_deferred("checks")
func checks() -> void:
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://placement.json"))
	node_policy = JSON.parse_string(FileAccess.get_file_as_string("res://node_policy.json"))
	var world := Node3D.new()
	root.add_child(world)
	for row in plan.rooms + plan.chunks:
		if row.get("retained",false): continue
		var cell := Node3D.new()
		cell.name=row.chunk_id
		world.add_child(cell)
		cell.position=Vector3(row.position[0],row.position[1],row.position[2])
		var meshes := 0
		for layer in row.exports:
			var resource := load("res://"+row.exports[layer]) as PackedScene
			if resource == null:
				failures.append({"chunk":row.chunk_id,"failure":"Broken GLB import","layer":layer})
				continue
			var visual := resource.instantiate() as Node3D
			cell.add_child(visual)
			for part in visual.find_children("*","MeshInstance3D",true,false):
				meshes+=1
				if node_policy.get(str(part.name),{}).get("collide",true):part.create_trimesh_collision()
		await physics_frame
		await physics_frame
		var space := world.get_world_3d().direct_space_state
		var probes: Array = []
		if row.has("front_sign_x"):
			var sign_x: float=row.front_sign_x
			for uv in [[0.0,-5.0],[0.0,-3.2],[-3.5,4.5]]:
				probes.append(Vector3(row.position[0]-sign_x*uv[1],52.5,row.position[2]+uv[0]))
		else:
			# Check additive floor triangle centroids rather than retained ownership gaps.
			for floor_row in plan.floor_proposals:
				if floor_row.chunk_id!=row.chunk_id:continue
				var tri: Array=floor_row.triangles_xz[0]
				probes.append(Vector3((tri[0][0]+tri[1][0]+tri[2][0])/3.0,52.5,(tri[0][1]+tri[1][1]+tri[2][1])/3.0))
		var contacts := 0
		var body_clear := 0
		for p: Vector3 in probes:
			var ray := PhysicsRayQueryParameters3D.create(p+Vector3.UP*.15,p-Vector3.UP*.60)
			var hit: Dictionary=space.intersect_ray(ray)
			if hit.is_empty() or absf(hit.position.y-52.5)>.002:
				failures.append({"chunk":row.chunk_id,"failure":"Missing or wrong floor at construction probe","position":[p.x,p.y,p.z]})
			else:contacts+=1
			if row.has("front_sign_x"):
				var capsule := CapsuleShape3D.new()
				capsule.radius=.3
				capsule.height=2.2
				var query := PhysicsShapeQueryParameters3D.new()
				query.shape=capsule
				query.transform=Transform3D(Basis.IDENTITY,p+Vector3.UP*1.102)
				query.margin=0.0
				var hits := space.intersect_shape(query,8)
				if not hits.is_empty():failures.append({"chunk":row.chunk_id,"failure":"Major stationary obstruction","position":[p.x,p.y,p.z],"bodies":hits.size()})
				else:body_clear+=1
		receipts.append({"chunk":row.chunk_id,"imported_meshes":meshes,"floor_contacts":contacts,"stationary_capsule_probes_clear":body_clear})
		cell.queue_free()
		await process_frame
	var result := {"passed":failures.is_empty(),"chunks_checked":receipts.size(),"constructed_room_targets":99,"capsule_reference":{"height_m":2.2,"radius_m":.3,"scope":"Three stationary construction probes per new shop; no route or species/cart acceptance"},"failures":failures,"receipts":receipts,"excluded":"Retained R070 and ten large venues are preserved by byte/hash and allocation checks; no exhaustive reruns"}
	var file := FileAccess.open(ProjectSettings.globalize_path("res://").path_join("../qa/godot_quick_checks.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(result,"\t"))
	file.close()
	print("SHOPPING_QUICK_CHECKS ",result.passed," chunks ",receipts.size()," failures ",failures.size())
	quit(0 if failures.is_empty() else 1)
