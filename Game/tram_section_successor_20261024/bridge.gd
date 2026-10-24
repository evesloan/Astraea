extends Node3D
# CENTRAL-only longer panel; original interlocks, height and width retained.
var panel_reach := 1.3852191498493105
var threshold_shape:BoxShape3D
var threshold_center_x := 0.0
# Adapter to the retained authored bridge. Dock/door authority belongs to the shared tram owner.
var model_path:String
var moving:AnimatableBody3D
var fraction:=0.0
var dock_authorized:=false
var requested_deployed:=false
var obstructed:=false
func _ready()->void:
 var document:=GLTFDocument.new();var state:=GLTFState.new()
 var error:=document.append_from_file(ProjectSettings.globalize_path(model_path),state)
 if error!=OK:push_error("Exact CENTRAL bridge source failed to load");set_physics_process(false);return
 var source:Node3D=document.generate_scene(state);assert(source!=null);add_child(source)
 threshold_shape=BoxShape3D.new()
 # Preserve the original [-.07,+.077407...] end margins and full 2.22m width.
 var end_x:float=panel_reach+(1.17-1.0925925925925928)
 threshold_shape.size=Vector3(end_x+.07,2.,2.22);threshold_center_x=(end_x-.07)*.5
 var pivot:Node3D=source.find_child("BRIDGE_MOVING_PANEL",true,false)
 assert(pivot!=null,"Retained explicit hinge datum is required")
 moving=AnimatableBody3D.new();moving.name="AuthoredMovingBridge";moving.sync_to_physics=false;add_child(moving)
 var meshes:Array[Node]=pivot.find_children("*","MeshInstance3D",true,false)
 for mesh:MeshInstance3D in meshes:
  var pose:Transform3D=moving.global_transform.affine_inverse()*mesh.global_transform
  mesh.reparent(moving,true);mesh.transform=pose
  var contact:=CollisionShape3D.new();contact.shape=mesh.mesh.create_convex_shape(false,false)
  contact.transform=pose;moving.add_child(contact)
 var fixed:Node3D=source.find_child("BRIDGE_FIXED_RECEIVER_ROOT",true,false);assert(fixed!=null)
 load("res://scripts/static_contact_cache.gd").attach_group(fixed,fixed.find_children("*","MeshInstance3D",true,false))
 moving.rotation.z=PI/2;moving.sync_to_physics=true
func request_deploy()->bool:
 if not dock_authorized:return false
 requested_deployed=true;return true
func request_stow()->void:requested_deployed=false
func threshold_occupied()->bool:
 assert(threshold_shape!=null,"Bridge readiness cannot precede source loading")
 var query:=PhysicsShapeQueryParameters3D.new();query.shape=threshold_shape
 query.transform=global_transform*Transform3D(Basis.IDENTITY,Vector3(threshold_center_x,1.0,0))
 for hit in get_world_3d().direct_space_state.intersect_shape(query,64):
  if hit.collider is CharacterBody3D or hit.collider is RigidBody3D:return true
 return false
func safe_to_depart()->bool:
 return fraction<.0001 and not threshold_occupied()
func _physics_process(delta:float)->void:
 var target:=1.0 if requested_deployed and dock_authorized else 0.0
 if is_equal_approx(target,fraction):return
 obstructed=threshold_occupied()
 if obstructed:return
 fraction=move_toward(fraction,target,delta*.5)
 moving.rotation.z=(1.0-fraction)*PI/2
