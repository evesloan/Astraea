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
		if "/Group4Completion/" in row.owner:continue
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
	var assembly:Node3D=load("res://aquatic_tram_interior_20261026/integration/assembly.gd").create(world,"AFT_MIDSHIP")
	assert(assembly!=null)
	var exclude_rids:Array[RID]=[]
	var car:AnimatableBody3D=assembly.get_node("Group4OwnedTram_Source024");exclude_rids.append(car.get_rid())
	for body:CollisionObject3D in car.find_children("*","CollisionObject3D",true,false):exclude_rids.append(body.get_rid())
	for body:CollisionObject3D in assembly.find_children("*","CollisionObject3D",true,false):
		if "/RollingGuidewayContacts/" in str(body.get_path()):exclude_rids.append(body.get_rid())
	var original_models:Array=[{"path":"res://assets/models/AST-CIR-005_aft_midship_d04_port_threshold_r001.glb","xyz":[0,0,272]}]
	for y in [44.,52.5,61.]:
		for xz in [[20,186],[50,244],[12,243]]:original_models.append({"path":"res://assets/models/AST-STR-001-H810.glb" if y==61 else "res://assets/models/AST-STR-001.glb","xyz":[xz[0],y,xz[1]]})
	# Include the retained aquatic enclosure/edges and both original switchbacks.
	# These are permanent source geometry, independent of detail residency.
	for row in [{"path":"res://assets/models/AST-CIR-004.glb","xyz":[12,44,235]},{"path":"res://assets/models/AST-AQU-012.glb","xyz":[8,61,182]},{"path":"res://assets/models/AST-AQU-013.glb","xyz":[8,44,182]}]:original_models.append(row)
	for base_y in [44.0,52.5]:
		var stairs:Node3D=load("res://aquatic_tram_interior_20261026/integration/assembly.gd").raw_model("res://assets/models/AST-CIR-001.glb")
		world.add_child(stairs);stairs.position=Vector3(10,base_y,200.5)
		for part:MeshInstance3D in stairs.find_children("CIR_Guard*","MeshInstance3D",true,false):
			part.create_trimesh_collision()
			for body:StaticBody3D in part.find_children("*","StaticBody3D",true,false):body.set_meta("original_owner","Aquatic/Switchback_"+str(base_y)+"/"+str(part.name))
		_original_contact(world,[Vector3(10,base_y,200.5),Vector3(12.5,base_y,200.5),Vector3(12.5,base_y+4.25,193),Vector3(10,base_y+4.25,193)])
		_original_contact(world,[Vector3(10,base_y+4.25,193),Vector3(16,base_y+4.25,193),Vector3(16,base_y+4.25,190),Vector3(10,base_y+4.25,190)])
		_original_contact(world,[Vector3(13.5,base_y+8.5,200.5),Vector3(16,base_y+8.5,200.5),Vector3(16,base_y+4.25,193),Vector3(13.5,base_y+4.25,193)])
	var added:=0
	for entry:Dictionary in original_models:
		var model:Node3D=load("res://aquatic_tram_interior_20261026/integration/assembly.gd").raw_model(entry.path);world.add_child(model);model.position=vec(entry.xyz)
		for mesh:MeshInstance3D in model.find_children("*","MeshInstance3D",true,false):
			var bounds:AABB=mesh.global_transform*mesh.get_aabb()
			if not bounds.intersects(AABB(Vector3(-25,54.5,110),Vector3(85,7,215))):continue
			var body:=StaticBody3D.new();body.set_meta("original_owner",str(entry.path)+"/"+str(entry.xyz)+"/"+str(mesh.name))
			var collision:=CollisionShape3D.new();collision.shape=mesh.mesh.create_trimesh_shape();body.add_child(collision);world.add_child(body);body.global_transform=mesh.global_transform;added+=1
	print("COMPLETE_CORE_COLUMN_CONTACTS ",added)
	var crossings:Array=JSON.parse_string(FileAccess.get_file_as_string("res://aquatic_tram_interior_20261026/r009/CROSSING_SOURCES.json"))
	for crossing:Dictionary in crossings:
		for entry:Dictionary in crossing.sources:
			var path:String="res://"+str(entry.path).trim_prefix("Game/")
			assert(FileAccess.get_sha256(path)==str(entry.sha256),"Exact retained crossing bytes")
			var doc:=GLTFDocument.new();var state:=GLTFState.new()
			assert(doc.append_from_file(ProjectSettings.globalize_path(path),state)==OK)
			var model:Node3D=doc.generate_scene(state);world.add_child(model);model.position=vec(crossing.position)
			for mesh:MeshInstance3D in model.find_children("*","MeshInstance3D",true,false):
				var body:=StaticBody3D.new();body.set_meta("original_owner",str(crossing.id)+"/"+str(entry.layer)+"/"+str(mesh.name))
				var collision:=CollisionShape3D.new();collision.shape=mesh.mesh.create_trimesh_shape();body.add_child(collision);world.add_child(body);body.global_transform=mesh.global_transform
	for i in range(3):await physics_frame
	var state:=world.get_world_3d().direct_space_state;var results:Array=[]
	for variant:Dictionary in variants.variants:
		var owners:Dictionary={};var poses:Array=variant.poses;var queries:=0;var unresolved:Array=[]
		for i in range(poses.size()-1):
			var a:Array=poses[i];var b:Array=poses[i+1];var delta:=wrapf(float(b[3])-float(a[3]),-PI,PI);var half:=absf(delta)*.5
			var box:=BoxShape3D.new();box.size=Vector3(2*(2*cos(half)+2.7*sin(half)),4.,2*(2.7*cos(half)+2*sin(half)))
			var q:=PhysicsShapeQueryParameters3D.new();q.shape=box;q.margin=0;q.exclude=exclude_rids
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
					q.exclude=exclude_rids
					unresolved.append({"pose":a,"safe_fraction":sweep[0],"unsafe_fraction":sweep[1],"rest_owner":rest_owner,"rest":str(rest),"isolated":isolated})
			assert(hits.size()<512,"Query hit capacity")
			for hit:Dictionary in hits:
				var name:String=hit.collider.get_meta("original_owner",str(hit.collider.get_path()))
				if not owners.has(name):owners[name]={"first_pose":a.slice(0,4),"last_pose":a.slice(0,4),"hit_count":0}
				owners[name].last_pose=a.slice(0,4);owners[name].hit_count+=1
		var result:={"crossing_z":variant.crossing_z,"queries":queries,"owners":owners,"unresolved_sweeps":unresolved,"grouped_receiving":"Exact live factory r005 including original bridge/station receivers; full retained core/columns and four crossing sources; intentional rolling rails excluded"}
		if args.has("--components") and owners.is_empty() and unresolved.is_empty():
			result.component_sweep=await component_check(world,poses,exclude_rids)
		results.append(result)
	var output:String=args["--result"];assert(not FileAccess.file_exists(output))
	var file:=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify({"scope":"Exact four retained crossing floor/shell sources plus protected core snapshot and authored station; not full installed acceptance","excluded":excluded,"results":results},"\t"));file.close()
	for result:Dictionary in results:print("ALIGNMENT ",result.crossing_z," owners=",result.owners.size())
	quit(0)

func component_check(world:Node3D,poses:Array,world_exclusions:Array[RID])->Dictionary:
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
	var exclusions:Array[RID]=world_exclusions.duplicate()
	assert(cart.products.size()==4 and body.get_meta("exact_original_portal_contact_components",0)==18)
	var result:Dictionary=load("res://orchard_tram_interior_20261025/integration/component_sweep.gd").audit(ship,assembly,poses,[poses[0][0],poses[-1][0]],exclusions,world.get_world_3d().direct_space_state)
	result.exact_portal_frame_components=18;result.original_cart_stock_count=4
	viewport.queue_free();return result

func _original_contact(parent:Node3D,quad:Array[Vector3])->void:
	load("res://scripts/aquatic_section.gd")._contact(parent,quad)
