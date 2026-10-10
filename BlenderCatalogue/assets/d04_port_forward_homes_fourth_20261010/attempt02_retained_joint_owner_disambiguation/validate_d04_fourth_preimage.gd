extends SceneTree
var checks:Dictionary={}
var failures:Array=[]
func record(k:String,ok:bool,detail:Variant=null)->void:
 checks[k]=ok
 if not ok:failures.append({"key":k,"detail":detail})
func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func _initialize()->void:call_deferred("run")
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_forward_homes_fourth_20261010/PLAN.json"))
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(90):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.global_position=Vector3(-44,16.53,-328);player.velocity=Vector3.ZERO
 ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
 for i in range(15):await physics_frame
 var space:=ship.get_world_3d().direct_space_state;var receiving:Node3D=ship.find_child("D04PortForwardNorthernReceiving",true,false);var receipts:Array=[]
 for f in p.source_pins:record("pin_"+str(f),FileAccess.get_sha256("/workspace/astraea-recovered-532087b9-20261010T083844Z/"+str(f))==p.source_pins[f])
 for g in p.guard_preimages:
  var mesh:MeshInstance3D=receiving.find_child(g.name,true,false);var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for v in g.preimage.verts:lo=lo.min(vec(v));hi=hi.max(vec(v))
  var b:AABB=mesh.global_transform*mesh.get_aabb();record("guard_"+str(g.name),b.position.distance_to(lo)<.00005 and b.end.distance_to(hi)<.00005)
 for i in range(p.transfer_contact_samples.size()):
  var f:Dictionary=p.transfer_contact_samples[i]
  for dx in[-.05,0,.05]:
   for dz in[-.05,0,.05]:
    var at:=vec(f.at)+Vector3(dx,0,dz);var h:Dictionary=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.02,at-Vector3.UP*.02));var owner:String=""if h.is_empty()else str(h.collider.get_parent().name);record("bearing_"+str(i)+"_"+str(dx)+"_"+str(dz),owner==str(f.owner)and absf(h.position.y-16.26)<.002,owner)
 var all:Array=p.commons_parts+p.guard_successor_parts
 for r in p.rooms:all+=r.parts
 for part in all:
  if not part.runtime_collision:continue
  var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for v in part.verts:lo=lo.min(vec(v));hi=hi.max(vec(v))
  var size:=hi-lo-Vector3.ONE*.004
  if size.x<=0 or size.y<=0 or size.z<=0:continue
  var points:=PackedVector3Array();var center:=(hi+lo)/2;var factor:=size/(hi-lo)
  for v in part.verts:points.append(center+(vec(v)-center)*factor)
  var shape:=ConvexPolygonShape3D.new();shape.points=points;shape.margin=0;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=Transform3D.IDENTITY;var bad:Array=[]
  for h in space.intersect_shape(q,128):
   var name:=str(h.collider.get_parent().name)
   if name not in["D04NR_WestGuard_1","D04NR_EastGuard_0"]:bad.append(str(h.collider.get_path()))
  record("volume_"+str(part.name),bad.is_empty(),bad);receipts.append({"part":part.name,"foreign_contacts":bad,"query_inset_m":.002,"convex_candidate_hull":true})
 var result={"status":"PASS"if failures.is_empty()else"FAIL","plan_sha256":FileAccess.get_sha256("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_forward_homes_fourth_20261010/PLAN.json"),"source_pins":p.source_pins.size(),"transfer_sample_count":p.transfer_contact_samples.size()*9,"candidate_foreign_volume_queries":receipts,"checks":checks.size(),"failures":failures,"ray_excludes":0,"primary_load_accepted":false,"source_geometry_modified":false}
 FileAccess.open("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_forward_homes_fourth_20261010/PREIMAGE_SUPPORT.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":result.checks,"failures":failures}));quit(0 if failures.is_empty()else 1)
