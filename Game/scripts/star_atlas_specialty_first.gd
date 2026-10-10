extends RefCounted
static func contact_visual(parent:Node3D,file:String)->Node3D:
	var visual:Node3D=load("res://assets/models/"+file).instantiate()
	parent.add_child(visual)
	var solids:Array[Node]=[]
	for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
		var extra:Dictionary=mesh.get_meta("extras",{})
		if str(extra.get("material_role",""))=="hospitality_glass":
			var glass:=ShaderMaterial.new();glass.shader=load("res://shaders/hospitality_glass.gdshader");mesh.material_override=glass
		if bool(extra.get("runtime_collision",false)):solids.append(mesh)
	load("res://scripts/static_contact_cache.gd").attach_group(visual,solids)
	return visual
static func build(ship:Node3D)->Node3D:
	var districts:Node3D=ship.get_node("ShipSpace/Districts")
	if districts.has_node("StarAtlasSpecialtyCandidates"):return districts.get_node("StarAtlasSpecialtyCandidates")
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_SPECIALTY_FIRST.json"))
	var root:=Node3D.new();root.name="StarAtlasSpecialtyCandidates";districts.add_child(root)
	root.set_meta("new_units",0);root.set_meta("receiving_structure_accepted",false);root.set_meta("species_assignment",null)
	for item in p.receiving.exports:assert(FileAccess.get_sha256("res://assets/models/"+str(item.export))==item.export_sha256)
	contact_visual(root,p.receiving.model_file)
	var patch:Node3D=load("res://assets/models/"+str(p.receiving.commons_patch_file)).instantiate()
	root.add_child(patch)
	var upper:Node3D=districts.get_node("D15_D17_StarAtlasUpper_WIP")
	for mesh:MeshInstance3D in patch.find_children("*","MeshInstance3D",true,false):
		var old:=upper.find_child(str(mesh.name),true,false) as MeshInstance3D
		assert(old!=null)
		for child in old.get_children():
			if child is StaticBody3D:child.free()
		old.mesh=mesh.mesh
		load("res://scripts/static_contact_cache.gd").attach(old)
	patch.free()
	for room in p.rooms:
		assert(FileAccess.get_sha256("res://assets/models/"+str(room.model_file))==room.model_sha256)
		var home:=Node3D.new();home.name=room.allocation.proposed_runtime_id;root.add_child(home)
		home.set_meta("candidate_state","unassigned_environment_candidate");home.set_meta("species_ready",false);home.set_meta("historical_save_identity_recovered",false)
		home.set_meta("allocation_sha256",room.allocation.allocation_sha256);home.set_meta("rest_slot_ids",room.allocation.proposed_rest_slot_ids);home.set_meta("species_assignment",null)
		contact_visual(home,room.model_file)
		for d in room.doors:
			var door:Node3D=load("res://scripts/"+str(d.controller)).new();door.name=d.name;door.persistent_id=d.persistent_id;door.position=Vector3(d.position[0],d.position[1],d.position[2]);door.rotation.y=d.yaw;home.add_child(door)
		for item in room.lights:
			var light:=SpotLight3D.new();light.name=item.name;light.position=Vector3(item.position[0],item.position[1],item.position[2]);light.rotation.x=-PI/2;light.light_color=Color(1,.93,.8);light.light_energy=item.energy;light.spot_range=item.range;light.spot_angle=70;light.shadow_enabled=false;home.add_child(light)
	load("res://scripts/star_atlas_specialty_structural_receiving.gd").build(ship)
	return root
