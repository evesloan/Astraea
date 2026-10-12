extends RefCounted
# Optional, narrowly pinned successor to the retained source-open metadata predicate.
# The shared structure test still owns exact native bounds, programme IDs and triangle fidelity.
const PROOF:="res://data/architecture/group8/MEDICAL_PRIVACY_SUCCESSOR_PROOF.json"
static var pristine_meshes:Dictionary={}
static func pinned_plan()->Dictionary:
	var proof:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(PROOF))
	assert(proof.scope=="Eight retained source-open clinical privacy pairs; asset-specific fitting only")
	for path in proof.file_pins:assert(FileAccess.get_sha256(str(path))==str(proof.file_pins[path]),"Exact medical fitting successor source required: "+str(path))
	return JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/medical_privacy.json"))
static func validate_fitted_leaf(node:MeshInstance3D)->bool:
	var p:=pinned_plan();var matches:Array=[]
	for row in p.doors:
		for side in ["left","right"]:
			if str(node.name)=="TRIAGE_%02d_privacy_leaf_%s"%[int(row.source_pod_number),side]:matches.append({"row":row,"side":side})
	if matches.size()!=1:return false
	var item:Dictionary=matches[0];var row:Dictionary=item.row;var hinge:Node3D=node.get_parent();var driver:Node3D=hinge.get_parent()
	if str(hinge.name)!="SourceHinge_"+str(item.side)or str(driver.name)!=str(row.name):return false
	if driver.get_script()!=load("res://scripts/group8/medical_privacy_door.gd")or str(driver.persistent_id)!=str(row.persistent_id):return false
	if not driver.desired_open or not is_equal_approx(driver.open_fraction,1.0)or driver.bound_meshes.size()!=10 or driver.hinge_nodes.size()!=2:return false
	if str(driver.get_parent().name)!="AuthoredMedicalWelcome"or str(driver.get_meta("programme_child",""))!=str(row.programme_child):return false
	if not node.get_meta("original_source_open_static",false)or node.get_meta("source_open_static",true)or not node.get_meta("operation_enabled",false):return false
	if str(node.get_meta("group8_privacy_driver",""))!=str(row.persistent_id):return false
	if not driver.original_open_poses.has(str(node.name))or not node.global_transform.is_equal_approx(driver.original_open_poses[str(node.name)]):return false
	if pristine_meshes.is_empty():
		var original:Node3D=(load("res://assets/models/"+str(p.original_architecture_file))as PackedScene).instantiate()
		for mesh:MeshInstance3D in original.find_children("*","MeshInstance3D",true,false):pristine_meshes[str(mesh.name)]=mesh.mesh
		original.free()
	if node.mesh!=pristine_meshes.get(str(node.name)):return false
	var contacts:Array=node.find_children("*","CollisionShape3D",true,false)
	if contacts.size()!=1 or not contacts[0].get_parent()is AnimatableBody3D:return false
	var body:AnimatableBody3D=contacts[0].get_parent()
	if body.sync_to_physics or not (PhysicsServer3D.body_get_state(body.get_rid(),PhysicsServer3D.BODY_STATE_TRANSFORM)as Transform3D).is_equal_approx(body.global_transform):return false
	return true
