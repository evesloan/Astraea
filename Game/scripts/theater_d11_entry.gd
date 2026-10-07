extends RefCounted
# Additive source-bound D11 entrance. No new floor or alteration of closed interfaces.
const CONTRACT: String="res://data/architecture/THEATER_D11_MAIN_ENTRY023.json"
static func xyz(a: Array) -> Vector3:return Vector3(float(a[0]),float(a[1]),float(a[2]))
static func build(parent: Node3D, ship: Node3D) -> void:
	var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	assert(data.schema=="astraea.theater.d11.main_entry023")
	for path in data.protected_runtime_sha256:
		assert(FileAccess.get_sha256("res://"+str(path))==str(data.protected_runtime_sha256[path]),"Theater door source changed: "+str(path))
	var venue: Node3D=parent.get_node("GrandLanternTheater_ConnectedStaticStage_WIP")as Node3D
	var motion: Node3D=venue.get_node("TheaterUnpoweredDoorLiftAssemblies")as Node3D
	assert(not motion.has_node("D11MainEntrance"))
	var controller: Node3D=load("res://scripts/theater_d11_main_door.gd").new()as Node3D
	controller.name="D11MainEntrance";controller.set("persistent_id",StringName(str(data.persistent_id)))
	controller.set("authored_motion",motion);controller.set("fitting",data)
	motion.add_child(controller)
	# The exterior plate is a separate editable retained-family derivative.
	# Its exact source-backed face areas provide the same focused E controls on both sides.
	assert(FileAccess.get_sha256(str(data.exterior_call.asset_path))==str(data.exterior_call.asset_sha256))
	var call: Node3D=(load(str(data.exterior_call.asset_path))as PackedScene).instantiate()as Node3D
	call.name="D11MainExteriorCall";venue.add_child(call)
	assert(call.find_children("*","MeshInstance3D",true,false).size()==2)
	for item: Node in call.find_children("*","MeshInstance3D",true,false):
		var mesh: MeshInstance3D=item as MeshInstance3D
		assert(str(mesh.name)in data.exterior_call.mesh_nodes)
		var body: StaticBody3D=StaticBody3D.new();body.name="SourceStaticContact"
		var shape: CollisionShape3D=CollisionShape3D.new();shape.name="ExactSourceTriangles"
		var contact: ConcavePolygonShape3D=ConcavePolygonShape3D.new()
		contact.set_faces(load("res://scripts/court_a_increment004.gd").raw_faces(mesh.mesh));contact.margin=.001;shape.shape=contact;body.add_child(shape);mesh.add_child(body)
	for record: Dictionary in data.controls:
		var area: Area3D=Area3D.new();area.name=str(record.id);area.monitoring=false;area.collision_layer=1;area.collision_mask=0
		var shape: CollisionShape3D=CollisionShape3D.new();var box: BoxShape3D=BoxShape3D.new()
		box.size=xyz(record.target_box_size);box.margin=.0001;shape.shape=box;area.add_child(shape);controller.add_child(area);area.position=xyz(record.target_native)
		area.set_meta("physical_control_source",str(record.physical_source));area.set_meta("target_is_within_actual_lens_face",true)
	venue.set_meta("D11_main_entry_operation","manual focused RMB/E; other external interfaces and cabin remain inactive")
	assert(ship.get_node("ShipSpace/Districts")==parent)
