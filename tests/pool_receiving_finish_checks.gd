extends RefCounted
# Additive r04 checks. All old gallery walking, sightline and fixture checks remain.
static func closest_triangle(p: Vector3,a: Vector3,b: Vector3,c: Vector3) -> Vector3:
	var ab:=b-a;var ac:=c-a;var ap:=p-a
	var d1:=ab.dot(ap);var d2:=ac.dot(ap)
	if d1<=0 and d2<=0:return a
	var bp:=p-b;var d3:=ab.dot(bp);var d4:=ac.dot(bp)
	if d3>=0 and d4<=d3:return b
	var vc:=d1*d4-d3*d2
	if vc<=0 and d1>=0 and d3<=0:return a+ab*(d1/(d1-d3))
	var cp:=p-c;var d5:=ab.dot(cp);var d6:=ac.dot(cp)
	if d6>=0 and d5<=d6:return c
	var vb:=d5*d2-d1*d6
	if vb<=0 and d2>=0 and d6<=0:return a+ac*(d2/(d2-d6))
	var va:=d3*d6-d5*d4
	if va<=0 and d4-d3>=0 and d5-d6>=0:return b+(c-b)*((d4-d3)/((d4-d3)+(d5-d6)))
	var denominator:=1.0/(va+vb+vc)
	return a+ab*(vb*denominator)+ac*(vc*denominator)
static func surface_distance(mesh: MeshInstance3D,point: Vector3) -> float:
	var faces: PackedVector3Array=mesh.mesh.get_faces()
	var local:=mesh.to_local(point);var closest:=INF
	for i in range(0,faces.size(),3):
		var hit:=closest_triangle(local,faces[i],faces[i+1],faces[i+2])
		closest=minf(closest,mesh.to_global(hit).distance_to(point))
	return closest
static func check(owner: RefCounted) -> void:
	var data: Dictionary=owner.data
	var area: Node3D=owner.area
	var group:=area.get_node("ConnectedGalleryFurniture/ReceivingStock") as Node3D
	assert(group!=null and group.transform==Transform3D.IDENTITY and group.get_child_count()==8)
	var stock_rids: Array[RID]=[]
	for body in group.find_children("*","StaticBody3D",true,false):stock_rids.append(body.get_rid())
	var results: Array=[]
	for entry in data.receiving_stock:
		var spec: Dictionary=data.models[str(entry.asset)]
		var path: String="res://assets/models/"+str(spec.file)
		assert(FileAccess.get_sha256(path)==str(spec.sha256))
		var item:=group.get_node(NodePath(str(entry.name))) as Node3D
		assert(item.scale==Vector3.ONE and item.position.distance_to(owner.v3(entry.position_xyz))<.00005)
		assert(absf(item.rotation.y-float(entry.yaw_radians))<.000001)
		var support:=area.get_node(NodePath("ConnectedGalleryFurniture/"+str(entry.support_instance))) as Node3D
		var visual:=item.get_child(0) as Node3D
		var prototype: Node3D=(load(path) as PackedScene).instantiate()
		var minimum:=INF;var vertices: Array[Vector3]=[];var count:=0
		for mesh in visual.find_children("*","MeshInstance3D",true,false):
			var original:=prototype.get_node(visual.get_path_to(mesh)) as MeshInstance3D
			assert(original!=null and mesh.mesh==original.mesh and mesh.transform==original.transform)
			assert(mesh.material_override==null and mesh.material_overlay==null)
			var body:=mesh.get_node("StaticContact") as StaticBody3D
			assert(body!=null and body.collision_layer==1 and body.get_child_count()==1)
			var shape:=body.get_child(0) as CollisionShape3D
			var expected: ConcavePolygonShape3D=mesh.mesh.create_trimesh_shape()
			assert(not shape.disabled and shape.shape is ConcavePolygonShape3D and shape.shape.get_faces()==expected.get_faces())
			for vertex in owner.raw_faces(mesh):
				var p: Vector3=mesh.to_global(vertex);minimum=minf(minimum,p.y);vertices.append(p)
			count+=1
		prototype.free()
		assert(count>0 and absf(minimum-float(entry.position_xyz[1]))<.0002,"Receiving stock source base moved")
		var probes:=0;var seen: Dictionary={}
		for p in vertices:
			if absf(p.y-minimum)>.00005 or seen.has(p):continue
			seen[p]=true
			var hit: Dictionary=owner.ray(p+Vector3.UP*.025,p-Vector3.UP*.025,stock_rids)
			assert(not hit.is_empty() and support.is_ancestor_of(hit.collider),"Receiving stock base is unsupported: "+str(entry.name))
			assert(absf(hit.position.y-p.y)<.0002,"Receiving stock base has a native contact gap")
			probes+=1
		assert(probes>=3)
		results.append({"name":entry.name,"retained_native_meshes":count,"actual_supported_base_vertices":probes,"original_scale":true,"stock_gameplay_accepted":false})
	var mounts: Array=[]
	for row in data.finish_mount_contacts:
		var part: MeshInstance3D=owner.meshes[str(row.part)]
		var support: MeshInstance3D=owner.meshes[str(row.support)]
		var maximum:=0.0
		for sample in row.points:
			var p: Vector3=owner.v3(sample.point_xyz)
			maximum=maxf(maximum,maxf(surface_distance(part,p),surface_distance(support,p)))
		assert(maximum<.00016,"Source fixture contact exceeds actual collider-grid representation: "+str(row.part))
		mounts.append({"part":row.part,"support":row.support,"contact_samples":row.points.size(),"max_native_surface_representation_distance_m":maximum})
	owner.records["receiving_stock"]=results
	owner.records["finish_mounts"]=mounts
	print("POOL RECEIVING FINISH PASS: eight retained stock instances supported, 18 source fixture joints preserved in actual native collider-grid geometry")
