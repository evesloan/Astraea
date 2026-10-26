extends SceneTree
# Bounded single-source ownership check. Flush stages before native calls.
var report:FileAccess
func mark(stage:String,detail:Dictionary={})->void:
	report.store_line(JSON.stringify({"stage":stage,"detail":detail}));report.flush()
func _initialize()->void:
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--output="):report=FileAccess.open(arg.substr(9),FileAccess.WRITE)
	if report==null:quit(2);return
	mark("initialized")
	call_deferred("run")
func run()->void:
	mark("before_load")
	var packed:PackedScene=load("res://assets/group2_completion/788.glb")
	mark("loaded",{"resources":Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT)})
	var state:=packed.get_state()
	var meshes:Dictionary={};var shadows:Dictionary={};var refs:Array[WeakRef]=[]
	for n in state.get_node_count():
		for p in state.get_node_property_count(n):
			if state.get_node_property_name(n,p)!=&"mesh":continue
			var mesh:Mesh=state.get_node_property_value(n,p)
			meshes[mesh.get_rid().get_id()]=true
			refs.append(weakref(mesh))
			if mesh is ArrayMesh and mesh.shadow_mesh!=null:
				shadows[mesh.shadow_mesh.get_rid().get_id()]=true
				if shadows.size()==1:
					var surfaces:Array=mesh.shadow_mesh.get("_surfaces")
					var fields:Dictionary={}
					for key:Variant in surfaces[0]:
						var value:Variant=surfaces[0][key]
						fields[str(key)]={"type":type_string(typeof(value)),"value":str(value) if typeof(value) in [TYPE_STRING,TYPE_INT,TYPE_FLOAT,TYPE_NIL,TYPE_OBJECT] else "binary_or_structured"}
					mark("shadow_surface_fields",fields)
	mark("owners",{"main_mesh_rids":meshes.size(),"shadow_mesh_rids":shadows.size()})
	state=null;packed=null
	await process_frame
	var retained:=0
	for ref:WeakRef in refs:
		if ref.get_ref()!=null:retained+=1
	mark("released",{"remaining_main_meshes":retained,"resources":Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT)})
	report.close();quit(0)
