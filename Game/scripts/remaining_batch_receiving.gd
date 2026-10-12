extends Node3D
# Additive source integration; detailed traversal, gameplay and polish deferred.
static func build(ship: Node3D) -> void:
	var floor_data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/REMAINING_BATCH_FLOORS.json"))
	assert(FileAccess.get_sha256("res://data/generated/structural_meshes.json")==str(floor_data.source_checks.baseline_structural_sha256))
	load("res://scripts/structural_floor_builder.gd").build_regions(ship.get_node("ShipSpace"),ship.stone,ship.ivory,floor_data.regions,{"staff_floor":ship.surface("staff_floor",Color.WHITE)},"RemainingBatchStructuralFloors")
	var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/REMAINING_BATCH_SECTIONS.json"))

	var stream:Node3D=load("res://scripts/remaining_batch_receiving.gd").new()
	stream.name="RemainingBatchStreaming"
	ship.get_node("ShipSystems").add_child(stream)
	stream.setup(ship,data.sections)

var host:Node3D
var entries:Array=[]
var rooms:Dictionary={}
var actor:Node3D
var elapsed:float=0.0
func setup(ship:Node3D,rows:Array)->void:
	host=ship
	entries=rows
	actor=ship.get_node("ShipSpace/PersistentActors/Player")
	process_physics_priority=-100
	for item in entries:
		var room:=Node3D.new()
		room.name=str(item.name)+"Receiving_WIP"
		room.set_meta("programme_key",str(item.key))
		room.set_meta("stream_loaded",false)
		var xyz:Array=item.position
		room.position=Vector3(xyz[0],xyz[1],xyz[2])
		ship.get_node("ShipSpace/Districts").add_child(room)
		rooms[str(item.key)]=room
	refresh()
func _physics_process(delta:float)->void:
	elapsed+=delta
	if elapsed>=.2:
		elapsed=0
		refresh()
func refresh()->void:
	if not is_instance_valid(actor):return
	var pos:=actor.global_position
	var pending:Array=[]
	for item in entries:
		var lo:Array=item.bounds_min
		var hi:Array=item.bounds_max
		var room:Node3D=rooms[str(item.key)]
		var loaded:bool=room.get_meta("stream_loaded",false)
		# Wider retention boundary prevents repeated unload/reload at door thresholds.
		var margin:float=55.0 if loaded else 35.0
		var y_margin:float=3.0 if loaded else 1.0
		var close:=pos.y>=float(lo[1])-y_margin and pos.y<=float(hi[1])+y_margin and pos.x>=float(lo[0])-margin and pos.x<=float(hi[0])+margin and pos.z>=float(lo[2])-margin and pos.z<=float(hi[2])+margin
		if close and not loaded:pending.append(item)
		elif not close and loaded:
			var budget:=host.get_node("ShipSystems/LocalShadowSourceBudget")
			for light in room.find_children("*","Light3D",true,false):
				budget.sources.erase(light)
				budget.requested_shadow.erase(light.get_instance_id())
			for child in room.get_children():child.free()
			room.set_meta("stream_loaded",false)
			budget.refresh()
	for item in pending:install(host,item,rooms[str(item.key)])
static func install(ship:Node3D,item:Dictionary,room:Node3D)->Node3D:
	assert(FileAccess.get_sha256(str(item.runtime))==str(item.hash))
	room.set_meta("programme_key",str(item.key))
	room.set_meta("installed_acceptance",false)
	var xyz:Array=item.position
	room.position=Vector3(xyz[0],xyz[1],xyz[2])
	var source:Node3D=(load(str(item.runtime)) as PackedScene).instantiate()
	room.add_child(source)
	var meshes:=source.find_children("*","MeshInstance3D",true,false)
	assert(meshes.size()==int(item.meshes))
	for mesh:MeshInstance3D in meshes:
		var n:=str(mesh.name).replace(".","_")
		# Receiving-owned collision decision for six 18mm painted bay borders.
		# Signs, supports and seating remain precise collidable geometry.
		var visual_border:=str(item.key)=="D11_directory_02" and (n.begins_with("WP13_C1_R01_P01_bay_") or n.begins_with("WP13_C1_R01_P20_bay_")) and (n.ends_with("bay_front") or n.ends_with("bay_side") or n.ends_with("bay_side_001"))
		if visual_border:
			mesh.set_meta("receiving_collision_policy","visual bay border")
		else:load("res://scripts/static_contact_cache.gd").attach(mesh)
	load("res://scripts/static_room_occlusion.gd").install(source)
	var lights:Array[Light3D]=load("res://scripts/receiving_source_lights.gd").normalize(source,int(item.lights))

	for fixture in item.get("fixture_lights",[]):
		var light:=OmniLight3D.new()
		light.name=str(fixture.name)+"_PhysicalSource"
		room.add_child(light)
		var xyz2:Array=fixture.world_xyz
		light.global_position=Vector3(xyz2[0],xyz2[1],xyz2[2])
		var color:Array=fixture.color
		light.light_color=Color(color[0],color[1],color[2])
		light.light_energy=1.2
		light.omni_range=8.0
		light.visible=false
		light.shadow_enabled=false
		light.set_meta("fixture_powered",true)
		light.set_meta("calibration","bounded_initial_unaccepted")
		lights.append(light)
	load("res://scripts/receiving_source_lights.gd").register(lights,ship)
	room.set_meta("normalized_source_count",lights.size())

	if str(item.key)=="D12_directory_02":load("res://scripts/group8/library_service.gd").build(ship,room)
	room.set_meta("stream_loaded",true)
	return room
