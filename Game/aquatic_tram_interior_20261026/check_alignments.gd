extends SceneTree
func _initialize()->void:call_deferred("run")
func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func run()->void:
	var args:Dictionary={}
	for arg:String in OS.get_cmdline_user_args():
		var split:=arg.split("=",true,1)
		if split.size()==2:args[split[0]]=split[1]
	var snapshot:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(args["--snapshot"]))
	var variants:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(args["--variants"]))
	var world:=Node3D.new();root.add_child(world)
	var excluded:Array=[]
	for row:Dictionary in snapshot.rows:
		if "/OrchardInteriorReceiving/FixedReceivingContacts/" in row.owner:continue
		# Only deliberate rolling guideway and the original stationary vehicle are
		# excluded. Old receiving supports remain visible as conflicts to reconcile.
		if "/RollingGuidewayContacts/" in row.owner or "/Group4OwnedTram_Source024" in row.owner:
			excluded.append(row.owner);continue
		var shape:Shape3D
		match row["class"]:
			"ConcavePolygonShape3D":
				shape=ConcavePolygonShape3D.new();var points:=PackedVector3Array()
				for p:Array in row.points:points.append(vec(p))
				shape.set_faces(points);shape.backface_collision=row.backface_collision
			"ConvexPolygonShape3D":
				shape=ConvexPolygonShape3D.new();var points:=PackedVector3Array()
				for p:Array in row.points:points.append(vec(p))
				shape.points=points
			"BoxShape3D":shape=BoxShape3D.new();shape.size=vec(row.size)
			"CylinderShape3D":shape=CylinderShape3D.new();shape.radius=row.radius;shape.height=row.height
			"CapsuleShape3D":shape=CapsuleShape3D.new();shape.radius=row.radius;shape.height=row.height
			"SphereShape3D":shape=SphereShape3D.new();shape.radius=row.radius
			_:assert(false,"Unsupported retained shape");quit(2);return
		shape.margin=row.margin
		var body:=StaticBody3D.new();body.set_meta("original_owner",row.owner);body.collision_layer=int(row.layer)
		var col:=CollisionShape3D.new();col.shape=shape;body.add_child(col);world.add_child(body)
		body.transform=Transform3D(Basis(vec(row.transform[0]),vec(row.transform[1]),vec(row.transform[2])),vec(row.transform[3]))
	for i in range(3):await physics_frame
	var state:=world.get_world_3d().direct_space_state;var results:Array=[]
	for variant:Dictionary in variants.variants:
		var owners:Dictionary={};var poses:Array=variant.poses;var queries:=0;var unresolved:Array=[]
		for i in range(poses.size()-1):
			var a:Array=poses[i];var b:Array=poses[i+1];var delta:=wrapf(float(b[3])-float(a[3]),-PI,PI);var half:=absf(delta)*.5
			var box:=BoxShape3D.new();box.size=Vector3(2*(2*cos(half)+2.7*sin(half)),4.,2*(2.7*cos(half)+2*sin(half)))
			var q:=PhysicsShapeQueryParameters3D.new();q.shape=box;q.margin=0
			q.transform=Transform3D(Basis(Vector3.UP,float(a[3])+delta*.5),Vector3(a[1],58.1,a[2]))
			var hits:=state.intersect_shape(q,256);q.motion=Vector3(b[1]-a[1],0,b[2]-a[2]);var sweep:=state.cast_motion(q);queries+=1
			if sweep[0]<1:
				var rest:=state.get_rest_info(q)
				var rest_owner:=""
				if not rest.is_empty():
					var collider=instance_from_id(rest.collider_id)
					if collider!=null:rest_owner=collider.get_meta("original_owner",str(collider.get_path()))
				q.transform.origin+=q.motion*minf(1,sweep[1]+.0001);q.motion=Vector3.ZERO;hits.append_array(state.intersect_shape(q,256))
				if hits.is_empty():
					q.transform=Transform3D(Basis(Vector3.UP,float(a[3])+delta*.5),Vector3(a[1],58.1,a[2]))
					q.motion=Vector3(b[1]-a[1],0,b[2]-a[2])
					var isolated:Array=[]
					var bodies:=world.find_children("*","CollisionObject3D",true,false)
					var all_rids:Array[RID]=[]
					for body:CollisionObject3D in bodies:all_rids.append(body.get_rid())
					for body:CollisionObject3D in bodies:
						var exclusions:Array[RID]=all_rids.duplicate();exclusions.erase(body.get_rid());q.exclude=exclusions
						var single:=state.cast_motion(q)
						if single[0]<1:isolated.append({"owner":body.get_meta("original_owner",str(body.get_path())),"safe":single[0],"unsafe":single[1]})
					q.exclude=[]
					unresolved.append({"pose":a,"safe_fraction":sweep[0],"unsafe_fraction":sweep[1],"rest_owner":rest_owner,"rest":str(rest),"isolated":isolated})
			assert(hits.size()<512,"Query hit capacity")
			for hit:Dictionary in hits:
				var name:String=hit.collider.get_meta("original_owner")
				if not owners.has(name):owners[name]={"first_pose":a.slice(0,4),"last_pose":a.slice(0,4),"hit_count":0}
				owners[name].last_pose=a.slice(0,4);owners[name].hit_count+=1
		var result:={"crossing_z":variant.crossing_z,"queries":queries,"owners":owners,"unresolved_sweeps":unresolved,"grouped_receiving":"Original installed snapshot only"}
		if args.has("--components") and owners.is_empty() and unresolved.is_empty():
			result.component_sweep=await component_check(world,poses)
		results.append(result)
	var output:String=args["--result"];assert(not FileAccess.file_exists(output))
	var file:=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify({"scope":"Frozen installed active-shape snapshot; geometry choice only, not installed acceptance","excluded":excluded,"results":results},"\t"));file.close()
	for result:Dictionary in results:print("ALIGNMENT ",result.crossing_z," owners=",result.owners.size())
	quit(0)

func component_check(world:Node3D,poses:Array)->Dictionary:
	var viewport:=SubViewport.new();viewport.own_world_3d=true;viewport.render_target_update_mode=SubViewport.UPDATE_DISABLED;root.add_child(viewport)
	var ship:=Node3D.new();viewport.add_child(ship)
	var space:=Node3D.new();space.name="ShipSpace";ship.add_child(space)
	var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
	var districts:=Node3D.new();space.add_child(districts)
	var factory=load("res://tram_passenger_successor_20261024/assembly_initial_pose_r002.gd")
	var assembly:Node3D=factory.create(districts)
	var body:AnimatableBody3D=assembly.get_node("Group4OwnedTram_Source024")
	var cart:RigidBody3D=load("res://scripts/cleaning_cart.gd").new();cart.name="CustodialCart"
	cart.transform=body.global_transform*Transform3D(Basis.IDENTITY,Vector3(0,.025,.14));actors.add_child(cart);cart.freeze=true
	for stock:RigidBody3D in cart.products:stock.freeze=true
	var motor:Node3D=factory.attach_original_cart(assembly,cart)
	var actor:CharacterBody3D=load("res://scripts/player.gd").new();actor.position=body.to_global(Vector3(0,.025,-1.3));actor.spawn_position=actor.position;actors.add_child(actor)
	actor.set_physics_process(false);actor.set_process_input(false);actor.set_process_unhandled_input(false)
	var budget:Node=load("res://scripts/lighting_budget.gd").new();districts.add_child(budget);budget.configure(districts,actor)
	load("res://scripts/group4_tram_operating_controls.gd").build(assembly,body,assembly.get_node("Group4BoardingSafety"),assembly.get_node("Group4OriginalCartRestraint"),motor,actor,budget)
	for i in range(3):await physics_frame
	var exclusions:Array[RID]=[]
	assert(cart.products.size()==4 and body.get_meta("exact_original_portal_contact_components",0)==18)
	var result:Dictionary=load("res://orchard_tram_interior_20261025/integration/component_sweep.gd").audit(ship,assembly,poses,[poses[0][0],poses[-1][0]],exclusions,world.get_world_3d().direct_space_state)
	result.exact_portal_frame_components=18;result.original_cart_stock_count=4
	viewport.queue_free();return result
