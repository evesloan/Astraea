extends SceneTree
const POOL=preload("res://visible_resource_budget_20261026/exact_contact_pool.gd")
var output:String
var rows:Array=[]
var checks:=0
func _initialize()->void:
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--output="):output=arg.substr(9)
	call_deferred("run")
func save()->void:
	var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify(rows,"\t"));f.close()
func sample(stage:String)->void:
	rows.append({"stage":stage,"static_bytes":OS.get_static_memory_usage(),"nodes":Performance.get_monitor(Performance.OBJECT_NODE_COUNT),"resources":Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT),"pool_hits":POOL.hits,"pool_groups":POOL.entries.size()});save()
func pass_sources(pooled:bool)->void:
	var host:=Node3D.new();root.add_child(host)
	var names:=["SOL_D10_directory_06_source001.glb","SOL_D09_directory_03_source001.glb","SOL_D11_directory_05_source001.glb","SOL_D11_directory_07_source001.glb","SOL_D11_directory_03_source001.glb","SOL_D11_directory_04_source001.glb","SOL_D10_directory_10_source001.glb","SOL_D09_directory_07_source001.glb","SOL_D01_directory_10_remaining_r001.glb"]
	var shapes:Dictionary={};var refs:Array[WeakRef]=[]
	var start:=Time.get_ticks_usec()
	sample("before_pooled="+str(pooled))
	for name:String in names:
		var path:="res://assets/models/"+name
		var packed:PackedScene=load(path)
		load("res://group2_resource_lifetime_20261025/shadow_mesh_pool.gd").intern_scene(packed)
		var visual:Node3D=packed.instantiate();host.add_child(visual)
		# Mirror exact retained per-mesh static builder, preserving body ancestry.
		var local:Dictionary={}
		for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
			if mesh.mesh==null or not mesh.visible or mesh.name.begins_with("ALC_VisualFloor"):continue
			var id:=mesh.mesh.get_instance_id();var shape:ConcavePolygonShape3D=local.get(id)
			if shape==null:
				var faces:=mesh.mesh.get_faces()
				shape=POOL.intern(faces) if pooled else mesh.mesh.create_trimesh_shape()
				assert(shape.get_faces().to_byte_array()==faces.to_byte_array());checks+=1
				local[id]=shape
			if not shapes.has(shape.get_instance_id()):shapes[shape.get_instance_id()]=true;refs.append(weakref(shape))
			var body:=StaticBody3D.new();body.name="StaticContact";mesh.add_child(body)
			var col:=CollisionShape3D.new();col.name="SharedShape";col.shape=shape;body.add_child(col)
		packed=null;local.clear()
		await process_frame
		rows.append({"source":path,"pooled":pooled,"sha256":FileAccess.get_sha256(path)});save()
	await physics_frame
	sample("live_pooled="+str(pooled))
	rows.append({"pooled":pooled,"unique_shapes":shapes.size(),"elapsed_us":Time.get_ticks_usec()-start,"exact_checks":checks});save()
	host.free()
	for i in 3:await process_frame
	for reference:WeakRef in refs:assert(reference.get_ref()==null)
	POOL.prune();assert(POOL.entries.is_empty())
	sample("released_pooled="+str(pooled))
func run()->void:
	await pass_sources(false)
	await pass_sources(true)
	print(JSON.stringify(rows));quit()
