extends "res://tools/night_garden_residency_20261022/fixture_host.gd"
func register_private_interior(home:Node3D,file:String)->Node3D:
	load("res://night_garden_panoramic_suites_20261022/adapter.gd").prepare(private_detail_residency,file)
	var shell:Node3D=super.register_private_interior(home,file)
	load("res://night_garden_panoramic_suites_20261022/adapter.gd").glazing(shell)
	return shell
