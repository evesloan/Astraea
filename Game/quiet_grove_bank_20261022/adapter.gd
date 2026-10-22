extends RefCounted
const P:="res://quiet_grove_bank_20261022/"
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func decorate_shell(shell:Node3D,room:Dictionary)->void:
	var center:float=(room.allocation.allocation_x[0]+room.allocation.allocation_x[1])*.5
	for mesh:MeshInstance3D in shell.find_children("*","MeshInstance3D",true,false):
		if mesh.get_meta("extras",{}).get("construction_role","")!="window":continue
		var plane:float=(mesh.global_transform*mesh.get_aabb()).get_center().x
		var material:=ShaderMaterial.new();material.shader=load("res://night_garden_view_galleries_20261022/private_view.gdshader");material.set_shader_parameter("plane_x",plane);material.set_shader_parameter("interior_sign",signf(center-plane));mesh.material_override=material
static func build(ship:Node3D)->Node3D:
	var package:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PACKAGE.json"))
	var index:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/INDEX.json")).rooms
	var receipt:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/RECEIVING_BUILD.json"))
	var guard_plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/GUARD_PLAN.json"))
	var districts:Node3D=ship.get_node("ShipSpace/Districts")
	assert(not districts.has_node("QuietGroveD15Specialty20261022"))
	var old_district:Node3D=districts.get_node("QuietGrove17Specialty20261022")
	assert(not old_district.get_meta("whole_bank_view_successor",false))
	var house:Node3D=districts.get_node("QuietGroveReceivingCandidate")
	assert(FileAccess.get_sha256("res://assets/models/QUIET_GROVE_ARCHITECTURE_lift_r003.glb")==guard_plan.source_sha256)
	var manager:Node=ship.private_detail_residency;assert(manager!=null)
	var patch:Node3D=load(P+"runtime/QuietGrove30Receiving_r001.scn").instantiate()
	var old_guards:Array[MeshInstance3D]=[]
	for row in receipt.guard_batches:
		var old:=house.find_child(str(row.batch),true,false)as MeshInstance3D
		assert(old!=null and old.mesh!=null and old.get_meta("extras",{}).get("category","")=="guard")
		assert(old.find_children("StaticContact","StaticBody3D",true,false).size()==1)
		assert(patch.find_child(str(row.batch),true,false)!=null);old_guards.append(old)
	# Preflight every identity/resource and existing-room occupancy before touching any owner.
	for room in package.rooms:
		var record:Dictionary=index[room.model_file]
		assert(record.room_id==room.allocation.proposed_runtime_id and record.sha256==room.model_sha256)
		assert(FileAccess.get_sha256(record.shell_path)==record.shell_sha256 and FileAccess.get_sha256(record.detail_path)==record.detail_sha256)
		assert(not manager.index.has(room.model_file))
		if str(room.allocation.deck)!="D15":
			var home:Node3D=old_district.get_node(str(record.room_id));assert(home.get_meta("rest_slot_ids")==room.allocation.proposed_rest_slot_ids)
			var found:Array=manager.entries.filter(func(e):return e.home.get_ref()==home);assert(found.size()==1)
			assert(not is_instance_valid(found[0].detail),"Do not refit an occupied/resident private detail")
		else:assert(districts.find_child(str(record.room_id),true,false)==null)
	var district:=Node3D.new();district.name="QuietGroveD15Specialty20261022";districts.add_child(district)
	district.set_meta("new_allocations",0);district.set_meta("reserved_rests",40);district.set_meta("finished",false);district.set_meta("visual_accepted",false)
	for room in package.rooms:
		var record:Dictionary=index[room.model_file];var home:Node3D
		if str(room.allocation.deck)=="D15":
			home=Node3D.new();home.name=record.room_id;district.add_child(home)
		else:
			home=old_district.get_node(str(record.room_id))
			var entry:Dictionary=manager.entries.filter(func(e):return e.home.get_ref()==home)[0]
			var shells:Array=home.get_children().filter(func(c):return c.scene_file_path==str(entry.record.shell_path));assert(shells.size()==1)
			shells[0].free();entry.witness.free();manager.entries.erase(entry)
		manager.index[room.model_file]=record;manager.night_files[room.model_file]=true
		home.set_meta("census_source_index",room.allocation.source_envelope_index);home.set_meta("allocation_sha256",room.allocation.allocation_sha256);home.set_meta("rest_slot_ids",room.allocation.proposed_rest_slot_ids);home.set_meta("species_ready",false);home.set_meta("finished",false)
		var actual_rests:Array=room.components.filter(func(c):return c.has("rest_slot_id"))
		home.set_meta("bank_rest_bindings",actual_rests)
		if home.has_meta("rest_fittings"):home.set_meta("pre_bank_rest_fittings",home.get_meta("rest_fittings"))
		var fittings:Array=[]
		for binding in actual_rests:fittings.append({"rest_slot_id":binding.rest_slot_id,"binding":binding,"operation_accepted":false})
		home.set_meta("rest_fittings",fittings);home.set_meta("cocoon_view_lounge_minimum_m",2.8)
		var shell:Node3D=manager.register_room(home,str(room.model_file));decorate_shell(shell,room)
		for data in room.doors:
			var door:Node3D=home.get_node_or_null(str(data.name))
			if door==null:
				assert(str(room.allocation.deck)=="D15");door=load("res://scripts/"+str(data.controller)).new();door.name=data.name;door.persistent_id=data.persistent_id;door.position=v(data.position);door.rotation.y=data.yaw;home.add_child(door)
			else:
				assert(str(door.persistent_id)==str(data.persistent_id));door.position=v(data.position);door.rotation.y=data.yaw
		for data in room.lights:
			var light:=home.get_node_or_null(str(data.name))as SpotLight3D
			if light==null:light=SpotLight3D.new();light.name=data.name;home.add_child(light)
			light.position=v(data.position);light.rotation.x=-PI/2;light.light_color=Color(1,.90,.74);light.light_energy=data.energy;light.spot_range=data.range;light.spot_angle=72;light.shadow_enabled=false
		home.set_meta("whole_bank_view_successor",true)
	district.add_child(patch)
	for mesh:MeshInstance3D in patch.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
	for old in old_guards:old.free()
	old_district.set_meta("whole_bank_view_successor",true);old_district.set_meta("visual_accepted",false)
	district.set_meta("view_bank_total_rooms",47);district.set_meta("view_bank_reserved_rests",59);district.set_meta("original_guard_batches_replaced",receipt.guard_batches.size())
	return district
