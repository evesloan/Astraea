extends "res://scripts/warm_interior_integration_20261022/fixture_host.gd"
func _ready()->void:
	super._ready()
	var contract:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/design_contract.json"))
	for datum in contract.deck_datums:deck_y.append(float(datum.floor_elevation_m))
func register_private_interior(home:Node3D,file:String)->Node3D:
	load("res://night_garden_atrium_interiors_20261022/adapter.gd").prepare(private_detail_residency,file)
	var shell:Node3D=super.register_private_interior(home,file)
	load("res://night_garden_atrium_interiors_20261022/adapter.gd").glazing(shell)
	return shell
