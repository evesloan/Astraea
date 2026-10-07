extends SceneTree
# Scratch-output diagnostic of actual imported PhysicsServer shape resources.
const ENTRY=preload("res://tests/theater_d11_entry_probe.gd")
const RAW=preload("res://scripts/court_a_increment004.gd")
func _initialize() -> void:call_deferred("run")
func xyz(v: Vector3) -> Array:return [v.x,v.y,v.z]
func rows(a: PackedVector3Array) -> Array:
	var out: Array=[]
	for v in a:out.append(xyz(v))
	return out
func triangles(shape: Shape3D) -> PackedVector3Array:
	if shape is ConcavePolygonShape3D:return shape.get_faces()
	if shape is BoxShape3D:
		var h: Vector3=shape.size*.5
		var corners: Array[Vector3]=[Vector3(-h.x,-h.y,-h.z),Vector3(h.x,-h.y,-h.z),Vector3(h.x,h.y,-h.z),Vector3(-h.x,h.y,-h.z),Vector3(-h.x,-h.y,h.z),Vector3(h.x,-h.y,h.z),Vector3(h.x,h.y,h.z),Vector3(-h.x,h.y,h.z)]
		var faces: PackedVector3Array=PackedVector3Array()
		for index in [0,2,1,0,3,2,4,5,6,4,6,7,0,1,5,0,5,4,3,7,6,3,6,2,0,4,7,0,7,3,1,2,6,1,6,5]:faces.append(corners[index])
		return faces
	assert(false,"Unscreened shape type within entry sweep: "+shape.get_class());return PackedVector3Array()
func run() -> void:
	var output: String=OS.get_environment("THEATER_ENTRY_CONTACT_OUTPUT")
	assert(not output.is_empty() and not FileAccess.file_exists(output))
	var main: Node=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
	for frame in range(4):await physics_frame
	var ship: Node3D=main.get_node("World360/Astraea")as Node3D
	var door: Node3D=ENTRY.get_door(ship)
	ENTRY.check_installation(ship)
	var bounds: Array=door.fitting.swept_bounds_native
	var sweep: AABB=AABB(ENTRY.xyz(bounds[0]),ENTRY.xyz(bounds[1])-ENTRY.xyz(bounds[0])).grow(.004)
	var moving: Array=[]
	for i in range(2):
		var body: AnimatableBody3D=door.leaves[i]
		for node in body.get_children():
			if not node is CollisionShape3D:continue
			var shape: CollisionShape3D=node as CollisionShape3D
			var closed: Transform3D=door.global_transform*door.closed_poses[i]*shape.transform
			var faces: PackedVector3Array=closed*(shape.shape as ConcavePolygonShape3D).get_faces()
			moving.append({"group":i,"mesh":str(shape.get_meta("source_mesh")),"margin":shape.shape.margin,"faces":rows(faces),"travel":xyz(door.travel_vectors[i])})
	var fixed: Array=[]
	for item in ship.find_children("*","StaticBody3D",true,false):
		var body: StaticBody3D=item as StaticBody3D
		if body in door.leaves or (body.collision_layer&1)==0:continue
		for item_shape in body.find_children("*","CollisionShape3D",true,false):
			var shape: CollisionShape3D=item_shape as CollisionShape3D
			if shape.disabled or shape.shape==null:continue
			var local: AABB=shape.shape.get_debug_mesh().get_aabb()
			var world: AABB=shape.global_transform*local
			if not sweep.intersects(world):continue
			var faces: PackedVector3Array=shape.global_transform*triangles(shape.shape)
			fixed.append({"path":str(shape.get_path()),"shape_class":shape.shape.get_class(),"margin":shape.shape.margin,"faces":rows(faces),"animatable":body is AnimatableBody3D})
	assert(moving.size()==6 and not fixed.is_empty())
	var file: FileAccess=FileAccess.open(output,FileAccess.WRITE);assert(file!=null)
	file.store_string(JSON.stringify({"status":"ACTUAL_IMPORTED_CONTACTS_DUMPED_NOT_YET_SCREENED","moving":moving,"fixed":fixed,"source_scope":"All loaded ship static/animatable collision shapes whose transformed debug AABB intersects the full entry sweep, plus its six exact moving shapes. No shape-query false clearance.","sweep_bounds":bounds},"  ",true,true));file.close()
	print("THEATER ENTRY ACTUAL CONTACTS DUMPED: ",moving.size()," moving batches, ",fixed.size()," neighboring shape owners")
	main.queue_free();await process_frame;quit(0)
