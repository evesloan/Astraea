extends "res://scripts/court_completion_integration_20261022/ship.gd"
const ATRIUM_CEILING:="res://atrium_ceiling_completion_20261022/"
func _construction_step(label:String)->void:
	await super._construction_step(label)
	if label=="central_homes/night_garden_residency_20261022":
		assert(FileAccess.get_sha256(ATRIUM_CEILING+"adapter.gd") == "369f92a0c84a37dd9ba705707382ad0ef0427d9c6c4b58a98a73d520b398ccb9")
		assert(FileAccess.get_sha256(ATRIUM_CEILING+"evidence/BUILD.json") == "5ed0b95a24e49390797abd233f91b8987825b8302085e327e39b0efb18b93d97")
		assert(FileAccess.get_sha256(ATRIUM_CEILING+"evidence/BAKE.json") == "f4a7eec5972d3b8f2bdb83ab9bed43d65b86fad2f0d23e14312e6fed2c99ed7e")
		assert(FileAccess.get_sha256(ATRIUM_CEILING+"evidence/PREREQUISITES.json") == "dfc83c049eaee06a74c01db32a7d86297fd37cefdd5abc71d233428f42f78581")
		load(ATRIUM_CEILING+"adapter.gd").finish(self)
