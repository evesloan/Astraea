extends "res://scripts/service_door.gd"
# Physical candidate fitting. Private access always needs explicit known consent;
# the retained visit interface has no production provider.
var authored_visual:Node3D
var fitting:Dictionary
var custodian:WeakRef
var visit:RefCounted
var access_refused:=false
var visit_opened:=false
func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func _ready()->void:
	assert(authored_visual!=null and not persistent_id.is_empty() and leaves.is_empty())
	open_fraction=0.0;desired_open=false;pose_initialized=false
	var body:=AnimatableBody3D.new();body.name="PhysicalServiceLeaf";body.sync_to_physics=false;add_child(body);body.global_transform=Transform3D(Basis.IDENTITY,v(fitting.pivot))
	for name in fitting.members:
		var mesh:MeshInstance3D=authored_visual.find_child(str(name),true,false);assert(mesh!=null)
		for old in mesh.get_children():
			if old is StaticBody3D:old.free()
		var contact:=CollisionShape3D.new();contact.shape=mesh.mesh.create_convex_shape();contact.shape.margin=.001;contact.transform=body.global_transform.affine_inverse()*mesh.global_transform;body.add_child(contact);mesh.reparent(body,true)
	for name in fitting.control_members:
		var fixed:Node3D=authored_visual.find_child(str(name),true,false);assert(fixed!=null);fixed.reparent(self,true)
	leaves.append(body);_apply_pose();body.sync_to_physics=true
	set_meta("production_access_provider_available",false)
func granted(candidate:CharacterBody3D)->bool:
	return custodian!=null and custodian.get_ref()==candidate and (not fitting.requires_visit or (visit!=null and visit.allows(candidate,persistent_id)))
func egress_allowed(candidate:CharacterBody3D)->bool:
	return visit_opened and custodian!=null and custodian.get_ref()==candidate and (candidate.global_position-v(fitting.closed_center)).dot(v(fitting.private_side_normal))>.2
func get_interaction_label()->String:
	if obstructed:return "Clear service fitting swing"
	if desired_open:return "E · Close service fitting"
	var actor:CharacterBody3D=custodian.get_ref() if custodian!=null else null
	if actor!=null and (granted(actor) or egress_allowed(actor)):return "E · Open service fitting"
	return "Service visit required"
func interact(candidate:CharacterBody3D)->void:
	if custodian==null or custodian.get_ref()!=candidate:access_refused=true;return
	if not desired_open and not granted(candidate) and not egress_allowed(candidate):access_refused=true;return
	if fitting.requires_visit and granted(candidate):visit_opened=true
	access_refused=false;super.interact(candidate)
func _physics_process(delta:float)->void:
	var actor:CharacterBody3D=custodian.get_ref() if custodian!=null else null
	if desired_open and open_fraction<.999 and (actor==null or (not granted(actor) and not egress_allowed(actor))):desired_open=false
	super._physics_process(delta)
func _apply_pose()->void:
	if not leaves.is_empty():leaves[0].global_transform=Transform3D(Basis(Vector3.UP,deg_to_rad(float(fitting.candidate_open_degrees))*open_fraction),v(fitting.pivot))
func _sweep_occupied()->bool:
	var lo:=v(fitting.sweep_min);var hi:=v(fitting.sweep_max);var q:=PhysicsShapeQueryParameters3D.new();var box:=BoxShape3D.new();box.size=hi-lo;box.margin=.001;q.shape=box;q.transform=Transform3D(Basis.IDENTITY,(lo+hi)/2)
	var hits:=get_world_3d().direct_space_state.intersect_shape(q,64)
	if hits.size()>=64:return true
	for hit in hits:
		if hit.collider is CharacterBody3D or hit.collider is RigidBody3D:return true
	return false
