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
var maximum_native_support_offset := 0.0
var plant_quantization_bounds: Dictionary = {}
var maximum_plant_source_offset := 0.0

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

func float32_ulp(value: float) -> float:
	var bytes:=PackedByteArray()
	bytes.resize(4);bytes.encode_float(0,value)
	var exponent:=int((bytes.decode_u32(0)>>23)&255)
	return pow(2.0,-149.0 if exponent==0 else float(exponent-127-23))

func world_float_bound(a: Vector3,b: Vector3) -> Vector3:
	# Independent rounding of ideal/world-transformed native float32 positions.
	return Vector3(float32_ulp(a.x)+float32_ulp(b.x),float32_ulp(a.y)+float32_ulp(b.y),float32_ulp(a.z)+float32_ulp(b.z))

func pins() -> void:
	var retained_plant_imports: Dictionary = {"res://assets/models/AST-BOT-003_pool_basal_00.glb.import":"1489d4c0636f1a8575039a8333ff9a925fa830a3fb9067fd0519efeb74f009ac","res://assets/models/AST-BOT-002_pool_middle_00.glb.import":"28d8f6400d2e3cc43d22b305460a7c35e43a4375a0ec202c6b5090eb27d16872","res://assets/models/AST-BOT-003_pool_basal_01.glb.import":"54a3b219d296288944f36509c3d12cca553fc314e8dfed8f4759c4b93e846819","res://assets/models/AST-BOT-002_pool_middle_01.glb.import":"09dfe236441a3d8e6b9899d6d7c1d6a6844296fb5f9212be666de2e3fa01613f","res://assets/models/AST-BOT-003_pool_basal_02.glb.import":"eb9b86895c2d8bb11d2a878a93ab02b632c1d14aa6b0e1183a075985c93c6608","res://assets/models/AST-BOT-002_pool_middle_02.glb.import":"355c2d6fab8746e6fce176244f43a965d086031f62ba985604d6fc12252bf676","res://assets/models/AST-BOT-003_pool_basal_03.glb.import":"619fb9722ae8d82229112e17cb7169f2d5b588b006a679df87f0a6ec2a8dcd6f","res://assets/models/AST-BOT-002_pool_middle_03.glb.import":"35aa63b47cdbd34d69a149a3ccbbfe56df600f683daa7efb43cff19659347116","res://assets/models/AST-BOT-003_pool_basal_04.glb.import":"7ab22249ed44b5aea1a4a64dd13789e4637fe0b8879525027689fdbd01398f25","res://assets/models/AST-BOT-002_pool_middle_04.glb.import":"954f0788db29a9da3c09ac6a183ca496ae812b69bd21168d59635ffc027c259f","res://assets/models/AST-BOT-003_pool_basal_05.glb.import":"364d39ef6b646ab358954879cafba58963023186390a0c0d7564b6a75a70b447","res://assets/models/AST-BOT-002_pool_middle_05.glb.import":"59a9a73b116643ff79689e873be6db98c4f35c31f959124c728ce69ceefb39a0"}
	for path in retained_plant_imports:
		assert(FileAccess.get_sha256(path)==retained_plant_imports[path],"Retained plant import policy changed")
	assert(FileAccess.get_sha256("res://assets/models/AST-AQU-016.glb.import")=="ecd15cf4bf417b752363efc637f12b2265dd724a6c403480ef6d44f64c64d8f0","Retained roof import policy changed")
	var engine: Dictionary=Engine.get_version_info()
	assert(engine.major==4 and engine.minor==6 and engine.patch==3,"Native collision representation requires reviewed engine version")
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
		var seen_roots: Dictionary = {}
		var quantization_bound:=Vector3.ZERO
		for mesh in node.find_children("*","MeshInstance3D",true,false):
			# Godot4.6.3 compresses position coordinates to uint16 within the
			# mesh AABB. One full quantization step is size/65535 per local axis.
			# This is a conversion bound, separate from the50um soil contact gate.
			var compressed:=false
			for surface in range(mesh.mesh.get_surface_count()):
				if mesh.mesh.surface_get_format(surface)&Mesh.ARRAY_FLAG_COMPRESS_ATTRIBUTES:compressed=true
			if compressed:
				var step: Vector3=mesh.mesh.get_aabb().size/65535.0
				var basis: Basis=mesh.global_basis
				quantization_bound=quantization_bound.max(basis.x.abs()*step.x+basis.y.abs()*step.y+basis.z.abs()*step.z)
			for vertex in render_faces(mesh.mesh):
				var world: Vector3=mesh.global_transform*vertex
				if absf(world.y-float(entry.position_xyz[1]))<.00005 and not seen_roots.has(world):
					seen_roots[world]=true;roots.append(world)
		var expected_roots:=0
		for probe in data.plant_support_probes:
			if str(probe.item)==str(entry.name):expected_roots+=1
		assert(roots.size()==expected_roots and expected_roots>0,"Imported plant soil-level root membership changed")
		actual_plant_roots[str(entry.name)]=roots
		plant_quantization_bounds[str(entry.name)]=quantization_bound
	assert(ray(Vector3(-31,52.6,-432),Vector3(-31,52.4,-432),[actor.get_rid()]).is_empty(),"Architecture created a pool-void bridge")

func native_collision_projection(mesh: MeshInstance3D,start: Vector3,end: Vector3) -> Variant:
	# Independently reproduce Godot4.6.3 TriangleMesh.create's documented source
	# implementation: snap raw render vertices to0.0001m before collider creation.
	# Compare the physics query to this native representation, not ideal source
	# coordinates below its quantization grid. No collision tolerance is widened.
	var a:=mesh.to_local(start)
	var b:=mesh.to_local(end)
	var vertices:=render_faces(mesh.mesh)
	var nearest: Variant=null
	var distance:=INF
	for i in range(0,vertices.size(),3):
		var hit: Variant=Geometry3D.segment_intersects_triangle(a,b,vertices[i].snappedf(.0001),vertices[i+1].snappedf(.0001),vertices[i+2].snappedf(.0001))
		if hit==null:continue
		var world: Vector3=mesh.to_global(hit)
		var value:=start.distance_squared_to(world)
		if value<distance:distance=value;nearest=world
	return nearest

func support_checks() -> void:
	var excluded: Array[RID] = [actor.get_rid()]
	for body in built.find_children("*","CollisionObject3D",true,false): excluded.append(body.get_rid())
	assert(data.retained_support_probes.size()==114)
	assert(data.plant_support_probes.size()==639 and data.seat_surface_probes.size()==3)
	assert(data.seat_approaches.size()==3 and data.preserved_view_probes.size()==159)
	for probe in data.retained_support_probes:
		var p := xyz(probe.position_xyz)
		var direction := xyz(probe.into_support_xyz)
		var expected:=p
		if str(probe.owner).begins_with("GP_"):
			var reference:=original.get_node("GrandPoolConnectedArchitecture").find_child(str(probe.expected_support_batch),true,false)as MeshInstance3D
			assert(reference!=null and reference.global_transform.is_equal_approx(Transform3D.IDENTITY))
			var projected: Variant=native_collision_projection(reference,p-direction*.02,p+direction*.02)
			assert(projected!=null,"Retained native support surface is missing")
			expected=projected
			maximum_native_support_offset=maxf(maximum_native_support_offset,p.distance_to(expected))
		var hit := ray(p-direction*.02,p+direction*.02,excluded)
		assert(not hit.is_empty() and hit.position.distance_to(expected)<.00005,"Missing retained support in its actual native collision representation: "+str(probe.part))
		var owner: Node3D
		if str(probe.owner).begins_with("GP_"): owner=original.get_node("GrandPoolConnectedArchitecture")
		else: owner=floors.get_node(NodePath(str(probe.floor_owner)))
		assert(owner.is_ancestor_of(hit.collider),"Wrong existing support owner: "+str(probe.part))
		if str(probe.owner).begins_with("GP_"):
			assert(str(hit.collider.get_parent().name)==str(probe.expected_support_batch),"Wrong actual retained roof-rib batch")
	var mapped_roots: Dictionary = {}
	for probe in data.plant_support_probes:
		var p := xyz(probe.position_xyz)
		var hit := ray(p+Vector3.UP*.015,p-Vector3.UP*.015,[actor.get_rid()])
		assert(not hit.is_empty() and hit.position.distance_to(p)<.00005 and built.get_node("GrandPoolWetLoggias").is_ancestor_of(hit.collider),"Botanical root lost its soil contact")
		assert(str(hit.collider.get_parent().name)==str(probe.expected_support_batch),"Root hit the wrong soil batch")
		var nearest:=Vector3.INF
		var distance:=INF
		for vertex in actual_plant_roots[str(probe.item)]:
			if vertex.distance_to(p)<distance:distance=vertex.distance_to(p);nearest=vertex
		var conversion_bound: Vector3=plant_quantization_bounds[str(probe.item)]+world_float_bound(p,nearest)
		var delta: Vector3=(nearest-p).abs()
		assert(delta.x<=conversion_bound.x and delta.y<=conversion_bound.y and delta.z<=conversion_bound.z,"Imported root differs beyond documented16bit conversion and world float32 roundoff")
		maximum_plant_source_offset=maxf(maximum_plant_source_offset,distance)
		var native_hit:=ray(nearest+Vector3.UP*.015,nearest-Vector3.UP*.015,[actor.get_rid()])
		assert(not native_hit.is_empty() and native_hit.position.distance_to(nearest)<.00005,"Actual imported root lost its physical soil contact")
		assert(built.get_node("GrandPoolWetLoggias").is_ancestor_of(native_hit.collider) and str(native_hit.collider.get_parent().name)==str(probe.expected_support_batch),"Actual imported root contacted the wrong soil owner or batch")
		var mapped_key:=str(probe.item)+str(nearest)
		assert(not mapped_roots.has(mapped_key),"Source root correspondence is not one-to-one")
		mapped_roots[mapped_key]=true
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
	await load("res://tests/pool_feature_layers_checks.gd").new().check(self,ship)
	await load("res://tests/pool_east_gallery_checks.gd").new().check(self,ship)
	print("POOL SOURCE TO RETAINED NATIVE SUPPORT REPRESENTATION MAX OFFSET M ",maximum_native_support_offset)
	print("POOL SOURCE TO RETAINED IMPORTED PLANT ROOT MAX OFFSET M ",maximum_plant_source_offset)
	print("GRAND POOL ARCHITECTURE PASS: three checked derivative assemblies, 451 source parts, 114 retained support roots, 12 soil-supported plant instances, three accessible pool-facing curved seats; original 126 programme preserved. Cart/lift, affected original checks and actual visual acceptance remain separate.")
	main.queue_free();await process_frame;quit(0)
