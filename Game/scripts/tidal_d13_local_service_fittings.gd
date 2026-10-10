extends RefCounted
const DATA := "res://data/architecture/TIDAL_D13_LOCAL_SERVICE_FITTINGS.json"
static func build(ship:Node3D,house:Node3D)->Node3D:
	var prior:=house.get_node_or_null("TidalD13LocalServiceFittings") as Node3D
	if prior!=null:return prior
	var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(DATA))
	for path in d.preimage_pins:
		if str(path).begins_with("Game/"):
			assert(FileAccess.get_sha256("res://"+str(path).trim_prefix("Game/"))==str(d.preimage_pins[path]),str(path))
	assert(house.get_node_or_null("TidalD13ServiceReceiving")!=null)
	assert(FileAccess.get_sha256("res://assets/models/"+str(d.model_file))==str(d.model_sha256))
	var group:Node3D=load("res://assets/models/"+str(d.model_file)).instantiate()
	group.name=str(d.root_name)
	group.set_meta("persistent_id",str(d.persistent_id))
	group.set_meta("acceptance","installed_physical_fittings_operational_hold")
	group.set_meta("stock_returns_save_enabled",false)
	group.set_meta("new_cart_count",0)
	group.set_meta("new_room_count",0)
	group.set_meta("new_floor_count",0)
	house.add_child(group)
	var meshes:=group.find_children("*","MeshInstance3D",true,false)
	assert(meshes.size()==int(d.mesh_count))
	for mesh:MeshInstance3D in meshes:load("res://scripts/static_contact_cache.gd").attach(mesh)
	for item in d.assemblies:
		var assembly:=group.find_child(str(item.name),true,false) as Node3D
		assert(assembly!=null)
		assembly.set_meta("persistent_id",str(item.persistent_id))
		assembly.set_meta("construction_role",str(item.role))
		assembly.set_meta("operation_hold",str(d.operations))
	group.set_meta("parking_persistent_id",str(d.parking.persistent_id))
	group.set_meta("parking_empty",true)
	group.set_meta("parking_capacity_accepted",false)
	return group
