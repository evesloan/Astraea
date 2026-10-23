extends SceneTree
# Run with the editor executable's --main-pack from an empty directory.
# This inspects sealed export inputs; it does not instantiate the ship.
func stop(message: String) -> void:
	push_error(message)
	quit(1)

func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 3:
		stop("Expected output receipt, exact manifest SHA256, selected main scene")
		return
	var source_receipt_path := "res://runtime_source_contracts_receipt.json"
	if not FileAccess.file_exists(source_receipt_path):
		stop("Missing exact-source receipt in exported pack")
		return
	var sealed: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(source_receipt_path))
	var nested_sha := FileAccess.get_sha256("res://runtime_source_contracts.pck")
	if nested_sha != str(sealed.sha256):
		stop("Nested source-pack digest mismatch")
		return
	if not ProjectSettings.load_resource_pack("res://runtime_source_contracts.pck"):
		stop("Cannot mount nested exact-source pack")
		return
	var manifest := "res://scripts/runtime_contracts_20261022/SOURCE_CONTRACTS.json"
	var manifest_sha := FileAccess.get_sha256(manifest)
	if manifest_sha != args[1] or manifest_sha != str(sealed.manifest_sha256):
		stop("Packaged manifest differs from frozen source")
		return
	var rows: Array = JSON.parse_string(FileAccess.get_file_as_string(manifest))
	if rows.size() != int(sealed.files):
		stop("Packaged source count mismatch")
		return
	var total := 0
	for row: Dictionary in rows:
		if FileAccess.get_sha256(str(row.path)) != str(row.sha256):
			stop("Packaged source bytes differ: " + str(row.path))
			return
		total += int(row.bytes)
	var main: String = str(ProjectSettings.get_setting("application/run/main_scene", ""))
	if main.begins_with("uid://"):
		main = ResourceUID.get_id_path(ResourceUID.text_to_id(main))
	if main != args[2]:
		stop("Export selected the wrong main scene: " + main)
		return
	if not load(main) is PackedScene:
		stop("Selected bootstrap scene failed to load")
		return
	var pins: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://royalty790_integration_20261022/evidence/INPUT_PINS.json"))
	var pin_count := 0
	for path: String in pins:
		if not path.begins_with("Game/"):
			continue
		if FileAccess.get_sha256("res://" + path.trim_prefix("Game/")) != str(pins[path]):
			stop("Royalty retained bytes differ: " + path)
			return
		pin_count += 1
	var group5: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group5/CONSTRUCTION.json"))
	var source_scenes := 0
	for row: Dictionary in group5.fitout_revisions:
		if not load(str(row.scene_path)) is PackedScene:
			stop("Required Group 5 scene failed to load: " + str(row.scene_path))
			return
		source_scenes += 1
	var result := {"status":"PACK_CONTRACTS_PASS", "exact_files":rows.size(), "exact_bytes":total,
		"manifest_sha256":manifest_sha, "nested_pack_sha256":nested_sha,
		"main_scene":main, "royalty_source_pins":pin_count, "group5_scenes":source_scenes,
		"ship_instantiated":false, "windows_executable_tested":false, "playable_accepted":false}
	var f := FileAccess.open(args[0], FileAccess.WRITE)
	if f == null:
		stop("Cannot write pack receipt")
		return
	f.store_string(JSON.stringify(result, "  ") + "\n")
	f.close()
	print(JSON.stringify(result))
	quit(0)
