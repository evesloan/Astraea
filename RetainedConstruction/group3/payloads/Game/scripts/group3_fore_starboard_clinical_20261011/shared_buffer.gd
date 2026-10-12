extends "res://scripts/group3_port2_clinical_20261011/crossing_supervisor.gd"
# Exact retained fore shared buffer. Original door sequencing remains inherited.
func buffer_occupied()->bool:
 var box:=BoxShape3D.new();box.size=Vector3(4.44,2.8,10.08)
 var q:=PhysicsShapeQueryParameters3D.new();q.shape=box;q.transform=Transform3D(Basis.IDENTITY,Vector3(21.28,22.4,-500.9));q.margin=.001
 var hits:=get_world_3d().direct_space_state.intersect_shape(q,128)
 if hits.size()==128:return true
 for hit in hits:
  if hit.collider is CharacterBody3D or hit.collider is RigidBody3D:return true
 return false
