extends SceneTree
const CONTRACT := "res://data/architecture/GRAND_POOL_FINISH_RUNTIME.json"
var data: Dictionary
var ship: Node3D
var built: Node3D
var original: Node3D
var furniture: Node3D
var floors: Node3D
var actor: CharacterBody3D
var space: PhysicsDirectSpaceState3D
var walked := 0
var started := 0
var supports := 0
var selected_new_sources: Dictionary = {}

func _initialize() -> void:
	started = Time.get_ticks_msec()
	call_deferred("run")

func _process(_delta: float) -> bool:
	if Time.get_ticks_msec()-started > 230000:
		push_error("Grand Pool finish check exceeded 230-second watchdog")
		quit(1)
	return false

func xyz(p: Array) -> Vector3: return Vector3(p[0],p[1],p[2])

func ray(a: Vector3, b: Vector3, excluded: Array[RID] = []) -> Dictionary:
	var query := PhysicsRayQueryParameters3D.create(a,b,1)
	query.hit_back_faces = true
	query.exclude = excluded
	return space.intersect_ray(query)

func item(name: String) -> Node3D:
	var found := built.get_node_or_null(NodePath(name)) as Node3D
	if found == null: found = furniture.get_node_or_null(NodePath(name)) as Node3D
	assert(found != null, "Missing checked pool item: " + name)
	return found

func exclusions(node: Node3D) -> Array[RID]:
	var ids: Array[RID] = [actor.get_rid()]
	for body in node.find_children("*","CollisionObject3D",true,false): ids.append(body.get_rid())
	return ids

func pins() -> void:
	for path in data.preserved_file_sha256:
		assert(FileAccess.get_sha256("res://"+str(path)) == data.preserved_file_sha256[path], "Retained bytes changed: "+str(path))
	for key in data.models:
		var spec: Dictionary = data.models[key]
		var path := "res://assets/models/"+str(spec.file)
		assert(FileAccess.get_sha256(path) == spec.sha256)
		var remap := ConfigFile.new()
		assert(remap.load(path+".import") == OK)
		var imported: String = remap.get_value("remap","path","")
		assert(not imported.is_empty() and FileAccess.file_exists(imported))
		var md5 := ConfigFile.new()
		assert(md5.load(imported.get_basename()+".md5") == OK)
		assert(md5.get_value("","source_md5","") == FileAccess.get_md5(path), "Stale derivative import")

func check_contacts(node: Node3D, spec: Dictionary) -> void:
	var count := 0
	for mesh in node.find_children("*","MeshInstance3D",true,false):
		assert(mesh.mesh != null and mesh.material_override == null)
		var physical: bool = spec.collision == "concave_static_surface"
		if spec.has("meshes"):
			assert(spec.meshes.has(str(mesh.name)))
			physical = spec.meshes[str(mesh.name)].physical
		var contact := mesh.get_node_or_null("StaticContact")
		assert((contact != null) == physical, "Wrong per-mesh contact policy: "+str(mesh.name))
		if physical:
			var shapes := contact.find_children("*","CollisionShape3D",true,false)
			assert(not shapes.is_empty())
			for shape in shapes:
				assert(shape.shape is ConcavePolygonShape3D and not shape.disabled)
				assert(shape.shape.get_faces().size() > 0)
		count += 1
	if spec.has("meshes"): assert(count == spec.meshes.size())
	else: assert(count > 0)

func structure() -> void:
	assert(furniture.get_child_count() == 51 and data.logical_furnishing_count == 126)
	assert(floors.get_child_count() == int(data.compiler_owner_count))
	assert(data.placements.size() == 71 and data.assemblies.size() == 3)
	assert(built.get_child_count() == 88)
	for entry in data.assemblies: check_contacts(item(str(entry.name)),data.models[str(entry.asset)])
	for entry in data.placements:
		var node := item(str(entry.name))
		assert(node.global_position.distance_to(xyz(entry.position_xyz)) < .0001)
		assert(absf(node.rotation.y-float(entry.yaw_radians)) < .00001 and node.scale == Vector3.ONE)
		var lo := Vector3(INF,INF,INF)
		var hi := Vector3(-INF,-INF,-INF)
		for mesh in node.find_children("*","MeshInstance3D",true,false):
			for i in range(8):
				var p: Vector3 = mesh.global_transform*mesh.get_aabb().get_endpoint(i)
				lo=lo.min(p);hi=hi.max(p)
		assert(lo.distance_to(xyz(entry.envelope_min_xyz)) < .003 and hi.distance_to(xyz(entry.envelope_max_xyz)) < .003,"Imported bounds drift: "+str(entry.name))
		check_contacts(node,data.models[str(entry.asset)])
	assert(ray(Vector3(-31,52.6,-432),Vector3(-31,52.4,-432),[actor.get_rid()]).is_empty(),"New finish illegally bridges the pool void")

func support_checks() -> void:
	for probe in data.support_probes:
		var p := xyz(probe.position_xyz)
		var hit := ray(p+Vector3.UP*.018,p-Vector3.UP*.018,exclusions(item(str(probe.item))))
		assert(not hit.is_empty() and absf(hit.position.y-p.y)<.003,"Unsupported actual exported root/foot: "+str(probe))
		var host: Node3D
		if probe.host == "original_architecture": host = original.get_node("GrandPoolConnectedArchitecture")
		elif str(probe.host).begins_with("D09_"): host = floors.get_node(NodePath(str(probe.host)))
		else: host = item(str(probe.host))
		assert(host.is_ancestor_of(hit.collider),"Wrong physical support owner for "+str(probe.item))
		supports += 1

func contains_world(mesh: MeshInstance3D, world: Vector3) -> bool:
	# Generalized winding number on actual imported triangles, in local coordinates.
	# The bark batches contain closed support solids, not the visual open leaves.
	var point := mesh.to_local(world)
	var vertices := mesh.mesh.get_faces()
	var angle := 0.0
	for i in range(0,vertices.size(),3):
		var a: Vector3 = vertices[i]-point
		var b: Vector3 = vertices[i+1]-point
		var c: Vector3 = vertices[i+2]-point
		var denominator := a.length()*b.length()*c.length()+a.dot(b)*c.length()+b.dot(c)*a.length()+c.dot(a)*b.length()
		angle += 2.0*atan2(a.dot(b.cross(c)),denominator)
	return absf(angle)>2.0*PI

func crown_contact_checks() -> void:
	assert(data.retained_crown_joins.size()==5)
	for join in data.retained_crown_joins:
		var new_mesh := item(str(join.item)).find_child(str(join.new_mesh),true,false) as MeshInstance3D
		var retained := item(str(join.retained_item)).find_child(str(join.retained_mesh),true,false) as MeshInstance3D
		var marker := item(str(join.item)).find_child(str(join.marker),true,false) as Node3D
		assert(new_mesh != null and retained != null and marker != null)
		var center := xyz(join.position_xyz)
		assert(marker.global_position.distance_to(center)<.00005)
		for direction in [Vector3.ZERO,Vector3.UP,Vector3.DOWN,Vector3.LEFT,Vector3.RIGHT,Vector3.FORWARD,Vector3.BACK]:
			var p: Vector3=center+direction*float(join.interior_radius_m)
			assert(contains_world(new_mesh,p) and contains_world(retained,p),"Fullness whorl lost its real retained crown joint: "+str(join.item))

func source_lights() -> void:
	var lights := built.find_children("GrandPoolFinishSource_*","SpotLight3D",true,false)
	assert(lights.size()==14)
	for entry in data.fixtures:
		var light := built.get_node("GrandPoolFinishSource_"+str(entry.name)) as SpotLight3D
		assert(light.global_position.distance_to(xyz(entry.position_xyz)) < .00005)
		assert((-light.global_basis.z).normalized().dot(xyz(entry.direction_xyz).normalized()) > .999999)
		assert(is_equal_approx(light.light_energy,float(entry.suggested_energy)))
		assert(is_equal_approx(light.spot_range,float(entry.suggested_range_m)))
		assert(is_equal_approx(light.spot_angle,float(entry.suggested_spot_angle_degrees)))
		assert(light.get_meta("illumination_anchor").distance_to(xyz(entry.receiver_xyz)) < .00001)
		var delta := xyz(entry.receiver_xyz)-light.global_position
		assert(delta.length()<light.spot_range and delta.normalized().dot(-light.global_basis.z)>=cos(deg_to_rad(light.spot_angle)))
		var budget: Node = ship.get_node("ShipSystems/LocalShadowSourceBudget")
		assert(budget._clear_sample(light.global_position,xyz(entry.receiver_xyz)),"Actual new fixture cannot reach its authored receiver: "+str(entry.name))

func sample_lights(label: String) -> void:
	var budget: Node = ship.get_node("ShipSystems/LocalShadowSourceBudget")
	budget.refresh()
	var active: Array[String] = []
	for light in budget.sources:
		if not budget.requested_shadow[light.get_instance_id()]: continue
		assert(light.visible == light.shadow_enabled)
		if light.visible:
			assert(budget._has_visible_sample(light))
			active.append(str(light.name))
			if str(light.name).begins_with("GrandPoolFinishSource_"): selected_new_sources[str(light.name)] = true
	assert(active.size() <= 8)
	print("POOL FINISH LIGHT SAMPLE ",label," ",active)

func signage_and_media() -> void:
	var signs := item("GrandPoolFinishWayfinding")
	for sign in data.signs:
		var board := signs.find_child("SIGN_"+str(sign.id),true,false) as Node3D
		assert(board != null)
		var backing := signs.find_child("PWF_"+str(sign.id)+"_MapBacking",true,false) as MeshInstance3D
		assert(backing != null)
		var p := xyz(sign.origin_xyz)+xyz(sign.normal_xyz)*.124
		var hit := ray(xyz(sign.viewpoint_xyz),p-xyz(sign.normal_xyz)*.01,[actor.get_rid()])
		assert(not hit.is_empty() and backing.is_ancestor_of(hit.collider),"Sign sightline does not reach physical board: "+str(sign.id))
	var display := item("GrandPoolComfortDisplays")
	var screens := 0
	for mesh in display.find_children("*","MeshInstance3D",true,false):
		if not str(mesh.name).ends_with("original_pool_leisure_image"): continue
		var mat := mesh.get_active_material(0) as StandardMaterial3D
		assert(mat != null and mat.albedo_texture != null and mat.emission_enabled)
		assert(mat.albedo_texture.get_width() >= 512 and mat.albedo_texture.get_height() >= 256)
		assert(mesh.get_node_or_null("StaticContact") == null)
		screens += 1
	assert(screens==4)
	for index in range(data.media_candidates.size()):
		var candidate: Dictionary = data.media_candidates[index]
		var prefix := "WET" if index == 3 else "M"+str(index)
		var glazing := display.find_child(prefix+"__recessed_display_glazing",true,false) as MeshInstance3D
		assert(glazing != null)
		for probe in candidate.sampled_current_triangle_sightlines:
			var target := xyz(probe.target_xyz)
			var eye := xyz(probe.eye_xyz)
			# Image plane stays visual. Physical ray reaches its immediately backed glazing.
			var delta := (target-eye).normalized()
			var hit := ray(eye,target+delta*.04,[actor.get_rid()])
			assert(not hit.is_empty() and glazing.is_ancestor_of(hit.collider) and hit.position.distance_to(target)<.03,"Seated display image is physically occluded: "+str(candidate.name))

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
		var v:=delta.normalized()*3.1
		actor.velocity=Vector3(v.x,-.1 if actor.is_on_floor() else actor.velocity.y-9.8/60,v.z)
		actor.move_and_slide()
		await physics_frame
		walked+=1
		assert(absf(actor.position.y-target.y)<.18 and walked<30000)
	assert(reached,"Stock approach obstructed at %s toward %s" %[actor.position,target])

func run() -> void:
	data=JSON.parse_string(FileAccess.get_file_as_string(CONTRACT));pins()
	var main: Node=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
	for f in range(90): await physics_frame
	ship=main.get_node("World360/Astraea");actor=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false)
	space=ship.get_world_3d().direct_space_state;built=ship.find_child("GrandPoolFinish_WIP",true,false);original=ship.find_child("GrandPoolOrchardSection_WIP",true,false);furniture=ship.find_child("GrandPoolFirstPassEssentials_WIP",true,false);floors=ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms")
	assert(built != null and furniture != null)
	structure();support_checks();crown_contact_checks();source_lights();signage_and_media()
	for path in data.stock_approach_paths:
		await settle(xyz(path.points_xyz[0]))
		for p in path.points_xyz: await walk_to(xyz(p))
		sample_lights(str(path.display))
		var reverse: Array=path.points_xyz.duplicate();reverse.reverse()
		for p in reverse: await walk_to(xyz(p))
	for p in [[-45.9,46.2,-451],[-45.9,46.2,-444],[-45.9,46.2,-433],[-45.9,46.2,-425],[-45.9,46.2,-416],[-45.9,52.5,-451],[-45.9,52.5,-433],[-45.9,52.5,-416]]:
		await settle(xyz(p));sample_lights(str(p))
	assert(not selected_new_sources.is_empty(),"No source-backed finish light participates in the unchanged budget")
	pins()
	print("GRAND POOL FINISH PASS: preserved 51; 48 stocked furnishings, 23 fuller botanical derivatives, 4 housed leisure displays, 11 mounted signs, 14 source fixtures; ",supports," exported foot/root support probes; six supported stock approaches; unchanged eight-source budget. Selected new sources: ",selected_new_sources.keys(),". Retained route/cart/lift checks and actual visual acceptance remain separate.")
	main.queue_free();await process_frame;quit(0)
