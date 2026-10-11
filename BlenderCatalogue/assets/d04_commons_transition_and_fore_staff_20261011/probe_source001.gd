extends SceneTree
func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func _initialize():call_deferred("run")
func run():
 var path="res://../BlenderCatalogue/assets/d04_commons_transition_and_fore_staff_20261011/";var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(path+"PLAN.json"));var main=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship=main.get_node("World360/Astraea");var rows:Array=[];var space=ship.get_world_3d().direct_space_state;var targets:Array=[]
 for q in p.fore_cuts:targets.append({"name":q.name,"model":q.source_model,"expected_bounds":q.bounds})
 for q in p.fore_original_court_preimages:
  var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for a in q.preimage.verts:lo=lo.min(v(a));hi=hi.max(v(a))
  targets.append({"name":q.preimage.name,"model":q.model_file,"expected_bounds":[[lo.x,lo.y,lo.z],[hi.x,hi.y,hi.z]]})
 for q in targets:
  var mesh:MeshInstance3D=ship.find_child(q.name,true,false);assert(mesh!=null);var a:AABB=mesh.global_transform*mesh.get_aabb();assert(a.position.distance_to(v(q.expected_bounds[0]))<.00015 and a.end.distance_to(v(q.expected_bounds[1]))<.00015);var vs:Array=[]
  for point in mesh.mesh.get_faces():var at:Vector3=mesh.global_transform*point;vs.append([at.x,at.y,at.z])
  rows.append({"name":q.name,"source_path":str(mesh.get_path()),"source_model":q.model,"world_triangle_vertices":vs,"bounds":[[a.position.x,a.position.y,a.position.z],[a.end.x,a.end.y,a.end.z]]})
 var commons:Array=[]
 for a in [Vector3(-75,16.5,-5),Vector3(-71.8,16.5,-5),Vector3(-75,16.5,-3.48),Vector3(-71.8,16.5,-3.48),Vector3(-84,16.5,-11.4),Vector3(-75,16.5,-12.5)]:
  var cap:=CapsuleShape3D.new();cap.height=1.8;cap.radius=.3;cap.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=cap;q.transform=Transform3D(Basis.IDENTITY,a+Vector3.UP*.925);var hits=space.intersect_shape(q,64);var upper=space.intersect_ray(PhysicsRayQueryParameters3D.create(a+Vector3.UP*1.9,a+Vector3.UP*4));var floor=space.intersect_ray(PhysicsRayQueryParameters3D.create(a+Vector3.UP*.05,a-Vector3.UP*.1));commons.append({"at":[a.x,a.y,a.z],"worker_blockers":hits.map(func(h):return str(h.collider.get_path())),"floor":{}if floor.is_empty()else{"y":floor.position.y,"owner":str(floor.collider.get_path())},"ceiling":{}if upper.is_empty()else{"y":upper.position.y,"owner":str(upper.collider.get_path())}})
 var cap:=CapsuleShape3D.new();cap.height=2.4;cap.radius=.5;var q:=PhysicsShapeQueryParameters3D.new();q.shape=cap;q.transform=Transform3D(Basis.IDENTITY,Vector3(-75,17.74,-12.5));var hits=space.intersect_shape(q,64)
 FileAccess.open(path+"SOURCE_PREFLIGHT.json",FileAccess.WRITE).store_string(JSON.stringify({"fore_runtime_preimages":rows,"commons_original_cells":commons,"northern_service_rear_broad_public_capsule_blockers":hits.map(func(h):return str(h.collider.get_path()))},"  "));print("Actual source preimages/commons interfaces captured");quit()
