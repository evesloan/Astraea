extends SceneTree
var checks:Dictionary={}
var errors:Array=[]
func record(key:String,ok:bool)->void:
 checks[key]=ok
 if not ok:errors.append(key)
func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func _initialize()->void:call_deferred("run")
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://../BlenderCatalogue/assets/d04_commons_social_dayroom_20261011/PLAN.json"))
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(90):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state
 for f in p.source_pins:record("source_"+str(f),FileAccess.get_sha256("/workspace/astraea-recovered-532087b9-20261010T083844Z/"+str(f))==p.source_pins[f])
 var pre:Dictionary=p.preimages[0];var mesh:MeshInstance3D=ship.find_child(pre.name,true,false);var low:=Vector3(INF,INF,INF);var high:=-low
 for v in pre.verts:low=low.min(vec(v));high=high.max(vec(v))
 record("exact_preimage",mesh!=null and (mesh.global_transform*mesh.get_aabb()).position.distance_to(low)<.00004 and (mesh.global_transform*mesh.get_aabb()).end.distance_to(high)<.00004)
 for i in range(p.foundation_feet.size()):
  for dx in[-.44,0,.44]:
   for dz in[-.44,0,.44]:
    var at:=vec(p.foundation_feet[i].at)+Vector3(dx,-.3,dz);var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(at-Vector3.UP*.02,at+Vector3.UP*.02));record("keel_"+str(i)+"_"+str(dx)+"_"+str(dz),not h.is_empty() and str(h.collider.get_parent().name)=="HUL_KeelPan"and absf(h.position.y+3.5)<.002)
 var q:=PhysicsShapeQueryParameters3D.new();var b:=BoxShape3D.new();b.size=Vector3(11.78,.20,11.88);q.shape=b;q.transform=Transform3D(Basis.IDENTITY,Vector3(-78.9,16.38,-369.95));var floor_hits:Array=[]
 for h in space.intersect_shape(q,256):floor_hits.append(str(h.collider.get_path()))
 record("missing_floor_volume_clear",floor_hits.is_empty())
 b=BoxShape3D.new();b.size=Vector3(11.4,3.7,11.4);q.shape=b;q.transform=Transform3D(Basis.IDENTITY,Vector3(-78.9,18.48,-369.95));var room_hits:Array=[]
 for h in space.intersect_shape(q,256):room_hits.append(str(h.collider.get_path()))
 record("missing_room_volume_clear",room_hits.is_empty())
 var result={"status":"PASS"if errors.is_empty()else"FAIL","checks":checks.size(),"errors":errors,"floor_hits":floor_hits,"room_hits":room_hits,"source_pin_count":p.source_pins.size()};FileAccess.open("res://artifacts/d04_social_dayroom_preimage.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify(result));quit(0 if errors.is_empty()else 1)
