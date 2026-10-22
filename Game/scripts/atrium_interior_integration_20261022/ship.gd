extends "res://scripts/warm_interior_integration_20261022/ship.gd"
const ATRIUM_INTERIOR := "res://night_garden_atrium_interiors_20261022/"
var atrium_interiors_verified := false
func register_private_interior(home:Node3D,file:String)->Node3D:
	if file.begins_with("NightGardenD15Specialty_"):
		if not atrium_interiors_verified:
			assert(FileAccess.get_sha256(ATRIUM_INTERIOR+"adapter.gd") == "4d315cf4b349d08e28cc5ad606415496aa46573d3f2a381ef80b3e825ba9bc8e")
			assert(FileAccess.get_sha256(ATRIUM_INTERIOR+"evidence/INDEX_R002.json") == "92d72c83776105ed736feaab70808cf6200988a63e91019ee87c29dbb59e9281")
			assert(FileAccess.get_sha256(ATRIUM_INTERIOR+"evidence/BUILD_R002.json") == "ed3661b9568f88f62dc9c41fb2bd76085d61359906a3a474620a78e028398e93")
			atrium_interiors_verified=true
		load(ATRIUM_INTERIOR+"adapter.gd").prepare(private_detail_residency,file)
	var shell:Node3D=super.register_private_interior(home,file)
	if file.begins_with("NightGardenD15Specialty_"):load(ATRIUM_INTERIOR+"adapter.gd").glazing(shell)
	return shell
func _construction_step(label:String)->void:
	await super._construction_step(label)
	if label=="central_homes/night_garden_residency_20261022":
		assert(atrium_interiors_verified)
		load(ATRIUM_INTERIOR+"adapter.gd").finish(self)
