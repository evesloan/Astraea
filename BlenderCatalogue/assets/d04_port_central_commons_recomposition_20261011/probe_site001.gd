extends SceneTree
func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func _initialize()->void:call_deferred("run")
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_central_commons_recomposition_20261011/AUDIT_INPUT_PLAN.json"))
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var d:Node3D=ship.get_node("ShipSpace/Districts");var space:=ship.get_world_3d().direct_space_state;var meshes:Array=[];var floors:Array=[];var bearings:Array=[];var stances:Array=[]
 var targets:Array=p.cuts.duplicate();targets.append_array(p.moves)
 for row in targets:
  var mesh:MeshInstance3D=d.get_node(row.source_root).find_child(row.name,true,false);assert(mesh!=null);var a:AABB=mesh.global_transform*mesh.get_aabb();var faces:Array=[]
  for v in mesh.mesh.get_faces():var q:Vector3=mesh.global_transform*v;faces.append([q.x,q.y,q.z])
  meshes.append({"name":row.name,"source_root":row.source_root,"bounds":[[a.position.x,a.position.y,a.position.z],[a.end.x,a.end.y,a.end.z]],"world_triangle_vertices":faces})
 FileAccess.open("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_central_commons_recomposition_20261011/SITE_PREFLIGHT001.json",FileAccess.WRITE).store_string(JSON.stringify({"meshes":meshes,"floors":floors,"bearings":bearings,"stances":stances,"supports":supports,"roof_rows":roof_rows,"ledgers":ledgers},"  "));print("Court work-link site preflight complete");quit()
