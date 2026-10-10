extends RefCounted
static func vec(v:Array)->Vector3:return Vector3(v[0],v[1],v[2])
static func build(ship:Node3D)->Node3D:
	var districts:Node3D=ship.get_node("ShipSpace/Districts")
	if districts.has_node("StarAtlasSpecialtyTwelfthCandidates"):return districts.get_node("StarAtlasSpecialtyTwelfthCandidates")
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_SPECIALTY_TWELFTH.json"))
	var guards:Node3D=ship.get_node("ShipSpace/CentralResidentialStreetFloors/CentralResidentialStreetGuards")
	for edge in p.receiving.removed_source_guards:
		var contact:StaticBody3D=guards.get_node(str(edge.id)+"Contact")
		assert(contact.position.distance_to((vec(edge.a)+vec(edge.b))*.5+Vector3.UP*.55)<.0001)
		var collision:CollisionShape3D=contact.get_child(0)
		assert(absf(collision.shape.size.x-vec(edge.a).distance_to(vec(edge.b)))<.0001)
		for node in guards.get_children():
			if str(node.name).begins_with(str(edge.id)):node.free()
	var root:=Node3D.new();root.name="StarAtlasSpecialtyTwelfthCandidates";districts.add_child(root)
	root.set_meta("new_allocations",0);root.set_meta("species_ready_rooms",0);root.set_meta("removed_source_guard_count",4);root.set_meta("removed_previous_guard_mesh_count",0)
	var helper:Script=load("res://scripts/star_atlas_specialty_first.gd")
	for room in p.rooms:
		assert(FileAccess.get_sha256("res://assets/models/"+str(room.model_file))==room.model_sha256)
		var home:=Node3D.new();home.name=room.allocation.proposed_runtime_id;root.add_child(home)
		home.set_meta("candidate_state","proposed_specialty_habitat");home.set_meta("proposed_design_species",room.proposed_design_species);home.set_meta("reserved_rest_count",room.allocation.proposed_rest_place_count);home.set_meta("species_ready",false);home.set_meta("historical_save_identity_recovered",false);home.set_meta("allocation_sha256",room.allocation.allocation_sha256);home.set_meta("rest_slot_ids",room.allocation.proposed_rest_slot_ids)
		helper.contact_visual(home,room.model_file)
		for d in room.doors:
			var door:Node3D=load("res://scripts/"+str(d.controller)).new();door.name=d.name;door.persistent_id=d.persistent_id;door.position=vec(d.position);door.rotation.y=d.yaw;home.add_child(door)
		for item in room.lights:
			var light:=SpotLight3D.new();light.name=item.name;light.position=vec(item.position);light.rotation.x=-PI/2;light.light_color=Color(1,.93,.8);light.light_energy=item.energy;light.spot_range=item.range;light.spot_angle=70;light.shadow_enabled=false;home.add_child(light)
	var structure:=Node3D.new();structure.name="StarAtlasSpecialtyTwelfthReceiving";districts.add_child(structure)
	assert(FileAccess.get_sha256("res://assets/models/"+str(p.receiving.model_file))==p.receiving.model_sha256)
	helper.contact_visual(structure,p.receiving.model_file)
	structure.set_meta("always_present_structural_contacts",true);structure.set_meta("engineering_load_capacity_accepted",false)
	return root
