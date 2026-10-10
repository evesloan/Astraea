extends SceneTree
var checks:Dictionary={}
var errors:Array=[]
func record(key:String,ok:bool)->void:
	checks[key]=ok
	if not ok:errors.append(key)
func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func ray(space:PhysicsDirectSpaceState3D,a:Vector3,b:Vector3)->Dictionary:
	return space.intersect_ray(PhysicsRayQueryParameters3D.create(a,b))
func capsule_clear(space:PhysicsDirectSpaceState3D,at:Vector3)->bool:
	var q:=PhysicsShapeQueryParameters3D.new();var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8;shape.margin=.001
	q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*.925)
	if not space.intersect_shape(q,32).is_empty():return false
	# Opposite cross-rays also catch a stance placed wholly inside an opaque
	# closed mesh; concave surface queries alone can miss that case.
	for delta in [Vector3(.3,0,0),Vector3(0,0,.3)]:
		if not ray(space,at+Vector3.UP-delta,at+Vector3.UP+delta).is_empty():return false
	return true
func cart_clear(space:PhysicsDirectSpaceState3D,at:Vector3,yaw:float)->bool:
	var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/cleaning_cart_contacts.json"))
	var pose:=Transform3D(Basis(Vector3.UP,yaw),at+Vector3.UP*.005)
	for item in d.boxes:
		var shape:=BoxShape3D.new();shape.size=vec(item.size);shape.margin=.001
		var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=pose*Transform3D(Basis.IDENTITY,vec(item.center))
		if not space.intersect_shape(q,32).is_empty():return false
	for item in d.wheel_contacts:
		var shape:=SphereShape3D.new();shape.radius=float(item.radius);shape.margin=.001
		var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=pose*Transform3D(Basis.IDENTITY,vec(item.center))
		if not space.intersect_shape(q,32).is_empty():return false
	return true
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var receiving:Node3D=ship.find_child("StarAtlasD17ReceivingFirst",true,false)
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_D17_RECEIVING_FIRST.json"))
	var space:=ship.get_world_3d().direct_space_state
	var floor:Node3D=receiving.find_child("D17R_ReceivedFloor",true,false)
	var source:Node3D=ship.get_node("ShipSpace/CentralResidentialStreetFloors/D16_STAR_ATLAS_MISSING_STREET_1")
	var source_count:=0
	for pier in p.piers:
		for dx in [-.16,0,.16]:
			for dz in [-.16,0,.16]:
				var at:=Vector3(float(pier.x)+dx,97.5,float(pier.z)+dz)
				var h:=ray(space,at+Vector3.UP*.04,at-Vector3.UP*.04)
				record("source_pier_"+str(source_count),not h.is_empty()and source.is_ancestor_of(h.collider)and absf(h.position.y-97.5)<.002);source_count+=1
	for item in [{"name":"SA_LongBeam_-64_2_106_26","at":Vector3(-64.02,106.12,12.6),"delta":Vector3(.03,0,0)},{"name":"SA_CrossBeam_12_7_106_26","at":Vector3(-66.7,106.12,12.88),"delta":Vector3(0,0,.03)}]:
		var owner:Node3D=ship.find_child(item.name,true,false);var h:=ray(space,item.at+item.delta,item.at-item.delta)
		record("source_frame_"+str(item.name),owner!=null and not h.is_empty()and owner.is_ancestor_of(h.collider))
	var route:Array[Vector3]=[Vector3(-65,102,15.3),Vector3(-65,102,16.6),Vector3(-63.8,102,16.6),Vector3(-61.5,102,16.6),Vector3(-61.5,102,22),Vector3(-61.5,102,28),Vector3(-61.5,102,35.6),Vector3(-61.5,102,38.3)]
	for i in range(route.size()):
		var at:Vector3=route[i];var h:=ray(space,at+Vector3.UP*.05,at-Vector3.UP*.05)
		record("received_floor_"+str(i),not h.is_empty()and floor.is_ancestor_of(h.collider)and absf(h.position.y-102)<.002)
		record("capsule_stance_"+str(i),capsule_clear(space,at))
		record("real_cart_shapes_"+str(i),cart_clear(space,at,PI/2 if i in [2,3]else 0.0))
	for item in [{"name":"D17R_Hanger_0_01","at":Vector3(-62.75,103.6,22)},{"name":"D17R_TrussDiag_0_01","at":Vector3(-62.75,105.52,19.65)}]:
		var owner:Node3D=receiving.find_child(item.name,true,false);var h:=ray(space,item.at+Vector3(.2,0,0),item.at-Vector3(.2,0,0))
		record("actual_member_"+str(item.name),owner!=null and not h.is_empty()and owner.is_ancestor_of(h.collider))
	for i in range(p.guards.size()):
		var g:Dictionary=p.guards[i];var a:=Vector3(g.a[0],102.7,g.a[1]);var b:=Vector3(g.b[0],102.7,g.b[1]);var n:Vector3=(b-a).normalized().cross(Vector3.UP)*.2;var at:Vector3=(a+b)*.5
		var owner:Node3D=receiving.find_child(str(g.name),true,false);var h:=ray(space,at+n,at-n)
		record("guard_"+str(g.name),not h.is_empty()and owner.is_ancestor_of(h.collider))
	var old_wall:Node3D=ship.find_child("SA_D17_SouthWall_0",true,false)
	var gateway:Node3D=receiving.get_node("StandardHouseReceivingDoor")
	if not p.open_gateway:
		var h:=ray(space,Vector3(-65,103.2,13.3),Vector3(-65,103.2,14.6))
		record("original_wall_remains_sealed_until_receiving_verified",old_wall!=null and not h.is_empty()and old_wall.is_ancestor_of(h.collider))
	else:
		record("exact_original_wall_superseded",old_wall==null)
		var controllers:Array[Node3D]=[gateway]
		# Temporary first-room source fixture; the production branch keeps its
		# contained reservation guard and does not instantiate this room.
		for name in ["D17R_HeldRoom823","D17R_HeldRoom823_Cap","D17R_HeldRoom823_Base"]:receiving.find_child(name,true,false).free()
		var home:=Node3D.new();home.name="ValidationOnly823EntryFit";ship.add_child(home)
		var recipe:Dictionary=p.first_room.recipe
		var visual:Node3D=load("res://assets/models/"+str(p.first_room.candidate_model)).instantiate();home.add_child(visual)
		record("fitted_candidate_export_sha",FileAccess.get_sha256("res://assets/models/"+str(p.first_room.candidate_model))==p.first_room.candidate_sha256)
		load("res://scripts/static_contact_cache.gd").attach_group(visual,visual.find_children("*","MeshInstance3D",true,false))
		var threshold:MeshInstance3D=visual.find_child("D17_823_ContainedThreshold",true,false)
		for d in [{"name":"EntryDoor","controller":"guest_entry_door","at":p.first_room.entry_origin,"yaw":p.first_room.entry_yaw},{"name":"BathroomDoor","controller":"guest_privacy_door","at":p.first_room.bath_origin,"yaw":p.first_room.bath_yaw}]:
			var door:Node3D=load("res://scripts/"+str(d.controller)+".gd").new();door.name=d.name;door.persistent_id=StringName(str(p.first_room.allocation.proposed_runtime_id)+"__source_fit_"+str(d.name));door.position=vec(d.at);door.rotation.y=float(d.yaw);home.add_child(door);controllers.append(door)
		for d in controllers:if d.desired_open:d.interact(null)
		for i in range(100):await physics_frame
		for d in controllers:record("closed_"+str(d.name),not d.desired_open and d.open_fraction<.001 and not d.obstructed)
		for d in [gateway,controllers[1]]:
			var n:Vector3=d.global_basis.z*.5;var at:Vector3=d.global_position+Vector3.UP*1.2;var h:=ray(space,at-n,at+n)
			record("closed_collision_"+str(d.name),not h.is_empty()and d.is_ancestor_of(h.collider))
		for d in controllers:d.interact(null)
		for i in range(100):
			await physics_frame
			if i in [0,20,40,60,80,99]:
				for d in [gateway,controllers[1]]:
					for leaf in d.leaves:
						var contact:CollisionShape3D=leaf.get_node("LeafContact")
						var q:=PhysicsShapeQueryParameters3D.new();q.shape=contact.shape;q.transform=contact.global_transform;q.margin=.001
						var foreign:Array=[]
						for hit in space.intersect_shape(q,64):
							if not d.is_ancestor_of(hit.collider):foreign.append(str(hit.collider.get_path()))
						record("moving_sweep_"+str(d.name)+"_"+str(leaf.name)+"_"+str(i),foreign.is_empty())
						if not foreign.is_empty():errors.append({"sweep_foreign":foreign,"origin":str(contact.global_position)})
		for d in controllers:record("open_"+str(d.name),d.desired_open and d.open_fraction>.999 and not d.obstructed)
		for d in [gateway,controllers[1]]:
			var n:Vector3=d.global_basis.z*.5;var at:Vector3=d.global_position+Vector3.UP*1.2
			record("open_aperture_"+str(d.name),ray(space,at-n,at+n).is_empty())
		record("open_actual_cart_shared_threshold",cart_clear(space,Vector3(-65,102,14.13),0))
		for z in [36.5,37.6,38.55]:
			var h:=ray(space,Vector3(-64,103.2,z),Vector3(-62.8,103.2,z))
			var privacy:MeshInstance3D=visual.find_child("D17_823_BathPrivacyReturn",true,false)
			record("adapted_bath_privacy_"+str(z),not h.is_empty() and home.is_ancestor_of(h.collider) and (privacy.global_transform*privacy.get_aabb()).grow(.003).has_point(h.position))
		for at in [Vector3(-65,102,13.95),Vector3(-62.7,102,35.6),Vector3(-63.6,102,35.6)]:record("open_passage_"+str(at),capsule_clear(space,at))
		var h:=ray(space,Vector3(-63.025,102.03,35.6),Vector3(-63.025,101.97,35.6))
		record("contained_threshold_floor",not h.is_empty()and home.is_ancestor_of(h.collider) and (threshold.global_transform*threshold.get_aabb()).grow(.00003).has_point(h.position)and absf(h.position.y-102)<.002)
		for d in controllers:d.interact(null)
		for i in range(100):await physics_frame
		for d in controllers:record("final_closed_"+str(d.name),not d.desired_open and d.open_fraction<.001)
	var homes:Node3D=ship.find_child("StarAtlasRoomCandidates",true,false)
	record("original85_homes",int(homes.get_meta("source_candidate_units",0))==85)
	record("original221_anchors",int(homes.get_meta("source_rest_slots",0))==221)
	record("culling_enabled",ship.get_node("ShipSystems/ReceivedRoomResidency").enabled)
	record("first_room_stays_unadopted",not receiving.get_meta("first_room_adopted"))
	var report={"status":"PASS"if errors.is_empty()else"FAIL","stage":"connected_gateway_and_temporary_first_room_fit"if p.open_gateway else"sealed_wall_receiving_gate","model_sha256":p.model_sha256,"checks":checks,"check_count":checks.size(),"errors":errors,"source_bearing_witnesses":38,"ray_excludes":0,"real_cart_shape_station_queries":route.size(),"capsule_stations":route.size(),"first_room_fixture_validation_only":p.open_gateway,"first_room_adopted":false,"new_floor_area_m2":p.new_floor_area_m2,"primary_engineering_load_accepted":false,"whole_Group1_complete":false,"limits":p.limits}
	var path:="res://artifacts/d17_receiving_first.json"if p.open_gateway else"res://artifacts/d17_receiving_sealed.json"
	FileAccess.open(path,FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print(JSON.stringify(report));quit(0 if errors.is_empty()else 1)
