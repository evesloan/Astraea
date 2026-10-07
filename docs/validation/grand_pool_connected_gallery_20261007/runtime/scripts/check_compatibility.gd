extends SceneTree
# File/proof-chain check only; this does not claim completed medical physical QA.
func _initialize() -> void:
	var medical: Variant=load("res://tests/medical_successor_guard.gd")
	var proof: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://docs/MEDICAL_ADDITIVE_SUCCESSOR.json"))
	assert(medical.retained_sha256("data/spatial_layout.json")==str(proof.predecessors["data/spatial_layout.json"].sha256))
	var pool: Variant=load("res://tests/grand_pool_feature_builder_successor.gd")
	assert(pool.retained_sha256("scripts/grand_pool_architecture.gd")==pool.PREVIOUS_BUILDER_SHA)
	print("CONNECTED POOL GALLERY COMPATIBILITY PASS: exact pool successor and medical file/floor-record chain; loaded medical validation remains its separate receipt.")
	quit(0)
