extends RefCounted
static func build_source_fixture(parent:Node3D)->Node3D:
	assert(parent.has_meta("group2_isolated_source_fixture"))
	var kit:Node3D=(load("res://assets/group2_family_meal/FAMILY_MEAL_FITTINGS_r001.glb")as PackedScene).instantiate();parent.add_child(kit)
	load("res://scripts/static_contact_cache.gd").attach_group(kit,kit.find_children("*","MeshInstance3D",true,false));kit.set_meta("production_adoption",false);return kit

# Sole integration consumer; retained isolated fixture method above remains unchanged.
static func build_on_current_receiver(ship:Node3D)->Node3D:
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_family_meal/COMPONENT_r001.json"))
	var preflight:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_family_meal/CURRENT_TABLE_PREFLIGHT.json"))
	assert(FileAccess.get_sha256("res://assets/models/FAMILY_TERRACE_ARCHITECTURE_lift_r003.glb")==str(data.source_runtime_sha256))
	var path:="res://assets/group2_family_meal/FAMILY_MEAL_FITTINGS_r001.glb";assert(FileAccess.get_sha256(path)==str(data.export_sha256))
	var packed:PackedScene=load(path);assert(packed!=null)
	var house:Node3D=ship.get_node_or_null("ShipSpace/Districts/FamilyTerraceReceivingCandidate");assert(house!=null and house.global_transform.is_equal_approx(Transform3D.IDENTITY))
	assert(house.get_node_or_null("Group2FamilyMealReceiving")==null)
	for row in preflight.table_parts:
		var batch:MeshInstance3D=house.find_child(str(row.batch_node),true,false);assert(batch!=null)
		var extras:Dictionary=batch.get_meta("extras",{});var matching:Array=[]
		for source_part in extras.get("source_part_ranges",[]):
			if str(source_part.source_part_id)==str(row.name):matching.append(source_part)
		assert(matching.size()==1 and int(matching[0].vertex_start)==int(row.vertex_start)and int(matching[0].vertex_count)==int(row.vertex_count))
		assert(batch.mesh.surface_get_format(0)==int(row.imported_surface_format))
		var vertices:PackedVector3Array=batch.mesh.surface_get_arrays(0)[Mesh.ARRAY_VERTEX];var floats:=PackedFloat32Array();var lo:=Vector3(INF,INF,INF);var hi:=Vector3(-INF,-INF,-INF)
		for i in range(int(row.vertex_start),int(row.vertex_start)+int(row.vertex_count)):
			var v:Vector3=vertices[i];floats.append(v.x);floats.append(v.y);floats.append(v.z);var at:Vector3=batch.global_transform*v;lo=lo.min(at);hi=hi.max(at)
		var actual_hash:String=load("res://scripts/release_operations_20261023/guard.gd").sha256_bytes(floats.to_byte_array())
		if not load("res://scripts/release_operations_20261023/guard.gd").require_ok(actual_hash==str(row.imported_vertex_sha256),"Family meal exact vertex preimage differs"):return null
		assert(lo.distance_to(Vector3(row.min[0],row.min[1],row.min[2]))<.0001 and hi.distance_to(Vector3(row.max[0],row.max[1],row.max[2]))<.0001)
	var root:=Node3D.new();root.name="Group2FamilyMealReceiving";house.add_child(root)
	var kit:Node3D=packed.instantiate();kit.name="FAMILY_MEAL_FITTINGS_r001";root.add_child(kit)
	load("res://scripts/static_contact_cache.gd").attach_group(kit,kit.find_children("*","MeshInstance3D",true,false))
	root.set_meta("default_main_adoption",true);root.set_meta("new_floor_owners",0);root.set_meta("new_seats_or_capacity",0);root.set_meta("food_stock_hygiene_or_staff_operation",false);root.set_meta("programme_or_dining_designation_accepted",false);root.set_meta("source_settings",12);root.set_meta("existing_parent_programme","D16_directory_06")
	return root
