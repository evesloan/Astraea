extends SceneTree
const POOL=preload("res://group2_resource_lifetime_20261025/shadow_mesh_pool.gd")
var failures:Array=[]
var checks:=0
var report:FileAccess
func require(ok:bool,message:String)->void:
	checks+=1
	if not ok:failures.append(message);push_error(message)
func _initialize()->void:
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--output="):report=FileAccess.open(arg.substr(9),FileAccess.WRITE)
	call_deferred("run")
func geometry(mesh:Mesh)->PackedByteArray:
	var data:Array=[]
	for i in mesh.get_surface_count():data.append([mesh.surface_get_arrays(i),mesh.surface_get_primitive_type(i),mesh.surface_get_material(i),mesh.surface_get_name(i)])
	return var_to_bytes([data,mesh.get_aabb(),mesh.custom_aabb])
func scenario()->Dictionary:
	var sources:Array[PackedScene]=[];var refs:Array[WeakRef]=[];var rows:Array=[]
	var all_main:Dictionary={};var all_shadow:Dictionary={}
	for key:String in ["788","812","824","836","818"]:
		var packed:PackedScene=load("res://assets/group2_completion/"+key+".glb");sources.append(packed)
		var state:=packed.get_state();var originals:Array=[]
		for n in state.get_node_count():
			for p in state.get_node_property_count(n):
				if state.get_node_property_name(n,p)!=&"mesh":continue
				var mesh:ArrayMesh=state.get_node_property_value(n,p)
				originals.append({"mesh":mesh,"main":geometry(mesh),"shadow":POOL.payload(mesh.shadow_mesh),"rid":mesh.get_rid()})
		var counts:Dictionary=POOL.intern_scene(packed)
		for row:Dictionary in originals:
			var mesh:ArrayMesh=row.mesh
			require(geometry(mesh)==row.main,key+": unchanged main geometry/material resources/names/AABB")
			require(mesh.get_rid()==row.rid,key+": unchanged main RID")
			require(POOL.payload(mesh.shadow_mesh)==row.shadow,key+": byte-exact shadow data including LODs/bounds/format")
			all_main[mesh.get_rid().get_id()]=true;all_shadow[mesh.shadow_mesh.get_rid().get_id()]=true
			refs.append(weakref(mesh));refs.append(weakref(mesh.shadow_mesh))
		rows.append({"key":key,"counts":counts})
	return {"rows":rows,"main_rids":all_main.size(),"shadow_rids":all_shadow.size(),"refs":refs}
func run()->void:
	var runs:Array=[]
	for cycle in 2:
		var result:=scenario()
		await process_frame
		var live:=0
		for ref:WeakRef in result.refs:
			if ref.get_ref()!=null:live+=1
		require(live==0,"All source main/shadow references expire after owners release")
		POOL.prune();require(POOL.entries.is_empty(),"Weak pool prunes fully")
		result.erase("refs");result.live_after_release=live;runs.append(result)
	var final:Dictionary={"checks":checks,"failures":failures,"cycles":runs,"scope":"Exact main/material identity and complete shadow stored-byte equivalence; no ship FPS or visual acceptance"}
	report.store_string(JSON.stringify(final,"\t"));report.close();print(JSON.stringify(final));quit(0 if failures.is_empty() else 1)
