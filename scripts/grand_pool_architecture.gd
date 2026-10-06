extends RefCounted
# Independently checked source derivatives, added without replacing the old pool.
const CONTRACT := "res://data/architecture/GRAND_POOL_ARCHITECTURE_RUNTIME.json"

static func xyz(p: Array) -> Vector3: return Vector3(p[0],p[1],p[2])

static func build(parent: Node3D, ship: Node3D) -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	assert(parent.get_node_or_null("GrandPoolArchitecture_WIP") == null)
	for key in data.models:
		var spec: Dictionary = data.models[key]
		assert(FileAccess.get_sha256("res://assets/models/"+str(spec.file)) == spec.sha256)
	var root := Node3D.new()
	root.name = "GrandPoolArchitecture_WIP"
	root.set_meta("persistent_id","grand_pool_architecture_003")
	root.set_meta("scope","Checked wet loggias, focal end and roof; planting, market thresholds and native light readability remain under review")
	parent.add_child(root)
	for entry in data.assemblies:
		var item: Node3D = ship.model(root,str(entry.model_file),str(entry.name),Vector3.ZERO)
		var spec: Dictionary = data.models[str(entry.asset)]
		var seen: Array[String] = []
		for mesh in item.find_children("*","MeshInstance3D",true,false):
			assert(spec.meshes.has(str(mesh.name)))
			assert(mesh.get_node_or_null("StaticContact") != null)
			mesh.set_meta("runtime_collision_contract","concave_static_surface")
			seen.append(str(mesh.name))
		assert(seen.size() == spec.meshes.size())
		item.set_meta("checked_source_sha256",spec.source_sha256)
	for entry in data.plants:
		var item: Node3D = ship.model(root,str(entry.model_file),str(entry.name),xyz(entry.position_xyz),float(entry.yaw_radians))
		item.set_meta("persistent_id","grand_pool_architecture_"+str(entry.name)+"_003")
		item.set_meta("placement_support",entry.support)
		item.set_meta("collision_contract","visual_only")
		assert(item.find_children("*","CollisionObject3D",true,false).is_empty())
	assert(data.fixtures.is_empty() and root.find_children("*","Light3D",true,false).is_empty())
