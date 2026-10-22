extends "res://scripts/startup_contact_residency_20261022/ship.gd"
# The retained Tidal/contact, Royalty and original district builders stay in force.
const PANORAMA := "res://night_garden_panoramic_suites_20261022/"
var panoramic_inputs_verified := false
func register_private_interior(home:Node3D,file:String)->Node3D:
	if file.begins_with("NightGardenD15Specialty_"):
		if not panoramic_inputs_verified:
			assert(FileAccess.get_sha256(PANORAMA+"adapter.gd")=="ee76550015b986af603ca60753887bc192ef4c2bf80575200d5c9c5906f5d5fa")
			assert(FileAccess.get_sha256(PANORAMA+"evidence/INDEX.json")=="7d8123c3a0a79beed0820840e8b5d30a310aade78bdf8b37b24306bf56054c84")
			assert(FileAccess.get_sha256(PANORAMA+"evidence/BUILD.json")=="6fd10172f21069f9d4235c9a97ba5edaf573d9212692193e620ad687195391f0")
			panoramic_inputs_verified=true
		load(PANORAMA+"adapter.gd").prepare(private_detail_residency,file)
	var shell:Node3D=super.register_private_interior(home,file)
	if file.begins_with("NightGardenD15Specialty_"):load(PANORAMA+"adapter.gd").glazing(shell)
	return shell
func _construction_step(label:String)->void:
	if label=="central_homes/night_garden_residency_20261022":
		assert(panoramic_inputs_verified)
		load(PANORAMA+"adapter.gd").finish(self)
	await super._construction_step(label)
