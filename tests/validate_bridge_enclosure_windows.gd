extends SceneTree
# Candidate framing and real collidable glass only. No all-species seated-fit claim.
const CONTRACT := "res://data/architecture/BRIDGE_ENCLOSURE_RUNTIME.json"
const GLASS_SHADER := "res://shaders/hospitality_glass.gdshader"
var failures: Array[String] = []
var space: PhysicsDirectSpaceState3D
var shell: Node3D
var old_shell: Node3D
var exclusions: Array[RID] = []
var contacts := 0

func _initialize() -> void:
	call_deferred("run")

func check(ok: bool, detail: String) -> bool:
	if not ok:
		failures.append(detail)
		push_error(detail)
	return ok

func ray(a: Vector3,b: Vector3) -> Dictionary:
	var q := PhysicsRayQueryParameters3D.create(a,b)
	q.exclude = exclusions
	return space.intersect_ray(q)

func glass_contact(hit: Dictionary,expected: Node3D,label: String) -> void:
	if not check(not hit.is_empty(),"Missing collidable glass: "+label):
		return
	check(expected.is_ancestor_of(hit.collider),"Wrong architecture caught glass ray: "+label)
	var mesh := hit.collider.get_parent() as MeshInstance3D
	if check(mesh != null and "glass" in str(mesh.name).to_lower(),"Non-glass obstruction: "+label):
		check(mesh.is_visible_in_tree() and mesh.material_override is ShaderMaterial and mesh.material_override.shader.resource_path == GLASS_SHADER,"Visible hospitality glass shader missing: "+label)
	contacts += 1

func validate_new_windows(data: Dictionary) -> void:
	check(data.windows.size()==13,"Expected all13 source window assemblies")
	var ids: Dictionary = {}
	for window in data.windows:
		check(not ids.has(str(window.id)),"Duplicated source window identity")
		ids[str(window.id)] = true
		var a := Vector3(float(window.a_xz[0]),0,float(window.a_xz[1]))
		var b := Vector3(float(window.b_xz[0]),0,float(window.b_xz[1]))
		var tangent := (b-a).normalized()
		var normal := Vector3(tangent.z,0,-tangent.x)
		check(absf(float(window.y[0])-107.1)<0.001 and absf(float(window.y[1])-110.55)<0.001 and bool(window.closed_glass_collision),"Source aperture/glass extent changed")
		for t in [0.2,0.5,0.8]:
			for y in [107.4,108.4,110.25]:
				var p := a.lerp(b,t)
				p.y = y
				for side in [-1.0,1.0]:
					glass_contact(ray(p+normal*side*0.35,p-normal*side*0.35),shell,str(window.id))
		# Interior gallery-facing pane sees the real opposite public-gallery glass
		# across the exterior slot. It is deliberately not called an open panorama.
		if str(window.id).begins_with("PortFore"):
			var p := a.lerp(b,0.5)
			p.y = 108.4
			glass_contact(ray(p+Vector3(0,0,-0.25),p+Vector3(0,0,-2.5)),old_shell,"Fore-left existing gallery destination")

func validate_old_windows(data: Dictionary) -> void:
	check(data.windows.size()==24,"All24 original bypass panes must survive")
	for window in data.windows:
		var b: Array = window.world_aabb
		var p := Vector3((float(b[0])+float(b[1]))*0.5,0,(float(b[4])+float(b[5]))*0.5)
		var n := Vector3(float(window.outward_normal[0]),float(window.outward_normal[1]),float(window.outward_normal[2]))
		for y in [107.3,108.4,110.1]:
			p.y = y
			for side in [-1.0,1.0]:
				glass_contact(ray(p+n*side*0.4,p-n*side*0.4),old_shell,str(window.id))
		if str(window.side) in ["port","fore"]:
			p.y = 108.4
			check(ray(p+n*0.4,p+n*700).is_empty(),"Previously exterior bypass axis blocked")

func validate_candidate_views() -> void:
	check(FileAccess.get_sha256("res://shaders/astraea_space.gdshader")=="08f0ec4c92b7de0c45afa539f8d9abdd65ec00c3d4af1831548f0ec24d485b2d","Shared world sky composition changed")
	var direction := Vector3(cos(deg_to_rad(12.0))*cos(deg_to_rad(12.0)),sin(deg_to_rad(12.0)),sin(deg_to_rad(12.0))*cos(deg_to_rad(12.0)))
	for eye_y in [107.65,108.10]:
		var eye := Vector3(28,eye_y,-145)
		var wall := eye+direction*(7.7/direction.x)
		check(ray(eye,wall-direction*0.1).is_empty(),"Candidate upper-limb interior ray obstructed")
		glass_contact(ray(eye,wall+direction*0.2),shell,"Source-backed upper-limb glass intersection")
		check(ray(wall+direction*0.2,eye+direction*(80.0/direction.x)).is_empty(),"Candidate upper-limb exterior ray obstructed")
	for y in [107.65,108.10]:
		var eye := Vector3(28,y,-145)
		var target := Vector3(35.7,y,-145)
		check(ray(eye,target-Vector3(0.1,0,0)).is_empty(),"Candidate seated/standing horizontal eye-to-glass obstructed")
		glass_contact(ray(eye,target+Vector3(0.3,0,0)),shell,"Candidate starboard seated/standing glass")
		check(ray(target+Vector3(0.25,0,0),target+Vector3(700,0,0)).is_empty(),"Candidate starboard exterior ray obstructed")
	# Forward-right honestly frames sky. The opposite side frames a gallery.
	var eye := Vector3(16,108.1,-164)
	glass_contact(ray(eye,Vector3(16,108.1,-172)),shell,"Forward-right glass")
	check(ray(Vector3(16,108.1,-172),Vector3(16,108.1,-850)).is_empty(),"Forward-right outward sky candidate obstructed")

func run() -> void:
	var main := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(30):
		await physics_frame
	var ship := main.get_node("World360/Astraea") as Node3D
	shell = ship.get_node_or_null("ShipSpace/Districts/BridgeEnclosure_WIP/BridgeEnclosureArchitecture") as Node3D
	old_shell = ship.get_node("ShipSpace/Districts/BridgePlatform_WIP/BridgePlatformArchitecture") as Node3D
	if not check(shell != null,"Enclosure shell absent"):
		quit(1)
		return
	space = ship.get_world_3d().direct_space_state
	for body in ship.find_children("*","CollisionObject3D",true,false):
		if not body is StaticBody3D or body is AnimatableBody3D:
			exclusions.append(body.get_rid())
	check(FileAccess.get_sha256(CONTRACT)=="cbce60485b8bb2789fe6eed2a299871c923c83719570ee53fb5a49b78880a195","Final reviewed window contract changed")
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	var old: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/BRIDGE_PLATFORM_RUNTIME.json"))
	validate_new_windows(data)
	validate_old_windows(old)
	validate_candidate_views()
	check(contacts==387,"All234 new pane contacts,144 old contacts,4 gallery targets and5 view contacts must execute")
	print(("BRIDGE ENCLOSURE WINDOWS PASS:" if failures.is_empty() else "BRIDGE ENCLOSURE WINDOWS FAILED:")+" %d physical glass contacts; %d failures. Candidate seated/standing starboard and forward sky framing; honest gallery destination. No species-fit or final composition claim." % [contacts,failures.size()])
	main.queue_free()
	await process_frame
	quit(0 if failures.is_empty() else 1)
