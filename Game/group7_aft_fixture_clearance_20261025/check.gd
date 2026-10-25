extends SceneTree
const ADAPTER=preload("res://group7_aft_fixture_clearance_20261025/adapter.gd")
const BASE="res://group7_aft_fixture_clearance_20261025/"
var output:String
var failures:Array[String]=[]
func _initialize()->void:call_deferred("run")
func require(ok:bool,label:String)->void:
	if not ok:failures.append(label);push_error(label)
func hits(ship:Node3D)->Array[String]:
	var shape:=BoxShape3D.new();shape.size=Vector3(7.98,4.0,.12)
	var query:=PhysicsShapeQueryParameters3D.new();query.shape=shape;query.margin=0;query.transform.origin=Vector3(0,108.505,193.7)
	var result:Array[String]=[]
	for hit:Dictionary in ship.get_world_3d().direct_space_state.intersect_shape(query,32):result.append(str(hit.collider.name)+":"+str(hit.collider.get_parent().name))
	return result
func run()->void:
	for a:String in OS.get_cmdline_user_args():
		if a.begins_with("--output="):output=a.trim_prefix("--output=")
	if output.is_empty():quit(2);return
	var receipt:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(BASE+"BUILD_RECEIPT.json"))
	var before:Dictionary=ADAPTER.meshes(load("res://assets/models/AST-CMD-005.glb"))
	var after:Dictionary=ADAPTER.meshes(load(BASE+"AST-CMD-005_fixture_clearance_r002.glb"))
	var changed:Dictionary={}
	for row:Dictionary in receipt.changed_runtime_batches:changed[row.node]=true
	var proof:Dictionary={"batches":[],"unchanged_batches":0,"changed_vertices":0}
	require(before.keys()==after.keys(),"same imported source mesh names")
	for name:String in before:
		var a:ArrayMesh=before[name];var b:ArrayMesh=after[name]
		if not changed.has(name):require(ADAPTER.digest(a)==ADAPTER.digest(b),"Unchanged imported geometry: "+name);proof.unchanged_batches+=1;continue
		var whole:bool=name.ends_with("warm_opal")
		var moved:ArrayMesh=a if whole else ADAPTER.partition(a,true)
		var retained:ArrayMesh=null if whole else ADAPTER.partition(a,false)
		require(moved!=null and (whole or retained!=null),"Valid triangle partitions")
		if moved==null or (not whole and retained==null):quit(1);return
		var count:=0
		for v:Vector3 in a.surface_get_arrays(0)[Mesh.ARRAY_VERTEX]:
			if ADAPTER.selected(v):count+=1
		require(count==24,"24 selected vertices per half")
		for part:ArrayMesh in [moved,retained]:
			if part==null:continue
			for surface in a.get_surface_count():
				var aa:=a.surface_get_arrays(surface);var bb:=part.surface_get_arrays(surface)
				for k in Mesh.ARRAY_MAX:
					if k!=Mesh.ARRAY_INDEX:require(aa[k]==bb[k],"Exact vertex normal tangent UV buffers: "+name)
				var da:Dictionary=a.get("_surfaces")[surface];var db:Dictionary=part.get("_surfaces")[surface]
				for key:String in da:
					if key not in ["index_data","index_count","lods"]:require(da[key]==db[key],"Encoded buffer unchanged: "+name+":"+key)
		var original:PackedVector3Array=a.get_faces();var mf:PackedVector3Array=moved.get_faces();var rf:=PackedVector3Array() if whole else retained.get_faces()
		var expected_m:=PackedVector3Array();var expected_r:=PackedVector3Array()
		for i in range(0,original.size(),3):
			if ADAPTER.selected(original[i]):expected_m.append_array(original.slice(i,i+3))
			else:expected_r.append_array(original.slice(i,i+3))
		require(mf==expected_m and rf==expected_r,"Exact triangle conservation and original ordering")
		proof.changed_vertices+=count
		proof.batches.append({"name":name,"before_sha256":ADAPTER.digest(a),"moved_sha256":ADAPTER.digest(moved),"retained_sha256":"" if whole else ADAPTER.digest(retained),"whole_batch":whole,"changed_vertices":count,"moved_triangle_vertices":mf.size(),"retained_triangle_vertices":rf.size()})
	if not failures.is_empty():quit(1);return
	var file:=FileAccess.open(BASE+"RESOURCE_PROOF.json",FileAccess.WRITE);file.store_string(JSON.stringify(proof,"\t"));file.close()
	var ship:=Node3D.new();root.add_child(ship)
	var space:=Node3D.new();space.name="ShipSpace";ship.add_child(space)
	var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
	var service:Node3D=load("res://scripts/ship.gd").new()
	load("res://scripts/aft_crown_platform.gd").build(districts,service)
	for i in range(3):await physics_frame
	var prior:=hits(ship);require(prior.size()==4,"Four metre probe reproduces both opal halves and both housing halves")
	var light:SpotLight3D=ship.get_node(ADAPTER.ROOT+"/AftPlatformSource_"+str(receipt.fixture_marker))
	var settings:Array=[light.light_energy,light.light_color,light.spot_range,light.spot_angle,light.shadow_enabled]
	require(ADAPTER.build(ship),"Apply checked fixture successor")
	for i in range(3):await physics_frame
	var corrected:=hits(ship);require(corrected.is_empty(),"Actual4m high passage probe")
	require(settings==[light.light_energy,light.light_color,light.spot_range,light.spot_angle,light.shadow_enabled],"Light settings unchanged")
	var result:Dictionary={"status":"PASS" if failures.is_empty() else "FAIL","failures":failures,"unchanged_imported_batches":proof.unchanged_batches,"changed_batches":proof.batches.size(),"vertices_shifted_50mm":proof.changed_vertices,"before_contacts":prior,"after_contacts":corrected,"query_height_m":4.0,"query_bottom_y":106.505,"lens_min_y":110.52,"floor_y":106.5,"light_settings_preserved":true,"light_position":str(light.global_position),"whole_ship_acceptance":false}
	file=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify(result,"\t"));file.close();print("FIXTURE_CHECK ",JSON.stringify(result))
	ship.free();service.free();quit(0 if failures.is_empty() else 1)
