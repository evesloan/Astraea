extends SceneTree
# Explicit bounded candidate fixture, not installed ship or moving acceptance.
const P := "res://orchard_tram_interior_20261025/r002/"
var world: Node3D
var contacts := 0
var checks := 0
var hits: Array[Dictionary] = []
var started := Time.get_ticks_msec()

func _initialize() -> void:
	call_deferred("run")

func model(path: String, label: String, offset: Vector3, rolling := false) -> void:
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file(ProjectSettings.globalize_path(path), state) == OK)
	var node := document.generate_scene(state)
	assert(node != null)
	node.name = label
	node.position = offset
	world.add_child(node)
	for mesh: MeshInstance3D in node.find_children("*", "MeshInstance3D", true, false):
		# Only intentional rolling rail/web contact is omitted. All receiving
		# shoes, drops, headers, guards, room meshes and protected parts remain.
		if rolling and ("ContinuousWeb" in str(mesh.name) or "Orchard_Rail_" in str(mesh.name)):
			continue
		if mesh.mesh == null or mesh.mesh.get_surface_count() == 0:
			continue
		var body := StaticBody3D.new()
		body.name = "PhysicalCandidate"
		mesh.add_child(body)
		var shape := CollisionShape3D.new()
		shape.shape = mesh.mesh.create_trimesh_shape()
		body.add_child(shape)
		contacts += 1

func run() -> void:
	world = Node3D.new()
	world.name = "OrchardCandidateFixture_NOT_INSTALLED"
	root.add_child(world)
	model(P+"Orchard_receiving_exact.glb", "Orchard", Vector3(4,52.5,-250))
	model(P+"Retail_receiving_exact.glb", "Retail", Vector3(8,52.5,-216))
	model(P+"OrchardInteriorReceiving.glb", "NewReceiving", Vector3.ZERO, true)
	model("res://assets/models/AST-CIR-001.glb", "ProtectedSwitchback", Vector3(8,52.5,-237.5))
	var bearings := [[5.45,-248.4],[22.48,-248.4],[13,-226],[13,-206],[26,-230],[26,-216],[26,-202]]
	for i in range(bearings.size()):
		model("res://assets/models/AST-STR-001-H826.glb", "ProtectedBearing"+str(i), Vector3(bearings[i][0],52.5,bearings[i][1]))
	await physics_frame
	await physics_frame
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN.json"))
	var poses: Array = JSON.parse_string(FileAccess.get_file_as_string(P+"POSE_KNOTS.json"))
	var box := BoxShape3D.new()
	box.size = Vector3(4,4.35,5.4)
	for i in range(0, poses.size(), 5):
		var pose: Array = poses[i]
		if pose[0] < plan.orchard_interval_m[0] or pose[0] > plan.orchard_interval_m[1]:
			continue
		var query := PhysicsShapeQueryParameters3D.new()
		query.shape = box
		query.transform = Transform3D(Basis(Vector3.UP,pose[3]),Vector3(pose[1],57.925,pose[2]))
		query.margin = 0.0
		var found := world.get_world_3d().direct_space_state.intersect_shape(query,64)
		checks += 1
		for hit: Dictionary in found:
			var owner := str(hit.collider.get_path())
			var seen := false
			for previous: Dictionary in hits:
				if previous.owner == owner:seen = true;break
			if not seen:hits.append({"owner":owner,"first_cursor":pose[0],"pose":pose.slice(1,4)})
		if Time.get_ticks_msec()-started > 40000:
			finish("DEADLINE_HOLD");return
	finish("PASS_CANDIDATE_RESERVED_ENVELOPE" if hits.is_empty() else "FAIL_CANDIDATE_RESERVED_ENVELOPE")

func finish(status: String) -> void:
	var result := {"status":status,"selected":false,"scope":"Candidate room/receiver triangle contacts with 4m x 5.4m reserved box, Y55.75..60.1; 0.5m samples; not full vehicle articulation, cart, installed ship or operating admission","contacts":contacts,"queries":checks,"unique_conflicts":hits,"elapsed_seconds":(Time.get_ticks_msec()-started)/1000.0}
	var output := ""
	for arg: String in OS.get_cmdline_user_args():
		if arg.begins_with("--result="):output = arg.substr(9)
	assert(not output.is_empty() and not FileAccess.file_exists(output))
	var file := FileAccess.open(output,FileAccess.WRITE)
	assert(file != null)
	file.store_string(JSON.stringify(result,"\t")+"\n")
	file.close()
	print(JSON.stringify(result))
	quit(0 if hits.is_empty() else 2)
