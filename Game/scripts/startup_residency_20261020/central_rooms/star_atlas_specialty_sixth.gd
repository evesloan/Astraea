extends RefCounted
static func build(ship:Node3D)->Node3D:
	var districts:Node3D=ship.get_node("ShipSpace/Districts")
	if districts.has_node("StarAtlasSpecialtySixthCandidates"):return districts.get_node("StarAtlasSpecialtySixthCandidates")
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_SPECIALTY_SIXTH.json"))
	assert(FileAccess.get_sha256("res://assets/models/StarAtlasSpecialtySecondReceiving.glb")==p.receiving.receiving_model_preimage_sha256)
	var first:Node3D=districts.get_node("StarAtlasSpecialtySecondReceiving")
	var old_visual:Node3D
	var removed_triangles:=0
	for name in p.receiving.removed_terminal_guard_names:
		var guard:=first.find_child(str(name),true,false) as MeshInstance3D
		assert(guard!=null)
		if old_visual==null:old_visual=guard.get_parent()
		assert(guard.get_parent()==old_visual)
		removed_triangles+=guard.mesh.get_faces().size()/3
		guard.free()
	assert(removed_triangles==24)
	old_visual.get_node("RoomStaticContacts").free()
	var old_solids:Array[Node]=[]
	for mesh:MeshInstance3D in old_visual.find_children("*","MeshInstance3D",true,false):
		if bool(mesh.get_meta("extras",{}).get("runtime_collision",false)):old_solids.append(mesh)
	load("res://scripts/static_contact_cache.gd").attach_group(old_visual,old_solids)
	var root:=Node3D.new();root.name="StarAtlasSpecialtySixthCandidates";districts.add_child(root)
	root.set_meta("removed_source_west_guard_triangles",removed_triangles);root.set_meta("new_allocations",0);root.set_meta("species_ready_rooms",0)
	var helper:Script=load("res://scripts/startup_residency_20261020/central_private_visual.gd")
	for room in p.rooms:
		assert(FileAccess.get_sha256("res://assets/models/"+str(room.model_file))==room.model_sha256)
		var home:=Node3D.new();home.name=room.allocation.proposed_runtime_id;root.add_child(home)
		home.set_meta("candidate_state","proposed_specialty_habitat");home.set_meta("proposed_design_species",room.proposed_design_species);home.set_meta("reserved_rest_count",room.allocation.proposed_rest_place_count);home.set_meta("species_ready",false);home.set_meta("historical_save_identity_recovered",false);home.set_meta("allocation_sha256",room.allocation.allocation_sha256);home.set_meta("rest_slot_ids",room.allocation.proposed_rest_slot_ids)
		helper.contact_visual(home,room.model_file)
		for d in room.doors:
			var door:Node3D=load("res://scripts/"+str(d.controller)).new();door.name=d.name;door.persistent_id=d.persistent_id;door.position=Vector3(d.position[0],d.position[1],d.position[2]);door.rotation.y=d.yaw;home.add_child(door)
		for item in room.lights:
			var light:=SpotLight3D.new();light.name=item.name;light.position=Vector3(item.position[0],item.position[1],item.position[2]);light.rotation.x=-PI/2;light.light_color=Color(1,.93,.8);light.light_energy=item.energy;light.spot_range=item.range;light.spot_angle=70;light.shadow_enabled=false;home.add_child(light)
		if room.proposed_design_species=="Baelins":
			for fitting in room.rest_fittings:
				var wet:=Area3D.new();wet.name="WetRegion_"+str(fitting.binding.name);wet.position=Vector3(fitting.frame_origin[0],fitting.frame_origin[1],fitting.frame_origin[2]);wet.rotation.y=fitting.yaw;wet.collision_layer=256;wet.collision_mask=1
				for cell in p.aquatic_wet_cells_local:
					var collision:=CollisionShape3D.new();var shape:=ConvexPolygonShape3D.new();var points:=PackedVector3Array()
					for v in cell.vertices:points.append(Vector3(v[0],v[1],v[2]))
					shape.points=points;shape.margin=0;collision.shape=shape;wet.add_child(collision)
				home.add_child(wet);wet.set_meta("source_derived_volume_m3",p.aquatic_wet_volume_m3);wet.set_meta("operation_hold",true)
	var structure:=Node3D.new();structure.name="StarAtlasSpecialtySixthReceiving";districts.add_child(structure)
	assert(FileAccess.get_sha256("res://assets/models/"+str(p.receiving.model_file))==p.receiving.model_sha256)
	var visual:Node3D=helper.contact_visual(structure,p.receiving.model_file)
	var retained:=0
	for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
		if bool(mesh.get_meta("extras",{}).get("persistent_structural_contact_only",false)):mesh.visible=false;retained+=1
	assert(retained==88)
	structure.set_meta("always_present_structural_contacts",true);structure.set_meta("retained_source_objects",retained);structure.set_meta("structural_capacity_accepted",false)
	return root
