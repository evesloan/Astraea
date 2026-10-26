extends SceneTree
# Bounded owner attribution; the selected ship and production sources are unchanged.
var output:String
var rows:Array=[]
func _initialize()->void:
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--output="):output=arg.substr(9)
	call_deferred("run")
func sample(label:String)->void:
	rows.append({"stage":label,"static_bytes":OS.get_static_memory_usage(),"resources":Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT),"nodes":Performance.get_monitor(Performance.OBJECT_NODE_COUNT),"video_bytes":RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_VIDEO_MEM_USED)})
	save()
func save()->void:
	var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify(rows,"\t"));f.close()
func one(path:String)->void:
	sample("before:"+path)
	var packed:PackedScene=load(path)
	load("res://group2_resource_lifetime_20261025/shadow_mesh_pool.gd").intern_scene(packed)
	sample("loaded:"+path)
	var node:Node3D=packed.instantiate();root.add_child(node)
	await process_frame
	sample("live_visual:"+path)
	var meshes:Array[Node]=node.find_children("*","MeshInstance3D",true,false)
	var start:=Time.get_ticks_usec()
	for mesh:MeshInstance3D in meshes:
		if mesh.mesh!=null and mesh.visible and not mesh.name.begins_with("ALC_VisualFloor"):
			load("res://scripts/static_contact_cache.gd").attach(mesh)
	await physics_frame
	sample("live_contacts:"+path)
	var shapes:Dictionary={};var triangles:=0;var bodies:=0
	for body:StaticBody3D in node.find_children("*","StaticBody3D",true,false):bodies+=1
	for col:CollisionShape3D in node.find_children("*","CollisionShape3D",true,false):
		if col.shape!=null and not shapes.has(col.shape.get_instance_id()):
			shapes[col.shape.get_instance_id()]=true
			if col.shape is ConcavePolygonShape3D:triangles+=col.shape.get_faces().size()/3
	rows.append({"source":path,"source_sha256":FileAccess.get_sha256(path),"mesh_nodes":meshes.size(),"static_bodies":bodies,"unique_shapes":shapes.size(),"unique_contact_triangles":triangles,"contact_build_us":Time.get_ticks_usec()-start})
	# Free only diagnostic source instance and resources, never original files.
	node.free();packed=null;meshes.clear();save()
func run()->void:
	for path:String in ["res://assets/models/SOL_D10_directory_06_source001.glb","res://assets/models/SOL_D09_directory_03_source001.glb","res://assets/models/SOL_D11_directory_05_source001.glb","res://assets/models/SOL_D01_directory_10_remaining_r001.glb"]:
		await one(path)
		for i in 3:await process_frame
		load("res://group2_resource_lifetime_20261025/shadow_mesh_pool.gd").prune()
		sample("released:"+path)
	print(JSON.stringify(rows));quit()
