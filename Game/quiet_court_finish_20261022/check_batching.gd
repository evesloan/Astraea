extends SceneTree
const P:="res://quiet_court_finish_20261022/"
func _initialize()->void:call_deferred("run")
func faces(part:Node3D)->Array[String]:
	var result:Array[String]=[]
	for mesh:MeshInstance3D in part.find_children("*","MeshInstance3D",true,false):
		if mesh.mesh==null:continue
		var pose:Transform3D=part.global_transform.affine_inverse()*mesh.global_transform
		var vertices:PackedVector3Array=mesh.mesh.get_faces()
		for i in range(0,vertices.size(),3):
			var tri:Array[String]=[]
			for j in range(3):
				var v:Vector3=pose*vertices[i+j];tri.append("%d,%d,%d"%[roundi(v.x*1000),roundi(v.y*1000),roundi(v.z*1000)])
			tri.sort();result.append("|".join(tri))
	result.sort();return result
func stats(node:Node3D)->Dictionary:
	var materials:={};var meshes:={};var count:=0
	for mesh:MeshInstance3D in node.find_children("*","MeshInstance3D",true,false):
		if mesh.mesh==null:continue
		count+=1;meshes[mesh.mesh.get_instance_id()]=true
		for s in mesh.mesh.get_surface_count():materials[mesh.get_active_material(s).get_instance_id()]=true
	return {"mesh_instances":count,"mesh_resources":meshes.size(),"materials":materials.size(),"nodes":node.find_children("*","",true,false).size()+1}
func run()->void:
	var original:Node3D=load(P+"runtime/QuietGroveCourtPlanting_r003.scn").instantiate();root.add_child(original)
	var successor:Node3D=load(P+"planting_batched.gd").build();root.add_child(successor)
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN_R003.json"));var rows:Array=[];var failed:=0
	for row in plan.placements:
		var a:=original.find_child(str(row.name),true,false)as Node3D;var b:=successor.get_node(str(row.name))as Node3D
		var same:bool=faces(a)==faces(b);var pose:bool=a.global_transform.is_equal_approx(b.global_transform)
		rows.append({"name":row.name,"world_pose_equal":pose,"all_triangle_vertices_equal_at_1mm":same})
		if not same or not pose:failed+=1
	var result:={"status":"PASS" if failed==0 else "FAIL","failed":failed,"placements":rows,"before":stats(original),"after":stats(successor),"scope":"All149 actual placements and complete triangle vertex multisets at1mm quantization; no triangles removed. Not FPS acceptance."}
	var f:=FileAccess.open(P+"evidence/BATCHING_CHECK.json",FileAccess.WRITE);f.store_string(JSON.stringify(result,"\t")+"\n");f.close();print("BATCHING ",result.before," -> ",result.after," failures=",failed);original.free();successor.free();quit(1 if failed else 0)
