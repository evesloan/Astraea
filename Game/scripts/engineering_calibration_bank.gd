extends Node3D
# SCRATCH RUNTIME V3. One exact deferred binding because the cell is constructed
# before ShipSpace/PersistentActors/Player; no _process discovery/polling.
var controls_by_id: Dictionary = {}
var active_controls: Dictionary = {}
var audio_owner: Node3D
var original_actor: CharacterBody3D
var listener_ready := false
var max_active_controls := 4
var listener_bind_attempts := 0

func bind_original_player_after_build(ship: Node3D) -> void:
	listener_bind_attempts += 1
	assert(listener_bind_attempts == 1)
	original_actor = ship.get_node_or_null("ShipSpace/PersistentActors/Player") as CharacterBody3D
	if original_actor == null or not original_actor.is_physics_processing():
		push_error("Original physical player missing at deferred calibration binding")
		return
	var camera := original_actor.get("camera") as Camera3D
	listener_ready = is_instance_valid(audio_owner) and audio_owner.bind_original_listener(camera)
	set_meta("original_listener_bound", listener_ready)

func try_begin_control(control: Node3D) -> bool:
	if not listener_ready or not audio_owner.listener_contract_holds(): return false
	var identity := str(control.persistent_id)
	if not controls_by_id.has(identity) or controls_by_id[identity] != control: return false
	if active_controls.has(identity) or active_controls.size() >= max_active_controls: return false
	active_controls[identity] = weakref(control)
	return true

func end_control(control: Node3D) -> void:
	active_controls.erase(str(control.persistent_id))

func play_local_cue(cue: String, point: Vector3) -> bool:
	if not is_instance_valid(audio_owner): return false
	return audio_owner.play_cue(cue, point)

func cancel_all() -> void:
	for reference in active_controls.values().duplicate():
		var control: Node3D = reference.get_ref()
		if is_instance_valid(control): control.cancel_and_restore()
	active_controls.clear()
	if is_instance_valid(audio_owner): audio_owner.stop_all()
