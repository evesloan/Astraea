extends SceneTree
var failures:Array=[]
func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func _initialize()->void:call_deferred("run")
func run()->void:
 var repo:String="/workspace/astraea-recovered-532087b9-20261010T083844Z/"
 var path:String=repo+"BlenderCatalogue/assets/d04_port_forward_northern_receiving_20261010/BUILD_PLAN.json"
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(path))
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(90):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea")
 ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(Vector3(-44,12.02,-324.5))
 for i in range(2):await physics_frame
 paused=true
 var space:=ship.get_world_3d().direct_space_state
 for f in p.source_pins:
  if FileAccess.get_sha256(repo+str(f))!=p.source_pins[f]:failures.append("source_pin_"+str(f))
 var bearings:Array=[];var volumes:Array=[];var guards:Array=[]
 var hull:Node=ship.find_child(p.foundation_owner,true,false)
 for i in range(p.foundation_feet.size()):
  var f:Dictionary=p.foundation_feet[i]
  for dx in[-.38,0,.38]:
   for dz in[-.38,0,.38]:
    var at:=Vector3(f.x+dx,p.foundation_y,f.z+dz)
    var h:Dictionary=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.035,at-Vector3.UP*.035))
    var valid:bool=not h.is_empty()and hull!=null and hull.is_ancestor_of(h.collider)and str(h.collider.get_parent().name)==p.foundation_source_mesh and absf(h.position.y-p.foundation_y)<.002
    bearings.append({"foot":i,"at":str(at),"valid":valid,"hit":""if h.is_empty()else str(h.collider.get_path()),"y":null if h.is_empty()else h.position.y})
    if not valid:failures.append("keel_bearing_"+str(i)+"_"+str(dx)+"_"+str(dz))
 var approved_guard_names:Array=p.guard_preimages.map(func(a):return str(a.name))
 var old:Node=ship.find_child("D04PortForwardReceiving",true,false)
 for g in p.guard_preimages:
  var mesh:MeshInstance3D=old.find_child(str(g.name),true,false)
  var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for vertex in g.verts:lo=lo.min(vec(vertex));hi=hi.max(vec(vertex))
  var valid:bool=mesh!=null
  if valid:
   var bounds:AABB=mesh.global_transform*mesh.get_aabb();valid=bounds.position.distance_to(lo)<.00005 and bounds.end.distance_to(hi)<.00005
  guards.append({"name":g.name,"valid":valid,"min":str(lo),"max":str(hi)})
  if not valid:failures.append("guard_preimage_"+str(g.name))
 for part in p.parts:
  if not part.runtime_collision:continue
  var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for vertex in part.verts:lo=lo.min(vec(vertex));hi=hi.max(vec(vertex))
  var inset:=Vector3.ONE*.002;var shape:=BoxShape3D.new();shape.size=hi-lo-inset*2;shape.margin=.001
  var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,(lo+hi)/2)
  var all_hits:Array=[];var foreign:Array=[]
  for h in space.intersect_shape(q,256):
   var name:String=str(h.collider.get_parent().name);all_hits.append(str(h.collider.get_path()))
   if not name in approved_guard_names:foreign.append(str(h.collider.get_path()))
  volumes.append({"part":part.name,"category":part.category,"query_inset_m":.002,"all_contacts":all_hits,"unapproved_contacts":foreign})
  if not foreign.is_empty():failures.append("candidate_foreign_volume_"+str(part.name));print("FOREIGN_CANDIDATE ",part.name," ",foreign)
 var result={"status":"PASS"if failures.is_empty()else"FAIL","plan_sha256":FileAccess.get_sha256(path),"source_pins_verified":p.source_pins.size(),"bearing_sample_count":bearings.size(),"bearings":bearings,"candidate_part_volumes":volumes,"exact_guard_preimages":guards,"failures":failures,"ray_excludes":0,"original_source_untouched":true,"new_runtime_installed":false,"primary_load_accepted":false,"cart_safe_vertical_accepted":false,"ordinary_graphics_review":false}
 FileAccess.open(repo+"BlenderCatalogue/assets/d04_port_forward_northern_receiving_20261010/PREIMAGE_SUPPORT.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
 print(JSON.stringify({"status":result.status,"bearings":bearings.size(),"volumes":volumes.size(),"errors":failures}));quit(0 if failures.is_empty()else 1)
