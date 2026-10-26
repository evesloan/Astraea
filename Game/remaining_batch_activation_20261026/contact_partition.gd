extends RefCounted
# Preserve receiving-edited walls as independent contacts; consolidate only static source triangles.
static var index:Dictionary={}
static var prepared:Dictionary={}
static var bodies:Dictionary={}
static var release_enabled:=false
static var pending_key:=""
static var loads:=0
static var releases:=0
static func prepare_all(host:Node3D,owner:Node3D=null)->void:
	if owner==null:owner=host.get_node("ShipSystems")
	assert(bodies.is_empty(),"One owner for the finite contact pool")
	var rows:Array=JSON.parse_string(FileAccess.get_file_as_string("res://remaining_batch_activation_20261026/contacts/INDEX.json"))
	var sections:Array=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/REMAINING_BATCH_SECTIONS.json")).sections
	var by_key:Dictionary={}
	for item in sections:by_key[str(item.key)]=item
	assert(rows.size()==18)
	for row in rows:
		assert(FileAccess.get_sha256(row.resource)==row.sha256)
		var shape:ConcavePolygonShape3D=load(row.resource)
		assert(shape!=null)
		index[str(row.key)]=row;prepared[str(row.key)]=shape
		var item:Dictionary=by_key[str(row.key)]
		assert(item.runtime==row.source and item.hash==row.source_sha256)
		var visual:Node3D=(load(row.source) as PackedScene).instantiate()
		var xyz:Array=item.position
		var pose:Transform3D=host.get_node("ShipSpace/Districts").global_transform*Transform3D(Basis.IDENTITY,Vector3(xyz[0],xyz[1],xyz[2]))*visual.transform
		visual.free()
		var body:=StaticBody3D.new();body.name="PreparedRemainingContacts_"+str(row.key);body.collision_layer=0;body.collision_mask=0
		owner.add_child(body);body.top_level=true;body.global_transform=pose
		var collider:=CollisionShape3D.new();collider.name="SharedRoomTriangles";collider.shape=shape;body.add_child(collider)
		bodies[str(row.key)]=body
static func release_room(key:String)->void:
	if not bodies.has(key):return
	bodies[key].collision_layer=0;bodies[key].collision_mask=0
	if release_enabled and prepared.has(key):
		bodies[key].get_node("SharedRoomTriangles").shape=null
		prepared.erase(key);releases+=1
static func enable_release()->void:
	if release_enabled:return
	release_enabled=true
	for key:String in bodies:
		if bodies[key].collision_layer==0:release_room(key)
static func _install_prepared(key:String,shape:ConcavePolygonShape3D)->void:
	assert(shape!=null and bodies.has(key) and bodies[key].collision_layer==0)
	prepared[key]=shape;bodies[key].get_node("SharedRoomTriangles").shape=shape;loads+=1
static func ensure_prepared(key:String)->void:
	if prepared.has(key):return
	if FileAccess.get_sha256(index[key].resource)!=index[key].sha256:
		push_error("Exact contact source changed");return
	var shape:ConcavePolygonShape3D
	if pending_key==key:
		shape=ResourceLoader.load_threaded_get(index[key].resource);pending_key=""
	else:shape=load(index[key].resource)
	if shape==null:
		push_error("Exact contact resource unavailable");return
	_install_prepared(key,shape)
static func discard_pending()->bool:
	if pending_key.is_empty():return true
	var status:=ResourceLoader.load_threaded_get_status(index[pending_key].resource)
	if status==ResourceLoader.THREAD_LOAD_IN_PROGRESS:return false
	if status==ResourceLoader.THREAD_LOAD_LOADED:ResourceLoader.load_threaded_get(index[pending_key].resource)
	pending_key=""
	return true
static func prefetch(key:String)->bool:
	if prepared.has(key):return true
	if not pending_key.is_empty() and pending_key!=key:
		if not discard_pending():return false
	if pending_key.is_empty():
		if FileAccess.get_sha256(index[key].resource)!=index[key].sha256:
			push_error("Exact contact source changed");return false
		var error:=ResourceLoader.load_threaded_request(index[key].resource,"ConcavePolygonShape3D",false)
		if error!=OK:
			push_error("Cannot prefetch exact contact source");return false
		pending_key=key
	var status:=ResourceLoader.load_threaded_get_status(index[key].resource)
	if status==ResourceLoader.THREAD_LOAD_IN_PROGRESS:return false
	if status!=ResourceLoader.THREAD_LOAD_LOADED:
		pending_key="";push_error("Exact contact prefetch failed");return false
	ensure_prepared(key);return prepared.has(key)
static func statistics()->Dictionary:
	return {"retained_shapes":prepared.size(),"finite_bodies":bodies.size(),"pending_key":pending_key,"loads":loads,"releases":releases,"release_enabled":release_enabled}
static func release_prepared(free_bodies:bool=true)->void:
	if not pending_key.is_empty():
		# Teardown consumes the one outstanding request; never leave a strong loader cache.
		ResourceLoader.load_threaded_get(index[pending_key].resource)
	if free_bodies:
		for body in bodies.values():
			if is_instance_valid(body):body.free()
	bodies.clear();prepared.clear();pending_key="";release_enabled=false
const RECEIVERS:={"D12_directory_02":"library_receiving", "D11_directory_08":"music_receiving", "D11_directory_09":"performers_receiving", "D11_directory_02":"cinema1_receiving", "D10_directory_09":"moonfruit_service"}
static func wall_names(key:String)->Dictionary:
	var names:Dictionary={}
	if RECEIVERS.has(key):
		var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/"+str(RECEIVERS[key])+"_20261016/NATIVE_VERIFICATION.json"))
		for row in p.walls:names[str(row.source_name)]=true
	return names
static func visual_border(mesh:MeshInstance3D,key:String)->bool:
	var n:=str(mesh.name).replace(".","_")
	return key=="D11_directory_02" and (n.begins_with("WP13_C1_R01_P01_bay_") or n.begins_with("WP13_C1_R01_P20_bay_")) and (n.ends_with("bay_front") or n.ends_with("bay_side") or n.ends_with("bay_side_001"))
static func attach(source:Node3D,meshes:Array[Node],key:String)->void:
	var timings:Array=[Time.get_ticks_usec()]
	var walls:=wall_names(key)
	var immutable:Array[Node]=[]
	for mesh:MeshInstance3D in meshes:
		if visual_border(mesh,key):
			mesh.set_meta("receiving_collision_policy","visual bay border")
			continue
		var independent:=walls.has(str(mesh.name))
		var ancestor:Node=mesh
		while ancestor!=source:
			if ancestor.get_script()!=null or ancestor is CollisionObject3D or (ancestor is Node3D and ancestor.top_level):independent=true
			ancestor=ancestor.get_parent()
			assert(ancestor!=null)
		if independent:load("res://scripts/static_contact_cache.gd").attach(mesh)
		else:immutable.append(mesh)
	timings.append(Time.get_ticks_usec())
	# Keep glass and shader surfaces on their original independently queryable mesh.
	for mesh:MeshInstance3D in immutable:
		var opaque:=true
		for surface in range(mesh.mesh.get_surface_count()):
			var material:Material=mesh.get_active_material(surface)
			if not material is BaseMaterial3D or material.transparency!=BaseMaterial3D.TRANSPARENCY_DISABLED or material.albedo_color.a<.999:opaque=false
		if not opaque:load("res://scripts/static_contact_cache.gd").attach(mesh)
	timings.append(Time.get_ticks_usec())
	assert(bodies.has(key),"Contact bodies must be prepared before player admission")
	ensure_prepared(key)
	if not prepared.has(key):
		push_error("Contact activation refused: exact resource unavailable");return
	var body:StaticBody3D=bodies[key]
	assert(body.global_transform.is_equal_approx(source.global_transform),"Never reuse pooled contacts at a different source pose")
	assert(body.collision_layer==0,"No duplicate live source owner")
	body.collision_layer=1;body.collision_mask=1
	source.set_meta("prepared_contact_body",body)
	timings.append(Time.get_ticks_usec())
	source.set_meta("contact_partition_timings_us",timings)
