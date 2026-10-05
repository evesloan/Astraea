extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/HULL_BODY_SECTION_PROPOSAL.json"))
	var samples:=0
	var outside:Array=[]
	for node in ship.find_children("*","MeshInstance3D",true,false):
		var item:=node as MeshInstance3D
		if not item.is_visible_in_tree() or item.mesh==null:continue
		if "All18DeckStructuralDatums_NOT_FINISHED_ARCHITECTURE" in str(item.get_path()):continue
		var count:=0
		var examples:Array=[]
		for surface in range(item.mesh.get_surface_count()):
			var arrays:Array=item.mesh.surface_get_arrays(surface)
			var verts:PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
			for vertex in verts:
				var p:Vector3=item.global_transform*vertex
				if p.y<-.3 or p.y>16.5:continue
				var index:=0 if p.y<6 else 1 if p.y<12 else 2
				var lo:Dictionary=data.levels[index]
				var hi:Dictionary=data.levels[index+1]
				var t:float=clampf((p.y-float(lo.floor_y))/(float(hi.floor_y)-float(lo.floor_y)),0,1)
				var boundary:=PackedVector2Array()
				for i in range(lo.inner_reservation_boundary.size()):
					var a:Array=lo.inner_reservation_boundary[i];var b:Array=hi.inner_reservation_boundary[i]
					boundary.append(Vector2(a[0],a[1]).lerp(Vector2(b[0],b[1]),t))
				samples+=1
				if not Geometry2D.is_point_in_polygon(Vector2(p.x,p.z),boundary):
					count+=1
					if examples.size()<3:examples.append([p.x,p.y,p.z])
		if count>0:outside.append({"mesh":str(item.get_path()),"outside_vertices":count,"examples":examples})
	var file:=FileAccess.open("res://artifacts/lower_body_mesh_fit.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"samples":samples,"outside_meshes":outside,"scope":"Visible MeshInstance3D vertex fit at lower body heights; datum guides excluded. Not triangles/sweeps, MultiMesh inventory, shell load or final hull acceptance."},"  "));file.close()
	print("LOWER BODY MESH AUDIT: ",samples," vertices; ",outside.size()," mesh records outside inner reservation")
	quit()
