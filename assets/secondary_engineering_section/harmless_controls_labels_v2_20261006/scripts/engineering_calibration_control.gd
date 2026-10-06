extends Node3D
# SCRATCH DRAFT. One source-authored actuator; receives the UNCHANGED player's
# first-hit RMB/E dispatch. No input handler, rigid body, new light or live-system API.
var persistent_id: StringName
var source_marker: StringName
var record: Dictionary
var manager: Node3D
var visual: Node3D
var actuator: MeshInstance3D
var target_area: Area3D
var busy := false
var activation_count := 0
var last_audio_started := false
var _home_local: Transform3D
var _home_source: Transform3D
var _axis: Vector3
var _pivot: Vector3
var _normal: Vector3
var _pulse_surface := -1
var _original_surface_override: Material
var _pulse_material: StandardMaterial3D
var _animation: Tween
var _last_activation_frame := -1000000

func configure(owner_node: Node3D, source_root: Node3D, mesh: MeshInstance3D,
		marker: Node3D, data: Dictionary) -> void:
	assert(is_inside_tree() and owner_node != null and source_root != null)
	manager = owner_node
	visual = source_root
	actuator = mesh
	record = data.duplicate(true)
	persistent_id = StringName(record.id)
	source_marker = StringName(record.source_marker)
	assert(str(marker.name) == str(source_marker) and str(mesh.name) == str(record.actuator_mesh_name))
	assert(not persistent_id.is_empty() and actuator.get_node_or_null("StaticContact") == null)
	_axis = _xyz(record.travel_axis_xyz)
	_pivot = _xyz(record.pivot_xyz)
	_normal = _xyz(record.target_normal_xyz)
	_home_local = actuator.transform
	_home_source = visual.global_transform.affine_inverse() * actuator.global_transform
	assert(_home_source.is_equal_approx(_source_transform(record.runtime_mesh_original_transform_rows)))
	global_transform = marker.global_transform
	assert(global_position.distance_to(visual.to_global(_xyz(record.target_center_xyz))) < .001)
	assert(is_equal_approx(_axis.length(), 1.0) and is_equal_approx(_normal.length(), 1.0))
	# Keep the Area fixed at the authored marker, independent of the tiny moving
	# visual. This is a bounded precise target, not a panel-sized proxy.
	target_area = Area3D.new()
	target_area.name = "SourceCalibrationTarget"
	target_area.collision_layer = 2
	target_area.collision_mask = 0
	target_area.monitoring = false
	target_area.monitorable = false
	var contact := CollisionShape3D.new()
	contact.name = "PreciseSourceTarget"
	var sphere := SphereShape3D.new()
	sphere.radius = float(record.target_radius_m)
	assert(is_equal_approx(sphere.radius, .018))
	contact.shape = sphere
	target_area.add_child(contact)
	add_child(target_area)
	set_meta("source_marker", str(source_marker))
	set_meta("effect_scope", "local calibration only")
	set_meta("source_effect_candidate", str(record.effect_candidate))
	if not str(record.pulse_material_name).is_empty():
		for surface in range(actuator.mesh.get_surface_count()):
			var material := actuator.get_active_material(surface)
			if material != null and material.resource_name == str(record.pulse_material_name):
				assert(_pulse_surface == -1 and material is StandardMaterial3D)
				_pulse_surface = surface
		assert(_pulse_surface >= 0)

func get_interaction_label() -> String:
	if busy: return str(record.faux_status)
	return str(record.label)

func interact(actor: CharacterBody3D) -> void:
	if busy or not _eligible_actor(actor): return
	if float(Engine.get_physics_frames() - _last_activation_frame) / float(Engine.physics_ticks_per_second) < float(record.cooldown_s): return
	if not manager.try_begin_control(self): return
	busy = true
	_last_activation_frame = Engine.get_physics_frames()
	activation_count += 1
	# The cake candidate remains a harmless press-and-return with no RNG/spawn.
	last_audio_started = manager.play_local_cue(str(record.cue_id), global_position)
	_begin_local_pulse()
	_animation = create_tween()
	_animation.set_process_mode(Tween.TWEEN_PROCESS_PHYSICS)
	_animation.tween_method(_animate_phase, 0.0, 1.0, float(record.duration_s))
	_animation.tween_callback(_finish_activation)

func _eligible_actor(actor: CharacterBody3D) -> bool:
	if not is_instance_valid(actor) or not actor.has_method("target_from_view"): return false
	if not actor.get("gameplay_input_enabled"): return false
	if is_instance_valid(actor.get("held_interaction")): return false
	if actor.get("interaction_target") != self: return false
	var camera := actor.get("camera") as Camera3D
	if camera == null or not camera.is_inside_tree(): return false
	# Range and occlusion are revalidated once at activation, never each frame.
	# The original first-hit query remains authoritative at its exact 2.5 m range.
	if actor.target_from_view() != self: return false
	var to_eye: Vector3 = camera.global_position - global_position
	if to_eye.length() > 2.5 + float(record.target_radius_m): return false
	var world_normal: Vector3 = (visual.global_basis * _normal).normalized()
	return to_eye.normalized().dot(world_normal) > .1

func _animate_phase(phase: float) -> void:
	var weight := 0.0
	if str(record.runtime_profile) == "detent_return":
		# Three bounded visual detents, then exact return. No meter is fabricated.
		if phase < .18: weight = phase / .18 * .35
		elif phase < .33: weight = .35
		elif phase < .48: weight = lerpf(.35, .7, (phase - .33) / .15)
		elif phase < .60: weight = .7
		elif phase < .72: weight = lerpf(.7, 1.0, (phase - .60) / .12)
		elif phase < .78: weight = 1.0
		else: weight = 1.0 - (phase - .78) / .22
	else:
		if phase < .22: weight = phase / .22
		elif phase < .48: weight = 1.0
		else: weight = 1.0 - (phase - .48) / .52
	_apply_motion(clampf(weight, 0.0, 1.0) * float(record.motion_endpoint))
	if _pulse_material != null:
		# Slow two-pulse face/index check, using this actuator's duplicate only.
		# This is emissive material feedback, never a dynamic room light.
		var wave := sin(phase * PI * 2.0)
		_pulse_material.emission_energy_multiplier = float(record.pulse_energy_max) * wave * wave

func _apply_motion(displacement: float) -> void:
	if not is_instance_valid(actuator) or not is_instance_valid(visual): return
	var limits: Array = record.travel_limits
	var value := clampf(displacement, float(limits[0]), float(limits[1]))
	var delta := Transform3D.IDENTITY
	if str(record.travel_type) == "rotation":
		var rotation_basis := Basis(_axis, deg_to_rad(value))
		delta = Transform3D(rotation_basis, _pivot - rotation_basis * _pivot)
	else:
		delta.origin = _axis * value
	# Source-space delta around the SOURCE pivot, applied to the complete mesh's
	# saved original pose. No cumulative rotation, rest recentering or reparenting.
	actuator.global_transform = visual.global_transform * delta * _home_source

func _begin_local_pulse() -> void:
	if _pulse_surface < 0: return
	_original_surface_override = actuator.get_surface_override_material(_pulse_surface)
	_pulse_material = actuator.get_active_material(_pulse_surface).duplicate() as StandardMaterial3D
	assert(_pulse_material != null)
	_pulse_material.resource_local_to_scene = true
	_pulse_material.emission_enabled = true
	var color: Array = record.pulse_color_rgb
	_pulse_material.emission = Color(float(color[0]), float(color[1]), float(color[2]))
	_pulse_material.emission_energy_multiplier = 0.0
	actuator.set_surface_override_material(_pulse_surface, _pulse_material)

func _restore_visual() -> void:
	if not is_instance_valid(actuator): return
	actuator.transform = _home_local
	if _pulse_material != null:
		actuator.set_surface_override_material(_pulse_surface, _original_surface_override)
		_pulse_material = null
		_original_surface_override = null

func _finish_activation() -> void:
	_restore_visual()
	busy = false
	_animation = null
	if is_instance_valid(manager): manager.end_control(self)

func cancel_and_restore() -> void:
	if _animation != null and _animation.is_valid(): _animation.kill()
	_finish_activation()

func _exit_tree() -> void:
	cancel_and_restore()

func _xyz(value: Array) -> Vector3:
	return Vector3(float(value[0]), float(value[1]), float(value[2]))

func _source_transform(rows: Array) -> Transform3D:
	var x := Vector3(float(rows[0][0]), float(rows[1][0]), float(rows[2][0]))
	var y := Vector3(float(rows[0][1]), float(rows[1][1]), float(rows[2][1]))
	var z := Vector3(float(rows[0][2]), float(rows[1][2]), float(rows[2][2]))
	var origin := Vector3(float(rows[0][3]), float(rows[1][3]), float(rows[2][3]))
	return Transform3D(Basis(x, y, z), origin)
