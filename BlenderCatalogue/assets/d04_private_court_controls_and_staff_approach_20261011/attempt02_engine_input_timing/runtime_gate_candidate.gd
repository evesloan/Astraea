extends "res://scripts/service_door.gd"
# Programme-owned fitting of the retained service-door interaction/timing loop.
# Access does not authorize entry to any home or replace occupancy/save rules.
var authored_visual:Node3D
var fitting:Dictionary
var custodian:WeakRef
var visit:RefCounted
var access_refused:=false
func _ready()->void:
	assert(not persistent_id.is_empty() and authored_visual!=null and leaves.is_empty())
	open_fraction=0.0;desired_open=false;pose_initialized=false
	var body:=AnimatableBody3D.new();body.name="CourtGateLeaf";body.sync_to_physics=false;add_child(body)
	body.global_transform=Transform3D(Basis.IDENTITY,Vector3(fitting.pivot[0],fitting.pivot[1],fitting.pivot[2]))
	for name in fitting.members:
		var mesh:MeshInstance3D=authored_visual.find_child(str(name),true,false);assert(mesh!=null)
		for old in mesh.get_children():
			if old is StaticBody3D:old.free()
		var local_pose:Transform3D=body.global_transform.affine_inverse()*mesh.global_transform
		var contact:=CollisionShape3D.new();contact.name=str(name)+"Contact";contact.shape=mesh.mesh.create_convex_shape();contact.shape.margin=.001;contact.transform=local_pose;body.add_child(contact);mesh.reparent(body,true)
	leaves.append(body);_apply_pose();body.sync_to_physics=true
	set_meta("private_home_entry_authorized",false);set_meta("production_access_provider_available",false)
func get_interaction_label()->String:
	if obstructed:return "Clear garden gate swing"
	if desired_open:return "E · Close garden service gate"
	var bound_actor:CharacterBody3D=custodian.get_ref() if custodian!=null else null
	if bound_actor==null or visit==null or not visit.allows(bound_actor,persistent_id):return "Garden service visit required"
	return "E · Open garden service gate"
func interact(candidate:CharacterBody3D)->void:
	if custodian==null or custodian.get_ref()!=candidate:access_refused=true;return
	if not desired_open and (visit==null or not visit.allows(candidate,persistent_id)):
		access_refused=true;return
	access_refused=false
	# Closing remains available to the bound worker after a visit is revoked.
	super.interact(candidate)
func _apply_pose()->void:
	if leaves.is_empty():return
	var pivot:=Vector3(fitting.pivot[0],fitting.pivot[1],fitting.pivot[2])
	leaves[0].global_transform=Transform3D(Basis(Vector3.UP,deg_to_rad(float(fitting.candidate_open_degrees))*open_fraction),pivot)
func _sweep_occupied()->bool:
	var query:=PhysicsShapeQueryParameters3D.new();var box:=BoxShape3D.new();box.size=Vector3(1.46,2.9,1.46);box.margin=.001;query.shape=box
	var direction:float=-1.0 if float(fitting.candidate_open_degrees)>0 else 1.0
	query.transform=Transform3D(Basis.IDENTITY,Vector3(fitting.pivot[0]+.61,fitting.pivot[1]+1.4,fitting.pivot[2]+direction*.61))
	var hits:=get_world_3d().direct_space_state.intersect_shape(query,64)
	# A saturated query is uncertain, so motion stays paused.
	if hits.size()>=64:return true
	for hit in hits:
		if hit.collider is CharacterBody3D or hit.collider is RigidBody3D:return true
	return false
