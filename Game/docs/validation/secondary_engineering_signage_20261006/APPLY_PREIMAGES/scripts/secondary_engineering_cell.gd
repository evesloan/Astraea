extends RefCounted
# Source-bound lowered workbay cell. No blanket trimesh import or inherited fitting scaling.
const CONTRACT := "res://data/architecture/SECONDARY_ENGINEERING_CELL_RUNTIME.json"
static func xyz(value: Array) -> Vector3:
	return Vector3(float(value[0]),float(value[1]),float(value[2]))
static func build(parent: Node3D, ship: Node3D) -> Dictionary:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	assert(data.adoption_gate_accepted and data.light_trial_values_accepted_for_test)
	assert(str(data.retained_source_commit).length()==40 and not data.first_pass_accepted)
	assert(FileAccess.get_sha256("res://assets/models/"+str(data.model_file))==str(data.model_sha256))
	assert(data.catalogue_id=="AST-ENG-008" and data.retain_original_section_and_essentials)
	var wrapper := Node3D.new()
	wrapper.name = "SecondaryEngineeringWorkbayCell"
	wrapper.set_meta("persistent_id","secondary_engineering_workbay_cell_001")
	wrapper.set_meta("catalogue_file",str(data.model_file))
	wrapper.set_meta("first_pass_quality_accepted",false)
	wrapper.set_meta("external_staff_connection","unbuilt; existing safety closures retained")
	wrapper.set_meta("cart_access","upper service ring only; portable tools use real stepped cell")
	parent.add_child(wrapper)
	var visual := (load("res://assets/models/"+str(data.model_file)) as PackedScene).instantiate() as Node3D
	visual.name = "AuthoredWorkbaySection"
	visual.set_meta("catalogue_file",str(data.model_file))
	wrapper.add_child(visual)
	assert(visual.position==Vector3.ZERO and visual.rotation==Vector3.ZERO and visual.scale==Vector3.ONE)
	var seen: Dictionary = {}
	var triangles := 0
	var proxies := 0
	for item in visual.find_children("*","MeshInstance3D",true,false):
		var part := item as MeshInstance3D
		var label := str(part.name)
		assert(data.groups.has(label) and not seen.has(label),"Unexpected source section mesh: "+label)
		seen[label] = true
		var expected: Dictionary = data.groups[label]
		var role := str(expected.collision_contract)
		assert(part.mesh!=null and part.mesh.get_faces().size()==int(expected.triangles)*3)
		assert(part.material_override==null and part.get_node_or_null("StaticContact")==null)
		assert(part.mesh.get_surface_count()==expected.materials.size())
		for surface in range(part.mesh.get_surface_count()):
			assert(part.get_active_material(surface).resource_name==str(expected.materials[surface]),"Retained source material required")
		triangles += int(expected.triangles)
		part.set_meta("validated_contact_policy",role)
		part.visible = bool(expected.visible)
		match role:
			"static_surface", "contact_only_glass_26mm", "stair_flight_contact":
				load("res://scripts/static_contact_cache.gd").attach(part)
				if role=="contact_only_glass_26mm": proxies += 1
			"actuator_no_body_contact":
				part.set_meta("calibration_interaction","separate next gate; no live system side effects")
			"visual_only_glass", "moving_door_leaf", "door_control_only", "visual_only_stair_tread", "none": pass
			_: assert(false,"Unreviewed collision role")
	assert(seen.size()==153 and triangles==47930 and proxies==10)
	assert(visual.find_children("ACT_*","MeshInstance3D",true,false).size()==120)
	var gate := Node3D.new()
	gate.name = "EngineeringCellGate"
	gate.set_script(load("res://scripts/engineering_cell_gate.gd"))
	gate.configure(visual,data.gate)
	wrapper.add_child(gate)
	for target in data.gate.targets:
		var marker := visual.find_child(str(target.marker),true,false) as Node3D
		assert(marker!=null and marker.global_position.distance_to(xyz(target.position_xyz))<.001)
		var control := Node3D.new()
		control.name = "EngineeringCellGateTarget_"+("OUTSIDE" if str(target.marker).ends_with("OUTSIDE") else "INSIDE")
		control.set_script(load("res://scripts/engineering_cell_gate_target.gd"))
		wrapper.add_child(control)
		control.configure(gate,marker)
	assert(data.local_light_trial.size()==4)
	for item in data.local_light_trial:
		var marker := visual.find_child(str(item.marker),true,false) as Node3D
		assert(marker!=null and marker.global_position.distance_to(xyz(item.expected_emitter_xyz))<.001)
		var light := SpotLight3D.new()
		light.name = str(item.light_name)
		wrapper.add_child(light)
		light.global_position = marker.global_position
		ship.apply_light_profile(light,"staff_work")
		light.look_at(xyz(item.aim_xyz),Vector3.UP)
		light.spot_range = float(item.range_m)
		light.light_energy = float(item.energy)
		light.spot_angle = float(item.spot_angle)
		light.shadow_enabled = true
		light.set_meta("source_marker",str(item.marker))
		light.set_meta("engineering_cell_local_trial",true)
		if item.has("illumination_anchor_xyz"):
			assert(str(item.marker)=="DATUM_CELL_LIGHT" and item.has("illumination_anchor_surface"))
			var anchor := xyz(item.illumination_anchor_xyz)
			var delta := anchor-light.global_position
			assert(delta.length()<light.spot_range and delta.normalized().dot(-light.global_basis.z)>=cos(deg_to_rad(light.spot_angle)))
			light.set_meta("illumination_anchor",anchor)
			# Existing selector admits only the independently proven real lit receiver.
			# Source position/range remain exactly source-backed; no selector edit.
	return data
