extends SceneTree
const P:="res://sunset_specialty_bank_20261022/"
func _initialize()->void:call_deferred("run")
func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func arr(p:Vector3)->Array:return [p.x,p.y,p.z]
func own(n:Node,r:Node)->void:
 for c in n.get_children():c.owner=r;own(c,r)
func save_scene(n:Node3D,path:String)->void:
 own(n,n);var p:=PackedScene.new();assert(p.pack(n)==OK);assert(not FileAccess.file_exists(path));assert(ResourceSaver.save(p,path,ResourceSaver.FLAG_COMPRESS)==OK)
func bounds(n:Node3D)->AABB:
 var box:=AABB();var first:=true
 for mesh:MeshInstance3D in n.find_children("*","MeshInstance3D",true,false):
  if mesh.mesh==null:continue
  var b:AABB=mesh.global_transform*mesh.get_aabb();box=b if first else box.merge(b);first=false
 assert(not first);return box
func run()->void:
 assert(ProjectSettings.load_resource_pack("/tmp/astraea-laptop-contract-1bc13d51/Astraea-1bc13d51.pck"))
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/Astraea-recovered-e6274e77-20261021/BlenderCatalogue/assets/sunset_specialty_bank_20261022/PLAN.json"))
 var index:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://quiet_grove_bank_20261022/evidence/INDEX.json")).rooms
 var corrections:Dictionary={}
 for row:Dictionary in JSON.parse_string(FileAccess.get_file_as_string("res://quiet_grove_bank_20261022/ENCLOSURES_R002.json")).rooms:corrections[int(row.index)]=row
 var result:Dictionary={"rooms":{},"status":"PASS","main_integrated":false,"native_sources":47,"new_capacity":0}
 for room:Dictionary in plan.rooms:
  var source:Dictionary=index[room.source_room_model]
  assert(FileAccess.get_sha256(source.shell_path)==source.shell_sha256 and FileAccess.get_sha256(source.detail_path)==source.detail_sha256)
  var shell:Node3D=load(source.shell_path).instantiate();var detail:Node3D=load(source.detail_path).instantiate()
  if corrections.has(int(room.source_allocation)):
   for part:Dictionary in corrections[int(room.source_allocation)].parts:
    var mesh:MeshInstance3D=shell.find_child(part.name,true,false)
    assert(mesh!=null)
    mesh.transform=Transform3D(Basis(Vector3.UP,float(part.yaw_delta)),v(part.target))*Transform3D(Basis.IDENTITY,-v(part.source))*mesh.transform
  var full:Node3D=shell.duplicate()
  for path:String in source.detail_mesh_paths:
   var mesh:MeshInstance3D=full.get_node(path);var from:MeshInstance3D=detail.get_node(path);assert(mesh.mesh==null and from.mesh!=null);mesh.mesh=from.mesh
  var containers:Array[Node3D]=[]
  for n:Node3D in [full,shell,detail]:
   var wrapper:=Node3D.new();wrapper.name="SunsetSpecialty";n.name="RetainedComposition";wrapper.add_child(n);root.add_child(wrapper)
   n.transform=Transform3D(Basis(Vector3.UP,PI),v(room.placement.translation));containers.append(wrapper)
  var model:String="SunsetSpecialty_%s_r001.scn"%str(room.allocation.source_envelope_index)
  var box:=bounds(containers[0]);var detail_box:=bounds(containers[2])
  var shell_paths:Array=[];var detail_paths:Array=[]
  for path:String in source.shell_mesh_paths:shell_paths.append("RetainedComposition/"+path)
  for path:String in source.detail_mesh_paths:detail_paths.append("RetainedComposition/"+path)
  var shell_path:String=P+"runtime/"+model.replace(".scn",".shell.scn");var detail_path:String=P+"runtime/"+model.replace(".scn",".detail.scn")
  save_scene(containers[0],"res://assets/models/"+model);save_scene(containers[1],shell_path);save_scene(containers[2],detail_path)
  var record:Dictionary=source.duplicate(true)
  record.merge({"model_file":model,"sha256":FileAccess.get_sha256("res://assets/models/"+model),"room_id":room.allocation.proposed_runtime_id,"shell_path":shell_path,"shell_sha256":FileAccess.get_sha256(shell_path),"detail_path":detail_path,"detail_sha256":FileAccess.get_sha256(detail_path),"shell_mesh_paths":shell_paths,"detail_mesh_paths":detail_paths,"bounds_min":arr(box.position),"bounds_max":arr(box.end),"detail_bounds_min":arr(detail_box.position),"detail_bounds_max":arr(detail_box.end)},true)
  result.rooms[model]=record;room.model_file=model;room.model_sha256=record.sha256
  for n:Node3D in containers:n.free()
  print("SUNSET_BAKED ",room.allocation.source_envelope_index)
 var f:=FileAccess.open(P+"evidence/INDEX.json",FileAccess.WRITE);f.store_string(JSON.stringify(result,"\t")+"\n");f.close()
 f=FileAccess.open(P+"PACKAGE.json",FileAccess.WRITE);f.store_string(JSON.stringify(plan,"\t")+"\n");f.close();quit()
