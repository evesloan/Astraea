extends "res://tram_section_successor_20261024/boarding.gd"
# Inherit all original docking/interlock/phase logic; bind receiver poses once.
static func build(parent:Node3D,existing_base:Node3D,existing_vehicle:AnimatableBody3D,candidate_only:bool=false)->Node3D:
	var p:Dictionary=data()
	if not p.active and not candidate_only:return null
	assert(not parent.has_node("Group4BoardingSafety"))
	var n:Node3D=load("res://aquatic_tram_interior_20261026/integration/boarding.gd").new()
	n.name="Group4BoardingSafety";n.plan=p.duplicate(true);n.base=existing_base;n.vehicle=existing_vehicle
	n.section=JSON.parse_string(FileAccess.get_file_as_string("res://aquatic_tram_interior_20261026/r009/PLAN.json"))
	var completion:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GROUP4_COMPLETION_CANDIDATE.json"))
	for mount in n.plan.station_mounts:
		for station in completion.stations:
			if station.label==mount.station:mount["vehicle_door_side"]=str(station.vehicle_door_side).to_upper()
		if mount.station=="CENTRAL":mount.origin=n.section.central.bridge_origin_xyz;mount.yaw=n.section.central.bridge_yaw
		if mount.station=="FORE_MIDSHIP":mount.origin=[14.9,56.1,-236.1];mount.yaw=0
		if mount.station=="AFT_MIDSHIP":mount.origin=[20.7,56.1,221];mount.yaw=PI
	n.set_meta("integration_boarding_admitted",false)
	parent.add_child(n);return n

func _section_receivers()->void:
	var item:Dictionary=model("barrier_receivers",plan)
	assert(FileAccess.get_sha256(MODELS+item.file)==item.sha256)
	var visual:Node3D=(load(MODELS+item.file)as PackedScene).instantiate();add_child(visual)
	var old_central:=Transform3D(Basis.IDENTITY,Vector3(-2.2,56.1,-72))
	var row:Dictionary=section.central
	var new_central:=Transform3D(Basis(Vector3.UP,float(row.bridge_yaw)),Vector3(row.bridge_origin_xyz[0],row.bridge_origin_xyz[1],row.bridge_origin_xyz[2]))
	var old_fore:=Transform3D(Basis.IDENTITY,Vector3(-7.8,56.1,-241))
	var new_fore:=Transform3D(Basis.IDENTITY,Vector3(14.9,56.1,-236.1))
	var old_aft:=Transform3D(Basis(Vector3.UP,PI),Vector3(-3.4,56.1,216))
	var new_aft:=Transform3D(Basis(Vector3.UP,PI),Vector3(20.7,56.1,221))
	var policies:Dictionary={};var members:Array[Node]=[];var central_count:=0;var fore_count:=0;var aft_count:=0
	for name:String in item.policies:policies[name.validate_node_name()]=item.policies[name]
	var count:=0
	for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
		count+=1;assert(policies.has(str(mesh.name)))
		if str(mesh.name).begins_with("CENTRAL_"):
			mesh.global_transform=base.global_transform*new_central*old_central.affine_inverse()*base.global_transform.affine_inverse()*mesh.global_transform;central_count+=1
		elif str(mesh.name).begins_with("FORE_MIDSHIP_"):
			mesh.global_transform=base.global_transform*new_fore*old_fore.affine_inverse()*base.global_transform.affine_inverse()*mesh.global_transform;fore_count+=1
		elif str(mesh.name).begins_with("AFT_MIDSHIP_"):
			mesh.global_transform=base.global_transform*new_aft*old_aft.affine_inverse()*base.global_transform.affine_inverse()*mesh.global_transform;aft_count+=1
		if policies[str(mesh.name)]!="no_collision_detail":members.append(mesh)
	assert(count==policies.size() and central_count==8 and fore_count==8 and aft_count==8)
	load("res://scripts/static_contact_cache.gd").attach_group(visual,members)
	visual.set_meta("central_receivers_rebound",central_count)
	visual.set_meta("foremid_receivers_rebound",fore_count)

	visual.set_meta("aftmid_receivers_rebound",aft_count)
