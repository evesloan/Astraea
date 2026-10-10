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
	var homes:Node3D=ship.get_node("ShipSpace/Districts/StarAtlasSpecialtyCandidates")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	for home in homes.get_children():
		for door:Node3D in home.find_children("*Door","Node3D",true,false):
			if door.has_method("interact"):door.interact(actor)
	for i in range(100):await physics_frame
	paused=true
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_SPECIALTY_STRUCTURAL_RECEIVING.json"))
	var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
	assert(residency.enabled,"Culling must remain enabled")
	var structure:Node3D=ship.get_node("ShipSpace/Districts/StarAtlasSpecialtyStructuralReceiving")
	assert(load("res://scripts/star_atlas_specialty_structural_receiving.gd").build(ship)==structure)
	assert(structure.get_meta("always_present_structural_contacts") and structure.get_meta("retained_source_objects")==88)
	var detached:=0
	for lower in p.lower_structural_owners:
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
	for lower in p.lower_structural_owners:
		for toe in lower.contacts:
			probe(space,Vector3(toe.position[0],toe.position[1],toe.position[2]),"persistent_lower_roof",excluded);roof_witnesses+=1
		probe(space,Vector3(-78,88.5,lower.origin[2]),"persistent_lower_floor",excluded);floor_witnesses+=1
	for toe in p.support_toes:
		probe(space,Vector3(toe.position[0],toe.position[1],toe.position[2]),"existing_floor_owner",source_excluded);floor_witnesses+=1
	var stances:=0
	for y in [84.0,88.5]:
		for z in [-42.0,-49.4,42.0,49.4]:
			probe(space,Vector3(-84,y,z),"retained_street_floor",source_excluded);floor_witnesses+=1
			var q:=PhysicsShapeQueryParameters3D.new();var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8;q.shape=capsule;q.transform.origin=Vector3(-84,y+.925,z);q.margin=.001
			if not space.intersect_shape(q,16).is_empty():errors.append({"kind":"retained_street_stance","point":str(q.transform.origin)})
			stances+=1
	var retained:=0
	for entry in residency.entries:
		if str(entry.parent.name)=="StarAtlasRoomCandidates":retained+=1
	assert(retained==85)
	var first:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_SPECIALTY_FIRST.json"))
	var doors:=0
	for room in first.rooms:
		var home:Node3D=homes.get_node(room.allocation.proposed_runtime_id)
		assert(home.get_meta("candidate_state")=="unassigned_environment_candidate" and not home.get_meta("species_ready") and not home.get_meta("historical_save_identity_recovered"))
		assert(home.get_meta("rest_slot_ids")==room.allocation.proposed_rest_slot_ids)
		for name in ["EntryDoor","WashDoor"]:
			var door:Node3D=home.get_node(name);assert(door.open_fraction<.001);doors+=1
	var report={"status":"PASS" if errors.is_empty() else "FAIL","lower_interiors_culled":detached,"culling_enabled":residency.enabled,"persistent_roof_contacts":roof_witnesses,"source_floor_owner_witnesses":floor_witnesses,"retained_street_capsule_stances":stances,"retained_homes":retained,"source_structure_objects":88,"frame_members":p.parts.size(),"source_wall_base_rails":p.base_rails.size(),"unchanged_controller_closures":doors,"unassigned_candidates":4,"species_ready_rooms":0,"errors":errors,"limits":"Exact geometric source receiving and bounded stationary/source/controller witnesses; structural load capacity, habitat compatibility, operations and final visuals remain unaccepted."}
	FileAccess.open("res://artifacts/star_atlas_specialty_structural_receiving.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("PASS: STAR_ATLAS_STRUCTURAL_RECEIVING " if errors.is_empty() else "FAIL: STAR_ATLAS_STRUCTURAL_RECEIVING ",JSON.stringify(report));quit(0 if errors.is_empty() else 1)
