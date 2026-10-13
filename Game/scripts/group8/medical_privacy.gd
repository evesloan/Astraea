extends RefCounted
# Group-local clinical privacy construction; no admission/pressure/treatment operation.
static func build(ship:Node3D)->Node3D:
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/medical_privacy.json"))
	assert(FileAccess.get_sha256("res://assets/models/"+str(p.original_architecture_file))==str(p.original_runtime_sha256))
	assert(FileAccess.get_sha256("res://assets/models/"+str(p.model_file))==str(p.model_sha256))
	var old:Node3D=ship.get_node("ShipSpace/Districts/"+str(p.original_root));var arch:Node3D=old.get_node("AuthoredMedicalWelcome")
	var districts:Node3D=ship.get_node("ShipSpace/Districts");assert(not districts.has_node(str(p.root_name)))
	var root:=Node3D.new();root.name=str(p.root_name);districts.add_child(root)
	root.set_meta("programme_key","D05_directory_01");root.set_meta("new_floor_owners",0);root.set_meta("new_capacity",0);root.set_meta("new_backend_implementations",0);root.set_meta("clinical_or_pressure_operation_accepted",false)
	var visual:Node3D=load("res://scripts/d04_port_forward_homes_fifth.gd").visual(root,str(p.model_file),p.collision_policy)
	var drivers:Dictionary={}
	for row in p.doors:
		var d:Node3D=load("res://scripts/group8/medical_privacy_door.gd").new();d.name=str(row.name);d.persistent_id=StringName(str(row.persistent_id));d.native_architecture=arch;d.binding=row
		d.position=arch.global_transform.affine_inverse()*Vector3(row.at[0],row.at[1],row.at[2]);d.rotation.y=float(row.yaw);arch.add_child(d);drivers[str(row.name)]=d
		d.set_meta("programme_child",str(row.programme_child));d.set_meta("identity_origin",str(row.identity_origin))
	for row in p.control_targets:
		var marker:Node3D=visual.find_child(str(row.marker),true,false);assert(marker!=null,"Exact exported clinical-control marker required")
		var d:Node3D=drivers[str(row.door_name)];var body:=StaticBody3D.new();body.name=str(row.side)+"PhysicalControl";d.add_child(body);body.position=d.global_transform.affine_inverse()*marker.global_position
		var shape:=BoxShape3D.new();shape.size=Vector3(row.size_world_local[0],row.size_world_local[1],row.size_world_local[2]);shape.margin=.001
		var contact:=CollisionShape3D.new();contact.name="PreciseControlContact";contact.shape=shape;body.add_child(contact);body.set_meta("group8_physical_control",true)
	old.set_meta("privacy_leaves_static",false);old.set_meta("group8_asset_specific_privacy_fitting",true)
	return root
