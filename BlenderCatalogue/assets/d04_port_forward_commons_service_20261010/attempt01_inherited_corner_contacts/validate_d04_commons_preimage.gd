extends SceneTree
var checks:Dictionary={}
var failures:Array=[]
const W="/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_forward_commons_service_20261010/"
func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func record(k:String,ok:bool,detail:Variant=null)->void:
 checks[k]=ok
 if not ok:failures.append({"key":k,"detail":detail})
func _initialize()->void:call_deferred("run")
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(W+"PLAN.json"))
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(90):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.global_position=Vector3(-66.1,16.53,-369.5);player.velocity=Vector3.ZERO;ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
 for i in range(15):await physics_frame
 var space:=ship.get_world_3d().direct_space_state
 for f in p.source_pins:record("pin_"+str(f),FileAccess.get_sha256("/workspace/astraea-recovered-532087b9-20261010T083844Z/"+str(f))==p.source_pins[f])
 for q in p.preimages:
  var mesh:MeshInstance3D=ship.find_child(q.name,true,false);var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for v in q.verts:lo=lo.min(vec(v));hi=hi.max(vec(v))
  record("preimage_"+str(q.name),mesh!=null and (mesh.global_transform*mesh.get_aabb()).position.distance_to(lo)<.00005 and (mesh.global_transform*mesh.get_aabb()).end.distance_to(hi)<.00005)
 for i in range(p.foundation_feet.size()):
  for dx in[-.35,0,.35]:
   for dz in[-.35,0,.35]:
    var at:=vec(p.foundation_feet[i].at)+Vector3(dx,0,dz);var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.02,at-Vector3.UP*.02));record("keel_"+str(i)+"_"+str(dx)+"_"+str(dz),not h.is_empty() and str(h.collider.get_parent().name)=="HUL_KeelPan" and absf(h.position.y+3.2)<.002,h.get("position"))
 var queries:Array=[]
 for part in p.parts+p.successor_parts:
  if not part.runtime_collision:continue
  var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for v in part.verts:lo=lo.min(vec(v));hi=hi.max(vec(v))
  var size:=hi-lo-Vector3.ONE*.004
  if size.x<=0 or size.y<=0 or size.z<=0:continue
  var points:=PackedVector3Array();var center:=(hi+lo)/2;var factor:=size/(hi-lo)
  for v in part.verts:points.append(center+(vec(v)-center)*factor)
  var shape:=ConvexPolygonShape3D.new();shape.points=points;shape.margin=0;var query:=PhysicsShapeQueryParameters3D.new();query.shape=shape;query.transform=Transform3D.IDENTITY;var bad:Array=[]
  for h in space.intersect_shape(query,128):
   if str(h.collider.get_parent().name) not in p.preimages.map(func(q):return str(q.name)):bad.append(str(h.collider.get_path()))
  record("volume_"+str(part.name),bad.is_empty(),bad);queries.append({"part":part.name,"foreign_contacts":bad,"inset_m":.002})
 var result={"status":"PASS"if failures.is_empty()else"FAIL","checks":checks.size(),"failures":failures,"plan_sha256":FileAccess.get_sha256(W+"PLAN.json"),"source_pins":p.source_pins.size(),"keel_top_samples":108,"candidate_foreign_volume_queries":queries,"ray_excludes":0,"primary_load_accepted":false}
 FileAccess.open(W+"PREIMAGE_SUPPORT.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks.size(),"failures":failures}));quit(0 if failures.is_empty()else 1)
