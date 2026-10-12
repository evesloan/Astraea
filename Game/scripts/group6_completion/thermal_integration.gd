extends RefCounted
# Group1-only call after its existing entries/support loop and light registration,
# before static occlusion/residency. No shared root or manager is edited here.
class LocalReflectionActivation:
	extends Node
	var room:Node3D
	var budget:Node
	func _process(_delta:float)->void:
		if not is_instance_valid(room) or not is_instance_valid(budget) or not room.is_inside_tree() or not is_instance_valid(budget.actor):return
		var addition:Node3D=room.get_node("Group6TidalNorthRoom")
		var reflection:ReflectionProbe=addition.get_node("TidalActualRoomReflection")
		if reflection.visible:set_process(false);return
		var at:Vector3=room.to_local(budget.actor.global_position)
		if at.x<27 or at.x>51.2 or at.y<43.95 or at.y>48 or at.z< -437 or at.z> -400:return
		var admitted:=0
		for light:Light3D in addition.find_children("*","Light3D",true,false):
			if not budget.sources.has(light):return
			if light.visible and light.shadow_enabled:admitted+=1
		if admitted==0:return
		load("res://scripts/group6_completion/tidal_north_room.gd").activate_reflection(room,budget)
		set_meta("admitted_room_sources_at_capture",admitted);set_process(false)
static func finish(ship:Node3D,include_tidal:bool=true)->Dictionary:
	assert(ship.get_node_or_null("ShipSystems/ReceivedRoomResidency")==null and not ship.has_meta("static_occlusion_registered"),"Install before occlusion/residency; restart instead of hot swapping")
	var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget");assert(budget.actor!=null)
	var additions:Array=[];var lights:Array[Light3D]=[]
	for key in ["D08_directory_02","D08_directory_03"]:
		if key=="D08_directory_02" and not include_tidal:continue
		var room:Node3D=ship.get_node("ShipSpace/Districts/ReceivedSections/"+key)
		assert(room.get_node_or_null("Group6ThermalEntries")!=null and room.get_node_or_null("Group6ThermalSupport")!=null)
		assert(room.get_node_or_null("Group6ThermalRecovery")==null,"Fresh construction required: never stack recovery revisions")
		var recovery:Node3D=load("res://scripts/group6_completion/thermal_recovery.gd").build(room,true);additions.append(recovery)
		if key=="D08_directory_02":
			var chamber:Node3D=load("res://scripts/group6_completion/tidal_north_room.gd").build(room);additions.append(chamber)
			var activation:=LocalReflectionActivation.new();activation.name="AfterBudgetLocalReflection";activation.room=room;activation.budget=budget;activation.process_priority=10;chamber.add_child(activation)
	for addition:Node3D in additions:
		for light:Light3D in addition.find_children("*","Light3D",true,false):
			assert(not budget.sources.has(light));lights.append(light)
	load("res://scripts/receiving_source_lights.gd").register(lights,ship)
	return {"recovery_rooms":2 if include_tidal else 1,"tidal_room_added":include_tidal,"new_registered_sources":lights.size(),"reflection":"automatic once on first local arrival after at least one owned source is admitted; stays inert outside room","scope":"Construction installation only; source fit/current-root check required, no occupied-water or whole-group acceptance"}
