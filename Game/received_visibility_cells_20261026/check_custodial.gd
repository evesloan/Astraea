extends SceneTree
class Budget:
	extends Node
	const MAX_VISIBILITY_CANDIDATES:=32
	var shadow_source_budget:=8
	var sources:Array[Light3D]=[]
	var requested_shadow:Dictionary={}
	func refresh()->void:pass
class Fixture:
	extends Node3D
	var stone:Material=StandardMaterial3D.new()
	var ivory:Material=StandardMaterial3D.new()
	func surface(_role:String,_color:Color)->Material:return stone
var checks:=0
var failures:Array=[]
func require(ok:bool,label:String)->void:
	checks+=1
	if not ok:failures.append(label);push_error(label)
func _initialize()->void:call_deferred("run")
func snapshot(room:Node3D)->Dictionary:
	var rows:Dictionary={}
	for node:MeshInstance3D in room.find_children("*","MeshInstance3D",true,false):
		var hash:=HashingContext.new();hash.start(HashingContext.HASH_SHA256)
		var materials:Array=[]
		for surface in node.mesh.get_surface_count():hash.update(var_to_bytes(node.mesh.surface_get_arrays(surface)));materials.append(node.mesh.surface_get_material(surface))
		rows[node.get_instance_id()]={"pose":node.transform,"parent":node.get_parent().get_instance_id(),"geometry":hash.finish().hex_encode(),"materials":materials,"ref":weakref(node.mesh)}
	return rows
func run()->void:
	var host:=Fixture.new();root.add_child(host);host.set_meta("runtime_ready",true)
	var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
	var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
	var systems:=Node.new();systems.name="ShipSystems";host.add_child(systems)
	var budget:=Budget.new();budget.name="LocalShadowSourceBudget";systems.add_child(budget)
	var before_load:=OS.get_static_memory_usage()
	var room:Node3D=load("res://scripts/custodial_depot_candidate.gd").build(host)
	require(room!=null and room.has_meta("source_mesh_lease_host"),"Actual production builder binds retained source")
	var before:=snapshot(room);require(before.size()==7400,"All7400 original mesh nodes accounted")
	var contacts:Array=[]
	for shape:CollisionShape3D in room.find_children("*","CollisionShape3D",true,false):contacts.append([shape.get_instance_id(),shape.shape.get_instance_id(),shape.transform])
	room.set_meta("test_persistent_state",{"baggage_receipt":"test-only","value":37})
	var loaded:=OS.get_static_memory_usage()
	districts.remove_child(room);load("res://scripts/received_homes_20261015/source_dispatch.gd").release(room)
	await process_frame
	var suspended:=OS.get_static_memory_usage();var live:=0
	for row:Dictionary in before.values():
		if row.ref.get_ref()!=null:live+=1
	require(live==0,"All original main mesh owners expire when detached")
	load("res://scripts/received_homes_20261015/source_dispatch.gd").ensure(room);districts.add_child(room)
	var after:=snapshot(room);require(after.size()==before.size(),"Same original mesh nodes")
	for id:int in before:
		for key:String in ["pose","parent","geometry","materials"]:require(before[id][key]==after[id][key],"Exact restored "+key)
	var current:Array=[]
	for shape:CollisionShape3D in room.find_children("*","CollisionShape3D",true,false):current.append([shape.get_instance_id(),shape.shape.get_instance_id(),shape.transform])
	require(current==contacts,"All contact identities shapes and poses preserved")
	require(room.get_meta("test_persistent_state").value==37 and room.get_meta("stock_operations")=="not_implemented","Persistent test state retained without inventing stock operations")
	require(budget.sources.size()==35,"Normalized light registration not duplicated on resume")
	districts.remove_child(room);load("res://scripts/received_homes_20261015/source_dispatch.gd").release(room);room.free()
	await process_frame
	for row:Dictionary in after.values():require(row.ref.get_ref()==null,"Second release and teardown expire mesh owners")
	var result:Dictionary={"checks":checks,"failures":failures,"mesh_nodes":before.size(),"contacts":contacts.size(),"live_after_suspend":live,"static_before_load":before_load,"static_loaded":loaded,"static_suspended":suspended,"saved_static_bytes":loaded-suspended}
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--output="):
			var f:=FileAccess.open(arg.substr(9),FileAccess.WRITE);f.store_string(JSON.stringify(result,"\t"));f.close()
	host.queue_free();await process_frame;await process_frame
	print(JSON.stringify(result));quit(0 if failures.is_empty() else 1)
