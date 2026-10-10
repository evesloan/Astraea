extends SceneTree
var errors:Array=[]
var floor_witnesses:=0
var roof_witnesses:=0
func _initialize()->void:call_deferred("run")
func probe(space:PhysicsDirectSpaceState3D,p:Vector3,label:String,excluded:Array[RID]=[])->void:
	var q:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.025,p-Vector3.UP*.025);q.exclude=excluded;q.hit_back_faces=true
	var h:=space.intersect_ray(q)
	if h.is_empty() or absf(h.position.y-p.y)>.003:errors.append({"kind":label,"point":str(p),"hit":str(h.get("position","none"))})
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var homes:Node3D=ship.get_node("ShipSpace/Districts/StarAtlasSpecialtyThirdCandidates")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	for home in homes.get_children():
		for door:Node3D in home.find_children("*Door*","Node3D",true,false):
			if door.has_method("interact"):door.interact(actor)
	for i in range(100):await physics_frame
	paused=true
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_SPECIALTY_THIRD.json"))
	var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
	assert(residency.enabled,"Culling must remain enabled")
	var structure:Node3D=ship.get_node("ShipSpace/Districts/StarAtlasSpecialtyThirdReceiving")
	assert(load("res://scripts/star_atlas_specialty_third.gd").build(ship)==homes)
	assert(structure.get_meta("always_present_structural_contacts") and structure.get_meta("retained_source_objects")==88)
	var detached:=0
	for lower in p.receiving.lower_structural_owners:
		for entry in residency.entries:
			if str(entry.room.name)==str(lower.owner):
				assert(not entry.room.is_inside_tree() and not entry.room.has_meta("resident_visual"),"Lower interior must stay culled while receiving contacts are tested")
				detached+=1
	assert(detached==4)
	var excluded:Array[RID]=[]
	for body:StaticBody3D in homes.find_children("*","StaticBody3D",true,false):excluded.append(body.get_rid())
	var source_excluded:Array[RID]=[]
	for body:StaticBody3D in structure.find_children("*","StaticBody3D",true,false):source_excluded.append(body.get_rid())
	var space:=ship.get_world_3d().direct_space_state
	for lower in p.receiving.lower_structural_owners:
		for toe in lower.contacts:
			probe(space,Vector3(toe.position[0],toe.position[1],toe.position[2]),"persistent_lower_roof",excluded);roof_witnesses+=1
		probe(space,Vector3(-78,88.5,lower.origin[2]),"persistent_lower_floor",excluded);floor_witnesses+=1
	for toe in p.receiving.support_toes:
		probe(space,Vector3(toe.position[0],toe.position[1],toe.position[2]),"existing_floor_owner",source_excluded);floor_witnesses+=1
	var stances:=0
	for y in [88.5]:
		for z in [-71.6,-79.0,71.6,79.0]:
			probe(space,Vector3(-84,y,z),"retained_street_floor",source_excluded);floor_witnesses+=1
			var q:=PhysicsShapeQueryParameters3D.new();var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8;q.shape=capsule;q.transform.origin=Vector3(-84,y+.925,z);q.margin=.001
			if not space.intersect_shape(q,16).is_empty():errors.append({"kind":"retained_street_stance","point":str(q.transform.origin)})
			stances+=1
	var retained:=0
	for entry in residency.entries:
		if str(entry.parent.name)=="StarAtlasRoomCandidates":retained+=1
	assert(retained==85)
	var first:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_SPECIALTY_THIRD.json"))
	var doors:=0
	for room in first.rooms:
		var home:Node3D=homes.get_node(room.allocation.proposed_runtime_id)
		assert(home.get_meta("candidate_state")=="proposed_mantelid_quiet_cocoon" and not home.get_meta("species_ready") and not home.get_meta("historical_save_identity_recovered"))
		assert(home.get_meta("rest_slot_ids")==room.allocation.proposed_rest_slot_ids)
		for name in ["EntryDoor","WashDoor"]:
			var door:Node3D=home.get_node(name);assert(door.open_fraction<.001);doors+=1
	var interior_witnesses:=0
	for room in first.rooms:
		var z:float=(room.allocation.allocation_z[0]+room.allocation.allocation_z[1])*.5
		for x in [-83.2,-81.7,-79.8,-76.0]:probe(space,Vector3(x,93,z-.6),"new_floor_or_threshold");interior_witnesses+=1
		for d in room.doors:
			var a:Vector3;var b:Vector3
			if d.name=="EntryDoor":a=Vector3(-82.3,94,z);b=Vector3(-81.3,94,z)
			else:a=Vector3(-78.75,94,z+.4);b=Vector3(-78.75,94,z+1.2)
			if space.intersect_ray(PhysicsRayQueryParameters3D.create(a,b)).is_empty():errors.append({"kind":"closed_door_leaf","room":room.allocation.proposed_runtime_id,"name":d.name})
		var glass:=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-70.5,94.95,z),Vector3(-68.6,94.95,z)))
		if glass.is_empty():errors.append({"kind":"new_oval_glass","room":room.allocation.proposed_runtime_id})
	for z in [-67.8,-67.9,-71.6,-75.3,-79.0,-82.2,67.8,67.9,71.6,75.3,79.0,82.2]:
		probe(space,Vector3(-84,93,z),"continued_street_floor");interior_witnesses+=1
		var q:=PhysicsShapeQueryParameters3D.new();var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8;q.shape=capsule;q.transform.origin=Vector3(-84,93.925,z);q.margin=.001
		if not space.intersect_shape(q,16).is_empty():errors.append({"kind":"continued_street_stance","point":str(q.transform.origin)})
	assert(homes.get_meta("removed_source_terminal_guard_triangles")==24)
	var first_root:Node3D=ship.get_node("ShipSpace/Districts/StarAtlasSpecialtyCandidates")
	assert(first_root.get_children().size()==5)
	var ref_contacts:=0;var rest_approaches:=0;var privacy_shell_rays:=0;var cocoon_doors:=0;var wash_stances:=0;var central_aisles:=0
	for room in p.rooms:
		var home:Node3D=homes.get_node(room.allocation.proposed_runtime_id)
		assert(home.get_meta("proposed_design_species")=="Mantelids" and home.get_meta("reserved_rest_count")==room.allocation.proposed_rest_place_count)
		assert(room.rest_fittings.size()==room.allocation.proposed_rest_slot_ids.size())
		for fitting in room.rest_fittings:
			var door:Node3D=home.get_node(fitting.privacy_door_name);assert(door.open_fraction<.001 and door.leaves.size()==1);cocoon_doors+=1
			for point in fitting.actual_reference_bottom_contacts_world:
				var at:=Vector3(point[0],point[1],point[2]);var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.015,at-Vector3.UP*.025);q.hit_back_faces=true;var h:=space.intersect_ray(q)
				if h.is_empty() or absf(h.position.y-(at.y-.005))>.002:errors.append({"kind":"retained_measured_reference_bottom","slot":fitting.rest_slot_id,"point":str(at),"hit":str(h.get("position","none"))})
				ref_contacts+=1
			var q:=PhysicsShapeQueryParameters3D.new();var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8;q.shape=capsule;q.transform.origin=Vector3(fitting.approach_world[0],93.925,fitting.approach_world[2]);q.margin=.001
			if not space.intersect_shape(q,16).is_empty():errors.append({"kind":"individual_rest_approach","slot":fitting.rest_slot_id,"point":str(q.transform.origin)})
			rest_approaches+=1
			var frame:=Transform3D(Basis(Vector3.UP,fitting.yaw),Vector3(fitting.frame_origin[0],fitting.frame_origin[1],fitting.frame_origin[2]))
			for ray in [[Vector3(0,1,-2),Vector3(0,1,-1.3)],[Vector3(-1.4,1,0),Vector3(0,1,0)],[Vector3(1.4,1,0),Vector3(0,1,0)],[Vector3(0,1,1.8),Vector3(0,1,0)],[Vector3(0,2.6,0),Vector3(0,1,0)]]:
				if space.intersect_ray(PhysicsRayQueryParameters3D.create(frame*ray[0],frame*ray[1])).is_empty():errors.append({"kind":"closed_individual_cocoon_privacy","slot":fitting.rest_slot_id})
				privacy_shell_rays+=1
		var z:float=(room.allocation.allocation_z[0]+room.allocation.allocation_z[1])*.5
		var q:=PhysicsShapeQueryParameters3D.new();var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8;q.shape=capsule;q.transform.origin=Vector3(-78.95,93.925,z+1.6);q.margin=.001
		if not space.intersect_shape(q,16).is_empty():errors.append({"kind":"shared_wash_stance","room":room.allocation.proposed_runtime_id})
		wash_stances+=1
		if room.allocation.proposed_rest_place_count==2:
			q.transform.origin=Vector3(-73.4,93.925,z)
			if not space.intersect_shape(q,16).is_empty():errors.append({"kind":"paired_cocoon_central_aisle","room":room.allocation.proposed_runtime_id})
			central_aisles+=1
	for idx in [443,467,491]:
		var earlier:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_EIGHT_HABITATS.json"))
		for room in earlier.rooms:
			if int(room.source_envelope_index)==idx:
				var old:Node3D=ship.get_node("ShipSpace/Districts").find_child(str(room.unit_proposal_id),true,false)
				assert(old.get_meta("proposed_design_species")=="" and not old.has_meta("species_assignment") and not old.get_meta("species_ready"))
	var report={"status":"PASS" if errors.is_empty() else "FAIL","lower_interiors_culled":detached,"culling_enabled":residency.enabled,"persistent_roof_contacts":roof_witnesses,"source_floor_owner_witnesses":floor_witnesses,"retained_street_capsule_stances":stances,"retained_homes":retained,"source_structure_objects":88,"frame_members":p.receiving.parts.size(),"source_wall_base_rails":p.receiving.base_rails.size(),"unchanged_controller_closures":doors,"affected_existing_third_batch_rooms":4,"cumulative_specialty_physical_candidates":16,"remaining_specialty_reservations":30,"affected_existing_reserved_rests":6,"cumulative_specialty_reserved_rests":22,"new_floor_witnesses":interior_witnesses,"old_terminal_guard_triangles_removed":24,"new_street_floor_area_m2":121.36,"species_ready_rooms":0,"actual_reference_bottom_contacts":ref_contacts,"individual_rest_approaches":rest_approaches,"closed_cocoon_doors":cocoon_doors,"privacy_shell_rays":privacy_shell_rays,"wash_stances":wash_stances,"paired_cocoon_central_aisles":central_aisles,"unassigned_alien_low_rest_units_preserved":3,"errors":errors,"limits":"Exact geometric source receiving and bounded stationary/source/controller witnesses; structural load capacity, canonical body/rig/animation, acoustic/molting gameplay, structural load capacity and final visuals remain unaccepted."}
	var phase:=OS.get_cmdline_user_args()[0] if not OS.get_cmdline_user_args().is_empty() else "before"
	var preview_meshes:=0
	for mesh:MeshInstance3D in homes.find_children("*","MeshInstance3D",true,false):
		if "Preview_Ground" in str(mesh.name):preview_meshes+=1
	var third_bodies:Array[RID]=[]
	for body:StaticBody3D in homes.find_children("*","StaticBody3D",true,false):third_bodies.append(body.get_rid())
	var isolate:Array[RID]=[]
	for body:CollisionObject3D in main.find_children("*","CollisionObject3D",true,false):
		if not body.get_rid() in third_bodies:isolate.append(body.get_rid())
	var phantom_probes:Array=[]
	for x in [-20.0,-40.0,-60.0]:
		var q:=PhysicsRayQueryParameters3D.create(Vector3(x,93.02,0),Vector3(x,92.97,0));q.exclude=isolate;q.hit_back_faces=true
		var hit:=space.intersect_ray(q);var expected:bool=phase=="before"
		if (not hit.is_empty())!=expected:errors.append({"kind":"isolated_third_batch_phantom_floor","phase":phase,"x":x})
		var allq:=PhysicsRayQueryParameters3D.create(Vector3(x,93.02,0),Vector3(x,92.97,0));allq.hit_back_faces=true;var unrestricted:=space.intersect_ray(allq)
		phantom_probes.append({"point":str(Vector3(x,92.995,0)),"outside_third_room_allocations":true,"isolated_third_batch_hit":not hit.is_empty(),"isolated_hit_y":hit.get("position",Vector3.ZERO).y,"unrestricted_world_hit":not unrestricted.is_empty(),"unrestricted_collider_path":str(unrestricted.collider.get_path()) if not unrestricted.is_empty() else "none","unrestricted_hit_y":unrestricted.get("position",Vector3.ZERO).y})
	assert(preview_meshes==(6 if phase=="before" else 0))
	report["phase"]=phase;report["runtime_preview_ground_meshes"]=preview_meshes;report["phantom_floor_probes"]=phantom_probes;report["errors"]=errors;report["status"]="PASS" if errors.is_empty() else "FAIL"
	if phase=="after":
		var controllers:Array[Node3D]=[]
		for home in homes.get_children():
			for door:Node3D in home.find_children("*Door*","Node3D",true,false):
				if door.has_method("interact"):controllers.append(door)
		assert(controllers.size()==14)
		paused=false
		for door in controllers:door.interact(actor)
		for i in range(100):await physics_frame
		var openings:=0
		for door in controllers:
			if door.open_fraction<.999 or not door.desired_open:errors.append({"kind":"retained_controller_open_roundtrip","door":str(door.get_path())})
			else:openings+=1
		for door in controllers:door.interact(actor)
		for i in range(100):await physics_frame
		var closures:=0
		for door in controllers:
			if door.open_fraction>.001 or door.desired_open:errors.append({"kind":"retained_controller_close_roundtrip","door":str(door.get_path())})
			else:closures+=1
		paused=true
		var fourth:Node3D=ship.get_node("ShipSpace/Districts/StarAtlasSpecialtyFourthCandidates")
		assert(fourth.get_child_count()==4)
		for mesh:MeshInstance3D in fourth.find_children("*","MeshInstance3D",true,false):assert(not "Preview_Ground" in str(mesh.name))
		report["retained_controller_open_roundtrips"]=openings;report["retained_controller_close_roundtrips"]=closures;report["fourth_live_candidates_retained"]=4;report["fourth_runtime_preview_ground_meshes"]=0
		report["errors"]=errors;report["status"]="PASS" if errors.is_empty() else "FAIL"
	FileAccess.open("res://artifacts/star_atlas_preview_ground_correction_"+phase+".json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("PASS: PREVIEW_GROUND_CORRECTION " if errors.is_empty() else "FAIL: PREVIEW_GROUND_CORRECTION ",JSON.stringify(report));quit(0 if errors.is_empty() else 1)
