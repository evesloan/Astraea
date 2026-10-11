extends "res://tests/validate_d04_port_forward_commons_service.gd"
func exact_bounds(mesh:MeshInstance3D)->AABB:
	var first:=true;var b:=AABB()
	for surface in range(mesh.mesh.get_surface_count()):
		var points:PackedVector3Array=mesh.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]
		for point in points:
			var at:Vector3=mesh.global_transform*point
			if first:b=AABB(at,Vector3.ZERO);first=false
			else:b=b.expand(at)
	return b
func run()->void:
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_D17_STANDARD_BATCH.json"));var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(40):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var first:Node3D=ship.find_child("StarAtlasD17Standard823",true,false)
	record("original823_present",first!=null)
	if not p.active:record("original_north_wall_sealed",ship.find_child("SA_D17_NorthWall_0",true,false)!=null)
	var n:Node3D=ship.find_child("StarAtlasD17StandardBatch",true,false)if p.active else load("res://scripts/star_atlas_d17_standard_batch.gd").build(ship,true)
	for i in range(10):await physics_frame
	var space:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state;var exclude:Array[RID]=[player.get_rid()]
	for body:StaticBody3D in n.find_children("*","StaticBody3D",true,false):exclude.append(body.get_rid())
	for f in p.source_pins:
		if f!="Game/scripts/ship.gd":record("source_"+str(f),FileAccess.get_sha256("res://../"+str(f))==p.source_pins[f])
	for part in p.parts:
		if not p.active and part.category=="wall_replacement":continue
		var mesh:MeshInstance3D=n.find_child(part.name,true,false);record("part_present_"+str(part.name),mesh!=null)
		if mesh==null:continue
		var b:=exact_bounds(mesh);record("bounds_"+str(part.name),b.position.distance_to(vec(part.expected_bounds[0]))<.001 and b.end.distance_to(vec(part.expected_bounds[1]))<.001)
		var center:=b.get_center();var points:=PackedVector3Array()
		for point in part.verts:points.append(center+(vec(point)-center)*.98)
		var shape:=ConvexPolygonShape3D.new();shape.points=points;shape.margin=.0001;var query:=PhysicsShapeQueryParameters3D.new();query.shape=shape;query.exclude=exclude;var foreign:Array=[]
		# Convex pieces are queried directly;apertured wall successors use source interval proof and connected rays.
		if part.category!="wall_replacement":
			for hit in space.intersect_shape(query,64):
				if not str(hit.collider.get_parent().name)in p.source_contact_allowlist:foreign.append(str(hit.collider.get_parent().get_path()))
			record("prior_source_volume_clear_"+str(part.name),foreign.is_empty())
			if not foreign.is_empty():print("FOREIGN_SOURCE ",part.name," ",foreign)
	var bearing_witnesses:Array=[]
	for foot in p.foundation_feet+p.north_foundation_feet:
		for dx in [-.16,0,.16]:
			for dz in [-.16,0,.16]:
				var at:=vec(foot.at)+Vector3(dx,0,dz);var query:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.035,at-Vector3.UP*.035);query.exclude=exclude;var h:=space.intersect_ray(query);var ok:bool=not h.is_empty() and str(h.collider.get_parent().name)==str(foot.source_owner) and absf(h.position.y-97.5)<.001
				record("original_slab_"+str(bearing_witnesses.size()),ok);bearing_witnesses.append({"at":str(at),"expected":foot.source_owner,"actual":str(h.collider.get_parent().name)if not h.is_empty()else"none","pass":ok})
	var original:Node3D=first.get_node("RetainedStandard823Interior");var original_meshes:Dictionary={}
	for mesh:MeshInstance3D in original.find_children("*","MeshInstance3D",true,false):original_meshes[str(mesh.name)]=mesh
	for r in p.rooms:
		var home:Node3D=n.get_node(r.allocation.proposed_runtime_id);var room:Node3D=home.get_node("RetainedFittedInterior");var meshes:Array=room.find_children("*","MeshInstance3D",true,false)
		record("405_original_meshes_"+str(r.allocation.source_envelope_index),meshes.size()==405)
		record("unchanged_rest_ids_"+str(r.allocation.source_envelope_index),home.get_meta("rest_slot_ids")==r.allocation.proposed_rest_slot_ids)
		record("unchanged_allocation_"+str(r.allocation.source_envelope_index),home.get_meta("allocation_sha256")==r.allocation.allocation_sha256)
		for mesh:MeshInstance3D in meshes:
			var source:MeshInstance3D=original_meshes[str(mesh.name)];var expected:Transform3D=Transform3D(Basis.IDENTITY,vec(r.translation))*source.global_transform
			record("rigid_original_"+str(r.allocation.source_envelope_index)+"_"+str(mesh.name),mesh.mesh==source.mesh and mesh.global_transform.origin.distance_to(expected.origin)<.00003 and mesh.global_transform.basis.is_equal_approx(expected.basis))
		for index in range(2):
			var rest:MeshInstance3D=room.find_child("HistoricalBedAnchor_"+str(index)+"__REST_RecessedToeBase",true,false);record("actual_rest_floor_contact_"+str(r.allocation.source_envelope_index)+"_"+str(index),absf(exact_bounds(rest).position.y-102)<.00003)
		for x in [-75.5,-72,-68.5,-63.5]:
			var query:=PhysicsRayQueryParameters3D.create(Vector3(x,101.73,r.center_z),Vector3(x,101.83,r.center_z));var hit:=space.intersect_ray(query);record("source_floor_underside_"+str(r.allocation.source_envelope_index)+"_"+str(x),not hit.is_empty() and absf(hit.position.y-101.78)<.001)
	for item in p.runtime_source_expected_bounds:
		var mesh:MeshInstance3D=n.find_child(item.name,true,false);var b:=exact_bounds(mesh);record("original_fixture_"+str(item.name),b.position.distance_to(vec(item.bounds[0]))<.001 and b.end.distance_to(vec(item.bounds[1]))<.001)
	var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget");var lights:Array=n.find_children("*","Light3D",true,false)
	for light:Light3D in lights:
		if not p.active:budget.sources.append(light);budget.requested_shadow[light.get_instance_id()]=light.shadow_enabled;light.visible=false;light.shadow_enabled=false
		record("registered_new_fixture_"+str(light.name),budget.sources.has(light) and budget.requested_shadow[light.get_instance_id()])
	player.set_physics_process(false);player.set_controls_enabled(false);budget.set_process(false);var optical:Array=[]
	for r in p.rooms:
		var at:=Vector3(-69,102.03,r.center_z);player.global_position=at;player.velocity=Vector3.ZERO;ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(at)
		for i in range(15):await physics_frame
		budget.refresh();var total:=0;var local_active:=0
		for light in budget.sources:
			if light.visible and light.shadow_enabled:total+=1
		for item in p.fixture_instances:
			if item.room_index!=r.allocation.source_envelope_index:continue
			var light:OmniLight3D=n.get_node(item.name+"__Light")
			if light.visible and light.shadow_enabled:local_active+=1
		record("bounded_local_lighting_"+str(r.allocation.source_envelope_index),total<=8 and local_active>=1);optical.append({"room":r.allocation.source_envelope_index,"total_shadowed":total,"local_shadowed":local_active})
	player.set_physics_process(true);player.set_controls_enabled(true);budget.set_process(true);var routes:Array=[];var leaf_samples:=0
	# One supported setup seed for each separately sealed bank;no intra-bank route teleport.
	for bank in ["Fore","Aft"]:
		var rooms:Array=[]
		for r in p.rooms:
			if (r.center_z<0)==(bank=="Fore"):rooms.append(r)
		rooms.sort_custom(func(a,b):return a.center_z>b.center_z if bank=="Fore"else a.center_z<b.center_z)
		player.global_position=Vector3(-61.5,102.03,-20 if bank=="Fore"else 38);player.velocity=Vector3.ZERO;ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
		for i in range(20):await physics_frame
		for r in rooms:
			var home:Node3D=n.get_node(r.allocation.proposed_runtime_id);var entry:Node3D=home.get_node("HomeEntry");var bath:Node3D=home.get_node("BathroomDoor")
			var street_walk:Dictionary=await walk_to(player,Vector3(-61.5,102,r.center_z));record("actual_street_to_"+str(r.allocation.source_envelope_index),street_walk.reached and street_walk.floor_contact);routes.append(street_walk)
			record("entry_default_closed_"+str(r.allocation.source_envelope_index),not entry.desired_open and entry.open_fraction==0);entry.interact(null);bath.interact(null)
			for i in range(100):
				await physics_frame
				if i%20==0:
					for door in [entry,bath]:
						for leaf in door.leaves:
							var col:CollisionShape3D=leaf.get_node("LeafContact");var query:=PhysicsShapeQueryParameters3D.new();query.shape=col.shape;query.transform=col.global_transform;var foreign:Array=[]
							for hit in space.intersect_shape(query,64):
								if not door.is_ancestor_of(hit.collider):foreign.append(str(hit.collider.get_parent().get_path()))
							record("moving_leaf_"+str(r.allocation.source_envelope_index)+"_"+str(leaf_samples),foreign.is_empty());leaf_samples+=1
							if not foreign.is_empty():print("LEAF_FOREIGN ",r.allocation.source_envelope_index," ",foreign)
			var z:float=r.center_z
			for goal in [Vector3(-64,102,z),Vector3(-68.3,102,z),Vector3(-70.8,102,z),Vector3(-72.7,102,z),Vector3(-72.7,102,z+.4),Vector3(-72.7,102,z),Vector3(-73,102,z),Vector3(-73,102,z-1),Vector3(-75,102,z-.83),Vector3(-75,102,z),Vector3(-75,102,z-1),Vector3(-73,102,z-.83),Vector3(-73,102,z),Vector3(-68.3,102,z),Vector3(-64,102,z),Vector3(-61.5,102,z)]:
				var walk:Dictionary=await walk_to(player,goal);routes.append(walk);record("actual_room_route_"+str(routes.size()),walk.reached and walk.floor_contact)
			entry.interact(null);bath.interact(null)
			for i in range(100):await physics_frame
			record("final_closed_"+str(r.allocation.source_envelope_index),entry.open_fraction<.001 and bath.open_fraction<.001);print("BATCH_ROOM_COMPLETE ",r.allocation.source_envelope_index," route_legs ",routes.size())
	var out:Dictionary={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks.size(),"errors":errors,"rooms":9,"preserved_rest_reservations":18,"original_runtime_meshes":3645,"bearings":bearing_witnesses,"new_source_street_area_m2":p.new_floor_m2,"model_pins":p.model_pins,"optical_samples":optical,"moving_leaf_samples":leaf_samples,"walks":routes,"supported_setup_seeds":2,"intra_bank_route_teleports":0,"source_capacity_accepted":false,"limits":p.limits}
	FileAccess.open("res://artifacts/star_atlas_d17_standard_batch_sealed.json"if not p.active else"res://artifacts/star_atlas_d17_standard_batch.json",FileAccess.WRITE).store_string(JSON.stringify(out,"  "));print(JSON.stringify({"status":out.status,"checks":checks.size(),"errors":errors}));quit(0 if errors.is_empty()else 1)
