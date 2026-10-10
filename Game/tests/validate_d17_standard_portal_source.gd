extends SceneTree
# Source-only fixture. The actual main scene retains its closed source wall.
var errors: Array = []
var checks: Dictionary = {}
func record(key: String, ok: bool) -> void:
	checks[key] = ok
	if not ok: errors.append(key)
func ray(space: PhysicsDirectSpaceState3D, a: Vector3, b: Vector3) -> Dictionary:
	return space.intersect_ray(PhysicsRayQueryParameters3D.create(a,b))
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var fixture := Node3D.new()
	root.add_child(fixture)
	var original: Node3D = load("res://assets/models/STAR_ATLAS_UPPER_COMMONS_r001.glb").instantiate()
	fixture.add_child(original)
	var source: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_UPPER_COMMONS.json"))
	record("original_export_sha256", FileAccess.get_sha256("res://assets/models/"+str(source.model_file))==source.model_sha256)
	var meshes := original.find_children("*","MeshInstance3D",true,false)
	record("original_514_source_parts",meshes.size()==514)
	var removed := 0
	for m: MeshInstance3D in meshes:
		if str(m.name)=="SA_D17_SouthWall_0":
			m.free(); removed+=1
		elif bool(m.get_meta("extras",{}).get("runtime_collision",false)):
			load("res://scripts/static_contact_cache.gd").attach(m)
	record("exact_one_wall_replaced_only_in_fixture",removed==1)
	var kit: Node3D = load("res://assets/models/STAR_ATLAS_D17_STANDARD_PORTAL_r001.glb").instantiate()
	fixture.add_child(kit)
	var replacements := kit.find_children("*","MeshInstance3D",true,false)
	record("three_replacement_parts",replacements.size()==3)
	for m: MeshInstance3D in replacements:
		load("res://scripts/static_contact_cache.gd").attach(m)
	var door: Node3D = load("res://scripts/guest_entry_door.gd").new()
	door.name="SourceOnlyStandardPortalController"
	door.persistent_id=&"D17_standard_portal_source_fixture_only"
	door.position=Vector3(-65,102,14.13)
	fixture.add_child(door)
	for i in range(10): await physics_frame
	var space := fixture.get_world_3d().direct_space_state
	for x in [-70.0,-63.1]:
		var h:=ray(space,Vector3(x,103.2,13.3),Vector3(x,103.2,14.6))
		record("retained_wall_contact_"+str(x),not h.is_empty() and kit.is_ancestor_of(h.collider))
	var header:=ray(space,Vector3(-65,105,13.3),Vector3(-65,105,14.6))
	record("retained_header_contact",not header.is_empty() and kit.is_ancestor_of(header.collider))
	var floor: Node3D = original.find_child("SA_D17_MissingOnlyFloor",true,false)
	for p in [Vector3(-66.5,102,13.0),Vector3(-63.5,102,13.0),Vector3(-66.5,102,13.7),Vector3(-63.5,102,13.7),Vector3(-65,102,13.4)]:
		var h:=ray(space,p+Vector3.UP*.05,p-Vector3.UP*.05)
		record("retained_floor_"+str(p),not h.is_empty() and floor.is_ancestor_of(h.collider) and absf(h.position.y-102)<.003)
	var no_floor:=ray(space,Vector3(-65,102.1,14.5),Vector3(-65,101.7,14.5))
	record("onward_floor_missing_adoption_hold",no_floor.is_empty())
	for cycle in range(2):
		if door.desired_open: door.interact(null)
		for i in range(100): await physics_frame
		record("closed_controller_"+str(cycle),not door.desired_open and door.open_fraction<.001 and not door.obstructed)
		var shut:=ray(space,Vector3(-65,103.2,13.3),Vector3(-65,103.2,14.6))
		record("closed_collision_"+str(cycle),not shut.is_empty() and door.is_ancestor_of(shut.collider))
		door.interact(null)
		for i in range(100): await physics_frame
		record("open_controller_"+str(cycle),door.desired_open and door.open_fraction>.999 and not door.obstructed)
		var opened:=ray(space,Vector3(-65,103.2,13.3),Vector3(-65,103.2,14.6))
		record("open_aperture_unrestricted_"+str(cycle),opened.is_empty())
		for z in [12.95,13.55]:
			var q:=PhysicsShapeQueryParameters3D.new()
			var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8;capsule.margin=.001
			q.shape=capsule;q.transform=Transform3D(Basis.IDENTITY,Vector3(-65,102.925,z))
			record("open_inner_stance_"+str(cycle)+"_"+str(z),space.intersect_shape(q,16).is_empty())
	door.interact(null)
	for i in range(100): await physics_frame
	record("final_closed_controller",door.open_fraction<.001 and not door.desired_open)
	var report={"status":"PASS"if errors.is_empty()else"FAIL","scope":"Isolated actual-retained-source fixture; no actual-main opening/adoption","check_count":checks.size(),"checks":checks,"errors":errors,"controller_roundtrips":2,"final_closed":true,"ray_exclude_count":0,"new_floor_area_m2":0,"actual_main_wall_changed":false,"adoption_status":"HOLD_MISSING_ONWARD_FLOOR_SUPPORT","limits":"No supported outward walk/cart route, ten standard rooms, seven VIPs, primary engineering/load design or final graphical acceptance is claimed"}
	FileAccess.open("res://artifacts/d17_standard_portal_source.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print(JSON.stringify(report));quit(0 if errors.is_empty()else 1)
