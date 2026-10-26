extends RefCounted
# Preserve authored nodes, controller state, transforms and contact shapes.
# Only release source Mesh resources while their entire room is detached.
static func source_bytes(path:String)->String:
	if FileAccess.file_exists(path):return path
	# Exported projects retain imported scene bytes rather than the original GLB.
	for suffix:String in [".remap",".import"]:
		var config:=ConfigFile.new()
		if config.load(path+suffix)!=OK:continue
		var mapped:String=str(config.get_value("remap","path",""))
		if not mapped.is_empty() and FileAccess.file_exists(mapped):return mapped
	return ""
static func bind(owner:Node3D,visual:Node3D,packed:PackedScene,path:String,guard_changes:bool=false)->bool:
	var bytes_path:=source_bytes(path)
	if bytes_path.is_empty():
		push_error("No readable exact Group2 source bytes for mesh restoration")
		return false
	load("res://group2_resource_lifetime_20261025/shadow_mesh_pool.gd").intern_scene(packed)
	var state:=packed.get_state()
	var rows:Array=[]
	for n in state.get_node_count():
		for p in state.get_node_property_count(n):
			if state.get_node_property_name(n,p)!=&"mesh":continue
			var mesh:Mesh=state.get_node_property_value(n,p)
			var node:MeshInstance3D=visual.get_node_or_null(state.get_node_path(n)) as MeshInstance3D
			if mesh==null or node==null or node.mesh!=mesh:
				push_error("Group2 lease requires exact non-local source mesh binding")
				return false
			var row:Dictionary={"node":weakref(node),"state_node":n,"state_property":p,"mesh_id":mesh.get_instance_id(),"suspended":false,"changed":false,"guard_changes":guard_changes}
			if guard_changes:
				var callback:Callable=func()->void:row.changed=true
				node.set_meta("source_mesh_change_callback",callback)
				mesh.changed.connect(callback)
			rows.append(row)
	owner.set_meta("group2_mesh_lease",{"path":path,"bytes_path":bytes_path,"sha256":FileAccess.get_sha256(bytes_path),"rows":rows})
	return true
static func suspend(owner:Node3D)->int:
	if owner.is_inside_tree():
		push_error("Group2 mesh release requires a detached room")
		return 0
	if not owner.has_meta("group2_mesh_lease"):return 0
	var lease:Dictionary=owner.get_meta("group2_mesh_lease")
	var count:=0
	for row:Dictionary in lease.rows:
		var node:MeshInstance3D=row.node.get_ref()
		# Independently replaced or removed geometry is not ours to restore.
		if node==null or node.mesh==null or node.mesh.get_instance_id()!=int(row.mesh_id) or bool(row.get("changed",false)):continue
		# Material objects may have exact texture interning or live authored edits.
		# Keep those small owners; release geometry without losing their state.
		var materials:Array[Material]=[]
		for surface in node.mesh.get_surface_count():materials.append(node.mesh.surface_get_material(surface))
		row.materials=materials
		node.mesh=null
		row.suspended=true
		count+=1
	if OS.get_environment("ASTRAEA_TRACE_GROUP2")=="1":print("GROUP2_MESH_RELEASE ",JSON.stringify({"key":str(owner.get_meta("group2_source_key","")),"released_mesh_nodes":count,"resources":Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT)}))
	return count
static func resume(owner:Node3D)->bool:
	if not owner.has_meta("group2_mesh_lease"):return true
	var lease:Dictionary=owner.get_meta("group2_mesh_lease")
	var needed:=false
	for row:Dictionary in lease.rows:
		if bool(row.suspended):needed=true;break
	if not needed:return true
	if FileAccess.get_sha256(str(lease.bytes_path))!=str(lease.sha256):
		push_error("Group2 retained mesh source changed; refusing restoration")
		return false
	var packed:PackedScene=load(str(lease.path))
	if packed==null:return false
	load("res://group2_resource_lifetime_20261025/shadow_mesh_pool.gd").intern_scene(packed)
	var state:=packed.get_state()
	# Validate every destination before restoring any of them.
	for row:Dictionary in lease.rows:
		if not bool(row.suspended):continue
		var node:MeshInstance3D=row.node.get_ref()
		if node==null:continue
		if node.mesh!=null or not state.get_node_property_value(int(row.state_node),int(row.state_property)) is Mesh:
			push_error("Group2 suspended mesh destination changed")
			return false
	for row:Dictionary in lease.rows:
		if not bool(row.suspended):continue
		var node:MeshInstance3D=row.node.get_ref()
		if node!=null:
			node.mesh=state.get_node_property_value(int(row.state_node),int(row.state_property))
			for surface in node.mesh.get_surface_count():
				if node.mesh.surface_get_material(surface)!=row.materials[surface]:node.mesh.surface_set_material(surface,row.materials[surface])
			row.mesh_id=node.mesh.get_instance_id()
			row.changed=false
			if bool(row.get("guard_changes",false)):
				var callback:Callable=node.get_meta("source_mesh_change_callback")
				if not node.mesh.changed.is_connected(callback):node.mesh.changed.connect(callback)
		row.erase("materials")
		row.suspended=false
	return true
