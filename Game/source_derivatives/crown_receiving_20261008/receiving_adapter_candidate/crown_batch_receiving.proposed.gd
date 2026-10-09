extends RefCounted
# Isolated candidate. Install only after independent retention and root receiving review.
static func build(crown:Node3D,ship:Node3D)->Node3D:
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/crown_batch/runtime_manifest.json"))
	assert(crown.transform.is_equal_approx(Transform3D.IDENTITY))
	assert(crown.get_node_or_null(str(data.root_name))==null)
	var common:Node3D=crown.get_node("CentralCrownArchitecture")
	assert(str(common.get_meta("catalogue_file"))==str(data.common_model_file))
	assert(FileAccess.get_sha256("res://assets/models/"+str(data.common_model_file))==str(data.common_runtime_sha256))
	assert(data.sections.size()==5)
	var root:=Node3D.new()
	root.name=str(data.root_name)
	root.set_meta("operational_acceptance",false)
	crown.add_child(root)
	var seen:Dictionary={}
	for section in data.sections:
		var programme:=str(section.programme_key)
		assert(programme in ["D18_directory_02","D18_directory_04","D18_directory_05","D18_directory_06","D18_directory_07"])
		assert(not seen.has(programme));seen[programme]=true
		assert(section.position==[0,0,0] and section.rotation==[0,0,0] and section.scale==[1,1,1])
		assert(crown.get_node_or_null("CrownDoor_"+str(section.existing_door.name))!=null)
		assert(FileAccess.get_sha256("res://assets/models/"+str(section.model_file))==str(section.runtime_sha256))
		var room:=Node3D.new()
		room.name=str(section.root_name)
		room.set_meta("programme_key",programme)
		room.set_meta("receiving_hold",str(section.receiving_hold))
		root.add_child(room)
		var model:Node3D=ship.model(room,str(section.model_file),"Source",Vector3.ZERO)
		assert(model.transform.is_equal_approx(Transform3D.IDENTITY))
	return root
