extends RefCounted
# Continuous conservative translation/rotation coverage of original components.
# No source shape, collider, actor pose or admission is changed by this query.
static func audit(ship:Node3D,assembly:Node3D,poses:Array,interval:Array,exclusions:Array[RID],space_override:PhysicsDirectSpaceState3D=null)->Dictionary:
	var body:AnimatableBody3D=assembly.get_node("Group4OwnedTram_Source024")
	var motor:Node3D=assembly.get_node("Group4LoadedSourceTravelActuator")
	var cart:RigidBody3D=ship.get_node("ShipSpace/PersistentActors/CustodialCart")
	var components:Array[Dictionary]=[];var hulls:Array[String]=[]
	for owner:Node3D in [body,cart]:
		for col:CollisionShape3D in owner.find_children("*","CollisionShape3D",true,false):
			if col.disabled or col.shape==null:continue
			var relative:Transform3D=owner.global_transform.affine_inverse()*col.global_transform
			var bogie:=-1
			if owner==body:
				for i in range(motor.bogies.size()):
					if motor.bogies[i].is_ancestor_of(col):bogie=i;relative=motor.bogies[i].global_transform.affine_inverse()*col.global_transform
			else:
				relative=Transform3D(Basis.IDENTITY,Vector3(0,.025,.14))*relative
			var shape:Shape3D=col.shape;var name:=str(owner.name)+"/"+str(owner.get_path_to(col))
			if shape is ConcavePolygonShape3D:
				var hull:=ConvexPolygonShape3D.new();hull.points=shape.get_faces();hull.margin=.001;shape=hull;hulls.append(name)
			var box:AABB=shape.get_debug_mesh().get_aabb();var radius:=0.0
			for i in range(8):radius=maxf(radius,box.get_endpoint(i).length())
			var scale:Vector3=relative.basis.get_scale().abs()
			components.append({"name":name,"shape":shape,"relative":relative,"bogie":bogie,"radius":radius*maxf(scale.x,maxf(scale.y,scale.z))})
	var seen_owners:Dictionary={}
	var collision_queries:=0
	var result:={"components":components.size(),"queries":0,"hits":[],"conservative_concave_hulls":hulls,"cart_scope":"Original cart/four-stock shape geometry at retained carried frame; actual loaded cart operation remains separate"}
	var state:PhysicsDirectSpaceState3D=space_override if space_override!=null else body.get_world_3d().direct_space_state
	for i in range(poses.size()-1):
		var a:Array=poses[i];var b:Array=poses[i+1]
		if a[0]<interval[0] or b[0]>interval[1]:continue
		for c:Dictionary in components:
			var ta:=pose_transform(a,c);var tb:=pose_transform(b,c)
			var body_angle:=Basis.from_euler(Vector3(a[12],a[3],0)).get_rotation_quaternion().angle_to(Basis.from_euler(Vector3(b[12],b[3],0)).get_rotation_quaternion())
			var angle:=ta.basis.orthonormalized().get_rotation_quaternion().angle_to(tb.basis.orthonormalized().get_rotation_quaternion())
			# Full angular displacement bound plus relative-origin curvature bound.
			# Overcoverage may hold a gate; it cannot hide a real collision.
			var origin_radius:float=c.relative.origin.length()
			var bogie_origin_margin:=0.0
			if c.bogie>=0:
				var column:int=4+c.bogie*3
				origin_radius+=Vector3(maxf(absf(a[column]),absf(b[column])),.2,1.5).length()
				bogie_origin_margin=c.relative.origin.length()*Basis.from_euler(Vector3(a[13+c.bogie*2],a[column+1],a[14+c.bogie*2])).get_rotation_quaternion().angle_to(Basis.from_euler(Vector3(b[13+c.bogie*2],b[column+1],b[14+c.bogie*2])).get_rotation_quaternion())
			var margin:float=c.radius*angle+origin_radius*body_angle+bogie_origin_margin+.00002
			var q:=PhysicsShapeQueryParameters3D.new();q.shape=c.shape;q.transform=ta;q.margin=margin;q.exclude=exclusions
			var initial:=state.intersect_shape(q,32);q.motion=tb.origin-ta.origin
			var sweep:=state.cast_motion(q);result.queries+=1
			if not initial.is_empty() or sweep[0]<1:
				var owners:Array[String]=[]
				for hit:Dictionary in initial:owners.append(str(hit.collider.get_path()))
				if owners.is_empty():
					q.transform.origin+=q.motion*minf(1.,sweep[1]+.0001);q.motion=Vector3.ZERO
					for hit:Dictionary in state.intersect_shape(q,32):owners.append(str(hit.collider.get_path()))
				collision_queries+=1
				var owner_key:=str(owners)
				if seen_owners.has(owner_key):continue
				seen_owners[owner_key]=true
				result.hits.append({"cursor":a[0],"component":c.name,"owners":owners,"safe_fraction":sweep[0],"rotation_margin":margin})
				if result.hits.size()>=48:
					result.collision_queries=collision_queries;result.truncated=true;return result
	result.collision_queries=collision_queries
	return result
static func pose_transform(p:Array,c:Dictionary)->Transform3D:
	var relative:Transform3D=c.relative
	if c.bogie>=0:
		var i:int=c.bogie;var column:=4+i*3
		relative=Transform3D(Basis.from_euler(Vector3(p[13+i*2],p[column+1],p[14+i*2])),Vector3(p[column],-.2,-1.5 if i==0 else 1.5))*relative
	return Transform3D(Basis.from_euler(Vector3(p[12],p[3],0)),Vector3(p[1],p[11],p[2]))*relative
