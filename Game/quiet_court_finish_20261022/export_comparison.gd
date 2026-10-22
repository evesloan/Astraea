extends SceneTree
const P:="res://quiet_court_finish_20261022/"
func _initialize()->void:call_deferred("run")
func points(part:Node3D)->Array:
 var out:Array=[]
 for mesh:MeshInstance3D in part.find_children("*","MeshInstance3D",true,false):
  if mesh.mesh==null:continue
  var pose:Transform3D=part.global_transform.affine_inverse()*mesh.global_transform
  for v in mesh.mesh.get_faces():
   var a:Vector3=pose*v;out.append([a.x,a.y,a.z])
 return out
func run()->void:
 var a:Node3D=load(P+"runtime/QuietGroveCourtPlanting_r003.scn").instantiate();root.add_child(a)
 var b:Node3D=load(P+"planting_batched.gd").build();root.add_child(b)
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN_R003.json"));var result:Array=[]
 for row in plan.placements:
  var aa:=a.find_child(str(row.name),true,false)as Node3D;var bb:=b.get_node(str(row.name))as Node3D
  result.append({"name":row.name,"source":points(aa),"batched":points(bb),"pose_equal":aa.global_transform.is_equal_approx(bb.global_transform)})
 var f:=FileAccess.open("/tmp/quiet-court-geometry-comparison.json",FileAccess.WRITE);f.store_string(JSON.stringify(result));f.close();a.free();b.free();quit()
