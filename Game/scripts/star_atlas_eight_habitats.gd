extends RefCounted
static func vector(v:Array)->Vector3:return Vector3(v[0],v[1],v[2])
static func build(ship:Node3D)->Node3D:
	var districts:Node3D=ship.get_node("ShipSpace/Districts")
	if districts.has_node("StarAtlasEightHabitatFittings"):return districts.get_node("StarAtlasEightHabitatFittings")
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_EIGHT_HABITATS.json"))
	assert(FileAccess.get_sha256("res://assets/models/"+str(p.runtime_model_file))==p.runtime_model_sha256)
	var root:=Node3D.new();root.name="StarAtlasEightHabitatFittings";districts.add_child(root)
	root.set_meta("allocation_proposal_status","reported ordinary design choices; no occupant/save migration")
	root.set_meta("species_ready_rooms",0);root.set_meta("reserved_rests",8);root.set_meta("new_allocations",0)
	load("res://scripts/star_atlas_specialty_first.gd").contact_visual(root,p.runtime_model_file)
	for room in p.rooms:
		var home:=districts.find_child(str(room.unit_proposal_id),true,false) as Node3D
		assert(home!=null and home.get_meta("rest_slot_ids")==room.rest_slot_ids)
		home.set_meta("proposed_design_species",room.proposed_design_species)
		home.set_meta("habitat_construction_status","physical construction reference; canonical bodies/animation/operations held")
		home.set_meta("canonical_body_accepted",false);home.set_meta("environment_operations_accepted",false)
		# Only replace explicitly superseded geometry; preserve original native/GLB sources.
		if room.has("remove_source_meshes"):
			for name in room.remove_source_meshes:
				var mesh:=home.find_child(str(name),true,false) as MeshInstance3D
				assert(mesh!=null);mesh.free()
			for contacts in home.find_children("RoomStaticContacts","StaticBody3D",true,false):contacts.free()
			var solids:Array[Node]=[]
			for mesh:MeshInstance3D in home.find_children("*","MeshInstance3D",true,false):
				var extra:Dictionary=mesh.get_meta("extras",{})
				if bool(extra.get("runtime_collision",false)) and str(extra.get("collision_policy",""))!="no_collision_detail":solids.append(mesh)
			load("res://scripts/static_contact_cache.gd").attach_group(home,solids)
		if room.has("privacy_door"):
			var d:Dictionary=room.privacy_door
			var door:Node3D=load("res://scripts/cocoon_privacy_door.gd").new();door.name="CocoonPrivacyDoor";door.persistent_id=d.persistent_id;door.position=vector(d.position);door.rotation.y=d.yaw;home.add_child(door)
			var zone:=Area3D.new();zone.name="QuietRestEnclosure_"+str(int(room.source_envelope_index));zone.position=vector(room.quiet_zone.center);zone.rotation.y=room.quiet_zone.yaw;zone.collision_layer=512;zone.collision_mask=1
			var collision:=CollisionShape3D.new();var shape:=BoxShape3D.new();shape.size=vector(room.quiet_zone.size);collision.shape=shape;zone.add_child(collision);root.add_child(zone);zone.set_meta("purpose","physical enclosed-rest detection; acoustic/molting operations held")
		if room.has("wet_cells_local"):
			var wet:=Area3D.new();wet.name="ContainedWetRegion_"+str(int(room.source_envelope_index));wet.position=vector(room.rest_source.position);wet.rotation.y=room.rest_source.yaw;wet.collision_layer=256;wet.collision_mask=1
			for c in room.wet_cells_local:
				var collision:=CollisionShape3D.new();var shape:=ConvexPolygonShape3D.new();var pts:=PackedVector3Array()
				for v in c.vertices:pts.append(vector(v))
				shape.points=pts;shape.margin=0;collision.shape=shape;wet.add_child(collision)
			root.add_child(wet);wet.set_meta("source_derived_volume_m3",room.wet_volume_m3);wet.set_meta("operation_hold",true);wet.set_meta("policy",p.wet_volume_policy)
	return root
