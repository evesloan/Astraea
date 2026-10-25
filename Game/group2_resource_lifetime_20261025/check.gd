extends SceneTree
# Bounded retained-source ownership measurement, not a whole ship or FPS test.
var rows:Array=[]
var output:String
func _initialize()->void:
	for a:String in OS.get_cmdline_user_args():
		if a.begins_with("--output="):output=a.substr(9)
	call_deferred("run")
func inspect(source:Node)->Dictionary:
	var main:Dictionary={};var shadows:Dictionary={};var refs:Array[WeakRef]=[]
	for node:MeshInstance3D in source.find_children("*","MeshInstance3D",true,false):
		if node.mesh==null:continue
		main[node.mesh.get_instance_id()]=true
		refs.append(weakref(node.mesh))
		if node.mesh is ArrayMesh and node.mesh.shadow_mesh!=null:
			shadows[node.mesh.shadow_mesh.get_instance_id()]=true
	return {"main":main.size(),"shadow":shadows.size(),"refs":refs}
func live(refs:Array)->int:
	var count:=0
	for reference:WeakRef in refs:
		if reference.get_ref()!=null:count+=1
	return count
func run()->void:
	if output.is_empty():quit(2);return
	for key:String in ["780","828","787"]:
		var room:=Node3D.new();root.add_child(room)
		room.set_meta("retained_group2_home",true)
		var before:=Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT)
		var source:Node3D=load("res://scripts/group2_completion/package.gd").build_section(room,key)
		room.set_meta("resident_visual",source)
		var info:=inspect(source)
		var loaded:=Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT)
		load("res://scripts/received_homes_20261015/source_dispatch.gd").release(room)
		await process_frame
		var detached:=Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT)
		var retained:=live(info.refs)
		var orphaned:=source.get_parent()==null
		room.remove_meta("resident_visual");source.free();source=null;room.free()
		await process_frame
		var remaining:=live(info.refs)
		rows.append({"key":key,"main_meshes":info.main,"shadow_meshes":info.shadow,"resource_count_before":before,"loaded":loaded,"after_release":detached,"mesh_references_after_release":retained,"source_detached":orphaned,"mesh_references_after_explicit_free":remaining,"resources_after_free":Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT)})
	var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify(rows,"\t"));f.close()
	print("GROUP2_LIFETIME ",JSON.stringify(rows));quit(0)
