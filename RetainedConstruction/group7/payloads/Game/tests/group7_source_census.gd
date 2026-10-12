extends SceneTree

var rows: Array = []
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var main: Node = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	await process_frame
	await physics_frame
	visit(main)
	var out := {"status":"PASS_SOURCE_CENSUS", "baseline":"affc5c807087ff87da29f3642c2d6e418241b896", "meshes":rows, "scope":"Actual initialized retained scene mesh AABBs, including transformed MultiMesh instances. Conservative construction screening; no capacity or route acceptance."}
	var file := FileAccess.open("res://../external_packages/group7_completion_20261011/qa/RETAINED_RUNTIME_CENSUS.json", FileAccess.WRITE)
	file.store_string(JSON.stringify(out,"\t")+"\n")
	print("GROUP7 SOURCE CENSUS PASS: ", rows.size(), " retained mesh bounds")
	quit()
func visit(node: Node) -> void:
	if node is MeshInstance3D and node.mesh != null:
		record(node,node.get_aabb(),node.global_transform)
	elif node is MultiMeshInstance3D and node.multimesh != null and node.multimesh.mesh != null:
		for i in range(node.multimesh.instance_count):
			record(node,node.multimesh.mesh.get_aabb(),node.global_transform*node.multimesh.get_instance_transform(i),i)
	for child in node.get_children(): visit(child)
func record(node: Node3D, box: AABB, pose: Transform3D, index := -1) -> void:
	var world := pose*box
	rows.append({"path":str(node.get_path()), "instance":index, "minimum":[world.position.x,world.position.y,world.position.z], "maximum":[world.end.x,world.end.y,world.end.z]})
