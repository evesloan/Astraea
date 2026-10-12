extends "res://scripts/service_door.gd"
# New source-sized fitting with unchanged service-door interaction/state lifecycle.
var closed_poses:Array[Transform3D]=[]
var supervisor:Node3D
var flow_axis:String
func _ready()->void:
 assert(not persistent_id.is_empty())
 var visual:Node3D=(load("res://assets/models/group3_clinical_full_20261011/AST-MED-G3-009.glb")as PackedScene).instantiate();add_child(visual)
 for side in ["LEFT","RIGHT"]:
  var source:Node3D=visual.find_child("LEAF_"+side,true,false);assert(source!=null)
  var body:=AnimatableBody3D.new();body.name="ClinicalLeaf_"+side;body.sync_to_physics=false;body.transform=global_transform.affine_inverse()*source.global_transform;add_child(body)
  source.reparent(body,true);source.transform=Transform3D.IDENTITY
  var c:=CollisionShape3D.new();c.name="DimensionedLeafContact";var box:=BoxShape3D.new();box.size=Vector3(1.798,2.398,.053);box.margin=.001;c.shape=box;c.transform=body.transform.affine_inverse()*Transform3D(Basis.IDENTITY,Vector3(-.9 if side=="LEFT"else .9,1.2,0));body.add_child(c)
  leaves.append(body);closed_poses.append(body.transform)
 for mesh in visual.find_children("*","MeshInstance3D",true,false):
  var moving:=false
  for leaf in leaves:
   if leaf.is_ancestor_of(mesh):moving=true
  if not moving:load("res://scripts/static_contact_cache.gd").attach(mesh)
 _apply_pose()
 for body in leaves:body.sync_to_physics=true
func _physics_process(delta:float)->void:super._physics_process(delta/1.9)
func _apply_pose()->void:
 for i in range(leaves.size()):
  var f:float=clampf(open_fraction/.85,0,1)if i==0 else clampf((open_fraction-.15)/.85,0,1)
  leaves[i].transform=closed_poses[i];leaves[i].position=closed_poses[i].origin+Vector3((-1.9 if i==0 else 1.9)*f,0,0)
func _sweep_occupied()->bool:
 if not is_inside_tree()or leaves.size()!=2:return true
 var q:=PhysicsShapeQueryParameters3D.new();var b:=BoxShape3D.new();b.size=Vector3(7.444,2.402,.324);b.margin=.001;q.shape=b;q.transform=global_transform*Transform3D(Basis.IDENTITY,Vector3(0,1.201,0))
 var excluded:Array[RID]=[]
 for leaf in leaves:excluded.append(leaf.get_rid())
 q.exclude=excluded;var hits:=get_world_3d().direct_space_state.intersect_shape(q,128)
 if hits.size()==128:return true
 for h in hits:
  if h.collider is CharacterBody3D or h.collider is RigidBody3D:return true
 return false
func interact(_actor:CharacterBody3D)->void:
 assert(supervisor!=null);supervisor.request_axis("closed"if supervisor.selected_axis==flow_axis else flow_axis)
func get_interaction_label()->String:
 if supervisor==null:return "Controlled clinical crossing"
 if not supervisor.blocked_reason.is_empty():return supervisor.blocked_reason
 return "E · Close clinical crossing"if desired_open else("E · Request clean passage"if flow_axis=="clean"else"E · Request sealed return")
