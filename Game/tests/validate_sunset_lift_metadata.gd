extends SceneTree
func _initialize()->void:
	var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/SUNSET_RECEIVING.json"))
	var path:String="res://assets/models/"+str(definition.model_file)
	assert(FileAccess.get_sha256(path)==definition.source_sha256)
	var model:Node3D=load(path).instantiate()
	var meshes:=model.find_children("*","MeshInstance3D",true,false)
	assert(meshes.size()==definition.mesh_count)
	for mesh in meshes:assert(mesh.get_meta("extras").source_plan_sha256==definition.plan_sha256)
	model.free()
	print("SUNSET_FINAL_METADATA PASS: ",meshes.size()," source-bound meshes; geometry binary unchanged from actual-main pass")
	quit()
