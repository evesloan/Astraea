extends SceneTree
# Read imported arrays only, with explicit new scratch output. No editor/import.
var output := ""
func _initialize() -> void: call_deferred("run")
func vector(a: Vector3) -> Array: return [a.x,a.y,a.z]
func run() -> void:
	var args := OS.get_cmdline_user_args()
	for i in range(args.size()):
		if args[i] == "--output" and i+1<args.size(): output=args[i+1]
	assert(output.begins_with("/workspace/scratch/375c2e438292/theater_resume/") and not FileAccess.file_exists(output+".json") and not FileAccess.file_exists(output+".bin"))
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/THEATER_RUNTIME_STAGE001.json"))
	var records: Array = []
	var imports: Dictionary = {}
	var binary := FileAccess.open(output+".bin",FileAccess.WRITE)
	assert(binary != null)
	for file in [data.static_file,data.moving_file,data.prototype_file,data.bridge_file]:
		var path := "res://assets/models/"+str(file)
		assert(FileAccess.get_sha256(path)==data.export_sha256[file])
		var config := ConfigFile.new()
		assert(config.load(path+".import")==OK and config.get_value("params","meshes/force_disable_compression",false))
		var cache := str(config.get_value("remap","path",""))
		var md5 := ConfigFile.new()
		assert(md5.load(cache.get_basename()+".md5")==OK and str(md5.get_value("","source_md5",""))==FileAccess.get_md5(path))
		imports[file] = {"source_sha256":FileAccess.get_sha256(path),"compression_disabled":true,"cache":cache}
		var scene := (load(path)as PackedScene).instantiate() as Node3D
		root.add_child(scene)
		await process_frame
		for item in scene.find_children("*","MeshInstance3D",true,false):
			var mesh := item as MeshInstance3D
			for surface in range(mesh.mesh.get_surface_count()):
				var arrays := mesh.mesh.surface_get_arrays(surface)
				var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
				var normals: PackedVector3Array = arrays[Mesh.ARRAY_NORMAL]
				var uv: PackedVector2Array = arrays[Mesh.ARRAY_TEX_UV]
				var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
				assert(vertices.size()==normals.size() and vertices.size()==uv.size())
				if indices.is_empty():
					for i in range(vertices.size()): indices.append(i)
				var values := PackedFloat32Array()
				var basis := mesh.global_basis.inverse().transposed()
				for index in indices:
					var p := mesh.global_transform*vertices[index]
					var n := (basis*normals[index]).normalized()
					values.append_array(PackedFloat32Array([p.x,p.y,p.z,uv[index].x,uv[index].y,n.x,n.y,n.z]))
				records.append({"file":file,"node":str(mesh.name),"surface":surface,"corners":indices.size(),"offset_bytes":binary.get_position()})
				binary.store_buffer(values.to_byte_array())
		scene.free()
	binary.close()
	var result := {"status":"Imported arrays captured; independent source comparison required","imports":imports,"records":records,"binary_sha256":FileAccess.get_sha256(output+".bin")}
	var receipt := FileAccess.open(output+".json",FileAccess.WRITE)
	receipt.store_string(JSON.stringify(result,"\t"));receipt.close()
	print("THEATER IMPORT PROBE: ",records.size()," surfaces recorded")
	quit(0)
