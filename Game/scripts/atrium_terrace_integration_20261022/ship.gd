extends "res://scripts/atrium_ceiling_integration_20261022/ship.gd"
const TERRACES:="res://atrium_terrace_inhabitation_20261022/"
func _construction_step(label:String)->void:
	await super._construction_step(label)
	if label=="central_homes/night_garden_residency_20261022":
		assert(FileAccess.get_sha256(TERRACES+"adapter_r003.gd") == "175e897deddb353f1f7ee52aca92538bc5b84c680a0458ed91597e7b85d62709")
		assert(FileAccess.get_sha256(TERRACES+"evidence/BUILD_R003.json") == "ccea6eaa71bb18082c955e396c8797123da95b2413e6020de65670bc608d817d")
		assert(FileAccess.get_sha256(TERRACES+"evidence/CEILING_BUILD.json") == "e3dea3e055dfb30e4769c55e105741b120a1296da22a00704c44a59f0fd73d62")
		assert(FileAccess.get_sha256(TERRACES+"evidence/BAKE_R003.json") == "b37e1e85457275dac43850f2b9fcb9b0255dba3dee93578d8b2302872b92bbe3")
		assert(FileAccess.get_sha256(TERRACES+"evidence/PREREQUISITES.json") == "aa8951163e4b2922514e94b14f9bb2da0be0b4145eabf48908e9020f13dc19ba")
		load(TERRACES+"adapter_r003.gd").finish(self)
