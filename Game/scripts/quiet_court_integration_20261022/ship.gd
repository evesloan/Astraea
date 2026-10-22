extends "res://scripts/quiet_grove_bank_integration_20261022/ship.gd"
const COURT:="res://quiet_court_finish_20261022/"
func _construction_step(label:String)->void:
	await super._construction_step(label)
	if label=="quiet_grove_adoption.gd":
		assert(FileAccess.get_sha256(COURT+"adapter_batched.gd")=="8660564c9bb7c66b6bb3daa25e92aa75cf9e9bf15a190f6ea63bfed401635d7a")
		assert(FileAccess.get_sha256(COURT+"planting_batched.gd")=="d49421832daf39f5dc5fb36e7fc8a307411026a16260eb28a2306ac44d9708da")
		assert(FileAccess.get_sha256(COURT+"PLAN_R003.json")=="7309c9a87f6cfdc8992a012d11f72daa8742df8483d9ce81686ef6f1d093c24d")
		assert(FileAccess.get_sha256(COURT+"evidence/BATCHED_STATUS.json")=="d03c1f1a94d43a03ad9d0921748058c0b54af1f5b26aa3fe48da8b4efb107aa2")
		load(COURT+"adapter_batched.gd").build(self)
