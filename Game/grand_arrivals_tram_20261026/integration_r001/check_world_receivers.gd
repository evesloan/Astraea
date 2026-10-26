extends SceneTree
const P:="res://grand_arrivals_tram_20261026/integration_r001/"
func _initialize()->void:call_deferred("run")
func run()->void:
	assert(load(P+"guards.gd").verify())
	# Compile the actual inherited entry without running its full _ready.
	var script:GDScript=load(P+"ship.gd");assert(script.can_instantiate())
	var host:=Node3D.new();root.add_child(host)
	var mat:=StandardMaterial3D.new()
	var floors:Node3D=load(P+"floors.gd").build(host,mat,mat)
	assert(floors.get_meta("lower_arrivals_exact_floor_changes")==6)
	var proof:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"WORLD_RECEIVING.json"))
	var checked:Array=[]
	for change:Dictionary in proof.floor_changes:
		assert(floors.has_node(change.after.id))
		var owner:Node3D=floors.get_node(change.after.id)
		assert(owner.get_meta("region_id")==change.before.id)
		var count:=0
		for col:CollisionShape3D in owner.find_children("*","CollisionShape3D",true,false):
			var points:PackedVector3Array=col.shape.get_faces()
			for i in range(0,points.size(),3):
				if absf(points[i].y-change.after.floor_y)<.00002 and absf(points[i+1].y-change.after.floor_y)<.00002 and absf(points[i+2].y-change.after.floor_y)<.00002:count+=1
		assert(count==change.after.triangles.size())
		checked.append({"id":change.after.id,"top_triangles":count})
	var original:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
	assert(floors.get_child_count()==original.regions.size())
	var region_count:=floors.get_child_count();host.free()
	var output:=""
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--output="):output=arg.substr(9)
	var result:Dictionary={"selected":false,"inherited_entry_compiles":true,"original_region_count_preserved":region_count,"exact_changed_receivers":checked,"scope":"Actual inherited entry compilation and all structural floor construction with six exact changed receivers. Full ship not instantiated; full graded rolling guideway/support and installed acceptance remain held."}
	var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify(result,"\t"));f.close();print(JSON.stringify(result));quit()
