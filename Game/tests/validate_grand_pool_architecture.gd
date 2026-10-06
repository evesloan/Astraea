extends SceneTree
const CONTRACT := "res://data/architecture/GRAND_POOL_ARCHITECTURE_RUNTIME.json"
var data: Dictionary
var ship: Node3D
var built: Node3D
var original: Node3D
var floors: Node3D
var actor: CharacterBody3D
var space: PhysicsDirectSpaceState3D
var started := 0
var walked := 0
var actual_plant_roots: Dictionary = {}

func _initialize() -> void:
	started = Time.get_ticks_msec()
	call_deferred("run")

func _process(_delta: float) -> bool:
	if Time.get_ticks_msec()-started > 230000:
		push_error("Pool architecture check exceeded 230-second watchdog")
		quit(1)
	return false

func xyz(p: Array) -> Vector3: return Vector3(p[0],p[1],p[2])
func ray(a: Vector3,b: Vector3,excluded: Array[RID] = []) -> Dictionary:
	var query := PhysicsRayQueryParameters3D.create(a,b,1)
	query.hit_back_faces = true
	query.exclude = excluded
	return space.intersect_ray(query)

func render_faces(resource: Mesh) -> PackedVector3Array:
	# get_faces() uses TriangleMesh's 0.0001m snapped collision/debug grid.
	# Render/source checks use the actual imported surface buffers and indices.
	var result := PackedVector3Array()
	for surface in range(resource.get_surface_count()):
		assert(resource.surface_get_primitive_type(surface)==Mesh.PRIMITIVE_TRIANGLES)
		var arrays: Array=resource.surface_get_arrays(surface)
		var positions: PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
		var indices: PackedInt32Array=arrays[Mesh.ARRAY_INDEX]
		assert(not indices.is_empty() and indices.size()%3==0)
		for index in indices:result.append(positions[index])
	return result

func pins() -> void:
	for path in data.preserved_file_sha256:
		assert(FileAccess.get_sha256(str(path)) == data.preserved_file_sha256[path],"Retained pool input changed: "+str(path))
	for key in data.models:
		var spec: Dictionary = data.models[key]
		var path := "res://assets/models/"+str(spec.file)
		assert(FileAccess.get_sha256(path) == spec.sha256)
		var remap := ConfigFile.new()
		assert(remap.load(path+".import") == OK)
		if spec.has("meshes"):
			assert(remap.get_value("params","meshes/force_disable_compression",false)==true,"New structural derivative must retain authored render precision")
		var imported: String = remap.get_value("remap","path","")
		assert(not imported.is_empty() and FileAccess.file_exists(imported))
		var digest := ConfigFile.new()
		assert(digest.load(imported.get_basename()+".md5") == OK)
		assert(digest.get_value("","source_md5","") == FileAccess.get_md5(path),"Stale pool architecture import")
	var compilation: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
	assert(data.retained_floor_records.size()==8)
	for record in data.retained_floor_records:
		var matches := 0
		for current in compilation.regions:
			if current.id == record.id:
				assert(current == record,"Retained pool floor or cap was altered")
				matches += 1
		assert(matches == 1)

func structure() -> void:
	assert(built.get_child_count() == 15 and data.source_parts == 451)
	assert(data.plants.size() == 12 and data.assemblies.size() == 3 and data.fixtures.is_empty())
	assert(ship.find_child("GrandPoolFirstPassEssentials_WIP",true,false).get_child_count() == 51)
	assert(ship.find_child("GrandPoolFinish_WIP",true,false).get_child_count() == 88)
	assert(built.find_children("*","Light3D",true,false).is_empty())
	for entry in data.assemblies:
		var node := built.get_node(NodePath(str(entry.name))) as Node3D
		assert(node.position == Vector3.ZERO and node.scale == Vector3.ONE)
		var spec: Dictionary = data.models[str(entry.asset)]
		var seen := 0
		for mesh in node.find_children("*","MeshInstance3D",true,false):
			assert(spec.meshes.has(str(mesh.name)) and mesh.material_override == null)
			var expected: Dictionary = spec.meshes[str(mesh.name)]
			var vertices: PackedVector3Array = render_faces(mesh.mesh)
			assert(vertices.size() == int(expected.triangles)*3)
			var lo := Vector3(INF,INF,INF)
			var hi := Vector3(-INF,-INF,-INF)
			for v in vertices:
				var p: Vector3 = mesh.global_transform*v
				lo=lo.min(p);hi=hi.max(p)
			assert(lo.distance_to(xyz(expected.bounds_min_xyz))<.00005 and hi.distance_to(xyz(expected.bounds_max_xyz))<.00005,"Imported checked geometry drift")
			assert(mesh.mesh.get_surface_count()==1)
			var material := mesh.get_active_material(0) as StandardMaterial3D
			assert(material != null and material.albedo_texture != null)
			var contact := mesh.get_node_or_null("StaticContact")
			assert(contact != null)
			var shapes := contact.find_children("*","CollisionShape3D",true,false)
			assert(shapes.size()==1 and shapes[0].shape is ConcavePolygonShape3D and not shapes[0].disabled)
			assert(shapes[0].shape.get_faces().size()==vertices.size())
			seen += 1
		assert(seen == spec.meshes.size())
	for entry in data.plants:
		var node := built.get_node(NodePath(str(entry.name))) as Node3D
		assert(node.global_position.distance_to(xyz(entry.position_xyz))<.00005 and node.scale==Vector3.ONE)
		assert(absf(node.rotation.y-float(entry.yaw_radians))<.00001)
		assert(node.find_children("*","CollisionObject3D",true,false).is_empty())
		var roots: Array[Vector3] = []
		for mesh in node.find_children("*","MeshInstance3D",true,false):
			for vertex in render_faces(mesh.mesh):
				var world: Vector3=mesh.global_transform*vertex
				if absf(world.y-float(entry.position_xyz[1]))<.00005: roots.append(world)
		assert(not roots.is_empty(),"Imported plant has no soil-level roots")
		actual_plant_roots[str(entry.name)]=roots
	assert(ray(Vector3(-31,52.6,-432),Vector3(-31,52.4,-432),[actor.get_rid()]).is_empty(),"Architecture created a pool-void bridge")

func support_checks() -> void:
	var excluded: Array[RID] = [actor.get_rid()]
	for body in built.find_children("*","CollisionObject3D",true,false): excluded.append(body.get_rid())
	assert(data.retained_support_probes.size()==114)
	assert(data.plant_support_probes.size()==639 and data.seat_surface_probes.size()==3)
	assert(data.seat_approaches.size()==3 and data.preserved_view_probes.size()==159)
	for probe in data.retained_support_probes:
		var p := xyz(probe.position_xyz)
		var direction := xyz(probe.into_support_xyz)
		var hit := ray(p-direction*.02,p+direction*.02,excluded)
		assert(not hit.is_empty() and hit.position.distance_to(p)<.00005,"Missing exact retained support: "+str(probe.part))
		var owner: Node3D
		if str(probe.owner).begins_with("GP_"): owner=original.get_node("GrandPoolConnectedArchitecture")
		else: owner=floors.get_node(NodePath(str(probe.floor_owner)))
		assert(owner.is_ancestor_of(hit.collider),"Wrong existing support owner: "+str(probe.part))
		if str(probe.owner).begins_with("GP_"):
			assert(str(hit.collider.get_parent().name)==str(probe.expected_support_batch),"Wrong actual retained roof-rib batch")
	for probe in data.plant_support_probes:
		var p := xyz(probe.position_xyz)
		var hit := ray(p+Vector3.UP*.015,p-Vector3.UP*.015,[actor.get_rid()])
		assert(not hit.is_empty() and hit.position.distance_to(p)<.00005 and built.get_node("GrandPoolWetLoggias").is_ancestor_of(hit.collider),"Botanical root lost its soil contact")
		assert(str(hit.collider.get_parent().name)==str(probe.expected_support_batch),"Root hit the wrong soil batch")
		var actual_root := false
		for vertex in actual_plant_roots[str(probe.item)]:
			if vertex.distance_to(p)<.00005: actual_root=true;break
		assert(actual_root,"Imported botanical root geometry is absent at its soil probe")
	for probe in data.seat_surface_probes:
		var p := xyz(probe.position_xyz)
		var hit := ray(p+Vector3.UP*.02,p-Vector3.UP*.02,[actor.get_rid()])
		assert(not hit.is_empty() and hit.position.distance_to(p)<.00005 and built.get_node("GrandPoolWetLoggias").is_ancestor_of(hit.collider),"Seat surface lost its physical contact")
		assert(str(hit.collider.get_parent().name)==str(probe.expected_support_batch),"Seat hit the wrong pad batch")

func new_render_segment_clear(start: Vector3,end: Vector3) -> bool:
	# Foliage intentionally has no collider. Check actual imported render triangles.
	for mesh in built.find_children("*","MeshInstance3D",true,false):
		var a: Vector3=mesh.to_local(start)
		var b: Vector3=mesh.to_local(end)
		var box: AABB=mesh.mesh.get_aabb().grow(.00005)
		if maxf(a.x,b.x)<box.position.x or minf(a.x,b.x)>box.end.x or maxf(a.y,b.y)<box.position.y or minf(a.y,b.y)>box.end.y or maxf(a.z,b.z)<box.position.z or minf(a.z,b.z)>box.end.z: continue
		var vertices: PackedVector3Array=render_faces(mesh.mesh)
		for i in range(0,vertices.size(),3):
			var hit: Variant=Geometry3D.segment_intersects_triangle(a,b,vertices[i],vertices[i+1],vertices[i+2])
			if hit != null: return false
	return true

func settle(p: Vector3) -> void:
	assert(ship.arrive_at(p+Vector3.UP*.1,0))
	for f in range(24):
		actor.velocity=Vector3(0,-.1 if actor.is_on_floor() else actor.velocity.y-9.8/60,0)
		actor.move_and_slide()
		await physics_frame
	assert(absf(actor.position.y-p.y)<.08)

func walk_to(target: Vector3) -> void:
	var limit := ceili(Vector2(target.x-actor.position.x,target.z-actor.position.z).length()/3.1*60)+240
	var reached := false
	for f in range(limit):
		var delta := Vector3(target.x-actor.position.x,0,target.z-actor.position.z)
		if delta.length()<.075: reached=true;break
		var v := delta.normalized()*3.1
		actor.velocity=Vector3(v.x,-.1 if actor.is_on_floor() else actor.velocity.y-9.8/60,v.z)
		actor.move_and_slide()
		await physics_frame
		walked += 1
		assert(absf(actor.position.y-target.y)<.18 and walked<12000)
	assert(reached,"New loggia seat approach is obstructed")

func check_seat_view_and_approach_budget(entry: Dictionary) -> void:
	assert(ray(xyz(entry.seated_eye_xyz),xyz(entry.pool_view_target_xyz),[actor.get_rid()]).is_empty(),"Pool-facing seat view is blocked")
	assert(new_render_segment_clear(xyz(entry.seated_eye_xyz),xyz(entry.pool_view_target_xyz)),"New foliage or architecture blocks the seated rendered pool view")
	var budget: Node = ship.get_node("ShipSystems/LocalShadowSourceBudget")
	budget.refresh()
	var selected: Array[String] = []
	for light in budget.sources:
		if not budget.requested_shadow[light.get_instance_id()]: continue
		assert(light.visible == light.shadow_enabled)
		if light.visible:
			assert(budget._has_visible_sample(light))
			selected.append(str(light.name))
	assert(selected.size()<=8)
	print("POOL ARCHITECTURE STANDING APPROACH LIGHT SAMPLE ",entry.name," ",selected)
	# This samples actual selected-source reach to the physical seat surface.
	# Readability/brightness is still an image gate, not a count-based pass.
	var surface_sources: Array[String] = []
	for probe in data.seat_surface_probes:
		if not str(probe.part).begins_with("LOG_"+str(entry.name)+"_Seat_"): continue
		var sample := xyz(probe.position_xyz)+Vector3.UP*.02
		for light in budget.sources:
			if not light.visible or not light is SpotLight3D: continue
			var delta: Vector3=sample-light.global_position
			if delta.length()<light.spot_range and delta.normalized().dot(-light.global_basis.z)>=cos(deg_to_rad(light.spot_angle)) and budget._clear_sample(light.global_position,sample):
				surface_sources.append(str(light.name))
	print("POOL ARCHITECTURE SEAT SURFACE REACH, VISUAL REVIEW PENDING ",entry.name," ",surface_sources)

func run() -> void:
	data=JSON.parse_string(FileAccess.get_file_as_string(CONTRACT));pins()
	var main: Node=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
	for f in range(90): await physics_frame
	ship=main.get_node("World360/Astraea");actor=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false)
	space=ship.get_world_3d().direct_space_state;built=ship.find_child("GrandPoolArchitecture_WIP",true,false);original=ship.find_child("GrandPoolOrchardSection_WIP",true,false);floors=ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms")
	assert(built != null and original != null)
	structure();support_checks()
	for probe in data.preserved_view_probes:
		var hit := ray(xyz(probe.eye_xyz),xyz(probe.target_xyz),[actor.get_rid()])
		assert(hit.is_empty() or not built.is_ancestor_of(hit.collider),"New architecture obstructs a retained view: "+str(probe.name))
		assert(new_render_segment_clear(xyz(probe.eye_xyz),xyz(probe.target_xyz)),"New render triangles obstruct a retained view: "+str(probe.name))
	for entry in data.seat_approaches:
		await settle(xyz(entry.approach_xyz[0]))
		for p in entry.approach_xyz: await walk_to(xyz(p))
		check_seat_view_and_approach_budget(entry)
		var reverse: Array=entry.approach_xyz.duplicate();reverse.reverse()
		for p in reverse: await walk_to(xyz(p))
	pins()
	print("GRAND POOL ARCHITECTURE PASS: three checked derivative assemblies, 451 source parts, 114 retained support roots, 12 soil-supported plant instances, three accessible pool-facing curved seats; original 126 programme preserved. Cart/lift, affected original checks and actual visual acceptance remain separate.")
	main.queue_free();await process_frame;quit(0)
