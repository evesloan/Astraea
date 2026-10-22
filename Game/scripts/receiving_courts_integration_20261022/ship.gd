extends "res://scripts/atrium_interior_integration_20261022/ship.gd"
const RECEIVING_COURTS:="res://night_garden_receiving_courts_20261022/"
func _construction_step(label:String)->void:
	await super._construction_step(label)
	if label=="central_homes/night_garden_residency_20261022":
		assert(atrium_interiors_verified)
		assert(bool(get_meta("central_residential_streets_installed",false)),"Retained central residential streets required")
		assert(FileAccess.get_sha256(RECEIVING_COURTS+"adapter.gd")=="5f345b82c35502dcd02bf2385ab5106834f2426c4c79c3124372fea98eb592ab")
		assert(FileAccess.get_sha256(RECEIVING_COURTS+"evidence/BUILD_R003.json")=="53cdc7ff46f9e2397cde297a1653bf3a0ade28186ee56fe4857c7accb114d47a")
		assert(FileAccess.get_sha256(RECEIVING_COURTS+"evidence/BAKE_R003.json")=="3ae8ebfc68411d15fd2dbfc22bfe96890fd97a7ab3269f0a2775d6c233d6412f")
		assert(FileAccess.get_sha256(RECEIVING_COURTS+"evidence/ENTRANCES.json")=="2f49d19b0f9885106ed82f0e9075f21f2031208bd0c393a90d20abb9bcabebb5")
		assert(FileAccess.get_sha256(RECEIVING_COURTS+"evidence/ENTRANCES_BAKE_POLICY.json")=="3cdd3e81f925f6688536a6ca62b3d557cac0499d39ca925bbd9b1c5c023d1b0b")
		load(RECEIVING_COURTS+"adapter.gd").build(self)
