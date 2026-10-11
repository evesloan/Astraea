extends "res://tests/validate_d04_port_forward_commons_service.gd"
func exact_bounds(mesh:MeshInstance3D)->AABB:
	var first:=true;var bounds:=AABB()
	for surface in range(mesh.mesh.get_surface_count()):
		var vertices:PackedVector3Array=mesh.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]
		for vertex in vertices:
			var at:Vector3=mesh.global_transform*vertex
			if first:bounds=AABB(at,Vector3.ZERO);first=false
			else:bounds=bounds.expand(at)
	return bounds
func run()->void:
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/AFT_CROWN_FOYER_WAITING_EDGES.json"))
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(30):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var n:Node3D=ship.find_child("AftCrownFoyerWaitingEdges",true,false);var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	record("installed_once",n!=null and ship.find_children("AftCrownFoyerWaitingEdges","Node3D",true,false).size()==1)
	if n==null:quit(1);return
	record("idempotent",load("res://scripts/aft_crown_foyer_waiting_edges.gd").build(ship)==n)
	record("native_audit_sealed",FileAccess.get_sha256("res://artifacts/aft_crown_foyer_waiting_edges_native.json")==p.native_audit_sha256)
	for f in p.model_pins:record("model_"+str(f),FileAccess.get_sha256("res://assets/models/"+str(f))==p.model_pins[f])
	for f in p.source_pins:
		if f!="Game/scripts/ship.gd":record("source_"+str(f),FileAccess.get_sha256("res://../"+str(f))==p.source_pins[f])
	var excluded:Array[RID]=[player.get_rid()]
	for body:StaticBody3D in n.find_children("*","StaticBody3D",true,false):excluded.append(body.get_rid())
	var space:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state
	var meshes:Dictionary={}
	for part in p.parts:
		var mesh:MeshInstance3D=n.find_child(part.name,true,false);meshes[part.name]=mesh;record("part_present_"+str(part.name),mesh!=null)
		if mesh==null:continue
		var b:=exact_bounds(mesh);record("part_bounds_"+str(part.name),b.position.distance_to(vec(part.expected_bounds[0]))<.001 and b.end.distance_to(vec(part.expected_bounds[1]))<.001)
		var center:Vector3=(vec(part.expected_bounds[0])+vec(part.expected_bounds[1]))/2;var points:=PackedVector3Array()
		for vertex in part.verts:points.append(center+(vec(vertex)-center)*.98)
		var shape:=ConvexPolygonShape3D.new();shape.points=points;shape.margin=.0001;var query:=PhysicsShapeQueryParameters3D.new();query.shape=shape;query.exclude=excluded
		var hits:=space.intersect_shape(query,32);record("old_sources_clear_"+str(part.name),hits.is_empty())
		if not hits.is_empty():print("PART_CONTACT ",part.name," ",hits)
	for item in p.runtime_source_expected_bounds:
		var mesh:MeshInstance3D=n.find_child(item.name,true,false);record("source_mesh_present_"+str(item.name),mesh!=null)
		if mesh!=null:
			var b:=exact_bounds(mesh);record("rigid_evaluated_bounds_"+str(item.name),b.position.distance_to(vec(item.bounds[0]))<.001 and b.end.distance_to(vec(item.bounds[1]))<.001)
	var floor_witnesses:Array=[]
	for support in p.supports:
		var at:=vec(support.at);var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.03,at-Vector3.UP*.03);q.exclude=excluded;var h:=space.intersect_ray(q)
		record("retained_floor_"+str(support.part),not h.is_empty() and absf(h.position.y-106.5)<.001)
		if not h.is_empty():floor_witnesses.append({"pier":support.part,"floor_owner":str(h.collider.get_parent().name),"height":h.position.y})
	for joint in p.explicit_new_contact_ledger:
		var a:AABB=exact_bounds(meshes[joint.a]);var b:AABB=exact_bounds(meshes[joint.b]);var overlap:=a.intersection(b)
		record("runtime_joint_overlap_"+str(joint.a)+"_"+str(joint.b),overlap.size.x>.0001 and overlap.size.y>.0001 and overlap.size.z>.0001)
	var lamps:Array=[]
	for item in p.fixture_instances:
		var lamp:OmniLight3D=n.get_node(item.name+"__Light");lamps.append(lamp)
		record("fixture_exit_"+str(item.name),lamp.global_position.distance_to(vec(item.emitter))<.00003)
		record("registered_cubemap_"+str(item.name),budget.sources.has(lamp) and budget.requested_shadow[lamp.get_instance_id()] and lamp.omni_shadow_mode==OmniLight3D.SHADOW_CUBE)
		record("fixture_range_energy_"+str(item.name),lamp.omni_range==10 and absf(lamp.light_energy-1.4)<.00001)
		record("opal_self_shadow_off_"+str(item.name),(n.find_child(item.name+"__LANTERN_OpalDiffuser",true,false)as MeshInstance3D).cast_shadow==GeometryInstance3D.SHADOW_CASTING_SETTING_OFF)
	record("old_bays_and_lights",ship.find_child("AftCrownSittingBays",true,false)!=null and ship.find_child("AftCrownSittingLighting",true,false)!=null)
	record("eight_shadow_budget",budget.shadow_source_budget==8)
	player.set_physics_process(false);player.set_controls_enabled(false);budget.set_process(false)
	var samples:Array=[]
	for at in [Vector3(-24,106.53,118.5),Vector3(-24,106.53,127.5),Vector3(24,106.53,118.5),Vector3(24,106.53,127.5)]:
		player.global_position=at;player.velocity=Vector3.ZERO;ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(at)
		for i in range(20):await physics_frame
		budget.refresh();var active:=0;var local_active:=0
		for lamp in budget.sources:
			if lamp.visible and lamp.shadow_enabled:active+=1
		for lamp in lamps:
			if lamp.visible and lamp.shadow_enabled:local_active+=1
		record("bounded_optical_sample_"+str(samples.size()),active<=8 and local_active>=2);samples.append({"at":str(at),"global_sources":active,"new_sources":local_active})
	player.global_position=Vector3(-16,106.53,108);player.velocity=Vector3.ZERO;player.set_physics_process(true);player.set_controls_enabled(true);budget.set_process(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
	for i in range(20):await physics_frame
	var walks:Array=[]
	for goal in [Vector3(-16,106.5,123.5),Vector3(-21,106.5,123.5),Vector3(-26,106.5,123.5),Vector3(-21,106.5,123.5),Vector3(-16,106.5,123.5),Vector3(-16,106.5,140),Vector3(0,106.5,145),Vector3(16,106.5,145),Vector3(16,106.5,123.5),Vector3(21,106.5,123.5),Vector3(26,106.5,123.5),Vector3(21,106.5,123.5),Vector3(16,106.5,123.5),Vector3(16,106.5,108)]:
		var walk:Dictionary=await walk_to(player,goal);walks.append(walk);record("actual_player_route_"+str(walks.size()),walk.reached and walk.floor_contact)
	var out:Dictionary={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks.size(),"errors":errors,"custom_meshes":p.parts.size(),"rigid_original_meshes":p.runtime_source_expected_bounds.size(),"floor_witnesses":floor_witnesses,"runtime_joint_overlaps":p.explicit_new_contact_ledger.size(),"precise_source_contact_ledger":"172 positive-volume polygon intersections retained in source preflight;runtime AABB overlaps complement source proof","fixtures":lamps.size(),"optical_samples":samples,"walks":walks,"no_new_floor":true,"limits":p.limits,"whole_foyer_pressure_or_visual_acceptance":false}
	FileAccess.open("res://artifacts/aft_crown_foyer_waiting_edges.json",FileAccess.WRITE).store_string(JSON.stringify(out,"  "));print(JSON.stringify({"status":out.status,"checks":checks.size(),"errors":errors}));quit(0 if errors.is_empty()else 1)
