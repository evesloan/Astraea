extends SceneTree
# Isolated production-load lifecycle census. No ship, camera or FPS claim.
const IDS=[575,503,527,479,455,407,431]
var report:Dictionary={"stages":[],"models":[]}
var output:String
var tracked:Array[WeakRef]=[]
func _initialize()->void:call_deferred("run")
func save()->void:
	var f:=FileAccess.open(output,FileAccess.WRITE)
	f.store_string(JSON.stringify(report,"\t"));f.close()
func stage(label:String)->Dictionary:
	var live:=0
	for ref:WeakRef in tracked:
		if ref.get_ref()!=null:live+=1
	var row:Dictionary={"label":label,"ms":Time.get_ticks_msec(),"static_bytes":OS.get_static_memory_usage(),"resources":Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT),"nodes":Performance.get_monitor(Performance.OBJECT_NODE_COUNT),"tracked_meshes_live":live,"render_video_bytes":RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_VIDEO_MEM_USED)}
	report.stages.append(row);save();print("COST_STAGE ",JSON.stringify(row));return row
func census(detail:Node3D)->Dictionary:
	var main:Dictionary={};var shadow:Dictionary={};var mats:Dictionary={};var textures:Dictionary={}
	var nodes:=0;var nulls:=0;var surfaces:=0;var vertices:=0;var indices:=0
	for node:MeshInstance3D in detail.find_children("*","MeshInstance3D",true,false):
		nodes+=1
		if node.mesh==null:nulls+=1;continue
		var mesh:Mesh=node.mesh
		if not main.has(mesh.get_instance_id()):
			main[mesh.get_instance_id()]=true;tracked.append(weakref(mesh))
			if mesh is ArrayMesh and mesh.shadow_mesh!=null:
				shadow[mesh.shadow_mesh.get_instance_id()]=true;tracked.append(weakref(mesh.shadow_mesh))
			for s in range(mesh.get_surface_count()):
				surfaces+=1
				if mesh is ArrayMesh:vertices+=mesh.surface_get_array_len(s);indices+=mesh.surface_get_array_index_len(s)
		for s in range(mesh.get_surface_count()):
			var material:=node.get_active_material(s)
			if material==null or mats.has(material.get_instance_id()):continue
			mats[material.get_instance_id()]=true
			for p:Dictionary in material.get_property_list():
				if int(p.type)!=TYPE_OBJECT or not(int(p.usage)&PROPERTY_USAGE_STORAGE):continue
				var value=material.get(str(p.name))
				if value is Texture2D:textures[value.get_instance_id()]={"width":value.get_width(),"height":value.get_height(),"path":value.resource_path}
	return {"mesh_nodes":nodes,"null_shell_mesh_nodes":nulls,"unique_meshes":main.size(),"shadow_meshes":shadow.size(),"surfaces":surfaces,"vertices":vertices,"indices":indices,"materials":mats.size(),"textures":textures.values(),"collision_shapes":detail.find_children("*","CollisionShape3D",true,false).size()}
func run()->void:
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
	if output.is_empty():quit(2);return
	var host:=Node3D.new();root.add_child(host)
	var manager:Node=load("res://scripts/startup_residency_20261020/private_detail_residency.gd").new()
	host.add_child(manager);manager.set_process(false);manager.set_physics_process(false)
	var interner=load("res://scripts/startup_residency_20261020/exact_texture_intern.gd").new()
	node_added.connect(interner.observe)
	var records:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(manager.DATA)).rooms
	var entries:Array[Dictionary]=[]
	stage("initial")
	for id:int in IDS:
		var file:="StarAtlasSpecialty_%d.glb"%id
		var record:Dictionary=records[file]
		assert(FileAccess.get_sha256("res://assets/models/"+file)==str(record.sha256))
		var home:=Node3D.new();home.name=record.room_id;host.add_child(home)
		var shell:Node3D=load(str(record.shell_path)).instantiate();home.add_child(shell);manager.contacts(shell)
		entries.append({"home":weakref(home),"record":record,"detail":null,"hidden":0.0})
	interner.flush();await process_frame;stage("seven_shells")
	for entry:Dictionary in entries:
		var before:int=OS.get_static_memory_usage();var start:int=Time.get_ticks_usec()
		manager._load_entry(entry);interner.flush()
		var row:Dictionary=census(entry.detail)
		row.model=entry.record.model_file;row.load_ms=(Time.get_ticks_usec()-start)/1000.0;row.static_delta=OS.get_static_memory_usage()-before
		report.models.append(row)
		for i in range(3):await process_frame
		stage(str(row.model))
	for i in range(30):await process_frame
	stage("all_seven_settled")
	for entry:Dictionary in entries:manager._release_entry(entry)
	interner.flush();interner.prune_expired_references()
	for i in range(30):await process_frame
	stage("details_released_shells_retained")
	report.interner=interner.statistics()
	host.free();interner.flush();interner.prune_expired_references()
	for i in range(30):await process_frame
	stage("all_owners_freed")
	quit(0)
