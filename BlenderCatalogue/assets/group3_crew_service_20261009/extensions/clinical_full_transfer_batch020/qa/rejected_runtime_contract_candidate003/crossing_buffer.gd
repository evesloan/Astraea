extends "res://scripts/group3_port2_clinical_20261011/crossing_supervisor.gd"
var bounds_xz:Array
func buffer_occupied()->bool:
 assert(bounds_xz.size()==4)
 var b:=BoxShape3D.new();b.size=Vector3(bounds_xz[2]-bounds_xz[0],2.8,bounds_xz[3]-bounds_xz[1]);b.margin=.001
 var q:=PhysicsShapeQueryParameters3D.new();q.shape=b;q.transform=Transform3D(Basis.IDENTITY,Vector3((bounds_xz[0]+bounds_xz[2])/2,22.4,(bounds_xz[1]+bounds_xz[3])/2))
 var hits:=get_world_3d().direct_space_state.intersect_shape(q,128)
 if hits.size()==128:return true
 for h in hits:
  if h.collider is CharacterBody3D or h.collider is RigidBody3D:return true
 return false
