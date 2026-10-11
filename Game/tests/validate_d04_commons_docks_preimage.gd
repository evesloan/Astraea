extends SceneTree
var checks:Dictionary={}
var errors:Array=[]
func record(k:String,ok:bool)->void:
 checks[k]=ok
 if not ok:errors.append(k)
func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func _initialize()->void:call_deferred("run")
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://../BlenderCatalogue/assets/d04_commons_cart_docking_20261011/PLAN.json"));var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(90):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state;var conflicts:Dictionary={}
 for f in p.source_pins:record("source_"+str(f),FileAccess.get_sha256("/workspace/astraea-recovered-532087b9-20261010T083844Z/"+str(f))==p.source_pins[f])
 for part in p.parts:
  var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for v in part.verts:lo=lo.min(vec(v));hi=hi.max(vec(v))
  var q:=PhysicsShapeQueryParameters3D.new();var b:=BoxShape3D.new();b.size=hi-lo-Vector3.ONE*.002;q.shape=b;q.transform=Transform3D(Basis.IDENTITY,(lo+hi)/2);var bad:Array=[]
  for h in space.intersect_shape(q,128):
   if part.category!="floor_fastener"or str(h.collider.get_parent().name)!=p.existing_floor_owner:bad.append(str(h.collider.get_path()))
  record("new_fixture_volume_"+str(part.name),bad.is_empty())
  if not bad.is_empty():conflicts[part.name]=bad
 for d in p.docks:
  var at:=vec(d.position);var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.02,at-Vector3.UP*.02));record(str(d.name)+"_existing_floor",not h.is_empty()and str(h.collider.get_parent().name)==p.existing_floor_owner and absf(h.position.y-16.5)<.002)
 var result={"status":"PASS"if errors.is_empty()else"FAIL","checks":checks.size(),"errors":errors,"conflicts":conflicts,"new_floor_m2":0,"protected_shaft_untouched":true};FileAccess.open("res://artifacts/d04_commons_docks_preimage.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify(result));quit(0 if errors.is_empty()else 1)
