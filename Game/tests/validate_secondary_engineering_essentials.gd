extends SceneTree
const MEDICAL_RETAINED = preload("res://tests/medical_successor_guard.gd")
# Actual additive contents/fixture checks and reachable guest-side diagnostics.
const CONTRACT := "res://data/architecture/SECONDARY_ENGINEERING_ESSENTIALS_TRIAL.json"
const SOURCE_RECEIVER_POINTS := {
	"DATUM_plant_inspection_n": Vector3(30.16106772205277,8.764956402776807,-433.56037766041635),
	"DATUM_plant_inspection_s": Vector3(38.83893227794723,8.764956402776805,-430.43962233958365),
	"DATUM_control_task": Vector3(26.0,7.489921475648871,-462.70419389009476),
	"DATUM_workbay_task": Vector3(26.485081554848556,6.935999870300293,-401.2925871949095),
	"DATUM_isolation_task": Vector3(36.0,7.438012905120863,-441.5957946777344)
}
var actor: CharacterBody3D
var ship: Node3D
var space: PhysicsDirectSpaceState3D
var floors: Node3D
var walked_frames := 0
var data: Dictionary

func _initialize() -> void:
	call_deferred("run")

func xyz(a: Array) -> Vector3:
	return Vector3(a[0],a[1],a[2])

func ray(a: Vector3, b: Vector3) -> Dictionary:
	var query := PhysicsRayQueryParameters3D.create(a,b,1)
	query.exclude = [actor.get_rid()]
	query.hit_back_faces = true
	return space.intersect_ray(query)

func walk_to(point: Vector2) -> void:
	var reached := false
	for frame in range(1300):
		var delta := Vector3(point.x-actor.global_position.x,0,point.y-actor.global_position.z)
		if delta.length()<.07:
			reached = true
			break
		actor.velocity.x = delta.normalized().x*2.0
		actor.velocity.z = delta.normalized().z*2.0
		actor.velocity.y = -.1 if actor.is_on_floor() else actor.velocity.y-9.8/60.0
		actor.move_and_slide()
		assert(absf(actor.global_position.y-6)<.15,"Guest viewpoint route lost Y6 support")
		walked_frames += 1
		await physics_frame
	assert(reached,"Guest-side diagnostic must be reached by actual capsule walking")
	var hit := ray(Vector3(point.x,6.10,point.y),Vector3(point.x,5.90,point.y))
	assert(not hit.is_empty() and floors.is_ancestor_of(hit.collider) and absf(hit.position.y-6)<.015)

func actual_contact_triangle_hits(section: Node3D, start: Vector3, end: Vector3, exclude_cell_baseline: bool = false) -> Array:
	var nearest_by_mesh: Dictionary = {}
	for item in section.find_children("*", "CollisionShape3D", true, false):
		var contact := item as CollisionShape3D
		# This retained-source-only comparison is additional to the complete composed physics ray below.
		if exclude_cell_baseline and "SecondaryEngineeringWorkbayCell" in str(contact.get_path()): continue
		if contact.disabled or not contact.shape is ConcavePolygonShape3D: continue
		var label := str(contact.get_parent().get_parent().name)
		var faces := (contact.shape as ConcavePolygonShape3D).get_faces()
		for index in range(0,faces.size(),3):
			var a := contact.global_transform*faces[index]
			var b := contact.global_transform*faces[index+1]
			var c := contact.global_transform*faces[index+2]
			var hit: Variant = Geometry3D.segment_intersects_triangle(start,end,a,b,c)
			if not hit is Vector3: continue
			var point: Vector3 = hit
			var distance := start.distance_to(point)
			if not nearest_by_mesh.has(label) or distance<float(nearest_by_mesh[label].distance):
				nearest_by_mesh[label] = {"node":label,"distance":distance,"point_xyz":[point.x,point.y,point.z],"triangle_xyz":[[a.x,a.y,a.z],[b.x,b.y,b.z],[c.x,c.y,c.z]]}
	var hits: Array = nearest_by_mesh.values()
	hits.sort_custom(func(a:Dictionary,b:Dictionary)->bool:return float(a.distance)<float(b.distance))
	return hits.slice(0,6)

func run() -> void:
	data = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	assert(data.adoption_gate_accepted and data.light_trial_values_accepted_for_test and not data.first_pass_essentials_accepted)
	var import_settings := ConfigFile.new()
	assert(import_settings.load("res://assets/models/"+str(data.model_file)+".import")==OK)
	assert(import_settings.get_value("params","meshes/force_disable_compression",false)==true,"Preserve submillimetre layered receiver geometry on this new asset")
	for path in data.retained_runtime_pins:
		load("res://tests/secondary_engineering_additive_guard.gd").validate_pinned_input(str(path),str(data.retained_runtime_pins[path]))
	assert(FileAccess.get_sha256("res://assets/models/"+str(data.model_file))==str(data.model_sha256))
	var main := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(90): await physics_frame
	ship = main.get_node("World360/Astraea")
	actor = ship.get_node("ShipSpace/PersistentActors/Player")
	actor.set_physics_process(false)
	space = ship.get_world_3d().direct_space_state
	floors = ship.find_child("CompiledStructuralFloors_NotFinishedRooms",true,false)
	var compiled: Dictionary = JSON.parse_string(MEDICAL_RETAINED.retained_text("res://data/generated/structural_meshes.json"))
	load("res://tests/secondary_engineering_additive_guard.gd").validate(compiled)
	validate_loaded_theater_roster(compiled)
	var root_section: Node3D = ship.find_child("SecondaryEngineeringSection_WIP",true,false)
	var contents: Node3D = root_section.get_node("SecondaryEngineeringEssentials_Trial")
	assert(root_section.get_meta("first_pass_quality_accepted")==false)
	assert(contents.position==Vector3.ZERO and contents.rotation==Vector3.ZERO and contents.scale==Vector3.ONE)
	var triangle_count := 0
	var contact_groups := 0
	var print_groups := 0
	var meshes := contents.find_children("*","MeshInstance3D",true,false)
	assert(meshes.size()==9)
	for node in meshes:
		var mesh := node as MeshInstance3D
		var expected: Dictionary = data.groups[str(mesh.name)]
		assert(mesh.is_visible_in_tree() and mesh.material_override==null)
		assert(mesh.mesh.get_surface_count()==1 and mesh.mesh.get_faces().size()==int(expected.triangles)*3)
		assert(mesh.get_active_material(0).resource_name==str(expected.material_name),"Imported material identity changed")
		triangle_count += int(mesh.mesh.get_faces().size()/3)
		var contact := mesh.get_node_or_null("StaticContact/SharedShape") as CollisionShape3D
		if str(expected.collision_contract)=="none":
			assert(contact==null,"Pigment-only faces may not invent a blocking plane")
			print_groups += 1
		else:
			assert(contact!=null and not contact.disabled and contact.shape is ConcavePolygonShape3D)
			assert((contact.shape as ConcavePolygonShape3D).get_faces().size()==mesh.mesh.get_faces().size(),"No convex cavity fill or simplified blocking proxy")
			contact_groups += 1
	assert(triangle_count==69748 and contact_groups==8 and print_groups==1)
	var budget: Node = ship.find_child("LocalShadowSourceBudget",true,false)
	var sources := root_section.find_children("SecondaryEngineeringSource_*","SpotLight3D",true,false)
	assert(sources.size()==9 and contents.find_children("*","Light3D",true,false).is_empty())
	assert(budget.shadow_source_budget==8)
	var records: Array = []
	var receiver_failures: Array = []
	var tuned: Dictionary = {}
	for item in data.local_light_trial:
		var name := str(item.marker)
		var light := root_section.find_child("SecondaryEngineeringSource_"+name,true,false) as SpotLight3D
		assert(light!=null and budget.sources.has(light))
		assert(light.global_position.distance_to(xyz(item.expected_emitter_xyz))<.0001)
		var target := xyz(item.aim_xyz)
		var direction := (target-light.global_position).normalized()
		assert((-light.global_basis.z).dot(direction)>.99999)
		assert(is_equal_approx(light.spot_range,float(item.range_m)) and is_equal_approx(light.light_energy,float(item.energy)) and is_equal_approx(light.spot_angle,float(item.spot_angle)))
		assert(ray(light.global_position,light.global_position+direction*.10).is_empty(),"Aimed ray trapped in real fixture housing")
		var receiver := ray(light.global_position,target+direction*.15)
		assert(not receiver.is_empty(),"Expected real source receiver absent")
		var expected_point: Vector3 = SOURCE_RECEIVER_POINTS[name]
		var expected_group := str(data.ray_first_contact_names[name])
		var chain: Dictionary = load("res://tests/secondary_engineering_additive_guard.gd").section_proof()
		if chain.receiver_successors.has(name):
			var successor: Dictionary = chain.receiver_successors[name]
			assert(expected_group==str(successor.historical_group) and expected_point.distance_to(xyz(successor.historical_point_xyz))<.000001)
			var retained_hits := actual_contact_triangle_hits(root_section,light.global_position,target+direction*.15,true)
			assert(not retained_hits.is_empty() and str(retained_hits[0].node)==expected_group)
			assert(xyz(retained_hits[0].point_xyz).distance_to(expected_point)<.001,"Retained source receiver still required independently")
			expected_point = xyz(successor.composed_point_xyz)
			expected_group = str(successor.composed_group)
			assert("SecondaryEngineeringWorkbayCell" in str(receiver.collider.get_path()),"New receiver requires exact cell ancestry")
		assert(receiver.position.distance_to(expected_point)<.001,"Actual receiver position exceeds original1mm source/import geometry tolerance")
		assert(absf(light.global_position.distance_to(receiver.position)-light.global_position.distance_to(expected_point))<.001,"Receiver distance exceeds1mm source tolerance")
		var geometry_hits := actual_contact_triangle_hits(root_section,light.global_position,target+direction*.15)
		print("IMPORTED CONTACT RECEIVER TRIANGLES:",JSON.stringify({"marker":name,"physics_node":str(receiver.collider.get_parent().name),"physics_point":[receiver.position.x,receiver.position.y,receiver.position.z],"triangles":geometry_hits}))
		if str(receiver.collider.get_parent().name)!=expected_group:
			receiver_failures.append({"marker":name,"expected":expected_group,"actual":str(receiver.collider.get_parent().name),"physics_point_xyz":[receiver.position.x,receiver.position.y,receiver.position.z],"actual_contact_triangles":geometry_hits})
		records.append({"marker":name,"receiver":str(receiver.collider.get_path()),"point":str(receiver.position)})
		tuned[name] = true
	assert(tuned.size()==5)
	var receiver_file := FileAccess.open("res://artifacts/engineering_receiver_contact_diagnostic.json",FileAccess.WRITE)
	receiver_file.store_string(JSON.stringify({"mismatches":receiver_failures},"  "))
	assert(receiver_failures.is_empty(),"Receiver material-group mismatches retained for triangle reconciliation; no assertion bypass")
	for item in sources:
		var light := item as SpotLight3D
		var name := str(light.get_meta("source_marker"))
		if tuned.has(name): continue
		assert(is_equal_approx(light.spot_range,6.0) and is_equal_approx(light.spot_angle,76.0))
		assert(is_equal_approx(light.light_energy,.85 if name=="DATUM_entry" else 1.0))
		assert((-light.global_basis.z).distance_to(Vector3.DOWN)<.0001)
	actor.global_position = Vector3(12,6.04,-432)
	actor.velocity = Vector3.ZERO
	var selection: Array = []
	for segment in data.guest_view_route_xz:
		await walk_to(Vector2(segment.to_xz[0],segment.to_xz[1]))
		budget.refresh()
		var active := 0
		for light in budget.sources:
			if light.visible and light.shadow_enabled: active+=1
		assert(active<=8)
		var visible: Array = []
		for light in sources:
			if light.visible and light.shadow_enabled: visible.append(str(light.get_meta("source_marker")))
		selection.append({"actor":str(actor.global_position),"active_ship_sources":active,"engineering_sources":visible})
	var file := FileAccess.open("res://artifacts/secondary_engineering_essentials_diagnostic.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"scope":"Runtime geometry/receiver/selection evidence only; actual visual acceptance pending","receivers":records,"guest_route_selection":selection,"walked_frames":walked_frames},"  "))
	print("SECONDARY ENGINEERING ESSENTIALS PASS: 69748 actual mesh/contact triangles in9groups;8concave contacts and1pigment-only group;5local existing-fixture trials, unchanged4sources and cap8; reachable guest-side capsule route frames:",walked_frames,". Existing access/loaded-cart, normal-eye visuals, independent staff connection and first-pass completion remain separate gates.")
	main.queue_free()
	await process_frame
	quit()

# The authenticated nine-record theater addition changes the global roster only.
# validate(compiled) above still proves every old258/current engineering4 record.
func validate_loaded_theater_roster(compiled: Dictionary) -> void:
	var guard = load("res://tests/secondary_engineering_additive_guard.gd")
	assert(FileAccess.get_sha256(guard.THEATER_PROPOSAL)==guard.THEATER_PROPOSAL_SHA)
	var proposal: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(guard.THEATER_PROPOSAL))
	var additions: Dictionary = proposal.new_compiled_records
	var approved_ids: Array = guard.ALLOWED_THEATER_COMPILED_IDS.duplicate()
	var added_ids: Array = additions.keys()
	approved_ids.sort()
	added_ids.sort()
	assert(added_ids==approved_ids and additions.size()==9,"Exactly the authenticated nine theater owners required")
	assert(compiled.regions.size()==271 and MEDICAL_RETAINED.retained_owner_count(floors)==271,"Exact reviewed combined floor count required")
	var current: Dictionary = {}
	for row in compiled.regions:
		assert(not current.has(str(row.id)),"Duplicate compiled owner")
		current[str(row.id)] = row
	for id in approved_ids:
		assert(current.has(id) and current[id]==additions[id],"Whole theater record changed: "+str(id))
	var loaded_ids: Array = []
	for owner in MEDICAL_RETAINED.retained_floor_children(floors):
		var id := str(owner.name)
		assert(current.has(id) and not loaded_ids.has(id),"Unknown or duplicate loaded floor owner: "+id)
		loaded_ids.append(id)
	var compiled_ids: Array = current.keys()
	compiled_ids.sort()
	loaded_ids.sort()
	assert(loaded_ids==compiled_ids,"Every exact compiled owner must exist in the loaded world")
