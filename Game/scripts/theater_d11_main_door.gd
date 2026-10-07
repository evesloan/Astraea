extends "res://scripts/service_door.gd"
# Local fitting of the existing door interaction/state lifecycle.
# Both complete source leaves retain their original Mesh and Shape resources.
var authored_motion: Node3D
var fitting: Dictionary
var leaf_groups: Array[Node3D]=[]
var closed_poses: Array[Transform3D]=[]
var travel_vectors: Array[Vector3]=[]
var source_contacts: Dictionary={}
var swept_box: AABB

static func xyz(a: Array) -> Vector3:
	return Vector3(float(a[0]),float(a[1]),float(a[2]))

static func relative(node: Node3D, ancestor: Node3D) -> Transform3D:
	var result: Transform3D=node.transform
	var cursor: Node=node.get_parent()
	while cursor!=ancestor:
		assert(cursor!=null and cursor is Node3D)
		result=(cursor as Node3D).transform*result
		cursor=cursor.get_parent()
	return result

func _ready() -> void:
	assert(not persistent_id.is_empty() and authored_motion!=null and leaves.is_empty())
	assert(get_parent()==authored_motion and transform==Transform3D.IDENTITY)
	assert(fitting.groups.size()==2 and float(fitting.travel_m)==2.65 and float(fitting.maximum_leaf_speed_m_s)==1.0)
	assert(FileAccess.get_sha256(str(fitting.original_moving_asset))==str(fitting.original_moving_sha256))
	var template: Node3D=(load(str(fitting.original_moving_asset))as PackedScene).instantiate()as Node3D
	open_fraction=1.0;desired_open=true;pose_initialized=false
	for record: Dictionary in fitting.groups:
		var source: Node3D=authored_motion.find_child(str(record.node),true,false)as Node3D
		var original: Node3D=template.find_child(str(record.node),true,false)as Node3D
		assert(source!=null and original!=null and source.get_meta("source_motion_group")==str(record.id))
		assert(not source.get_meta("operation_enabled") and float(source.get_meta("locked_pose_fraction"))==1.0)
		var closed: Transform3D=relative(original,template)
		var travel: Vector3=xyz(record.axis)*float(fitting.travel_m)
		var opened: Transform3D=closed;opened.origin+=travel
		assert(relative(source,authored_motion).is_equal_approx(opened))
		var meshes: Array[Node]=source.find_children("*","MeshInstance3D",true,false)
		assert(meshes.size()==record.mesh_nodes.size())
		var body: AnimatableBody3D=AnimatableBody3D.new()
		body.name=str(record.body_name);body.sync_to_physics=false;body.transform=opened;add_child(body)
		source.reparent(body,true);source.transform=Transform3D.IDENTITY
		for item: Node in meshes:
			var mesh: MeshInstance3D=item as MeshInstance3D
			assert(str(mesh.name)in record.mesh_nodes and not source_contacts.has(str(mesh.name)))
			var old_body: StaticBody3D=mesh.get_node("SourceStaticContact")as StaticBody3D
			var old_shape: CollisionShape3D=old_body.get_node("ExactSourceTriangles")as CollisionShape3D
			assert(old_body.transform==Transform3D.IDENTITY and old_shape.transform==Transform3D.IDENTITY)
			assert(old_shape.shape is ConcavePolygonShape3D and absf(old_shape.shape.margin-.001)<.000001 and not old_shape.disabled)
			var faces: PackedVector3Array=(old_shape.shape as ConcavePolygonShape3D).get_faces()
			assert(faces.to_byte_array()==mesh.mesh.get_faces().to_byte_array())
			var shape: CollisionShape3D=CollisionShape3D.new();shape.name=str(mesh.name)+"_RetainedContact"
			shape.shape=old_shape.shape;shape.transform=relative(mesh,source);shape.set_meta("source_mesh",str(mesh.name));body.add_child(shape)
			source_contacts[str(mesh.name)]={"mesh":mesh,"body":body,"shape":shape,"original_shape_resource":old_shape.shape,"faces":faces}
			old_body.free()
			assert(shape.shape.get_faces().to_byte_array()==faces.to_byte_array())
		leaves.append(body);leaf_groups.append(source);closed_poses.append(closed);travel_vectors.append(travel)
		source.set_meta("operation_enabled",true);source.remove_meta("locked_pose_fraction")
	template.free()
	assert(leaves.size()==2 and source_contacts.size()==6)
	var bounds: Array=fitting.swept_bounds_native
	swept_box=AABB(xyz(bounds[0]),xyz(bounds[1])-xyz(bounds[0])).grow(float(fitting.occupancy_reserve_m))
	_apply_pose()
	for body in leaves:body.sync_to_physics=true
	set_meta("source_family","AST-CUL-005");set_meta("source_motion_groups",["THEATER_D11_MAIN_LEAF_LEFT","THEATER_D11_MAIN_LEAF_RIGHT"])
	set_meta("only_D11_main_entry_enabled",true);set_meta("save_acceptance",false)

func _physics_process(delta: float) -> void:
	# The inherited normalized timing would make these larger leaves too fast.
	# Its unchanged .85 sequencing yields exactly the fitted maximum linear speed.
	super._physics_process(delta*float(fitting.maximum_leaf_speed_m_s)/float(fitting.travel_m))

func _apply_pose() -> void:
	if leaves.is_empty():return
	assert(leaves.size()==2)
	for i in range(2):
		var fraction: float=clampf(open_fraction/.85,0.,1.)if i==0 else clampf((open_fraction-.15)/.85,0.,1.)
		leaves[i].transform=closed_poses[i]
		leaves[i].position=closed_poses[i].origin+travel_vectors[i]*fraction
		leaf_groups[i].set_meta("current_pose_fraction",fraction)

func _sweep_occupied() -> bool:
	if not is_inside_tree()or leaves.size()!=2:return true
	var query: PhysicsShapeQueryParameters3D=PhysicsShapeQueryParameters3D.new()
	var box: BoxShape3D=BoxShape3D.new();box.size=swept_box.size;box.margin=.001
	query.shape=box;query.transform=global_transform*Transform3D(Basis.IDENTITY,swept_box.get_center())
	query.collision_mask=1;query.collide_with_areas=false
	var excluded: Array[RID]=[]
	for leaf in leaves:excluded.append(leaf.get_rid())
	query.exclude=excluded
	var hits: Array[Dictionary]=get_world_3d().direct_space_state.intersect_shape(query,128)
	if hits.size()==128:return true
	for hit: Dictionary in hits:
		if hit.collider is CharacterBody3D or hit.collider is RigidBody3D:return true
	return false

func get_interaction_label() -> String:
	if obstructed:return "Clear theater door travel"
	return "E · Close theater entrance"if desired_open else"E · Open theater entrance"
