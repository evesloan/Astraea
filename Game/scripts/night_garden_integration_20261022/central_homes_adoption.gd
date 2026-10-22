extends RefCounted
static func build(ship:Node3D)->void:
	assert(FileAccess.get_sha256("res://scripts/startup_residency_20261020/central_homes_adoption.gd")=="1b6a381fadde7890280914bd41729a53374490fccacff31e72c2da6f81fbda75")
	await load("res://scripts/startup_residency_20261020/central_homes_adoption.gd").build(ship)
	load("res://scripts/night_garden_integration_20261022/bridge.gd").build(ship)
	await ship._construction_step("central_homes/night_garden_residency_20261022")
