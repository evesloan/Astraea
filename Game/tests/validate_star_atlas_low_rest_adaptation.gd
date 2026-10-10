extends SceneTree
var errors:Array=[]
func _initialize()->void:call_deferred("run")
func vec(v:Array)->Vector3:return Vector3(v[0],v[1],v[2])
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var districts:Node3D=ship.get_node("ShipSpace/Districts")
	var fitted:Node3D=districts.get_node("StarAtlasEightHabitatFittings")
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_EIGHT_HABITATS.json"))
	assert(load("res://scripts/star_atlas_eight_habitats.gd").build(ship)==fitted)
	var chosen:Array=[]
	for room in p.rooms:
		if int(room.source_envelope_index) in [443,467,491]:chosen.append(room)
	assert(chosen.size()==3)
	p.rooms=chosen
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	for room in p.rooms:
		var home:Node3D=districts.find_child(str(room.unit_proposal_id),true,false)
		for name in ["EntryDoor","WashDoor","CocoonPrivacyDoor"]:
			if home.has_node(name):
				var door:Node3D=home.get_node(name)
				if door.desired_open:door.interact(actor)
	for i in range(100):await physics_frame
	paused=true
	var space:=ship.get_world_3d().direct_space_state
	var measured:Array=[]
	for ref in p.references:
		assert(FileAccess.get_sha256("res://assets/models/"+str(ref.model_file))==ref.model_sha256)
		var visual:Node3D=load("res://assets/models/"+str(ref.model_file)).instantiate();root.add_child(visual)
		var lo:=Vector3(INF,INF,INF);var hi:=Vector3(-INF,-INF,-INF);var vertices:=0
		for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
			for surface in range(mesh.mesh.get_surface_count()):
				for v:Vector3 in mesh.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]:
					var at:Vector3=mesh.global_transform*v;lo=lo.min(at);hi=hi.max(at);vertices+=1
		if lo.distance_to(vec(ref.bounds_min))>.0001 or hi.distance_to(vec(ref.bounds_max))>.0001:errors.append({"kind":"reference_import_bounds","key":ref.key,"lo":str(lo),"hi":str(hi)})
		measured.append({"key":ref.key,"dimensions_xyz_m":str(hi-lo),"imported_vertices":vertices,"status":"proposed construction reference; no canonical species rig/animation acceptance"});visual.free()
	var contacts:=0;var approaches:=0;var wet_points:=0;var dry_points:=0;var privacy_rays:=0;var closed_doors:=0;var quiet_points:=0
	for room in p.rooms:
		var home:=districts.find_child(str(room.unit_proposal_id),true,false) as Node3D
		assert(home.get_meta("rest_slot_ids")==room.rest_slot_ids and home.get_meta("proposed_design_species")==room.proposed_design_species)
		assert(not home.get_meta("species_ready") and not home.has_meta("species_assignment") and not home.get_meta("canonical_body_accepted") and not home.get_meta("environment_operations_accepted"))
		for point in room.rest_contacts_world:
			var at:=vec(point);var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.015,at-Vector3.UP*.025);q.hit_back_faces=true;var hit:=space.intersect_ray(q)
			if hit.is_empty() or absf(hit.position.y-(at.y-.005))>.002:errors.append({"kind":"measured_reference_bottom_support","room":room.source_envelope_index,"point":str(at),"hit":str(hit.get("position","none"))})
			contacts+=1
		var stance:=PhysicsShapeQueryParameters3D.new();var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8;stance.shape=capsule;stance.transform.origin=vec(room.approach_world)+Vector3.UP*.925;stance.margin=.001
		if not space.intersect_shape(stance,16).is_empty():errors.append({"kind":"player_service_approach","room":room.source_envelope_index,"point":str(stance.transform.origin)})
		approaches+=1
		if room.has("privacy_door"):
			var door:Node3D=home.get_node("CocoonPrivacyDoor");assert(door.open_fraction<.001 and door.leaves.size()==1);closed_doors+=1
			var frame:=Transform3D(Basis(Vector3.UP,room.rest_source.yaw),vec(room.rest_source.position))
			for ray in [[Vector3(0,1,-2),Vector3(0,1,-1.3)],[Vector3(-1.4,1,0),Vector3(0,1,0)],[Vector3(1.4,1,0),Vector3(0,1,0)],[Vector3(0,1,1.8),Vector3(0,1,0)],[Vector3(0,2.6,0),Vector3(0,1,0)]]:
				if space.intersect_ray(PhysicsRayQueryParameters3D.create(frame*ray[0],frame*ray[1])).is_empty():errors.append({"kind":"closed_cocoon_privacy_shell","room":room.source_envelope_index})
				privacy_rays+=1
			var query:=PhysicsPointQueryParameters3D.new();query.position=frame*Vector3(0,1,0);query.collide_with_areas=true;query.collide_with_bodies=false;query.collision_mask=512
			if space.intersect_point(query,4).is_empty():errors.append({"kind":"quiet_enclosure_detection","room":room.source_envelope_index})
			quiet_points+=1
		if room.has("wet_cells_local"):
			var wet:Area3D=fitted.get_node("ContainedWetRegion_"+str(int(room.source_envelope_index)));assert(wet.get_children().size()==room.wet_cells_local.size() and wet.collision_layer==256)
			for point in room.wet_probes_world:
				var query:=PhysicsPointQueryParameters3D.new();query.position=vec(point);query.collide_with_areas=true;query.collide_with_bodies=false;query.collision_mask=256
				if space.intersect_point(query,4).is_empty():errors.append({"kind":"actual_reference_immersed_mesh_vertex","room":room.source_envelope_index,"point":str(query.position)})
				wet_points+=1
			for local in [Vector3(0,.7,0),Vector3(0,.1,0),Vector3(1.5,.4,0),Vector3(0,.4,-2)]:
				var query:=PhysicsPointQueryParameters3D.new();query.position=wet.global_transform*local;query.collide_with_areas=true;query.collide_with_bodies=false;query.collision_mask=256
				if not space.intersect_point(query,4).is_empty():errors.append({"kind":"contained_wet_region_leak","room":room.source_envelope_index})
				dry_points+=1
		for name in room.get("remove_source_meshes",[]):assert(home.find_child(str(name),true,false)==null)
	var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");assert(residency.enabled)
	var retained:=0
	for entry in residency.entries:
		if str(entry.parent.name)=="StarAtlasRoomCandidates":retained+=1
	assert(retained==85 and p.reservation_total==8 and p.new_allocations==0)
	var controllers:Array=[];var roofs:=0;var roof_vertices:=0;var preview_probes:=0;var floor_hits:=0;var culled:=0;var care_stances:=0;var care_rays:=0
	for room in p.rooms:
		var idx:=int(room.source_envelope_index);var home:Node3D=districts.find_child(str(room.unit_proposal_id),true,false)
		assert(room.reservation_capacity==1 and room.rest_slot_ids.size()==1 and not home.get_meta("historical_save_identity_recovered"))
		for name in ["EntryDoor","WashDoor"]:
			var door:Node3D=home.get_node(name);assert(door.open_fraction<.001);controllers.append(door)
		if room.has("privacy_door"):controllers.append(home.get_node("CocoonPrivacyDoor"))
		var lane:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_SPECIALTY_"+("FIRST"if idx==443 else"SECOND")+".json"))
		var physical:Dictionary
		for candidate in lane.rooms:
			if int(candidate.allocation.source_envelope_index)==idx:physical=candidate
		assert(physical.allocation.proposed_rest_slot_ids==room.rest_slot_ids and physical.allocation.allocation_sha256==room.allocation_sha256)
		var excluded:Array[RID]=[]
		for body:StaticBody3D in home.find_children("*","StaticBody3D",true,false):excluded.append(body.get_rid())
		for contact in physical.receiving_contacts:
			var query:=PhysicsRayQueryParameters3D.create(vec(contact.position)+Vector3.UP*.025,vec(contact.position)-Vector3.UP*.025);query.exclude=excluded;query.hit_back_faces=true
			var hit:=space.intersect_ray(query)
			if hit.is_empty()or absf(hit.position.y-contact.position[1])>.003:errors.append({"kind":"persistent_source_roof","room":idx,"hit":str(hit.get("position","none"))})
			roofs+=1
			for v in contact.bottom_contact_vertices:
				query=PhysicsRayQueryParameters3D.create(vec(v)+Vector3.UP*.025,vec(v)-Vector3.UP*.025);query.exclude=excluded;query.hit_back_faces=true;hit=space.intersect_ray(query)
				if hit.is_empty()or absf(hit.position.y-v[1])>.003:errors.append({"kind":"full_toe_source_roof_vertex","room":idx})
				roof_vertices+=1
		var z:float=room.allocation_z[0]+3.6
		for x in [-84.0,-80.9,-78.8]:
			for y in [92.62,92.74]:
				var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,y+.015,z),Vector3(x,y-.015,z)))
				if not hit.is_empty():errors.append({"kind":"unrestricted_preview_height","room":idx,"position":str(hit.position)})
				preview_probes+=1
			var floor:=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,93.025,z),Vector3(x,92.975,z)))
			if floor.is_empty()or absf(floor.position.y-93)>.003:errors.append({"kind":"retained_floor_at_entry","room":idx,"x":x})
			floor_hits+=1
		for entry in residency.entries:
			if str(entry.room.name)==str(physical.below_unit.address):
				assert(not entry.room.is_inside_tree());culled+=1
		if idx==467:
			var q:=PhysicsShapeQueryParameters3D.new();var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8;q.shape=capsule;q.transform.origin=vec(room.service_stance_world)+Vector3.UP*.925;q.margin=.001
			if not space.intersect_shape(q,16).is_empty():errors.append({"kind":"new_aquatic_care_stance"})
			care_stances+=1
			for ray in [[Vector3(-75.35,93.73,54.15),Vector3(-75.35,93.73,53.7)],[Vector3(-72.55,94.1,53.8),Vector3(-72.55,94.1,54.3)]]:
				if space.intersect_ray(PhysicsRayQueryParameters3D.create(ray[0],ray[1])).is_empty():errors.append({"kind":"physical_care_shelf_or_wet_privacy"})
				care_rays+=1
	paused=false
	for door in controllers:door.interact(actor)
	for i in range(100):await physics_frame
	for door in controllers:
		if door.open_fraction<.99:errors.append({"kind":"controller_open","door":str(door.get_path())})
	for door in controllers:door.interact(actor)
	for i in range(100):await physics_frame
	for door in controllers:
		if door.open_fraction>.001:errors.append({"kind":"controller_close","door":str(door.get_path())})
	paused=true

	var report={"status":"PASS" if errors.is_empty() else "FAIL","adapted_existing_candidates":3,"unchanged_reserved_rests":3,"cumulative_specialty_candidates":30,"cumulative_reserved_rests":40,"new_allocations":0,"body_references":measured,"measured_reference_bottom_contacts":contacts,"player_approaches":approaches,"actual_reference_immersed_vertices":wet_points,"dry_containment_witnesses":dry_points,"wet_cells_per_basin":p.wet_cell_count,"source_derived_wet_volume_m3_per_basin":p.wet_volume_m3,"closed_reused_cocoon_doors":closed_doors,"privacy_shell_rays":privacy_rays,"quiet_enclosure_detections":quiet_points,"retained_original_homes":retained,"culling_enabled":residency.enabled,"canonical_species_ready_rooms":0,"persistent_roof_contacts":roofs,"full_toe_roof_vertices":roof_vertices,"unrestricted_preview_height_probes":preview_probes,"retained_floor_hits":floor_hits,"lower_interiors_culled":culled,"controller_roundtrips":controllers.size(),"aquatic_care_stances":care_stances,"care_shelf_privacy_rays":care_rays,"errors":errors,"limits":"Proposed reference rest poses and physical environments only. Canonical species/body/rig/animation, acoustic attenuation, water controls/fluid behavior, biological needs, cleaning/molting, occupants/stock/save, structural loads and final runtime visuals remain held."}
	FileAccess.open("res://artifacts/star_atlas_low_rest_adaptation.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("PASS: STAR_ATLAS_LOW_REST_ADAPTATION " if errors.is_empty() else "FAIL: STAR_ATLAS_LOW_REST_ADAPTATION ",JSON.stringify(report));quit(0 if errors.is_empty() else 1)
