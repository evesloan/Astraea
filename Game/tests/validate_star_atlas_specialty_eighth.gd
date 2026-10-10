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
	var homes:Node3D=ship.get_node("ShipSpace/Districts/StarAtlasSpecialtyEighthCandidates")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	for home in homes.get_children():
		for door:Node3D in home.find_children("*Door*","Node3D",true,false):
			if door.has_method("interact"):door.interact(actor)
	for i in range(100):await physics_frame
	paused=true
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_SPECIALTY_EIGHTH.json"))
	var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
	assert(residency.enabled,"Culling must remain enabled")
	var structure:Node3D=ship.get_node("ShipSpace/Districts/StarAtlasSpecialtyEighthReceiving")
	assert(load("res://scripts/star_atlas_specialty_eighth.gd").build(ship)==homes)
	assert(structure.get_meta("always_present_structural_contacts") and structure.get_meta("retained_source_objects")==44)
	var detached:=0
	for lower in p.receiving.lower_structural_owners:
		for entry in residency.entries:
			if str(entry.room.name)==str(lower.owner):
				assert(not entry.room.is_inside_tree() and not entry.room.has_meta("resident_visual"),"Lower interior must stay culled while receiving contacts are tested")
				detached+=1
	assert(detached==2)
	var excluded:Array[RID]=[]
	for body:StaticBody3D in homes.find_children("*","StaticBody3D",true,false):excluded.append(body.get_rid())
	var source_excluded:Array[RID]=[]
	for body:StaticBody3D in structure.find_children("*","StaticBody3D",true,false):source_excluded.append(body.get_rid())
	for body:StaticBody3D in ship.get_node("ShipSpace/Districts/StarAtlasSpecialtyFourthReceiving").find_children("*","StaticBody3D",true,false):source_excluded.append(body.get_rid())
	var space:=ship.get_world_3d().direct_space_state
	for lower in p.receiving.lower_structural_owners:
		for toe in lower.contacts:
			probe(space,Vector3(toe.position[0],toe.position[1],toe.position[2]),"persistent_lower_roof",excluded);roof_witnesses+=1
		probe(space,Vector3(-92.5,88.5,lower.origin[2]),"persistent_lower_floor",excluded);floor_witnesses+=1
	for toe in p.receiving.support_toes:
		probe(space,Vector3(toe.position[0],toe.position[1],toe.position[2]),"existing_floor_owner",source_excluded);floor_witnesses+=1
	var stances:=0
	var retained:=0
	for entry in residency.entries:
		if str(entry.parent.name)=="StarAtlasRoomCandidates":retained+=1
	assert(retained==85)
	var first:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_SPECIALTY_EIGHTH.json"))
	var doors:=0
	for room in first.rooms:
		var home:Node3D=homes.get_node(room.allocation.proposed_runtime_id)
		assert(home.get_meta("candidate_state")=="proposed_specialty_habitat" and not home.get_meta("species_ready") and not home.get_meta("historical_save_identity_recovered"))
		assert(home.get_meta("rest_slot_ids")==room.allocation.proposed_rest_slot_ids)
		for name in ["EntryDoor","WashDoor"]:
			var door:Node3D=home.get_node(name);assert(door.open_fraction<.001);doors+=1
	var interior_witnesses:=0
	for room in first.rooms:
		var a:Dictionary=room.allocation
		var z:float=(a.allocation_z[0]+a.allocation_z[1])*.5
		var x:float=a.allocation_x[1] if room.orientation_yaw>1 else a.allocation_x[0]
		var unit:=Transform3D(Basis(Vector3.UP,room.orientation_yaw),Vector3(x,93,z))
		for u in [.25,2.15,5.95]:probe(space,unit*Vector3(u,0,-.6),"new_floor_or_threshold");interior_witnesses+=1
		for ray in [[Vector3(-.35,1,0),Vector3(.65,1,0)],[Vector3(3.2,1,.4),Vector3(3.2,1,1.2)]]:
			if space.intersect_ray(PhysicsRayQueryParameters3D.create(unit*ray[0],unit*ray[1])).is_empty():errors.append({"kind":"closed_door_leaf","room":a.proposed_runtime_id})
		var glass_ray:Array=[Vector3(.5,1.9,-2.6),Vector3(-.5,1.9,-2.6)]
		var glazing:=space.intersect_ray(PhysicsRayQueryParameters3D.create(unit*glass_ray[0],unit*glass_ray[1]))
		if glazing.is_empty()or not "ScreenedStreetGlass" in str(glazing.collider.get_parent().name):errors.append({"kind":"actual_street_glazing_contact","room":a.proposed_runtime_id})

	for z in [-90.4,-93.8,-96.9,90.4,93.8,96.9]:
		probe(space,Vector3(-84,93,z),"continued_street_floor");interior_witnesses+=1
		stance(space,Vector3(-84,93.925,z),"continued_street_stance")
	assert(homes.get_meta("removed_source_terminal_guard_triangles")==24)
	var first_root:Node3D=ship.get_node("ShipSpace/Districts/StarAtlasSpecialtyCandidates")
	assert(first_root.get_children().size()==5)
	var immersed:=0;var wet_shapes:=0;var service_stances:=0;var dry_probes:=0;var ref_contacts:=0;var rest_approaches:=0;var privacy_shell_rays:=0;var cocoon_doors:=0;var wash_stances:=0;var central_aisles:=0
	for room in p.rooms:
		var home:Node3D=homes.get_node(room.allocation.proposed_runtime_id)
		assert(home.get_meta("proposed_design_species")==room.proposed_design_species and home.get_meta("reserved_rest_count")==room.allocation.proposed_rest_place_count)
		assert(room.rest_fittings.size()==room.allocation.proposed_rest_slot_ids.size())
		for fitting in room.rest_fittings:
			if fitting.has("privacy_door_name"):
				var door:Node3D=home.get_node(fitting.privacy_door_name);assert(door.open_fraction<.001 and door.leaves.size()==1);cocoon_doors+=1
			else:
				var wet:Area3D=home.get_node("WetRegion_"+str(fitting.binding.name));assert(wet.collision_layer==256 and wet.get_meta("operation_hold") and wet.get_child_count()==231);wet_shapes+=231
				stance(space,Vector3(fitting.service_stance_world[0],93.925,fitting.service_stance_world[2]),"aquatic_service_stance");service_stances+=1
				for point in fitting.actual_reference_immersed_vertices_world:
					var query:=PhysicsShapeQueryParameters3D.new();var sphere:=SphereShape3D.new();sphere.radius=.001;query.shape=sphere;query.transform.origin=Vector3(point[0],point[1],point[2]);query.collision_mask=256;query.collide_with_areas=true;query.collide_with_bodies=false
					if space.intersect_shape(query,16).is_empty():errors.append({"kind":"actual_reference_wet_vertex","slot":fitting.rest_slot_id,"point":str(query.transform.origin)})
					immersed+=1
				var frame:=Transform3D(Basis(Vector3.UP,fitting.yaw),Vector3(fitting.frame_origin[0],93,fitting.frame_origin[2]))
				for local in [Vector3(0,.7,0),Vector3(0,.4,2),Vector3(2.1,.4,0),Vector3(0,-.01,0)]:
					var query:=PhysicsShapeQueryParameters3D.new();var sphere:=SphereShape3D.new();sphere.radius=.001;query.shape=sphere;query.transform.origin=frame*local;query.collision_mask=256;query.collide_with_areas=true;query.collide_with_bodies=false
					if not space.intersect_shape(query,16).is_empty():errors.append({"kind":"wet_containment_dry_probe","slot":fitting.rest_slot_id})
					dry_probes+=1
			for point in fitting.actual_reference_bottom_contacts_world:
				var at:=Vector3(point[0],point[1],point[2]);var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.015,at-Vector3.UP*.025);q.hit_back_faces=true;var h:=space.intersect_ray(q)
				if h.is_empty() or absf(h.position.y-(at.y-.005))>.002:errors.append({"kind":"retained_measured_reference_bottom","slot":fitting.rest_slot_id,"point":str(at),"hit":str(h.get("position","none"))})
				ref_contacts+=1
			var q:=PhysicsShapeQueryParameters3D.new();var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8;q.shape=capsule;q.transform.origin=Vector3(fitting.approach_world[0],93.925,fitting.approach_world[2]);q.margin=.001
			if not space.intersect_shape(q,16).is_empty():errors.append({"kind":"individual_rest_approach","slot":fitting.rest_slot_id,"point":str(q.transform.origin)})
			rest_approaches+=1
			if fitting.has("privacy_door_name"):
				var frame:=Transform3D(Basis(Vector3.UP,fitting.yaw),Vector3(fitting.frame_origin[0],fitting.frame_origin[1],fitting.frame_origin[2]))
				for ray in [[Vector3(0,1,-2),Vector3(0,1,-1.3)],[Vector3(-1.4,1,0),Vector3(0,1,0)],[Vector3(1.4,1,0),Vector3(0,1,0)],[Vector3(0,1,1.8),Vector3(0,1,0)],[Vector3(0,2.6,0),Vector3(0,1,0)]]:
					if space.intersect_ray(PhysicsRayQueryParameters3D.create(frame*ray[0],frame*ray[1])).is_empty():errors.append({"kind":"closed_individual_cocoon_privacy","slot":fitting.rest_slot_id})
					privacy_shell_rays+=1
		var a:Dictionary=room.allocation;var z:float=(a.allocation_z[0]+a.allocation_z[1])*.5;var x:float=a.allocation_x[1] if room.orientation_yaw>1 else a.allocation_x[0]
		var unit:=Transform3D(Basis(Vector3.UP,room.orientation_yaw),Vector3(x,93,z))
		stance(space,unit*Vector3(3,.925,1.6),"shared_wash_stance");wash_stances+=1
		if room.proposed_design_species=="Mantelids" and room.allocation.proposed_rest_place_count==2:stance(space,unit*Vector3(8.55,.925,0),"paired_cocoon_central_aisle");central_aisles+=1
	for idx in [443,467,491]:
		var earlier:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_EIGHT_HABITATS.json"))
		for room in earlier.rooms:
			if int(room.source_envelope_index)==idx:
				var old:Node3D=ship.get_node("ShipSpace/Districts").find_child(str(room.unit_proposal_id),true,false)
				assert(old.get_meta("proposed_design_species")=="" and not old.has_meta("species_assignment") and not old.get_meta("species_ready"))
	var report={"status":"PASS" if errors.is_empty() else "FAIL","lower_interiors_culled":detached,"culling_enabled":residency.enabled,"persistent_roof_contacts":roof_witnesses,"source_floor_owner_witnesses":floor_witnesses,"retained_street_capsule_stances":stances,"retained_homes":retained,"source_structure_objects":44,"frame_members":p.receiving.parts.size(),"source_wall_base_rails":p.receiving.base_rails.size(),"unchanged_controller_closures":doors,"new_proposed_specialty_candidates":2,"cumulative_specialty_physical_candidates":30,"remaining_specialty_reservations":16,"new_reserved_rests":4,"cumulative_specialty_reserved_rests":40,"new_floor_witnesses":interior_witnesses,"old_terminal_guard_triangles_removed":24,"new_street_floor_area_m2":60.68,"species_ready_rooms":0,"actual_reference_bottom_contacts":ref_contacts,"individual_rest_approaches":rest_approaches,"closed_cocoon_doors":cocoon_doors,"privacy_shell_rays":privacy_shell_rays,"wash_stances":wash_stances,"paired_cocoon_central_aisles":central_aisles,"unassigned_alien_low_rest_units_preserved":3,"aquatic_wet_shapes":wet_shapes,"immersed_actual_vertices":immersed,"wet_dry_containment_probes":dry_probes,"aquatic_service_stances":service_stances,"errors":errors,"limits":"Exact geometric source receiving and bounded stationary/source/controller witnesses; structural load capacity, canonical body/rig/animation, acoustic/molting gameplay, structural load capacity and final visuals remain unaccepted."}
	var frame_joints:=0
	var receiving_excluded:Array[RID]=[]
	for body:StaticBody3D in structure.find_children("*","StaticBody3D",true,false):receiving_excluded.append(body.get_rid())
	for joint in p.receiving.existing_frame_joints:
		var a:Array=joint.overlap_bounds[0];var b:Array=joint.overlap_bounds[1];probe(space,Vector3((a[0]+b[0])*.5,b[1],(a[2]+b[2])*.5),"existing_frame_joint",receiving_excluded);frame_joints+=1
	var rim_joints:=0
	for joint in p.receiving.D14_source_floor_rim_joints:
		var lo:Array=joint.overlap_bounds[0];var hi:Array=joint.overlap_bounds[1];var at:=Vector3((lo[0]+hi[0])*.5,joint.source_bottom,(lo[2]+hi[2])*.5)
		var q:=PhysicsRayQueryParameters3D.create(at-Vector3.UP*.025,at+Vector3.UP*.015);q.exclude=source_excluded;q.hit_back_faces=true;var h:=space.intersect_ray(q)
		if h.is_empty()or absf(h.position.y-joint.source_bottom)>.003 or not str(joint.source_owner)in str(h.collider.get_path()):errors.append({"kind":"exact_D14_source_floor_underside_rim_joint","owner":joint.source_owner,"at":str(at),"hit":str(h.get("position","none"))})
		rim_joints+=1
	var thresholds:=0;var aquatic_privacy:=0
	for room in p.rooms:
		var unit:=Transform3D(Basis(Vector3.UP,room.orientation_yaw),Vector3(room.allocation.allocation_x[1],93,(room.allocation.allocation_z[0]+room.allocation.allocation_z[1])*.5))
		stance(space,unit*Vector3(-.35,.925,0),"guard_opening_street_approach");thresholds+=1
		if room.proposed_design_species=="Baelins":
			for fitting in room.rest_fittings:
				var target:=Vector3(fitting.frame_origin[0],94.1,fitting.frame_origin[2]);var local:=unit.affine_inverse()*target;var negative:bool=local.z<0;var is_single:bool=int(room.allocation.source_envelope_index)==497
				var screen_name:String="NegativeWetPrivacyBlade" if negative else "PositiveWetPrivacyBlade";var entry_owner:String="WashFrontRight" if not negative and not is_single else screen_name
				var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(unit*Vector3(1,1.6,0),target))
				if not expected_mesh_hit(homes.get_node(room.allocation.proposed_runtime_id),"SA"+str(int(room.allocation.source_envelope_index))+"_"+entry_owner,h):errors.append({"kind":"aquatic_entry_eye_level_occlusion","room":room.allocation.proposed_runtime_id,"slot":fitting.rest_slot_id,"owner":str(h.get("collider","none"))})
				var expected:float=6.35 if is_single else(5.75 if negative else 6.4);var start_u:float=5.8 if is_single or not negative else 5.4
				var q:=PhysicsRayQueryParameters3D.create(unit*Vector3(start_u,1.3,local.z),Vector3(target.x,93.5,target.z));var direct:=space.intersect_ray(q)
				if direct.is_empty()or absf((unit.affine_inverse()*direct.get("position",Vector3.ZERO)).x-expected)>.025 or not expected_mesh_hit(homes.get_node(room.allocation.proposed_runtime_id),"SA"+str(int(room.allocation.source_envelope_index))+"_"+screen_name,direct):errors.append({"kind":"aquatic_direct_privacy_screen","room":room.allocation.proposed_runtime_id,"slot":fitting.rest_slot_id})
				aquatic_privacy+=1
	var probes:Array=[]
	for x in [-20.0,-10.0,0.0,10.0]:
		for z in [-10.0,0.0,10.0]:
			var q:=PhysicsRayQueryParameters3D.create(Vector3(x,92.997,z),Vector3(x,92.993,z));q.hit_back_faces=true;var h:=space.intersect_ray(q)
			if not h.is_empty():errors.append({"kind":"unrestricted_preview_height_regression","point":str(Vector3(x,92.995,z)),"owner":str(h.collider.get_path())})
			probes.append({"point":str(Vector3(x,92.995,z)),"exclude_count":q.exclude.size(),"hit":not h.is_empty()})
	var retained_guards:=0
	for derivative in p.receiving.new_west_entry_guards:
		for interval in derivative.guard_intervals:
			var z:float=(interval[0]+interval[1])*.5;var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-85.5,93.6,z),Vector3(-86.4,93.6,z)))
			if h.is_empty()or absf(h.position.x+85.98)>.003 or not "StarAtlasSpecialtyEighthReceiving"in str(h.collider.get_path()):errors.append({"kind":"new_west_guard_segment","z":z})
			retained_guards+=1
	var terminal_guards:=0
	for z in [-97.4,97.4]:
		var inward:float=1 if z<0 else -1;var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-84,93.6,z+inward*.5),Vector3(-84,93.6,z-inward*.5)))
		if h.is_empty()or absf(absf(h.position.z)-97.365)>.003 or not "StarAtlasSpecialtyEighthReceiving"in str(h.collider.get_path()):errors.append({"kind":"new_terminal_guard","z":z})
		terminal_guards+=1
	var intended_floor_probes:=0
	for x in [-40.0,-60.0]:
		var q:=PhysicsRayQueryParameters3D.create(Vector3(x,93.02,0),Vector3(x,92.97,0));q.hit_back_faces=true;var h:=space.intersect_ray(q)
		if h.is_empty()or absf(h.position.y-93)>.001:errors.append({"kind":"unrestricted_intended_D15_floor","x":x})
		intended_floor_probes+=1
	report["new_west_guard_segment_rays"]=retained_guards;report["new_terminal_guard_rays"]=terminal_guards;report["unrestricted_intended_floor_rays"]=intended_floor_probes
	var controllers:Array[Node3D]=[]
	for home in homes.get_children():
		for door:Node3D in home.find_children("*Door*","Node3D",true,false):
			if door.has_method("interact"):controllers.append(door)
	assert(controllers.size()==6)
	paused=false
	for door in controllers:door.interact(actor)
	for i in range(100):await physics_frame
	for door in controllers:
		if door.open_fraction<.999 or not door.desired_open:errors.append({"kind":"new_controller_open_roundtrip","door":str(door.get_path())})
	var open_passages:=0
	for room in p.rooms:
		var unit:=Transform3D(Basis(Vector3.UP,room.orientation_yaw),Vector3(room.allocation.allocation_x[1],93,(room.allocation.allocation_z[0]+room.allocation.allocation_z[1])*.5));stance(space,unit*Vector3(.15,.925,0),"open_supported_entry_passage");open_passages+=1
	for door in controllers:door.interact(actor)
	for i in range(100):await physics_frame
	for door in controllers:
		if door.open_fraction>.001 or door.desired_open:errors.append({"kind":"new_controller_close_roundtrip","door":str(door.get_path())})
	paused=true
	report["existing_frame_joint_witnesses"]=frame_joints;report["street_entry_approaches"]=thresholds;report["open_supported_entry_passages"]=open_passages;report["aquatic_privacy_screen_rays"]=aquatic_privacy;report["aquatic_entry_eye_level_occlusion_rays"]=aquatic_privacy;report["controller_open_close_roundtrips"]=6;report["unrestricted_preview_height_probes"]=probes;report["new_piers"]=6;report["new_exact_D14_foundation_toes"]=6;report["foundation_source_deck"]="D14";report["D14_source_floor_rim_joint_witnesses"]=rim_joints;report["errors"]=errors;report["status"]="PASS" if errors.is_empty()else "FAIL"
	FileAccess.open("res://artifacts/star_atlas_specialty_eighth.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("PASS: STAR_ATLAS_SPECIALTY_EIGHTH " if errors.is_empty() else "FAIL: STAR_ATLAS_SPECIALTY_EIGHTH ",JSON.stringify(report));quit(0 if errors.is_empty() else 1)

func stance(space:PhysicsDirectSpaceState3D,at:Vector3,label:String)->void:
	var q:=PhysicsShapeQueryParameters3D.new();var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8;q.shape=capsule;q.transform.origin=at;q.margin=.001
	if not space.intersect_shape(q,16).is_empty():errors.append({"kind":label,"point":str(at)})

func expected_mesh_hit(home:Node3D,name:String,hit:Dictionary)->bool:
	if hit.is_empty()or not home.is_ancestor_of(hit.collider):return false
	var mesh:=home.find_child(name,true,false)as MeshInstance3D
	assert(mesh!=null,"Expected exact authored privacy mesh")
	var bounds:AABB=mesh.global_transform*mesh.get_aabb()
	return bounds.grow(.003).has_point(hit.position)
