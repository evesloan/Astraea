extends SceneTree
const PART=preload("res://remaining_batch_activation_20261026/author_contact_partition.gd")
var baked:Array=[]
var report:={"checks":[],"rooms":[],"failures":[]}
func _initialize()->void:call_deferred("run")
func require(ok:bool,label:String)->void:
	report.checks.append(label)
	if not ok:report.failures.append(label)
func run()->void:
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/REMAINING_BATCH_SECTIONS.json"))
	for item in data.sections:
		require(FileAccess.get_sha256(item.runtime)==item.hash,"Exact source "+str(item.key))
		var source:Node3D=(load(item.runtime) as PackedScene).instantiate();root.add_child(source)
		var meshes:=source.find_children("*","MeshInstance3D",true,false)
		var original:Dictionary={}
		for mesh:MeshInstance3D in meshes:original[mesh.get_instance_id()]={"mesh":mesh.mesh,"pose":mesh.global_transform}
		var start:=Time.get_ticks_usec();PART.attach(source,meshes,str(item.key));var usec:=Time.get_ticks_usec()-start
		var expected:=PackedVector3Array();var independent:=0;var skipped:=0;var error:=0.0
		for mesh:MeshInstance3D in meshes:
			require(mesh.mesh==original[mesh.get_instance_id()].mesh and mesh.global_transform==original[mesh.get_instance_id()].pose,"Original mesh/pose "+str(item.key)+"/"+str(mesh.name))
			var cols:=mesh.find_children("*","CollisionShape3D",true,false)
			if PART.visual_border(mesh,str(item.key)):
				require(cols.is_empty(),"Original visual-border exclusion");skipped+=1;continue
			if not cols.is_empty():
				independent+=1;require(cols.size()==1 and cols[0].shape.get_faces()==mesh.mesh.get_faces(),"Exact independent triangles "+str(mesh.name));continue
			var pose:=source.global_transform.affine_inverse()*mesh.global_transform
			for vertex in mesh.mesh.get_faces():expected.append(pose*vertex)
		var grouped:Node=source.get_node_or_null("RoomStaticContacts/SharedRoomTriangles")
		if expected.size()>0:
			require(grouped!=null,"Grouped contact exists "+str(item.key))
			if grouped!=null:
				var actual:PackedVector3Array=grouped.shape.get_faces();require(actual.size()==expected.size(),"Every original triangle retained "+str(item.key))
				if actual.size()==expected.size():
					for i in range(expected.size()):error=maxf(error,actual[i].distance_to(expected[i]))
				require(error<.0002,"Exact transformed triangle tolerance "+str(item.key))
		if grouped!=null and report.failures.is_empty():
			var target:="res://remaining_batch_activation_20261026/contacts/"+str(item.key)+".res"
			require(not FileAccess.file_exists(target),"Never overwrite retained contact resource")
			if not FileAccess.file_exists(target):
				require(ResourceSaver.save(grouped.shape,target)==OK,"Save exact baked contacts")
				baked.append({"key":item.key,"source":item.runtime,"source_sha256":item.hash,"resource":target,"sha256":FileAccess.get_sha256(target)})
		for name in PART.wall_names(str(item.key)):
			var mesh:Node=source.find_child(name,true,false)
			require(mesh!=null and mesh.find_children("*","CollisionShape3D",true,false).size()==1,"Receiving wall retains mutable contact "+str(name))
		report.rooms.append({"key":item.key,"runtime":item.runtime,"meshes":meshes.size(),"independent":independent,"excluded_original_borders":skipped,"grouped_triangles":expected.size()/3,"max_vertex_error":error,"contact_usec":usec})
		source.free();await process_frame
	var manifest:=FileAccess.open("res://remaining_batch_activation_20261026/contacts/INDEX.json",FileAccess.WRITE);manifest.store_string(JSON.stringify(baked,"\t"));manifest.close()
	var output:=""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--result="):output=arg.substr(9)
	assert(not output.is_empty() and not FileAccess.file_exists(output))
	var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify(report,"\t"));f.close()
	print("CONTACT_EQUIVALENCE rooms=",report.rooms.size()," checks=",report.checks.size()," failures=",report.failures)
	quit(0 if report.failures.is_empty() else 2)
