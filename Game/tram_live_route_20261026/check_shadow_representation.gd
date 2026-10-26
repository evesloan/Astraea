extends SceneTree
# One retained source, no ship, import, construction or production mutation.
func _initialize()->void:
	call_deferred("run")
func run()->void:
	var packed:PackedScene=load("res://assets/group2_completion/788.glb")
	var state:=packed.get_state()
	var unique:Dictionary={}
	var shadows:=0
	var main:=0
	var example:Dictionary={}
	for n in state.get_node_count():
		for p in state.get_node_property_count(n):
			if state.get_node_property_name(n,p)!=&"mesh":continue
			var mesh:Mesh=state.get_node_property_value(n,p)
			main+=1
			if not mesh is ArrayMesh or mesh.shadow_mesh==null:continue
			var shadow:ArrayMesh=mesh.shadow_mesh
			shadows+=1
			var payload:Dictionary={}
			for prop:Dictionary in shadow.get_property_list():
				if int(prop.usage)&PROPERTY_USAGE_STORAGE and str(prop.name) not in ["resource_name","resource_path","resource_local_to_scene"]:
					payload[str(prop.name)]=shadow.get(prop.name)
			var bytes:=var_to_bytes(payload)
			var ctx:=HashingContext.new();ctx.start(HashingContext.HASH_SHA256);ctx.update(bytes)
			var digest:=ctx.finish().hex_encode()
			if unique.has(digest):assert(unique[digest]==bytes,"Hash equality also requires exact bytes")
			else:unique[digest]=bytes
			if example.is_empty():
				example={"stored_properties":payload.keys(),"bytes":bytes.size(),"surfaces":shadow.get_surface_count(),"custom_aabb":str(shadow.custom_aabb)}
	var result:Dictionary={"key":"788","main_mesh_references":main,"shadow_mesh_references":shadows,"exact_shadow_serialized_groups":unique.size(),"example":example,"production_changed":false}
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--output="):
			var f:=FileAccess.open(arg.substr(9),FileAccess.WRITE);f.store_string(JSON.stringify(result,"\t"));f.close()
	print("EXACT_SHADOW_REPRESENTATION ",JSON.stringify(result))
	quit(0)
