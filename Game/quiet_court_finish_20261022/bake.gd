extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var p:="res://quiet_court_finish_20261022/"
	var state:=GLTFState.new();var doc:=GLTFDocument.new();assert(doc.append_from_file(p+"runtime/QuietGroveCourtPlanting_r001.glb",state)==OK)
	var visual:Node3D=doc.generate_scene(state);root.add_child(visual)
	var fix:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(p+"evidence/CLIPPED_BED_CORRECTION.json"))
	for row in fix.placements:
		var part:=visual.find_child(str(row.name),true,false)as Node3D;assert(part!=null)
		part.position=Vector3(row.after[0],row.after[1],row.after[2]);part.scale=Vector3.ONE*float(row.scale)
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(p+"PLAN_R003.json"));var bounds:Array=[]
	for row in plan.placements:
		var part:=visual.find_child(str(row.name),true,false)as Node3D;assert(part!=null)
		part.position=Vector3(row.position[0],row.position[1],row.position[2]);part.scale=Vector3.ONE*float(row.scale)
		var box:=AABB();var first:=true
		for mesh:MeshInstance3D in part.find_children("*","MeshInstance3D",true,false):
			if mesh.mesh==null:continue
			var b:AABB=mesh.global_transform*mesh.get_aabb();box=b if first else box.merge(b);first=false
		assert(not first);bounds.append({"name":row.name,"bed":row.receiving_bed,"min":[box.position.x,box.position.y,box.position.z],"max":[box.end.x,box.end.y,box.end.z]})
	var scene:=PackedScene.new();assert(scene.pack(visual)==OK);assert(ResourceSaver.save(scene,p+"runtime/QuietGroveCourtPlanting_r003.scn",ResourceSaver.FLAG_COMPRESS)==OK)
	var f:=FileAccess.open(p+"evidence/RUNTIME_BOUNDS.json",FileAccess.WRITE);f.store_string(JSON.stringify({"placements":bounds,"scene_sha256":FileAccess.get_sha256(p+"runtime/QuietGroveCourtPlanting_r003.scn")},"\t")+"\n");f.close();visual.free();print("COURT_BAKE_PASS ",bounds.size());quit()
