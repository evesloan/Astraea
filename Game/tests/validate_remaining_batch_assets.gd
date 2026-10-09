extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var rows:Array=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/REMAINING_BATCH_SECTIONS.json")).sections
	var results:Array=[]
	for item in rows:
		assert(FileAccess.get_sha256(str(item.runtime))==str(item.hash))
		var resource:PackedScene=ResourceLoader.load(str(item.runtime),"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
		assert(resource!=null)
		var source:Node3D=resource.instantiate()
		var meshes:=source.find_children("*","MeshInstance3D",true,false).size()
		var lights:=source.find_children("*","Light3D",true,false).size()
		assert(meshes==int(item.meshes) and lights==int(item.lights))
		results.append({"key":str(item.key),"meshes":meshes,"imported_lights":lights})
		source.free()
		resource=null
		await process_frame
		print("BATCH_ASSET_PASS ",item.key)
	FileAccess.open("res://artifacts/remaining_batch_assets.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS","assets":results,"scope":"Import identity and counts only; routes and visual review deferred"},"  "))
	quit(0)
