extends SceneTree
const LEASE=preload("res://group2_resource_lifetime_20261025/mesh_lease.gd")
var output:String
var results:Array=[]
var failures:Array=[]
func _initialize()->void:call_deferred("run")
func require(ok:bool,message:String)->void:
	if not ok:failures.append(message);push_error(message)
func geometry(mesh:Mesh)->String:
	var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256)
	for s in mesh.get_surface_count():h.update(var_to_bytes(mesh.surface_get_arrays(s)));h.update(var_to_bytes(mesh.surface_get_primitive_type(s)))
	return h.finish().hex_encode()
func snapshot(room:Node3D)->Dictionary:
	var rows:Dictionary={}
	for node:MeshInstance3D in room.find_children("*","MeshInstance3D",true,false):
		var mats:Array=[]
		for s in node.mesh.get_surface_count():mats.append(node.mesh.surface_get_material(s))
		rows[node.get_instance_id()]={"ref":weakref(node.mesh),"geometry":geometry(node.mesh),"pose":node.transform,"parent":node.get_parent().get_instance_id(),"materials":mats,"override":node.material_override}
	return rows
func contacts(room:Node3D)->Array:
	var rows:Array=[]
	for shape:CollisionShape3D in room.find_children("*","CollisionShape3D",true,false):rows.append([shape.get_instance_id(),shape.shape.get_instance_id(),shape.transform])
	return rows
func save()->void:
	var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify({"results":results,"failures":failures},"\t"));f.close()
func run()->void:
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
	if output.is_empty():quit(2);return
	var service:Node3D=load("res://scripts/ship.gd").new() # Not added: no whole-ship _ready.
	var host:=Node3D.new();root.add_child(host)
	var definitions:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/received_sections.json"))
	for section:Dictionary in definitions.sections:
		var path:String="res://assets/models/"+str(section.model_file)
		require(FileAccess.get_sha256(path)==str(section.source_sha256),path+": source bytes")
		var start:int=OS.get_static_memory_usage()
		var room:Node3D=service.model(host,str(section.model_file),str(section.programme_key),Vector3.ZERO)
		var packed:PackedScene=load(path)
		require(LEASE.bind(room,room.get_child(0),packed,path,true),path+": bind")
		packed=null
		var before:Dictionary=snapshot(room);var old_contacts:=contacts(room)
		var loaded:int=OS.get_static_memory_usage()
		host.remove_child(room)
		var suspended:int=LEASE.suspend(room)
		await process_frame
		var released:int=OS.get_static_memory_usage();var live:=0
		for row:Dictionary in before.values():
			if row.ref.get_ref()!=null:live+=1
		require(live==0,path+": no surviving source meshes")
		require(LEASE.resume(room),path+": restore")
		host.add_child(room)
		var after:Dictionary=snapshot(room)
		require(after.size()==before.size(),path+": same nodes")
		for id:int in before:
			for field:String in ["geometry","pose","parent","materials","override"]:require(before[id][field]==after[id][field],path+": unchanged "+field)
		require(old_contacts==contacts(room),path+": same contact nodes/shapes/poses")
		host.remove_child(room);var suspended_again:int=LEASE.suspend(room)
		require(suspended_again==suspended,path+": repeat release coverage")
		await process_frame
		for row:Dictionary in after.values():require(row.ref.get_ref()==null,path+": repeat weak reference expiry")
		require(LEASE.resume(room),path+": repeat restoration")
		require(old_contacts==contacts(room),path+": repeated contact identity")
		results.append({"file":section.model_file,"mesh_nodes":before.size(),"suspended":suspended,"second_suspend":suspended_again,"retained_mesh_references":live,"collision_shapes":old_contacts.size(),"loaded_static_delta":loaded-start,"suspended_static_saving":loaded-released})
		print("RECEIVED_LEASE ",JSON.stringify(results[-1]));save()
		room.free()
		await process_frame
	service.free();host.free();save();quit(0 if failures.is_empty() else 1)
