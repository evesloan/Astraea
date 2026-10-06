extends Node3D
# SCRATCH RUNTIME V3. Four finite spatial voices in the original player's World360.
# Readiness/playback checks are not proof that a person has heard these samples.
const CUE_PATHS := {
	"mechanical_click": "res://assets/audio/engineering_calibration/mechanical_click.wav",
	"relay_double": "res://assets/audio/engineering_calibration/relay_double.wav",
	"soft_hum": "res://assets/audio/engineering_calibration/soft_hum.wav",
	"courtesy_chirp": "res://assets/audio/engineering_calibration/courtesy_chirp.wav"
}
const MAX_START_HISTORY := 64
var available := false
var listener_ready := false
var missing_cues: Array[String] = []
var started_count := 0
var declined_count := 0
var start_history: Array[Dictionary] = []
var listener_camera: Camera3D
var _streams: Dictionary = {}
var _voices: Array[AudioStreamPlayer3D] = []
var _lease_until_frame: Array[int] = []
var _last_start_frame := -1000000
var _start_cooldown_s := .08

func configure(data: Dictionary) -> void:
	assert(is_inside_tree() and _voices.is_empty())
	assert(int(data.max_voices) == 4 and is_equal_approx(float(data.global_start_cooldown_s), .08))
	assert(float(data.volume_db) <= -12.0 and float(data.max_distance_m) <= 6.0)
	_start_cooldown_s = float(data.global_start_cooldown_s)
	for cue in CUE_PATHS:
		var path: String = CUE_PATHS[cue]
		if not ResourceLoader.exists(path) or FileAccess.get_sha256(path) != str(data.cues[cue].sha256):
			missing_cues.append(cue)
			continue
		var stream := load(path) as AudioStreamWAV
		if stream == null or stream.loop_mode != AudioStreamWAV.LOOP_DISABLED or stream.get_length() > .5 or stream.get_length() <= 0.0:
			missing_cues.append(cue)
			continue
		_streams[cue] = stream
	for index in range(4):
		var voice := AudioStreamPlayer3D.new()
		voice.name = "BoundedCalibrationVoice" + str(index + 1)
		voice.max_polyphony = 1
		voice.volume_db = float(data.volume_db)
		voice.max_distance = float(data.max_distance_m)
		voice.unit_size = float(data.unit_size_m)
		voice.attenuation_model = AudioStreamPlayer3D.ATTENUATION_INVERSE_DISTANCE
		voice.autoplay = false
		add_child(voice)
		_voices.append(voice)
		_lease_until_frame.append(-1)
	available = missing_cues.is_empty()
	set_meta("audio_assets_available", available)
	set_meta("listening_accepted", false)

func bind_original_listener(camera: Camera3D) -> bool:
	listener_camera = camera
	listener_ready = listener_contract_holds()
	if not listener_ready:
		push_error("Calibration requires the original current camera and four voices in listener-enabled World360")
	return listener_ready

func listener_contract_holds() -> bool:
	if not is_instance_valid(listener_camera) or not listener_camera.is_inside_tree(): return false
	var viewport := get_viewport()
	if not viewport is SubViewport or str(viewport.name) != "World360": return false
	if not viewport.audio_listener_enable_3d: return false
	if listener_camera.get_viewport() != viewport or viewport.get_camera_3d() != listener_camera: return false
	if listener_camera.get_world_3d() != get_world_3d(): return false
	# Four cached objects only, never a room scan or a per-frame callback.
	for voice in _voices:
		if voice.get_viewport() != viewport or voice.get_world_3d() != listener_camera.get_world_3d(): return false
	return _voices.size() == 4

func play_cue(cue_id: String, source_position: Vector3) -> bool:
	var frame := Engine.get_physics_frames()
	var ticks := float(Engine.physics_ticks_per_second)
	if not listener_ready or not listener_contract_holds() or not _streams.has(cue_id):
		declined_count += 1
		return false
	if float(frame - _last_start_frame) / ticks < _start_cooldown_s:
		declined_count += 1
		return false
	for index in range(_voices.size()):
		var voice: AudioStreamPlayer3D = _voices[index]
		# A finite frame lease removes an audio-server start/finish race and gives
		# accelerated headless scheduling tests the same bounded occupancy rule.
		# We still wait for .playing to clear; a lease never truncates a cue.
		if frame < _lease_until_frame[index] or voice.playing: continue
		voice.global_position = source_position
		voice.stream = _streams[cue_id]
		voice.play()
		_lease_until_frame[index] = frame + ceili(voice.stream.get_length() * ticks) + 1
		_last_start_frame = frame
		started_count += 1
		start_history.append({"frame":frame,"physics_hz":ticks,"voice":index,"cue":cue_id,
			"lease_end_frame":_lease_until_frame[index],"position":source_position})
		if start_history.size() > MAX_START_HISTORY: start_history.pop_front()
		return true
	declined_count += 1
	return false

func active_lease_count() -> int:
	var count := 0
	var frame := Engine.get_physics_frames()
	for index in range(_voices.size()):
		if frame < _lease_until_frame[index] or _voices[index].playing: count += 1
	return count

func stop_all() -> void:
	for index in range(_voices.size()):
		_voices[index].stop()
		_voices[index].stream = null
		_lease_until_frame[index] = -1
	# Do not reset start spacing: even cancellation cannot create <80 ms starts.

func _exit_tree() -> void:
	stop_all()
