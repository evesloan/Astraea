extends SceneTree
# Three dominant retained owners only; no ship, import, movement or FPS claim.
var output:String
var rows:Array=[]
func _initialize()->void:
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--output="):output=arg.substr(9)
	call_deferred("run")
func sample(label:String)->void:
	var row:Dictionary={"stage":label,"static_bytes":OS.get_static_memory_usage(),"resources":Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT),"nodes":Performance.get_monitor(Performance.OBJECT_NODE_COUNT),"video_bytes":RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_VIDEO_MEM_USED)}
	rows.append(row);print(JSON.stringify(row));save()
func save()->void:
	var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify(rows,"\t"));f.close()
func census(scene:PackedScene)->Dictionary:
	var meshes:Dictionary={};var materials:Dictionary={};var textures:Dictionary={};var bytes:=0;var image_bytes:=0;var shadows:Dictionary={}
	var state:=scene.get_state()
	for n in state.get_node_count():
		for p in state.get_node_property_count(n):
			if state.get_node_property_name(n,p)!=&"mesh":continue
			var mesh:ArrayMesh=state.get_node_property_value(n,p) as ArrayMesh
			if mesh==null or meshes.has(mesh.get_instance_id()):continue
			meshes[mesh.get_instance_id()]=true
			if mesh.shadow_mesh!=null:shadows[mesh.shadow_mesh.get_instance_id()]=true
			for surface:Dictionary in mesh.get("_surfaces"):
				for value:Variant in surface.values():
					if value is PackedByteArray:bytes+=value.size()
			for s in mesh.get_surface_count():
				var mat:Material=mesh.surface_get_material(s)
				if mat==null or materials.has(mat.get_instance_id()):continue
				materials[mat.get_instance_id()]=true
				for prop:Dictionary in mat.get_property_list():
					if int(prop.type)!=TYPE_OBJECT or not (int(prop.usage)&PROPERTY_USAGE_STORAGE):continue
					var tex:Variant=mat.get(prop.name)
					if not tex is Texture2D or textures.has(tex.get_instance_id()):continue
					textures[tex.get_instance_id()]=true
					var image:Image=tex.get_image()
					if image!=null:image_bytes+=image.get_data().size()
	return {"scene_nodes":state.get_node_count(),"main_meshes":meshes.size(),"shadow_meshes":shadows.size(),"main_surface_buffer_bytes":bytes,"materials":materials.size(),"textures":textures.size(),"texture_image_bytes":image_bytes}
func one(path:String)->void:
	sample("before:"+path)
	var packed:PackedScene=load(path)
	load("res://group2_resource_lifetime_20261025/shadow_mesh_pool.gd").intern_scene(packed)
	sample("loaded:"+path)
	rows.append({"source":path,"sha256":FileAccess.get_sha256(path),"census":census(packed)});save()
	var node:Node3D=packed.instantiate()
	sample("instantiated:"+path)
	node.free();packed=null
func run()->void:
	for path:String in ["res://assets/group2_completion/788.glb","res://assets/group2_completion/812.glb","res://assets/models/SOL_D01_directory_10_remaining_r001.glb"]:
		one(path)
		await process_frame
		load("res://group2_resource_lifetime_20261025/shadow_mesh_pool.gd").prune()
		sample("released:"+path)
	quit(0)
