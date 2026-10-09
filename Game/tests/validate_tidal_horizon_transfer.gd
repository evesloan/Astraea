extends SceneTree

# Source-derived contact fit only, not a structural load certification.
func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var contract: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/TIDAL_HORIZON_TRANSFER_CANDIDATE.json"))
	var tidal: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/TIDAL_GARDEN_RECEIVING_CANDIDATE.json"))
	var transfer_path := "res://assets/models/" + str(contract.model_file)
	assert(FileAccess.get_sha256(transfer_path) == str(contract.export_sha256))
	var horizon_path := "res://assets/models/SOL_D12_directory_01_entry001.glb"
	assert(FileAccess.get_sha256(horizon_path) == str(contract.source_pins["Game/assets/models/SOL_D12_directory_01_entry001.glb"]))
	var transfer: Node3D = load(transfer_path).instantiate()
	var horizon: Node3D = load(horizon_path).instantiate()
	var house: Node3D = load("res://assets/models/"+str(tidal.model_file)).instantiate()
	for scene in [horizon,house,transfer]:
		world.add_child(scene)
		for part: MeshInstance3D in scene.find_children("*","MeshInstance3D",true,false):
			if bool(part.get_meta("extras",{}).get("runtime_collision",true)):
				load("res://scripts/static_contact_cache.gd").attach(part)
	for frame in range(4): await physics_frame
	var excluded: Array[RID] = []
	for body in transfer.find_children("*","StaticBody3D",true,false): excluded.append(body.get_rid())
	var all_bodies := world.find_children("*","StaticBody3D",true,false)
	var physics := world.get_world_3d().direct_space_state
	var errors: Array = []
	var checks := 0
	for part in contract.parts:
		var lo: Array = part.bounds_world_xyz[0]
		var hi: Array = part.bounds_world_xyz[1]
		if str(part.role) in ["pier_contact","wall_contact"]:
			var p := Vector3((lo[0]+hi[0])/2.0,lo[1],(lo[2]+hi[2])/2.0)
			# Verify the specified bearing itself. The retained decorative canopy
			# is 9 mm above some rear pier tops and otherwise intercepts this ray.
			# This is not a canopy-clearance test or permission to move that source.
			var owner_name := "D12_directory_01__fan_rear_pier"+str(part.name).get_slice("_",2) if str(part.role)=="pier_contact" else "D12_directory_01__entry_right" if p.z < -432 else "D12_directory_01__entry_left"
			var owner := horizon.find_child(owner_name,true,false) as MeshInstance3D
			assert(owner != null, "Named retained bearing must exist")
			var bearing := owner.get_node("StaticContact") as StaticBody3D
			var bearing_exclusions: Array[RID] = []
			for body: StaticBody3D in all_bodies:
				if body != bearing: bearing_exclusions.append(body.get_rid())
			var ray := PhysicsRayQueryParameters3D.create(p+Vector3.UP*.02,p-Vector3.UP*.04)
			ray.exclude = bearing_exclusions
			var hit := physics.intersect_ray(ray)
			checks += 1
			if hit.is_empty() or absf(hit.position.y-p.y)>.001 or hit.normal.y<.9:
				errors.append({"part":part.name,"kind":"retained_support_contact","expected_xyz":[p.x,p.y,p.z],"hit":str(hit)})
		elif str(part.name).begins_with("TGH_Longitudinal"):
			for z in [-456.0,-448.0,-440.0,-432.0,-424.0,-416.0,-408.0]:
				var p := Vector3((lo[0]+hi[0])/2.0,83.76,z)
				var ray := PhysicsRayQueryParameters3D.create(p-Vector3.UP*.02,p+Vector3.UP*.04)
				ray.exclude = excluded
				var hit := physics.intersect_ray(ray)
				checks += 1
				if hit.is_empty() or absf(hit.position.y-p.y)>.001 or hit.normal.y>-.9:
					errors.append({"part":part.name,"kind":"retained_floor_underside_contact","expected_xyz":[p.x,p.y,p.z],"hit":str(hit)})
	assert(transfer.find_children("*","MeshInstance3D",true,false).size()==int(contract.source_part_count))
	var result := {"status":"PASS" if errors.is_empty() else "FAIL","checks":checks,"source_parts":contract.source_part_count,"errors":errors,"scope":"Exact retained Horizon support tops and corrected Tidal floor undersides contacted by the new additive source; no engineering load or complete house acceptance.","default_scene_enabled":false}
	var f := FileAccess.open("res://artifacts/tidal_horizon_transfer_contacts.json",FileAccess.WRITE)
	f.store_string(JSON.stringify(result,"  "))
	print("TIDAL_HORIZON_TRANSFER ",result.status," checks=",checks," failures=",errors.size())
	quit(0 if errors.is_empty() else 1)
