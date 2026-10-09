extends RefCounted
# Shared receiving rule: inert original witnesses and bounded runtime emitters.
# Does not change the production manager or its global budgets.
static func normalize(source: Node3D, expected_count: int) -> Array[Light3D]:
	var originals:=source.find_children("*","Light3D",true,false)
	assert(originals.size()==expected_count)
	var lights: Array[Light3D]=[]
	for original: Light3D in originals:
		assert(original is SpotLight3D or original is OmniLight3D)
		original.visible=false
		original.shadow_enabled=false
		original.set_meta("fixture_powered",false)
		original.set_meta("retained_source_light_witness",true)
		var light: Light3D
		if original is SpotLight3D:
			var spot:=SpotLight3D.new()
			spot.spot_range=8.0
			spot.spot_angle=minf(original.spot_angle,65.0)
			spot.spot_attenuation=1.0
			light=spot
		else:
			var omni:=OmniLight3D.new()
			omni.omni_range=8.0
			omni.omni_attenuation=1.0
			light=omni
		light.name=str(original.name)+"_PhysicalSource"
		light.transform=original.transform
		light.light_color=original.light_color
		light.light_energy=1.2
		light.visible=false
		light.shadow_enabled=false
		light.set_meta("fixture_powered",true)
		light.set_meta("source_light_name",str(original.name))
		light.set_meta("calibration","bounded_initial_unaccepted")
		original.get_parent().add_child(light)
		lights.append(light)
	return lights
static func register(lights: Array[Light3D],ship: Node3D) -> void:
	var budget:=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	assert(budget.shadow_source_budget==8 and budget.MAX_VISIBILITY_CANDIDATES==32)
	for light: Light3D in lights:
		assert(not budget.sources.has(light))
		budget.sources.append(light)
		budget.requested_shadow[light.get_instance_id()]=true
	budget.refresh()
