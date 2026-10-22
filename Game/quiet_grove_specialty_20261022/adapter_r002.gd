extends RefCounted
const P:="res://quiet_grove_specialty_20261022/"
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D)->Node3D:
	var package:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PACKAGE_R002.json"))
	var targets:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"TARGET_BINDINGS.json")).rooms
	var records:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/INDEX_R002.json")).rooms
	var receipt:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/RECEIVING_BUILD.json"))
	var guard_plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/GUARD_PLAN.json"))
	assert(FileAccess.get_sha256("res://assets/models/QUIET_GROVE_ARCHITECTURE_lift_r003.glb")==guard_plan.source_sha256)
	var districts:Node3D=ship.get_node("ShipSpace/Districts")
	assert(not districts.has_node("QuietGrove17Specialty20261022"))
	var house:Node3D=districts.get_node("QuietGroveReceivingCandidate")
	var manager:Node=ship.private_detail_residency
	assert(manager!=null and manager.get("night_files")!=null)
	var patch:Node3D=load(P+"runtime/QuietGrove17Receiving_r001.scn").instantiate()
	var predecessor:Array[MeshInstance3D]=[]
	for row in receipt.guard_batches:
		var old:=house.find_child(str(row.batch),true,false)as MeshInstance3D
		assert(old!=null and old.mesh!=null and old.get_meta("extras",{}).get("category","")=="guard")
		assert(old.find_children("StaticContact","StaticBody3D",true,false).size()==1,"Exact original guard contact owner required")
		assert(patch.find_child(str(row.batch),true,false)!=null)
		predecessor.append(old)
	for room in package.rooms:
		assert(not manager.index.has(str(room.model_file)))
		assert(not districts.find_child(str(room.allocation.proposed_runtime_id),true,false))
		var record:Dictionary=records[room.model_file]
		assert(record.sha256==room.model_sha256 and FileAccess.get_sha256(record.shell_path)==record.shell_sha256 and FileAccess.get_sha256(record.detail_path)==record.detail_sha256)
	var district:=Node3D.new();district.name="QuietGrove17Specialty20261022";districts.add_child(district)
	district.set_meta("new_allocations",0);district.set_meta("reserved_rests",19);district.set_meta("finished",false);district.set_meta("visual_accepted",false)
	for room in package.rooms:
		var record:Dictionary=records[room.model_file];record["room_id"]=room.allocation.proposed_runtime_id;manager.index[room.model_file]=record;manager.night_files[room.model_file]=true
		var home:=Node3D.new();home.name=room.allocation.proposed_runtime_id;district.add_child(home)
		assert(targets[room.model_file].rest_slot_ids==room.allocation.proposed_rest_slot_ids)
		home.set_meta("rest_fittings",targets[room.model_file].rest_fittings)
		home.set_meta("census_source_index",room.allocation.source_envelope_index);home.set_meta("rest_slot_ids",room.allocation.proposed_rest_slot_ids);home.set_meta("allocation_sha256",room.allocation.allocation_sha256);home.set_meta("species_ready",false);home.set_meta("finished",false)
		var shell:Node3D=manager.register_room(home,str(room.model_file))
		var center_x:float=(room.allocation.allocation_x[0]+room.allocation.allocation_x[1])*.5
		for mesh:MeshInstance3D in shell.find_children("*","MeshInstance3D",true,false):
			var extra:Dictionary=mesh.get_meta("extras",{})
			if str(extra.get("construction_role",""))!="window":continue
			var box:AABB=mesh.global_transform*mesh.get_aabb();var plane:float=box.get_center().x
			var material:=ShaderMaterial.new();material.shader=load("res://night_garden_view_galleries_20261022/private_view.gdshader");material.set_shader_parameter("plane_x",plane);material.set_shader_parameter("interior_sign",signf(center_x-plane));mesh.material_override=material
		for data in room.doors:
			var door:Node3D=load("res://scripts/"+str(data.controller)).new();door.name=data.name;door.persistent_id=data.persistent_id;door.position=v(data.position);door.rotation.y=data.yaw;home.add_child(door)
		for data in room.lights:
			var light:=SpotLight3D.new();light.name=data.name;light.position=v(data.position);light.rotation.x=-PI/2;light.light_color=Color(1,.90,.74);light.light_energy=data.energy;light.spot_range=data.range;light.spot_angle=72;light.shadow_enabled=false;home.add_child(light)
	# Rooms and their closure exist before any temporary guard is replaced.
	district.add_child(patch)
	for mesh:MeshInstance3D in patch.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
	for old in predecessor:old.free()
	district.set_meta("original_guard_batches_replaced",11);district.set_meta("original_house_floor_hull_cap_unchanged",true)
	return district
