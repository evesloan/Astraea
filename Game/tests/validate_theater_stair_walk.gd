extends SceneTree
const MEDICAL_RETAINED = preload("res://tests/medical_successor_guard.gd")
# DRAFT UNRUN. Actual reopened source proved; final native/control pins pending.
const ROUTE := "res://tests/fixtures/THEATER_STAIR_WALK_ROUTE_011.json"
const CONTACTS := "res://data/architecture/THEATER_STAIR_WALK_CONTACTS_011.json"
const RESULT := "res://artifacts/theater_stair_walk_011.json"
var contact_frames: Dictionary = {}
var started := Time.get_ticks_msec()
var probe = preload("res://tests/theater_stage_probe.gd").new()
var contract: Dictionary
var trace: Array = []
var ramp_root: Node3D
var ramp_rows: Dictionary = {}
var phase := "initial"
var failure := ""
var frames := 0
var travelled := 0.0
var peak_speed := 0.0
var last := Vector3.ZERO
func _initialize() -> void: call_deferred("run")
func xyz(a: Array) -> Vector3: return Vector3(a[0],a[1],a[2])
func as_array(v: Vector3) -> Array: return [v.x,v.y,v.z]
func key(down: bool) -> void:
	var event := InputEventKey.new();event.keycode=KEY_W;event.physical_keycode=KEY_W;event.pressed=down
	Input.parse_input_event(event);Input.flush_buffered_events()
func _process(_delta: float) -> bool:
	if Time.get_ticks_msec()-started>600000:
		key(false)
		push_error("Theater integrated stair walk 600-second watchdog")
		quit(1)
	return false
func inspect_integrated_contacts() -> void:
	var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(CONTACTS))
	var source: Dictionary=data.source_reopen_evidence
	for pair in [[source.qa_path,source.qa_sha256],[source.actual_export_path,source.actual_export_sha256],[source.source_checked_contract_path,source.source_checked_contract_sha256],[source.run_receipt_path,source.run_receipt_sha256],[source.catalogue_retention_manifest_path,source.catalogue_retention_manifest_sha256]]:
		assert(FileAccess.get_sha256("res://"+str(pair[0]))==str(pair[1]),"Source contact evidence changed")
	var qa: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://"+str(source.qa_path)))
	assert(qa.status=="PASS_REOPENED_SOURCE_CONTACTS" and qa.reopened_test_run and qa.original_source_hashes_unchanged)
	assert(qa.contacts==8 and qa.literal_treads_preserved==90 and qa.width_m==3.2 and qa.vertical_thickness_m==.04 and qa.margin_m==.001)
	assert(qa.max_reopened_vertex_error_m<=.00002 and qa.blend_sha256==source.blend_sha256 and qa.reopened_export_sha256==source.actual_export_sha256)
	var checked: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://"+str(source.source_checked_contract_path)))
	var exported: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://"+str(source.actual_export_path)))
	assert(exported.objects.size()==8 and exported.blend_sha256==source.blend_sha256)
	var actual_meshes: Dictionary={}
	for mesh in exported.objects:
		assert(not actual_meshes.has(str(mesh.id)))
		actual_meshes[str(mesh.id)]=mesh
	assert(FileAccess.get_sha256("res://"+str(data.runtime_vertex_binding.proof_path))==str(data.runtime_vertex_binding.proof_sha256))
	var geometry: Dictionary=data.duplicate(true)
	geometry.erase("source_reopen_evidence")
	geometry.erase("runtime_vertex_binding")
	for i in range(8):
		var current: Dictionary=geometry.contacts[i]
		var original: Dictionary=checked.contacts[i]
		var actual: Dictionary=actual_meshes[str(current.id)]
		assert(current.id==original.id and current.vertices_world==actual.vertices_world and current.faces==actual.faces)
		assert(current.top_quad_world==actual.vertices_world.slice(0,4) and current.shape_margin_m==.001)
		current.vertices_world=original.vertices_world
		current.top_quad_world=original.top_quad_world
	assert(geometry==checked,"Only exact reopened vertex readback plus its source evidence may differ from the checked source contract")
	ramp_root=probe.ship.get_node("ShipSpace/Districts/GrandLanternTheater_StairWalkingContacts")
	assert(ramp_root!=null and ramp_root.get_parent()==probe.venue.get_parent() and not probe.venue.is_ancestor_of(ramp_root))
	assert(ramp_root.global_transform.is_equal_approx(Transform3D.IDENTITY) and ramp_root.get_child_count()==8)
	assert(ramp_root.find_children("*","GeometryInstance3D",true,false).is_empty())
	for row in data.contacts:
		var body:=ramp_root.get_node(str(row.id)) as StaticBody3D
		assert(body!=null and body.get_child_count()==1 and body.transform.is_equal_approx(Transform3D.IDENTITY))
		assert(body.collision_layer==1 and body.collision_mask==1 and body.get_meta("source_flight_id")==row.source_flight.id)
		assert(body.get_meta("walking_contact_approximation") and body.get_meta("non_rendered") and body.get_meta("original_meshes_and_contacts_retained"))
		var collider:=body.get_child(0) as CollisionShape3D
		assert(collider!=null and not collider.disabled and collider.transform.is_equal_approx(Transform3D.IDENTITY))
		var shape:=collider.shape as ConvexPolygonShape3D
		assert(shape!=null and absf(shape.margin-.001)<.000001 and shape.points.size()==8)
		assert(shape.points.to_byte_array().size()==96,"Require eight standard float32 Vector3 contact points")
		for i in range(8):assert(shape.points[i]==xyz(row.vertices_world[i]),"Runtime contact point must exactly equal reopened source")
		ramp_rows[str(body.name)]=row
		contact_frames[str(body.name)]={"outward":0,"return":0}
	assert(ramp_rows.size()==8)
func sample() -> bool:
	frames+=1
	var actor: CharacterBody3D=probe.actor
	var step:=Vector2(actor.global_position.x-last.x,actor.global_position.z-last.z).length()
	if not actor.global_position.is_finite() or step>.08: failure="Discontinuous actor travel";return false
	travelled+=step;last=actor.global_position
	peak_speed=maxf(peak_speed,Vector2(actor.velocity.x,actor.velocity.z).length())
	var hit:=probe.ray(actor.global_position+Vector3.UP*.20,actor.global_position-Vector3.UP*.24,probe.exclusions())
	var expected: Array=[]
	if not hit.is_empty() and probe.shell.is_ancestor_of(hit.collider) and hit.normal.y>.7:
		for surface in contract.flat_source_surfaces:
			var bounds: Array=surface.bounds_xz
			if absf(hit.position.y-float(surface.top_y))>=.003 or hit.position.x<float(bounds[0])-.002 or hit.position.x>float(bounds[2])+.002 or hit.position.z<float(bounds[1])-.002 or hit.position.z>float(bounds[3])+.002: continue
			var polygon:=PackedVector2Array()
			for point in surface.boundary_xz:polygon.append(Vector2(point[0],point[1]))
			if Geometry2D.is_point_in_polygon(Vector2(hit.position.x,hit.position.z),polygon):expected.append(str(surface.owner))
	elif not hit.is_empty() and ramp_root.is_ancestor_of(hit.collider) and hit.normal.y>.7:
		var row: Dictionary=ramp_rows[str(hit.collider.name)]
		var a:=xyz(row.top_quad_world[0]);var b:=xyz(row.top_quad_world[2])
		var top_y: float=a.y+(hit.position.z-a.z)*(b.y-a.y)/(b.z-a.z)
		assert(absf(hit.position.y-top_y)<.003)
		expected.append(str(row.id))
		if phase.begins_with("outward:"): contact_frames[str(row.id)]["outward"]+=1
		elif phase.begins_with("return:"): contact_frames[str(row.id)]["return"]+=1
	elif not hit.is_empty() and probe.floors.is_ancestor_of(hit.collider) and hit.normal.y>.7:
		var identity:=str(hit.collider.get_parent().name)
		if identity in contract.compiled_route_owners and absf(hit.position.y-69.5)<.003: expected.append(identity)
	var collisions: Array=[]
	for i in range(actor.get_slide_collision_count()):
		var c:=actor.get_slide_collision(i)
		collisions.append({"path":str(c.get_collider().get_path()),"normal":as_array(c.get_normal()),"position":as_array(c.get_position())})
	trace.append({"frame":frames,"phase":phase,"position":as_array(actor.global_position),"velocity":as_array(actor.velocity),"is_on_floor":actor.is_on_floor(),"support":{}if hit.is_empty()else{"path":str(hit.collider.get_path()),"position":as_array(hit.position),"normal":as_array(hit.normal),"matched_authored_surfaces":expected},"slide_contacts":collisions})
	if expected.is_empty():failure="No actual approved route support beneath capsule";return false
	if actor.global_position.x< -80 or actor.global_position.x>0 or actor.global_position.y<69.45 or actor.global_position.y>84.15 or frames>20000:failure="Capsule left the bounded two-level route";return false
	return true
func walk(target: Vector3) -> bool:
	var actor: CharacterBody3D=probe.actor
	var initial_distance:=Vector2(target.x-actor.global_position.x,target.z-actor.global_position.z).length()
	for frame in range(ceili(initial_distance/3.1*60)+360):
		var delta:=Vector3(target.x-actor.global_position.x,0,target.z-actor.global_position.z)
		var speed:=Vector2(actor.velocity.x,actor.velocity.z).length()
		if delta.length()<.075 and speed<.08:
			key(false)
			if absf(actor.global_position.y-target.y)>.14:failure="Horizontal target reached on wrong vertical surface";return false
			return true
		actor.rotation.y=atan2(-delta.x,-delta.z)
		key(delta.length()>.06+speed*speed/32.0)
		await physics_frame
		if not sample():key(false);return false
	key(false);failure="Ordinary W movement stalled before the authored landing";return false
func run() -> void:
	assert(FileAccess.get_sha256(ROUTE)=="e338ff35145c66d400f8566d1d141917114a153f92c949e6ae21c3aa4279dfbf")
	contract=JSON.parse_string(FileAccess.get_file_as_string(ROUTE))
	assert(contract.adoption_ready and contract.pending_final_pins.is_empty(),"Final native/engineering source pins and coordinated adoption are still pending")
	for path in contract.input_sha256:assert(load("res://tests/theater_stair_ship_successor.gd").retained_input_sha256(str(path))==str(contract.input_sha256[path]))
	assert(contract.unsupported.is_empty() and contract.forward_waypoints.size()==42)
	var main: Node=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
	for frame in range(90):await physics_frame
	probe.configure(main.get_node("World360/Astraea"));probe.check_motion_poses_and_barriers()
	load("res://tests/secondary_engineering_additive_guard.gd").validate(JSON.parse_string(MEDICAL_RETAINED.retained_text("res://data/generated/structural_meshes.json")))
	probe.check_import_and_scene_census()
	probe.check_instances()
	inspect_integrated_contacts()
	for frame in range(3):await physics_frame
	var start:=xyz(contract.forward_waypoints[0].xyz)+Vector3.UP*.1
	assert(probe.ship.arrive_at(start,PI/2),"Actual supported fore-spine start required")
	probe.actor.set_controls_enabled(true)
	for frame in range(30):await physics_frame
	last=probe.actor.global_position
	var okay:=sample();var reached_waypoints: Array=[]
	if okay:
		for i in range(1,contract.forward_waypoints.size()):
			var row: Dictionary=contract.forward_waypoints[i];phase="outward: "+str(row.label)
			var reached: bool=await walk(xyz(row.xyz))
			if not reached:okay=false;break
			reached_waypoints.append(phase);probe.check_lights(phase)
	var ascended:=okay
	if okay:
		for i in range(contract.forward_waypoints.size()-2,-1,-1):
			var row: Dictionary=contract.forward_waypoints[i];phase="return: "+str(row.label)
			var reached: bool=await walk(xyz(row.xyz))
			if not reached:okay=false;break
			reached_waypoints.append(phase);probe.check_lights(phase)
	key(false);probe.check_motion_poses_and_barriers()
	var every_contact_both_ways:=true
	for id in contact_frames:
		if contact_frames[id].outward<1 or contact_frames[id]["return"]<1:every_contact_both_ways=false
	var passed: bool=okay and ascended and peak_speed>3.05 and peak_speed<=3.101 and reached_waypoints.size()==82 and every_contact_both_ways
	if failure.is_empty()and not passed:failure="Normal speed or full return criterion not established"
	var result: Dictionary={"status":"PASS_INSTALLED_STAIR_WALK_011"if passed else"FAILED_INSTALLED_STAIR_WALK_011","failure":failure,"ascended_both_levels":ascended,"returned":okay,"frames":frames,"travelled_m":travelled,"peak_speed":peak_speed,"route_contract_sha256":FileAccess.get_sha256(ROUTE),"input_sha256":contract.input_sha256,"source_geometry_and_controller_unchanged":true,"connected_installed_foyer_route_proven":passed,"auditorium_seat_aisles_proven":false,"diagnostic_ramps_added":0,"installed_contacts_checked":8,"contact_frames":contact_frames,"carts_on_stairs_proven":false,"court_interiors_proven":false,"proposal_sha256":FileAccess.get_sha256(CONTACTS),"installed":true,"reached_waypoints":reached_waypoints,"trace":trace}
	var file:=FileAccess.open(RESULT,FileAccess.WRITE);file.store_string(JSON.stringify(result,"  "));file.close()
	if passed: print("PASS: THEATER INSTALLED STAIR WALK 011; all82 destinations, actual eight contacts up/down, retained meshes/contacts and closed interfaces; no court/seat-aisle/cart acceptance")
	else: push_error("FAILED: THEATER INSTALLED STAIR WALK 011: "+failure)
	quit(0 if passed else 1)
