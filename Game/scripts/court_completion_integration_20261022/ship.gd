extends "res://scripts/receiving_courts_integration_20261022/ship.gd"
const COURT_COMPLETION:="res://night_garden_court_completion_20261022/"
func _construction_step(label:String)->void:
	await super._construction_step(label)
	if label=="central_homes/night_garden_residency_20261022":
		assert(FileAccess.get_sha256(COURT_COMPLETION+"adapter.gd")=="8e89a98106965a2069e1e6223b76fd99203dc059f7ee7da9a146741c91b7d87d")
		assert(FileAccess.get_sha256(COURT_COMPLETION+"lighting_budget.gd")=="ef54af36bede98bab31e06d1116651fae8ab1ed19e0d0556ae493dc129c4c1e7")
		assert(FileAccess.get_sha256(COURT_COMPLETION+"evidence/BUILD_R003.json")=="b618eb4a8b1488f77918d2cd2a1283fc1767a5943d3dedb24b36452ab720305b")
		assert(FileAccess.get_sha256(COURT_COMPLETION+"evidence/BAKE_R003.json")=="b7bd0c1a2bffb8df862bc104a8dd9923c260d837fdd1cfec8b519f3b846827d8")
		assert(FileAccess.get_sha256(COURT_COMPLETION+"evidence/PREREQUISITES.json")=="2a936a3ff689cfd6fbe8c4f3849c46b4214cf8c904013a3fa917aace3b968863")
		load(COURT_COMPLETION+"adapter.gd").finish(self)
	elif label=="group4_integrated_receiving.gd":
		var budget:Node=get_node("ShipSystems/LocalShadowSourceBudget")
		if budget.get_script()==load("res://scripts/lighting_budget.gd"):
			assert(budget.sources.is_empty(),"Do not replace an already configured lighting owner")
			var limit:int=budget.shadow_source_budget
			budget.set_script(load(COURT_COMPLETION+"lighting_budget.gd"))
			budget.shadow_source_budget=limit
		else:assert(budget.get_script()==load(COURT_COMPLETION+"lighting_budget.gd"),"Unexpected lighting owner")
