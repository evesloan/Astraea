extends "res://tests/validate_d04_port_forward_commons_service.gd"
func bounds(mesh:MeshInstance3D)->AABB:
	var first:=true;var b:=AABB()
	for surface in range(mesh.mesh.get_surface_count()):
		var points:PackedVector3Array=mesh.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]
		for point in points:
			var at:Vector3=mesh.global_transform*point
			if first:b=AABB(at,Vector3.ZERO);first=false
			else:b=b.expand(at)
	return b
func run()->void:
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_D17_STANDARD823.json"));var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(40):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var prior:Node3D=ship.find_child("StarAtlasD17ReceivingFirst",true,false)
	if not p.active:
		record("production_guard_sealed_before_test",prior.find_child("D17R_HeldRoom823",true,false)!=null)
		record("production_room_inactive",ship.find_child("StarAtlasD17Standard823",true,false)==null)
	var n:Node3D=ship.find_child("StarAtlasD17Standard823",true,false)if p.active else load("res://scripts/star_atlas_d17_standard823.gd").build(ship,true)
	for i in range(5):await physics_frame
	var room:Node3D=n.get_node("RetainedStandard823Interior");var space:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state
	record("original_candidate_export_unchanged",FileAccess.get_sha256("res://assets/models/"+str(p.room_model))==p.room_model_sha256)
	record("original405_runtime_room_meshes",room.find_children("*","MeshInstance3D",true,false).size()==405)
	if p.active:record("receiving_physical_candidate_metadata",prior.get_meta("first_room_adopted") and prior.get_meta("first_room_physical_candidate_only"))
	var old_homes:Node3D=ship.find_child("StarAtlasRoomCandidates",true,false);record("prior85_homes221_anchors",old_homes.get_meta("source_candidate_units")==85 and old_homes.get_meta("source_rest_slots")==221)
	record("two_original_reservation_ids",n.get_meta("rest_slot_ids")==p.room_preimage.allocation.proposed_rest_slot_ids and n.get_meta("rest_slot_ids").size()==2)
	record("allocation_identity_preserved",n.get_meta("allocation_sha256")==p.room_preimage.allocation.allocation_sha256)
	for f in p.source_pins:
		if f!="Game/scripts/ship.gd":record("source_pin_"+str(f),FileAccess.get_sha256("res://../"+str(f))==p.source_pins[f])
	var exclusions:Array[RID]=[player.get_rid()]
	for body:StaticBody3D in n.find_children("*","StaticBody3D",true,false):exclusions.append(body.get_rid())
	var native_floor:MeshInstance3D=room.find_child("SUI_Floor",true,false);var floor_bounds:=bounds(native_floor);record("source_floor_datum",absf(floor_bounds.end.y-102)<.00002)
	var root_beam:MeshInstance3D=prior.find_child("D17R_FloorLong_0",true,false)
	for part in p.parts:
		var mesh:MeshInstance3D=n.find_child(part.name,true,false);var b:=bounds(mesh)
		record("new_mesh_exact_bounds_"+str(part.name),b.position.distance_to(vec(part.expected_bounds[0]))<.001 and b.end.distance_to(vec(part.expected_bounds[1]))<.001)
		var query:=PhysicsShapeQueryParameters3D.new();var box:=BoxShape3D.new();box.size=b.size*.98;box.margin=.0001;query.shape=box;query.transform.origin=b.get_center();query.exclude=exclusions
		var hits:=space.intersect_shape(query,64);var foreign:Array=[]
		for hit in hits:
			if not str(hit.collider.get_parent().name)in p.source_root_allowlist:foreign.append(str(hit.collider.get_parent().get_path()))
		record("unchanged_source_clearance_"+str(part.name),foreign.is_empty())
		if not foreign.is_empty():print("FOREIGN_FRAME ",part.name," ",foreign)
		if part.category=="frame":
			var joint:=b.intersection(floor_bounds);record("original_floor_positive_contact_"+str(part.name),joint.size.x>.01 and joint.size.y>.015 and joint.size.z>.01)
			if str(part.name).begins_with("SA823_Transverse"):
				var root_joint:=b.intersection(bounds(root_beam));record("exact_existing_frame_root_joint_"+str(part.name),root_joint.size.x>.2 and root_joint.size.y>.1 and root_joint.size.z>.2)
		else:
			var walls:Array=[]
			for source:MeshInstance3D in room.find_children("*","MeshInstance3D",true,false):
				var overlap:=b.intersection(bounds(source))
				if overlap.size.x>.005 and overlap.size.y>.01 and overlap.size.z>.005:walls.append(str(source.name))
			record("fitted_original_wall_contact_"+str(part.name),not walls.is_empty());print("LAMP_MOUNT_CONTACT ",part.name," ",walls)
	for item in p.runtime_source_expected_bounds:
		var mesh:MeshInstance3D=n.find_child(item.name,true,false);var b:=bounds(mesh);record("rigid_original_fixture_"+str(item.name),b.position.distance_to(vec(item.bounds[0]))<.001 and b.end.distance_to(vec(item.bounds[1]))<.001)
	var entry:Node3D=n.get_node("HomeEntry");var bath:Node3D=n.get_node("BathroomDoor")
	for door in [entry,bath]:record("default_closed_"+str(door.name),not door.desired_open and door.open_fraction==0)
	for x in [-75.5,-73.5,-71.5,-69.5,-67.5,-65.5,-63.5]:
		for z in [32.2,35.6,39.0]:
			var query:=PhysicsRayQueryParameters3D.create(Vector3(x,101.73,z),Vector3(x,101.83,z));var h:=space.intersect_ray(query);record("original_room_floor_underside_"+str(x)+"_"+str(z),not h.is_empty() and absf(h.position.y-101.78)<.001)
	var resting:Array=[]
	for index in range(2):
		var support:MeshInstance3D=room.find_child("HistoricalBedAnchor_"+str(index)+"__REST_RecessedToeBase",true,false);var b:=bounds(support);record("original_rest_supported_"+str(index),absf(b.position.y-102)<.00002);resting.append({"reservation":p.room_preimage.allocation.proposed_rest_slot_ids[index],"original_source_support":str(support.name),"floor_y":b.position.y})
	var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget");var lamps:Array=[]
	for item in p.fixture_instances:
		var lamp:OmniLight3D=n.get_node(item.name+"__Light");lamps.append(lamp)
		if not p.active:budget.sources.append(lamp);budget.requested_shadow[lamp.get_instance_id()]=true
		record("actual_fixture_marker_"+str(item.name),lamp.global_position.distance_to(vec(item.emitter))<.00003)
		record("opal_self_shadow_off_"+str(item.name),(n.find_child(item.name+"__LANTERN_OpalDiffuser",true,false)as MeshInstance3D).cast_shadow==GeometryInstance3D.SHADOW_CASTING_SETTING_OFF)
	player.set_physics_process(false);player.set_controls_enabled(false);budget.set_process(false);var optics:Array=[]
	for at in [Vector3(-73.5,102.03,35.6),Vector3(-69,102.03,35.6),Vector3(-65,102.03,38)]:
		player.global_position=at;player.velocity=Vector3.ZERO;ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(at)
		for i in range(20):await physics_frame
		budget.refresh();var active:=0;var local_active:=0
		for lamp in budget.sources:
			if lamp.visible and lamp.shadow_enabled:active+=1
		for lamp in lamps:
			if lamp.visible and lamp.shadow_enabled:local_active+=1
		record("local_shadowed_fixture_admission_"+str(optics.size()),active<=8 and local_active>=1);optics.append({"at":str(at),"global_shadowed":active,"local_shadowed":local_active})
	player.global_position=Vector3(-61.5,102.03,35.6);player.velocity=Vector3.ZERO;player.set_physics_process(true);player.set_controls_enabled(true);budget.set_process(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
	for i in range(20):await physics_frame
	entry.interact(null);bath.interact(null)
	for i in range(100):
		await physics_frame
		if i%20==0:
			for door in [entry,bath]:
				for leaf in door.leaves:
					var col:CollisionShape3D=leaf.get_node("LeafContact");var query:=PhysicsShapeQueryParameters3D.new();query.shape=col.shape;query.transform=col.global_transform;var foreign:Array=[]
					for h in space.intersect_shape(query,64):
						if not door.is_ancestor_of(h.collider):foreign.append(str(h.collider.get_parent().get_path()))
					record("actual_moving_leaf_clear_"+str(door.name)+"_"+str(leaf.name)+"_"+str(i),foreign.is_empty())
					if not foreign.is_empty():print("LEAF_FOREIGN ",foreign)
	for door in [entry,bath]:record("entry_and_bath_open",door.open_fraction>.999 and not door.obstructed)
	var walks:Array=[]
	for goal in [Vector3(-64,102,35.6),Vector3(-68.3,102,35.6),Vector3(-70.8,102,35.6),Vector3(-72.7,102,35.6),Vector3(-72.7,102,36.0),Vector3(-72.7,102,35.6),Vector3(-73,102,35.6),Vector3(-73,102,34.6),Vector3(-75,102,34.77),Vector3(-75,102,35.6),Vector3(-75,102,34.6),Vector3(-73,102,34.77),Vector3(-73,102,35.6),Vector3(-70,102,35.6),Vector3(-68.3,102,35.6),Vector3(-64,102,35.6),Vector3(-61.5,102,35.6)]:
		var walk:Dictionary=await walk_to(player,goal);walks.append(walk);record("actual_room_route_"+str(walks.size()),walk.reached and walk.floor_contact)
	var out:Dictionary={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks.size(),"errors":errors,"sealed_stage":not p.active,"room_model_sha256":p.room_model_sha256,"model_pins":p.model_pins,"unchanged_room_meshes":405,"frame_root_joints":4,"frame_floor_contacts":7,"new_fixture_meshes":24,"original_rest_contacts":resting,"optical_samples":optics,"walks":walks,"source_frame_capacity_accepted":false,"limits":p.limits}
	FileAccess.open("res://artifacts/star_atlas_d17_standard823_sealed.json"if not p.active else"res://artifacts/star_atlas_d17_standard823.json",FileAccess.WRITE).store_string(JSON.stringify(out,"  "));print(JSON.stringify({"status":out.status,"checks":checks.size(),"errors":errors}));quit(0 if errors.is_empty()else 1)
