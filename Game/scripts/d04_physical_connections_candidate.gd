extends RefCounted
# Candidate assembly is called explicitly by bounded tests, never ship.gd.
static func model(parent:Node3D,spec:Dictionary)->Node3D:
	var node:Node3D=load("res://assets/models/"+str(spec.model_file)).instantiate();parent.add_child(node)
	for mesh:MeshInstance3D in node.find_children("*","MeshInstance3D",true,false):
		var item:Dictionary=spec.collision_policy[str(mesh.name)]
		if item.collide:load("res://scripts/static_contact_cache.gd").attach(mesh)
		if item.category=="stair_walk_surface":mesh.visible=false
	return node
static func build(ship:Node3D,player:CharacterBody3D,p:Dictionary)->Dictionary:
	assert(not p.production_active)
	var owner:=Node3D.new();owner.name="D04PhysicalConnectionsCandidateTestOnly";ship.add_child(owner)
	var prior:Dictionary=p.previous_candidate
	model(owner,prior.structure)
	var old:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_FORWARD_PRIVATE_COURT_SERVICE_CANDIDATE.json"))
	for row in old.preimages:
		var preimage:Node3D=ship.find_child(str(row.preimage.name),true,false);assert(preimage!=null);preimage.free()
	for row in p.cuts:
		assert(FileAccess.get_sha256("res://assets/models/"+str(row.source_model))==p.source_pins["Game/assets/models/"+str(row.source_model)])
		var preimage:MeshInstance3D=ship.find_child(str(row.name),true,false);assert(preimage!=null)
		var aabb: AABB=preimage.global_transform*preimage.get_aabb()
		assert(aabb.position.distance_to(Vector3(row.bounds[0][0],row.bounds[0][1],row.bounds[0][2]))<.0001)
		assert(aabb.end.distance_to(Vector3(row.bounds[1][0],row.bounds[1][1],row.bounds[1][2]))<.0001);preimage.free()
	var court:Node3D=model(owner,prior.court_candidate_model);var old_controls:Array=[]
	for i in range(prior.gates.size()):
		var control:Node3D=load("res://scripts/d04_court_service_gate.gd").new();control.name="PriorCourtGate_"+str(i);control.persistent_id=StringName("D04_southern_east_court_service_gate_"+str(i));control.authored_visual=court;control.fitting=prior.gates[i];control.custodian=weakref(player);owner.add_child(control);old_controls.append(control)
	model(owner,p.patch_model);var owned:Node3D=model(owner,p.owned_model);var controls:Array=[]
	for spec in p.gates:
		var control:Node3D=load("res://scripts/d04_physical_service_fitting.gd").new();control.name=spec.name;control.persistent_id=StringName(spec.id);control.authored_visual=owned;control.fitting=spec;control.custodian=weakref(player);owner.add_child(control);controls.append(control)
	return {"owner":owner,"owned":owned,"controls":controls,"old_controls":old_controls}
