extends SceneTree
const P:="res://orchard_tram_interior_20261025/integration/"
func _initialize()->void:call_deferred("run")
func run()->void:
	var presentation:Node=load(P+"main.tscn").instantiate();root.add_child(presentation)
	var ship:Node3D=presentation.world_view.get_node("Astraea")
	while not ship.get_meta("runtime_ready",false):await process_frame
	for i in range(3):await physics_frame
	var box:=BoxShape3D.new();box.size=Vector3(55,12,125)
	var query:=PhysicsShapeQueryParameters3D.new();query.shape=box;query.transform.origin=Vector3(7.5,56,-257.5)
	var hits:=ship.get_world_3d().direct_space_state.intersect_shape(query,16384)
	assert(hits.size()<16384,"Snapshot query truncated")
	var rows:Array=[];var seen:Dictionary={}
	for hit:Dictionary in hits:
		var owner:CollisionObject3D=hit.collider
		if seen.has(str(owner.get_path())):continue
		seen[str(owner.get_path())]=true
		for id:int in owner.get_shape_owners():
			if owner.is_shape_owner_disabled(id):continue
			var t:Transform3D=owner.global_transform*owner.shape_owner_get_transform(id)
			for i in range(owner.shape_owner_get_shape_count(id)):
				var shape:Shape3D=owner.shape_owner_get_shape(id,i)
				var row:={"owner":str(owner.get_path()),"class":shape.get_class(),"transform":[[t.basis.x.x,t.basis.x.y,t.basis.x.z],[t.basis.y.x,t.basis.y.y,t.basis.y.z],[t.basis.z.x,t.basis.z.y,t.basis.z.z],[t.origin.x,t.origin.y,t.origin.z]],"layer":owner.collision_layer,"margin":shape.margin}
				var points:=PackedVector3Array()
				if shape is ConcavePolygonShape3D:points=shape.get_faces();row.backface_collision=shape.backface_collision
				elif shape is ConvexPolygonShape3D:points=shape.points
				elif shape is BoxShape3D:row.size=[shape.size.x,shape.size.y,shape.size.z]
				elif shape is CapsuleShape3D or shape is CylinderShape3D:row.radius=shape.radius;row.height=shape.height
				elif shape is SphereShape3D:row.radius=shape.radius
				else:push_error("Unsupported snapshot shape "+shape.get_class());quit(2);return
				if not points.is_empty():
					var vertices:Array=[]
					for v:Vector3 in points:vertices.append([v.x,v.y,v.z])
					row.points=vertices
				rows.append(row)
	var output:=""
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--result="):output=arg.substr(9)
	assert(not output.is_empty() and not FileAccess.file_exists(output))
	var file:=FileAccess.open(output,FileAccess.WRITE)
	file.store_string(JSON.stringify({"scope":"Installed stationary active collision shapes intersecting X[-20,35] Y[50,62] Z[-320,-195]; not unloaded room completeness or travel acceptance","ready":true,"shape_count":rows.size(),"owners":seen.size(),"rows":rows}));file.close()
	print("APPROACH_SNAPSHOT shapes=",rows.size()," owners=",seen.size());quit(0)
