extends RefCounted
# Named initialization-only successor. The contact construction below is the
# exact retained source factory suffix; the imported convex floor is unchanged.
const MODELS := "res://source_derivatives/group4_boarding_safety_20261011/"

static func verify()->bool:
 var c:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tram_passenger_successor_20261024/CONTRACTS_r002.json"))
 for bucket:Dictionary in [c.prerequisites,c.owned]:
  for path:String in bucket:
   if FileAccess.get_sha256(path)!=str(bucket[path]):
    push_error("Initial-pose exact source mismatch: "+path);return false
 return true

static func create_candidate_vehicle(parent:Node3D,initial_pose:Transform3D)->AnimatableBody3D:
 # Construction test factory. No cart/products, motor, save identity or transport controller is created.
 if not verify():return null
 var source=load("res://scripts/group4_boarding_safety.gd")
 var p:Dictionary=source.data();var item:Dictionary=source.model("vehicle",p)
 assert(FileAccess.get_sha256(MODELS+item.file)==item.sha256)
 var body:=AnimatableBody3D.new();body.name="Group4OwnedTram_Source024";body.sync_to_physics=false
 # Full LOCAL transform is assigned before first ENTER_TREE / ENTER_WORLD.
 # No server velocity reset, live move, contact exclusion or actor relocation.
 body.transform=initial_pose
 body.set_meta("source_vehicle_model",item.file)
 body.set_meta("initial_pose_before_tree",initial_pose)
 parent.add_child(body)
 var visual:Node3D=(load(MODELS+item.file) as PackedScene).instantiate();body.add_child(visual)
 var c:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(MODELS+"VEHICLE_COLLISION_PROPOSAL.json"))
 var modified:Dictionary={}
 for key:String in c.modified_members:modified[key.validate_node_name()]=c.modified_members[key]
 var policies:Dictionary={}
 for key:String in item.policies:
  var name:String=key.validate_node_name();assert(not policies.has(name));policies[name]=item.policies[key]
 for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
  assert(policies.has(str(mesh.name)),"Every source vehicle member requires its exact contact policy")
  if policies[str(mesh.name)]=="no_collision_detail":continue
  if modified.has(str(mesh.name)):
   for cell in modified[str(mesh.name)]:
    var shape:=ConvexPolygonShape3D.new();var points:=PackedVector3Array()
    for y in cell.y:
     for point in cell.triangle_xz:points.append(Vector3(point[0],y,point[1]))
    shape.points=points;shape.margin=.001;var col:=CollisionShape3D.new();col.shape=shape;body.add_child(col)
  else:
   var col:=CollisionShape3D.new();col.shape=mesh.mesh.create_convex_shape(false,false);col.shape.margin=.001
   col.transform=body.global_transform.affine_inverse()*mesh.global_transform;body.add_child(col)
 body.sync_to_physics=true;return body
