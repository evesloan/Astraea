extends RefCounted
const DATA="res://data/architecture/TIDAL_SPECIALTY_102.json"
static func patch_frontage(visual:Node3D)->void:
	var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(DATA))
	var file:String="res://assets/models/"+str(d.frontage_model)
	assert(FileAccess.get_sha256(file)==d.frontage.export_sha256)
	var patch:Node3D=load(file).instantiate()
	for item in d.frontage.changed_batches:
		var target:MeshInstance3D=visual.find_child(str(item.batch),true,false)
		var replacement:MeshInstance3D=patch.find_child(str(item.batch),true,false)
		assert(target!=null and replacement!=null)
		assert(target.get_meta("extras",{}).category in ["guard","public_glass"])
		target.mesh=replacement.mesh
		target.set_meta("entry_102_guard_cut",true)
	patch.free()
static func _contacts(node:Node3D)->void:
	for mesh:MeshInstance3D in node.find_children("*","MeshInstance3D",true,false):
		load("res://scripts/static_contact_cache.gd").attach(mesh)
static func build(ship:Node3D)->Node3D:
	var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(DATA))
	var parent:=Node3D.new();parent.name="SpecialtyHomeCandidates"
	ship.get_node("ShipSpace/Districts").add_child(parent)
	var room:=Node3D.new();room.name=str(d.allocation.proposed_runtime_id);parent.add_child(room)
	room.set_meta("census_source_index",102)
	room.set_meta("source_identity_status",d.allocation.runtime_id_status)
	room.set_meta("habitat_profile","new_quiet_cocoon_candidate")
	room.set_meta("species_assignment","")
	room.set_meta("finished",false)
	room.set_meta("source_rest_slots",d.allocation.proposed_rest_slot_ids)
	var path:String="res://assets/models/"+str(d.model_file)
	assert(FileAccess.get_sha256(path)==d.model_sha256)
	var shell:Node3D=load(path).instantiate();room.add_child(shell)
	var glass:=ShaderMaterial.new();glass.shader=load("res://shaders/hospitality_glass.gdshader")
	var meshes:=shell.find_children("*","MeshInstance3D",true,false);assert(meshes.size()==int(d.part_count))
	for mesh:MeshInstance3D in meshes:
		var extra:Dictionary=mesh.get_meta("extras",{});assert(extra.source_plan_sha256==d.plan_sha256)
		if extra.role=="hospitality_glass":mesh.material_override=glass
		if bool(extra.runtime_collision):load("res://scripts/static_contact_cache.gd").attach(mesh)
	var component_path:String="res://assets/models/"+str(d.component_model)
	assert(FileAccess.get_sha256(component_path)==d.component_sha256)
	var support:Node3D=load(component_path).instantiate();support.name="QuietCocoonSupport";room.add_child(support)
	support.position=Vector3(d.component.world_origin[0],d.component.world_origin[1],d.component.world_origin[2]);support.rotation.y=float(d.component.godot_yaw)
	_contacts(support)
	var rest:=Marker3D.new();rest.name="ReservedRestPlace";support.add_child(rest);rest.position=Vector3(0,.6096875,0)
	rest.set_meta("rest_slot_id",d.allocation.proposed_rest_slot_ids[0]);rest.set_meta("body_pose_accepted",false)
	for item in d.fixtures:
		var fixture:Node3D=load("res://assets/models/"+str(item.catalogue_id)+".glb").instantiate();fixture.name=str(item.catalogue_id);room.add_child(fixture)
		fixture.position=Vector3(item.origin[0],item.origin[1],item.origin[2]);fixture.rotation.y=float(item.yaw);_contacts(fixture)
	for item in d.doors:
		var door:Node3D=load("res://scripts/guest_entry_door.gd" if item.name=="EntryDoor" else "res://scripts/guest_privacy_door.gd").new()
		door.name=str(item.name);door.persistent_id=StringName(str(item.identity));door.position=Vector3(item.world_origin[0],item.world_origin[1],item.world_origin[2]);door.rotation.y=float(item.godot_yaw);room.add_child(door)
	for item in d.lights:
		var light:=SpotLight3D.new();light.name=str(item.name);room.add_child(light);light.position=Vector3(item.position[0],item.position[1],item.position[2]);light.rotation.x=-PI/2;light.light_color=Color(1,.88,.67);light.light_energy=float(item.energy);light.spot_range=float(item.range);light.spot_angle=75;light.shadow_enabled=false
	return room
