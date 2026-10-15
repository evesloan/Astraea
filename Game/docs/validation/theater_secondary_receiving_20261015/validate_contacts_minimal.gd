extends SceneTree
const D="/workspace/astraea-integration-cutoff-20261013/theater_secondary_receiving_20261015/"
func _initialize()->void:
 assert(ProjectSettings.load_resource_pack(D+"CANDIDATE_OVERLAY.zip",true));call_deferred("run")
func at_contact(space:PhysicsDirectSpaceState3D,point:Vector3,needle:String)->bool:
 for axis:Vector3 in[Vector3.RIGHT,Vector3.UP,Vector3.FORWARD]:
  for sign_value in[-1.,1.]:
   var q:=PhysicsRayQueryParameters3D.create(point-axis*.24*sign_value,point+axis*.24*sign_value)
   for i in range(20):
    var hit:Dictionary=space.intersect_ray(q)
    if hit.is_empty():break
    if str(hit.collider.get_path()).contains(needle):return true
    var ex:Array[RID]=q.exclude;ex.append(hit.collider.get_rid());q.exclude=ex
 return false
func run()->void:
 var source:Node3D=(load("res://assets/models/AST-CUL-005_static_003.glb")as PackedScene).instantiate();root.add_child(source);var world:=source.get_world_3d()
 for key in["C005_S_0572","C005_S_0680"]:load("res://scripts/static_contact_cache.gd").attach(source.find_child(key,true,false))
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"NATIVE_VERIFICATION.json"));var made:Array=[]
 for row in data.models:
  if row.deck=="D11":continue
  var model:Node3D=(load("res://assets/theater_secondary_receiving_20261015/"+str(row.file))as PackedScene).instantiate();model.name=str(row.deck)+"Secondary";root.add_child(model);made.append(model);load("res://scripts/static_contact_cache.gd").attach_group(model,model.find_children("*","MeshInstance3D",true,false))
 for i in range(3):await physics_frame
 for y in[78.,84.]:
  for z in[-172.5,-171.,-169.5]:
   var point:=Vector3(-35.3,y-.11,z)
   assert(at_contact(world.direct_space_state,point,"C005_S_"),"Known actual native floor contact")
   assert(at_contact(world.direct_space_state,point,"Secondary/"),"Exact new below-floor lap contact")
 print("PASS_MINIMAL_UPPER_RECEIVING_CONTACTS six exact old/new joins;both ray directions")
 source.queue_free()
 for model in made:model.queue_free()
 for i in range(3):await physics_frame
 quit(0)
