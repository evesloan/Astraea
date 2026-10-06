extends Node3D
# SCRATCH DRAFT. One section-local owner, four finite spatial voices. No loops,
# bus/global edits, file generation or per-frame polling. Original scratch WAVs
# require real listening and an imported-runtime check before acceptance.
const CUE_PATHS := {
	"mechanical_click": "res://assets/audio/engineering_calibration/mechanical_click.wav",
	"relay_double": "res://assets/audio/engineering_calibration/relay_double.wav",
	"soft_hum": "res://assets/audio/engineering_calibration/soft_hum.wav",
	"courtesy_chirp": "res://assets/audio/engineering_calibration/courtesy_chirp.wav"
}
var available := false
var missing_cues: Array[String] = []
var started_count := 0
var declined_count := 0
var _streams: Dictionary = {}
var _voices: Array[AudioStreamPlayer3D] = []
var _last_start_frame := -1000000
var _start_cooldown_s := .08

func configure(data: Dictionary) -> void:
	assert(is_inside_tree() and _voices.is_empty())
	assert(int(data.max_voices) == 4 and float(data.global_start_cooldown_s) >= .08)
	assert(float(data.volume_db) <= -12.0 and float(data.max_distance_m) <= 6.0)
	_start_cooldown_s = float(data.global_start_cooldown_s)
	for cue in CUE_PATHS:
		var path: String = CUE_PATHS[cue]
		if not ResourceLoader.exists(path) or FileAccess.get_sha256(path) != str(data.cues[cue].sha256):
			missing_cues.append(cue)
			continue
		var stream := load(path) as AudioStreamWAV
		if stream == null or stream.loop_mode != AudioStreamWAV.LOOP_DISABLED or stream.get_length() > .5:
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
	available = missing_cues.is_empty()
	set_meta("audio_assets_available", available)
	set_meta("listening_accepted", false)

func play_cue(cue_id: String, source_position: Vector3) -> bool:
	if not _streams.has(cue_id) or float(Engine.get_physics_frames() - _last_start_frame) / float(Engine.physics_ticks_per_second) < _start_cooldown_s:
		declined_count += 1
		return false
	for voice in _voices:
		if voice.playing: continue
		voice.global_position = source_position
		voice.stream = _streams[cue_id]
		voice.play()
		_last_start_frame = Engine.get_physics_frames()
		started_count += 1
		return true
	declined_count += 1
	return false

func stop_all() -> void:
	for voice in _voices:
		voice.stop()
		voice.stream = null

func _exit_tree() -> void:
	stop_all()
