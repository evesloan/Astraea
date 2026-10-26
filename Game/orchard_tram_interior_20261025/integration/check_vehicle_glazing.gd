extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var parent:=Node3D.new();root.add_child(parent)
	var body:AnimatableBody3D=load("res://tram_passenger_successor_20261024/vehicle_initial_pose_r002.gd").create_candidate_vehicle(parent,Transform3D.IDENTITY)
	var shapes:Array=[]
	for col:CollisionShape3D in body.find_children("*","CollisionShape3D",true,false):shapes.append([col.get_instance_id(),col.shape.get_rid(),col.transform])
	var meshes:Array=[]
	for mesh:MeshInstance3D in body.find_children("*","MeshInstance3D",true,false):meshes.append([mesh,mesh.mesh.get_rid(),mesh.transform,mesh.material_override])
	load("res://orchard_tram_interior_20261025/integration/vehicle_glazing.gd").apply(body)
	var after:Array=[]
	for col:CollisionShape3D in body.find_children("*","CollisionShape3D",true,false):after.append([col.get_instance_id(),col.shape.get_rid(),col.transform])
	assert(shapes==after)
	var changed:Array=[]
	for row in meshes:
		assert(row[0].mesh.get_rid()==row[1] and row[0].transform==row[2])
		if row[0].material_override!=row[3]:changed.append(str(row[0].name))
	assert(changed.size()==2 and body.get_meta("retained_end_glazing_bound")==2)
	var output:=""
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--result="):output=arg.substr(9)
	assert(not FileAccess.file_exists(output))
	var result:={"changed_presentation_only":changed,"original_collision_shapes_unchanged":shapes.size(),"original_meshes_and_transforms_unchanged":meshes.size(),"shader":"res://shaders/hospitality_glass.gdshader","actual_ship_post_binding_visual_review":"pending"}
	var file:=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify(result,"\t")+"\n");file.close();print(JSON.stringify(result));quit()
