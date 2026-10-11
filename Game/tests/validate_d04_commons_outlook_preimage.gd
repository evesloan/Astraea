extends SceneTree
var checks:Dictionary={}
var errors:Array=[]
func record(k:String,ok:bool)->void:
 checks[k]=ok
 if not ok:errors.append(k)
func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func _initialize()->void:call_deferred("run")
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://../BlenderCatalogue/assets/d04_commons_outlook_service_20261011/PLAN.json"))
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(90):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state
 for f in p.source_pins:record("source_"+str(f),FileAccess.get_sha256("/workspace/astraea-recovered-532087b9-20261010T083844Z/"+str(f))==p.source_pins[f])
 var mesh:MeshInstance3D=ship.find_child(p.preimage.name,true,false);var low:=Vector3(INF,INF,INF);var high:=-low
 for v in p.preimage.verts:low=low.min(vec(v));high=high.max(vec(v))
 record("exact_screen_preimage",mesh!=null and (mesh.global_transform*mesh.get_aabb()).position.distance_to(low)<.00004 and (mesh.global_transform*mesh.get_aabb()).end.distance_to(high)<.00004)
 for item in p.outlook_cases:
  var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(vec(item.eye),vec(item.target)));record(str(item.name)+"_blocked_by_screen",not h.is_empty() and str(h.collider.get_parent().name)==p.preimage.name)
 var query:=PhysicsShapeQueryParameters3D.new();var b:=BoxShape3D.new();b.size=Vector3(.24,1.194,4.994);query.shape=b;query.transform=Transform3D(Basis.IDENTITY,Vector3(-72.91,17.85,-371));var unexpected:Array=[]
 for h in space.intersect_shape(query,128):
  if str(h.collider.get_parent().name)!=p.preimage.name:unexpected.append(str(h.collider.get_path()))
 record("bounded_glass_replacement_no_other_contacts",unexpected.is_empty())
 var result={"status":"PASS"if errors.is_empty()else"FAIL","checks":checks.size(),"errors":errors,"unexpected_contacts":unexpected,"new_floor_m2":0};FileAccess.open("res://artifacts/d04_commons_outlook_preimage.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify(result));quit(0 if errors.is_empty()else 1)
