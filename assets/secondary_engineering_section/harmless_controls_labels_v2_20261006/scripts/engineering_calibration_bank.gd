extends Node3D
# SCRATCH DRAFT. Owns only four bounded active controls and the local audio pool.
# It is not connected to gates, reactors, lifts, access control or networking.
var controls_by_id: Dictionary = {}
var active_controls: Dictionary = {}
var audio_owner: Node3D
var max_active_controls := 4

func try_begin_control(control: Node3D) -> bool:
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
	# Only on explicit teardown/test reset, not in any frame callback.
	for reference in active_controls.values().duplicate():
		var control: Node3D = reference.get_ref()
		if is_instance_valid(control): control.cancel_and_restore()
	active_controls.clear()
	if is_instance_valid(audio_owner): audio_owner.stop_all()
