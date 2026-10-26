extends SceneTree
const LEASE=preload("res://group2_resource_lifetime_20261025/mesh_lease.gd")
var output:String
var rows:Array=[]
var failures:Array=[]
func _initialize()->void:
	for a:String in OS.get_cmdline_user_args():
		if a.begins_with("--output="):output=a.substr(9)
	call_deferred("run")
func require(ok:bool,message:String)->void:
	if not ok:failures.append(message);push_error(message)
func digest(mesh:Mesh)->String:
	var hash:=HashingContext.new();hash.start(HashingContext.HASH_SHA256)
	for s in mesh.get_surface_count():
		hash.update(var_to_bytes(mesh.surface_get_arrays(s)))
		hash.update(var_to_bytes(mesh.surface_get_primitive_type(s)))
		var material:=mesh.surface_get_material(s)
		if material!=null:
			for prop:Dictionary in material.get_property_list():
				if not (int(prop.usage)&PROPERTY_USAGE_STORAGE):continue
				var value=material.get(prop.name)
				if value is Resource:value=str(value.resource_path)
				hash.update(var_to_bytes([prop.name,value]))
	return hash.finish().hex_encode()
func snapshot(source:Node3D)->Dictionary:
	var data:Dictionary={}
	for mesh:MeshInstance3D in source.find_children("*","MeshInstance3D",true,false):
		data[mesh.get_instance_id()]={"pose":mesh.transform,"parent":mesh.get_parent().get_instance_id(),"geometry":digest(mesh.mesh),"ref":weakref(mesh.mesh)}
	return data
func run()->void:
	if output.is_empty():quit(2);return
	for key:String in ["788", "812", "818"]:
		var room:=Node3D.new();root.add_child(room)
		var source:Node3D=load("res://scripts/group2_completion/package.gd").build_section(room,key)
		room.set_meta("retained_group2_home",true)
		room.set_meta("resident_visual",source)
		var before:=snapshot(source)
		var controls:Array=[]
		for node:Node in source.get_children():
			if str(node.name).begins_with("Fitting_"):
				node.open_fraction=0.37;node.desired_open=true;node._apply_pose()
				controls.append({"node":node,"id":node.persistent_id,"pose":node.open_fraction})
		before=snapshot(source)
		var contact_ids:Array=[]
		for node:CollisionShape3D in source.find_children("*","CollisionShape3D",true,false):contact_ids.append([node.get_instance_id(),node.shape.get_instance_id(),node.transform])
		var loaded:=Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT)
		root.remove_child(room)
		load("res://scripts/received_homes_20261015/source_dispatch.gd").release(room)
		var suspended:=0
		for row:Dictionary in source.get_meta("group2_mesh_lease").rows:
			if row.suspended:suspended+=1
		await process_frame
		var retained:=0
		for row:Dictionary in before.values():
			if row.ref.get_ref()!=null:retained+=1
		var after:=Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT)
		require(retained==0,key+": source meshes must expire while detached")
		load("res://scripts/received_homes_20261015/source_dispatch.gd").ensure(room)
		root.add_child(room)
		var after_snapshot:=snapshot(source)
		require(before.size()==after_snapshot.size(),key+": all mesh nodes retained")
		for id:int in before:
			require(after_snapshot.has(id),key+": same mesh node identity")
			for field:String in ["pose","parent","geometry"]:require(before[id][field]==after_snapshot[id][field],key+": exact "+field)
		for control:Dictionary in controls:require(control.node.persistent_id==control.id and control.node.open_fraction==control.pose and control.node.desired_open,key+": original door state retained")
		var current_contacts:Array=[]
		for node:CollisionShape3D in source.find_children("*","CollisionShape3D",true,false):current_contacts.append([node.get_instance_id(),node.shape.get_instance_id(),node.transform])
		require(contact_ids==current_contacts,key+": same contact nodes shapes and poses")
		rows.append({"key":key,"mesh_nodes":before.size(),"suspended":suspended,"mesh_references_after_suspend":retained,"resources_loaded":loaded,"resources_suspended":after,"doors":controls.size(),"contacts":contact_ids.size()})
		var source_ref:WeakRef=weakref(source)
		root.remove_child(room)
		load("res://scripts/received_homes_20261015/source_dispatch.gd").release(room)
		room.free();await process_frame
		require(source_ref.get_ref()==null,key+": released room owns and frees cached source")
	var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify({"rows":rows,"failures":failures},"\t"));f.close()
	print("GROUP2_LEASE ",JSON.stringify({"rows":rows,"failures":failures}));quit(0 if failures.is_empty() else 1)
