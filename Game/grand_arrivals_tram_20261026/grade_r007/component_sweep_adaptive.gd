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
	var result:={"components":components.size(),"queries":0,"coarse_holds":0,"refinement_queries":0,"refined_clear":0,"maximum_refined_margin":0.0,"hits":[],"conservative_concave_hulls":hulls,"cart_scope":"Original cart/four-stock shape geometry at retained carried frame; actual loaded cart operation remains separate"}
	var state:PhysicsDirectSpaceState3D=space_override if space_override!=null else body.get_world_3d().direct_space_state
	for i in range(poses.size()-1):
		var a:Array=poses[i];var b:Array=poses[i+1]
		if a[0]<interval[0] or b[0]>interval[1]:continue
		for c:Dictionary in components:
			var ta:=pose_transform(a,c);var tb:=pose_transform(b,c)
			var margin:=angular_bound(a,b,c)
			var q:=PhysicsShapeQueryParameters3D.new();q.shape=c.shape;q.transform=ta;q.margin=margin;q.exclude=exclusions
			var initial:=state.intersect_shape(q,32);q.motion=tb.origin-ta.origin
			var sweep:=state.cast_motion(q);result.queries+=1
			if not initial.is_empty() or sweep[0]<1:
				result.coarse_holds+=1
				var refined:=refine(a,b,c,state,exclusions,margin)
				result.refinement_queries+=refined.queries
				result.maximum_refined_margin=maxf(result.maximum_refined_margin,refined.max_margin)
				if not refined.hit:
					result.refined_clear+=1;continue
				var owners:Array=refined.owners
				var exact_owners:Array=refined.exact_owners
				collision_queries+=1
				var owner_key:=str(owners)
				if seen_owners.has(owner_key):continue
				seen_owners[owner_key]=true
				result.hits.append({"cursor":refined.cursor,"component":c.name,"owners":owners,"safe_fraction":refined.safe_fraction,"rotation_margin":refined.margin,"start_pose_exact_owners":exact_owners})
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

# Euler total variation is a conservative angular bound even below float32
# quaternion angle_to resolution. The same radius/origin bounds apply per interval.
static func angular_bound(a:Array,b:Array,c:Dictionary)->float:
	var body_angle:=absf(angle_difference(a[3],b[3]))+absf(angle_difference(a[12],b[12]))
	var truck_angle:=0.0;var origin_radius:float=c.relative.origin.length()
	if c.bogie>=0:
		var i:int=c.bogie;var column:int=4+i*3
		truck_angle=absf(angle_difference(a[column+1],b[column+1]))+absf(angle_difference(a[13+i*2],b[13+i*2]))+absf(angle_difference(a[14+i*2],b[14+i*2]))
		origin_radius+=Vector3(maxf(absf(a[column]),absf(b[column])),.2,1.5).length()
	return c.radius*(body_angle+truck_angle)+origin_radius*body_angle+c.relative.origin.length()*truck_angle+.00002
static func interpolate(a:Array,b:Array,t:float)->Array:
	var row:Array=[]
	for i in a.size():row.append(lerp_angle(a[i],b[i],t) if i in [3,5,8,12,13,14,15,16] else lerpf(a[i],b[i],t))
	return row
static func refine(a:Array,b:Array,c:Dictionary,state:PhysicsDirectSpaceState3D,exclusions:Array[RID],coarse_margin:float)->Dictionary:
	var steps:=maxi(1,ceili(coarse_margin/.0009))
	assert(steps<2000,"Unexpected refinement cost; no acceptance without bounded evidence")
	var result:={"hit":false,"queries":0,"max_margin":0.0}
	for j in steps:
		var u:=interpolate(a,b,float(j)/steps);var v:=interpolate(a,b,float(j+1)/steps)
		var ta:=pose_transform(u,c);var tb:=pose_transform(v,c);var margin:=angular_bound(u,v,c)
		result.max_margin=maxf(result.max_margin,margin)
		var q:=PhysicsShapeQueryParameters3D.new();q.shape=c.shape;q.transform=ta;q.margin=margin;q.exclude=exclusions
		var initial:=state.intersect_shape(q,32);q.motion=tb.origin-ta.origin;var sweep:=state.cast_motion(q);result.queries+=1
		if initial.is_empty() and sweep[0]>=1:continue
		var owners:Array[String]=[]
		for hit:Dictionary in initial:owners.append(str(hit.collider.get_path()))
		if owners.is_empty():
			q.transform.origin+=q.motion*minf(1.,sweep[1]+.0001);q.motion=Vector3.ZERO
			for hit:Dictionary in state.intersect_shape(q,32):owners.append(str(hit.collider.get_path()))
		q.transform=ta;q.motion=Vector3.ZERO;q.margin=.00002;var exact:Array[String]=[]
		for hit:Dictionary in state.intersect_shape(q,32):exact.append(str(hit.collider.get_path()))
		result.merge({"hit":true,"owners":owners,"exact_owners":exact,"cursor":u[0],"margin":margin,"safe_fraction":sweep[0]},true);return result
	return result
