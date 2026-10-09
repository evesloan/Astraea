extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for i in range(12):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	assert(ship.get_node_or_null("ShipSpace/Districts/TidalRoomCandidates")!=null)
	assert(ship.find_child("EngineeringCalibrationBank",true,false)!=null)
	assert(main.get_node_or_null("LivePerformanceReadout")!=null)
	var report:Dictionary=ship.get_meta("static_occlusion_registered")
	assert(int(report.triangles)>0 and int(report.cells)>0)
	var count_before:=ship.find_children("*","OccluderInstance3D",true,false).size()
	load("res://scripts/static_room_occlusion.gd").install(ship)
	assert(count_before==ship.find_children("*","OccluderInstance3D",true,false).size())
	var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	assert(budget.shadow_source_budget==8 and budget.MAX_VISIBILITY_CANDIDATES==32)
	var active:=0
	for light in budget.sources:
		if is_instance_valid(light) and light.shadow_enabled and light.visible:active+=1
	assert(active<=8)
	# Standalone aperture witness uses exact separated wall pieces; never a box over the opening.
	var fixture:=Node3D.new()
	root.add_child(fixture)
	var opaque:=StandardMaterial3D.new()
	for x in [-2.0,2.0]:
		var n:=MeshInstance3D.new()
		var a:=ArrayMesh.new()
		var tool:=SurfaceTool.new()
		tool.begin(Mesh.PRIMITIVE_TRIANGLES)
		for v in [Vector3(x-.5,0,0),Vector3(x+.5,0,0),Vector3(x+.5,5,0),Vector3(x-.5,0,0),Vector3(x+.5,5,0),Vector3(x-.5,5,0)]:tool.add_vertex(v)
		tool.set_material(opaque)
		n.mesh=tool.commit(a)
		fixture.add_child(n)
	var glass:=MeshInstance3D.new()
	var glass_material:=StandardMaterial3D.new()
	glass_material.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
	var glass_mesh:=ArrayMesh.new()
	var glass_tool:=SurfaceTool.new()
	glass_tool.begin(Mesh.PRIMITIVE_TRIANGLES)
	for v in [Vector3(-1,0,0),Vector3(1,0,0),Vector3(1,5,0)]:glass_tool.add_vertex(v)
	glass_tool.set_material(glass_material)
	glass.mesh=glass_tool.commit(glass_mesh)
	fixture.add_child(glass)
	var witness:Dictionary=load("res://scripts/static_room_occlusion.gd").install(fixture)
	assert(int(witness.triangles)==4)
	for o:OccluderInstance3D in fixture.find_children("*","OccluderInstance3D",true,false):
		for v in o.occluder.vertices:assert(absf(v.x)>=1.5)
	var result:Dictionary={"status":"PASS","actual_ship":report,"occluder_count":count_before,"aperture_and_glass_witness":"PASS exact wall triangles keep2m central opening; transparent witness excluded","idempotency":"PASS","active_shadow_sources":active,"scope":"Headless correctness, actual main load, opacity/aperture witness. No GPU timings, Windows FPS or visual acceptance."}
	FileAccess.open("res://artifacts/static_room_occlusion.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("STATIC_ROOM_OCCLUSION ",JSON.stringify(result))
	quit()
