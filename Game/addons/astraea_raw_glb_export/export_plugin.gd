@tool
extends EditorExportPlugin

func _get_name() -> String:
	return "AstraeaRawGlbExport"

func _export_file(path: String, _type: String, _features: PackedStringArray) -> void:
	if not path.to_lower().ends_with(".glb"):
		return
	# Called only for preset-selected files. Keep normal imported-resource export.
	var source := FileAccess.open(path, FileAccess.READ)
	if source == null:
		_fail("Cannot open raw GLB: %s (error %s)" % [path, FileAccess.get_open_error()])
		return
	var expected_size := source.get_length()
	var bytes := source.get_buffer(expected_size)
	var read_error := source.get_error()
	source.close()
	if expected_size <= 0 or bytes.size() != expected_size or read_error != OK:
		_fail("Incomplete raw GLB read: %s (%s/%s bytes; error %s)" % [path, bytes.size(), expected_size, read_error])
		return
	# No skip and no remap: FileAccess sees original bytes; ResourceLoader keeps imports.
	add_file(path, bytes, false)

func _fail(message: String) -> void:
	get_export_platform().add_message(EditorExportPlatform.EXPORT_MESSAGE_ERROR, "Astraea raw GLB export", message)
	push_error(message)

func _export_begin(_features: PackedStringArray, _is_debug: bool, _path: String, _flags: int) -> void:
	# Explicit runtime evidence required by unchanged dynamic source-pin gates.
	# These files are not ordinary documentation and must survive docs exclusion.
	var records: Array = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/startup_residency_20261020/runtime_required_receipts.json"))
	for record in records:
		var source_path: String = str(record.path)
		if FileAccess.get_sha256(source_path) != str(record.sha256):
			_fail("Required runtime receipt missing or changed: " + source_path)
			continue
		add_file(source_path, FileAccess.get_file_as_bytes(source_path), false)
