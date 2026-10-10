extends SceneTree
var errors:Array=[]
func _initialize()->void:call_deferred("run")
func vec(v:Array)->Vector3:return Vector3(v[0],v[1],v[2])
func stance(space:PhysicsDirectSpaceState3D,at:Vector3,label:String)->void:
	var q:=PhysicsShapeQueryParameters3D.new();var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8;q.shape=capsule;q.transform.origin=at+Vector3.UP*.925;q.margin=.001
	if not space.intersect_shape(q,16).is_empty():errors.append({"kind":label,"point":str(at)})
func floor_probe(space:PhysicsDirectSpaceState3D,at:Vector3,label:String,exclude:Array[RID]=[],owner:Node3D=null)->void:
	var q:=PhysicsRayQueryParameters3D.create(at-Vector3.UP*.025,at+Vector3.UP*.025)if owner!=null else PhysicsRayQueryParameters3D.create(at+Vector3.UP*.025,at-Vector3.UP*.025);q.exclude=exclude;q.hit_back_faces=true;var hit:=space.intersect_ray(q)
	if hit.is_empty()or absf(hit.position.y-at.y)>.003 or(owner!=null and not owner.is_ancestor_of(hit.collider)):errors.append({"kind":label,"point":str(at),"hit":str(hit.get("position","none"))})
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var districts:Node3D=ship.get_node("ShipSpace/Districts");var homes:Node3D=districts.get_node("StarAtlasSpecialtyEleventhCandidates")
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_SPECIALTY_ELEVENTH.json"));var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var controllers:Array=[]
	assert(load("res://scripts/star_atlas_specialty_eleventh.gd").build(ship)==homes and homes.get_meta("removed_source_guard_count")==0 and homes.get_meta("removed_previous_guard_mesh_count")==2)
	for room in p.rooms:
		var home:Node3D=homes.get_node(room.allocation.proposed_runtime_id)
		for d in room.doors:
			var door:Node3D=home.get_node(d.name);controllers.append(door)
			if door.desired_open:door.interact(actor)
	for i in range(100):await physics_frame
	paused=true
	var space:=ship.get_world_3d().direct_space_state;var supports:=0;var contacts:=0;var privacy:=0;var glazing:=0;var stances:=0;var floors:=0;var previews:Array=[];var guards:=0;var frame_joints:=0;var raker_contacts:=0;var brace_contacts:=0
	var excluded:Array[RID]=[]
	for group in [homes,districts.get_node("StarAtlasSpecialtyEleventhReceiving")]:
		for body:StaticBody3D in group.find_children("*","StaticBody3D",true,false):excluded.append(body.get_rid())
	for joint in p.receiving.slab_joints:
		var lo:=vec(joint.overlap_bounds[0]);var hi:=vec(joint.overlap_bounds[1]);var center:Vector3=(lo+hi)*.5;center.y=joint.source_bottom;floor_probe(space,center,"retained_source_slab_underside",excluded,ship.get_node("ShipSpace/CentralResidentialStreetFloors/"+str(joint.owner)));supports+=1
		for x in [lo.x+.001,hi.x-.001]:
			for z in [lo.z+.001,hi.z-.001]:floor_probe(space,Vector3(x,joint.source_bottom,z),"retained_slab_inset_corner",excluded,ship.get_node("ShipSpace/CentralResidentialStreetFloors/"+str(joint.owner)));supports+=1
	var previous:Node3D=districts.get_node("StarAtlasSpecialtyTenthReceiving")
	for name in ["SA_D13_TenthNorthTerminalGuard","SA_D13_TenthSouthTerminalGuard"]:assert(previous.find_child(name,true,false)==null)
	var preceding:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_SPECIALTY_TENTH.json"));var previous_parts:=0
	for part in preceding.receiving.parts:
		if str(part.name)in p.receiving.removed_previous_guard_meshes:continue
		assert(previous.find_child(str(part.name),true,false)!=null);previous_parts+=1
	assert(previous_parts==58)
	for joint in p.receiving.existing_frame_joints:
		var lo:=vec(joint.overlap_bounds[0]);var hi:=vec(joint.overlap_bounds[1]);var at:Vector3=(lo+hi)*.5;at.y=hi.y
		var witnesses:Array[Vector3]=[at]
		for x in [lo.x+.001,hi.x-.001]:
			for z in [lo.z+.001,hi.z-.001]:witnesses.append(Vector3(x,hi.y,z))
		for point in witnesses:
			var q:=PhysicsRayQueryParameters3D.create(point+Vector3.UP*.025,point-Vector3.UP*.025);q.exclude=excluded;var hit:=space.intersect_ray(q)
			if not expected_mesh_hit(previous,str(joint.existing_mesh),hit)or absf(hit.position.y-hi.y)>.003:errors.append({"kind":"previous_frame_overlap","mesh":joint.existing_mesh,"point":str(point)})
			frame_joints+=1

	var new_frame:Node3D=districts.get_node("StarAtlasSpecialtyEleventhReceiving")
	for raker in p.receiving.rakers:
		var at:Vector3=(vec(raker.anchor_center)+vec(raker.tip_center))*.5
		var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.15,at-Vector3.UP*.15))
		if not expected_mesh_hit(new_frame,str(raker.name),hit):errors.append({"kind":"actual_diagonal_raker","mesh":raker.name})
		raker_contacts+=1
	for brace in p.receiving.room_plan_braces:
		var at:Vector3=(vec(brace.start)+vec(brace.end))*.5
		var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.08,at-Vector3.UP*.08))
		if not expected_mesh_hit(new_frame,str(brace.name),hit):errors.append({"kind":"actual_floor_plan_brace","mesh":brace.name})
		brace_contacts+=1

	for room in p.rooms:
		var home:Node3D=homes.get_node(room.allocation.proposed_runtime_id);var a:Dictionary=room.allocation;var z:float=(a.allocation_z[0]+a.allocation_z[1])*.5
		assert(a.proposed_rest_place_count==1 and a.proposed_rest_slot_ids.size()==1 and home.get_meta("rest_slot_ids")==a.proposed_rest_slot_ids and home.get_meta("allocation_sha256")==a.allocation_sha256)
		assert(home.get_meta("proposed_design_species")=="Mantelids"and not home.get_meta("species_ready")and not home.get_meta("historical_save_identity_recovered"))
		var unit:=Transform3D(Basis(Vector3.UP,room.orientation_yaw),Vector3(a.allocation_x[1]if room.orientation_yaw>1 else a.allocation_x[0],84,z))
		for u in [1.0,2.1,5.8]:
			floor_probe(space,unit*Vector3(u,0,-.4),"intended_room_floor");floors+=1;stance(space,unit*Vector3(u,0,-.4),"arrival_aisle");stances+=1
		for f in room.rest_fittings:
			stance(space,vec(f.approach_world),"rest_approach");stances+=1
			for point in f.actual_reference_bottom_contacts_world:floor_probe(space,vec(point)-Vector3.UP*.005,"actual_reference_rest_support");contacts+=1
			var frame:=Transform3D(Basis(Vector3.UP,f.yaw),vec(f.frame_origin))
			for ray in [[Vector3(0,1,-2),Vector3(0,1,-1.3)],[Vector3(-1.4,1,0),Vector3(0,1,0)],[Vector3(1.4,1,0),Vector3(0,1,0)],[Vector3(0,1,1.8),Vector3(0,1,0)],[Vector3(0,2.6,0),Vector3(0,1,0)]]:
				if space.intersect_ray(PhysicsRayQueryParameters3D.create(frame*ray[0],frame*ray[1])).is_empty():errors.append({"kind":"closed_quiet_shell","room":a.source_envelope_index})
				privacy+=1
		var glass_ray:Array=[Vector3(12.5,1.95,0),Vector3(13.05,1.95,0)]if room.orientation_yaw<1 else[Vector3(.4,1.9,-2.6),Vector3(-.3,1.9,-2.6)]
		var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(unit*glass_ray[0],unit*glass_ray[1]))
		if hit.is_empty():errors.append({"kind":"actual_glazing","room":a.source_envelope_index})
		glazing+=1
		for x in [-84.0,unit.origin.x+(-.6 if room.orientation_yaw>1 else .6),unit.origin.x+(-2.0 if room.orientation_yaw>1 else 2.0)]:
			for y in [83.3,83.5]:
				var at:=Vector3(x,y,z);var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.015,at-Vector3.UP*.015));previews.append({"point":str(at),"hit":not h.is_empty(),"exclude_count":0})
				if not h.is_empty():errors.append({"kind":"unrestricted_preview_height","point":str(at)})
	for z in [-89.5,-86.4,-83.4,-82.7,82.7,83.4,86.4,89.5]:floor_probe(space,Vector3(-84,84,z),"supported_shared_street");floors+=1;stance(space,Vector3(-84,84,z),"shared_street_capsule");stances+=1
	var guards_root:Node3D=ship.get_node("ShipSpace/CentralResidentialStreetFloors/CentralResidentialStreetGuards");var original:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/CENTRAL_RESIDENTIAL_STREETS.json"));var old_retained:=0
	for e in original.exposed_edge_guards:
		if str(e.id)in["D13_STAR_ATLAS_MISSING_STREET_0_Guard_5","D13_STAR_ATLAS_MISSING_STREET_0_Guard_6","D13_STAR_ATLAS_MISSING_STREET_3_Guard_23"]:assert(not guards_root.has_node(str(e.id)+"Contact"))
		else:assert(guards_root.has_node(str(e.id)+"Contact"));old_retained+=1
	for z in [-89.5,-83.3,83.3,89.5]:
		for x in [-86.05,-81.95]:
			if space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x-.2,84.8,z),Vector3(x+.2,84.8,z))).is_empty():errors.append({"kind":"new_street_guard"})
			guards+=1
	if space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-82.15,84.8,86.4),Vector3(-81.75,84.8,86.4))).is_empty():errors.append({"kind":"unallocated_east_side_guard"})
	guards+=1
	for sign in [-1,1]:
		if space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-84,84.8,sign*89.8),Vector3(-84,84.8,sign*90.2))).is_empty():errors.append({"kind":"terminal_guard"})
		guards+=1

	var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");assert(residency.enabled);var retained:=0
	for entry in residency.entries:
		if str(entry.parent.name)=="StarAtlasRoomCandidates":retained+=1
	assert(retained==85)
	for door in controllers:assert(door.open_fraction<.001)
	paused=false
	for door in controllers:door.interact(actor)
	for i in range(100):await physics_frame
	var passages:=0
	for door in controllers:
		if door.open_fraction<.99:errors.append({"kind":"controller_open","door":str(door.get_path())})
	for room in p.rooms:
		var a:Dictionary=room.allocation;var z:float=(a.allocation_z[0]+a.allocation_z[1])*.5;var x:float=a.allocation_x[1]if room.orientation_yaw>1 else a.allocation_x[0];stance(space,Vector3(x+(-.12 if room.orientation_yaw>1 else .12),84,z),"open_entry_passage");passages+=1
	for door in controllers:door.interact(actor)
	for i in range(100):await physics_frame
	for door in controllers:
		if door.open_fraction>.001:errors.append({"kind":"controller_close","door":str(door.get_path())})
	var report={"status":"PASS"if errors.is_empty()else"FAIL","new_physical_candidates":3,"existing_reserved_rests":3,"cumulative_specialty_candidates":40,"cumulative_reserved_rests":50,"remaining_specialty_reservations":6,"new_allocations":0,"previous_frame_overlap_witnesses":frame_joints,"previous_receiving_parts_retained":previous_parts,"actual_diagonal_raker_contacts":raker_contacts,"actual_room_plan_brace_contacts":brace_contacts,"source_slab_overlap_witnesses":supports,"slab_corner_probe_inset_m":.001,"measured_reference_bottom_contacts":contacts,"capsule_stances":stances,"intended_floor_hits":floors,"privacy_shell_rays":privacy,"actual_glazing_rays":glazing,"unrestricted_preview_height_probes":previews,"guard_rays":guards,"unmodified_original_guards_retained":old_retained,"controller_roundtrips":controllers.size(),"open_entry_passages":passages,"retained_original_homes":retained,"culling_enabled":residency.enabled,"species_ready_rooms":0,"errors":errors,"limits":"Source-connected D13 slab/frame geometric witnesses; primary engineering capacity, canonical bodies/rig/poses/acoustics/molting/privacy/save/stock and final ordinary Godot/CRT/hardware visual acceptance held"}
	FileAccess.open("res://artifacts/star_atlas_specialty_eleventh.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("PASS: STAR_ATLAS_SPECIALTY_ELEVENTH "if errors.is_empty()else"FAIL: STAR_ATLAS_SPECIALTY_ELEVENTH ",JSON.stringify(report));quit(0 if errors.is_empty()else 1)

func expected_mesh_hit(home:Node3D,name:String,hit:Dictionary)->bool:
	if hit.is_empty()or not home.is_ancestor_of(hit.collider):return false
	var mesh:=home.find_child(name,true,false)as MeshInstance3D
	assert(mesh!=null,"Expected exact authored receiving mesh")
	var bounds:AABB=mesh.global_transform*mesh.get_aabb()
	return bounds.grow(.003).has_point(hit.position)
