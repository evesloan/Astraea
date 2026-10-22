extends SceneTree
const P := "res://night_garden_warm_interiors_20261022/"
func _initialize() -> void: call_deferred("run")
func own(node: Node, top: Node) -> void:
	for child in node.get_children(): child.owner=top;own(child,top)
func run() -> void:
	var build:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/BUILD.json"))
	assert(build.rooms.size()==16)
	var original:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://night_garden_panoramic_suites_20261022/evidence/INDEX.json"))
	var records:Dictionary={}
	for row in build.rooms:
		var record:Dictionary=original[row.model_file].duplicate(true)
		assert(FileAccess.get_sha256(record.shell_path)==record.shell_sha256 and FileAccess.get_sha256(record.detail_path)==record.detail_sha256)
		assert(FileAccess.get_sha256("res://"+row.export)==row.export_sha256)
		var doc:=GLTFDocument.new();var state:=GLTFState.new();assert(doc.append_from_file("res://"+row.export,state)==OK)
		var source:Node3D=doc.generate_scene(state);root.add_child(source)
		for kind in ["shell","detail"]:
			var target:Node3D=load(str(record[kind+"_path"])).instantiate();root.add_child(target)
			var paths:Array=record[kind+"_mesh_paths"]
			for path in paths:
				var old:MeshInstance3D=target.get_node(str(path))
				var replacement:MeshInstance3D=source.find_child(str(old.name),true,false)
				assert(replacement!=null and replacement.mesh!=null)
				old.mesh=replacement.mesh;old.global_transform=replacement.global_transform
			for name in row.finish_meshes:
				if kind=="detail":
					var placeholder:=MeshInstance3D.new();placeholder.name=str(name);target.add_child(placeholder)
					continue
				var from:MeshInstance3D=source.find_child(str(name),true,false);assert(from!=null)
				var added:MeshInstance3D=from.duplicate();target.add_child(added);added.global_transform=from.global_transform
				paths.append(str(target.get_path_to(added)))
			if kind=="detail":
				var bounds:=AABB();var first:=true
				for mesh:MeshInstance3D in target.find_children("*","MeshInstance3D",true,false):
					if mesh.mesh==null:continue
					var box:AABB=mesh.global_transform*mesh.get_aabb();bounds=box if first else bounds.merge(box);first=false
				record.detail_bounds_min=[bounds.position.x,bounds.position.y,bounds.position.z]
				record.detail_bounds_max=[bounds.end.x,bounds.end.y,bounds.end.z]
			own(target,target)
			var packed:=PackedScene.new();assert(packed.pack(target)==OK)
			var destination:String=P+"runtime/NG"+str(int(row.index))+"_"+str(kind)+"_r001.scn"
			assert(not FileAccess.file_exists(destination));assert(ResourceSaver.save(packed,destination)==OK)
			record[kind+"_path"]=destination;record[kind+"_sha256"]=FileAccess.get_sha256(destination)
			record[kind+"_mesh_paths"]=paths
			target.free()
		record.panoramic_source_export_sha256=row.export_sha256
		record.panoramic_native_sha256=row.native_sha256
		records[row.model_file]=record;source.free()
	var file:=FileAccess.open(P+"evidence/INDEX.json",FileAccess.WRITE);file.store_string(JSON.stringify(records,"\t")+"\n");file.close()
	print("WARM_INTERIOR_PARTITIONS 16 shells and16 details; original60 scenes preserved")
	quit()
