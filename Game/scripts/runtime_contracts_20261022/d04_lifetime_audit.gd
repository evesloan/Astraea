extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 assert(ProjectSettings.load_resource_pack("/tmp/astraea-laptop-contract-1bc13d51/Astraea-1bc13d51.pck"))
 var index:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/startup_residency_20261020/private_shells_d04.json"))
 var results:Array=[]
 for key in index.rooms.keys().slice(0,3):
  var record:Dictionary=index.rooms[key]
  var scene:PackedScene=load(record.detail_path)
  var state:=scene.get_state();var main:={};var shadow:={};var geometry:={};var main_shadow_aliases:=0
  for n in state.get_node_count():
   for p in state.get_node_property_count(n):
    if state.get_node_property_name(n,p)!="mesh":continue
    var mesh:Mesh=state.get_node_property_value(n,p)
    if mesh==null:continue
    main[mesh.get_instance_id()]=true
    var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(mesh.get_faces().to_byte_array());var digest:=h.finish().hex_encode()
    geometry[digest]=int(geometry.get(digest,0))+1
    if mesh is ArrayMesh and mesh.shadow_mesh!=null:
     shadow[mesh.shadow_mesh.get_instance_id()]=true
     if mesh.shadow_mesh==mesh:main_shadow_aliases+=1
  var first:Node=scene.instantiate();var second:Node=scene.instantiate();var combined:={};var instance_meshes:=0
  for instance:Node in [first,second]:
   for mesh:MeshInstance3D in instance.find_children("*","MeshInstance3D",true,false):
    if mesh.mesh!=null:combined[mesh.mesh.get_instance_id()]=true;instance_meshes+=1
  var row:={"model":key,"main_mesh_resources":main.size(),"additional_shadow_resources":shadow.size(),"self_shadow_aliases":main_shadow_aliases,"unique_triangle_geometry":geometry.size(),"two_instances_mesh_nodes":instance_meshes,"two_instances_unique_mesh_resources":combined.size(),"duplicate_instance_resource_growth":combined.size()-main.size()}
  assert(combined.size()==main.size(),"Unexpected per-instance mesh duplication")
  first.free();second.free();results.append(row)
  scene=null;state=null
  await process_frame
 var f:=FileAccess.open("/tmp/astraea-pack-inspection/D04_LIFETIME_AUDIT.json",FileAccess.WRITE);f.store_string(JSON.stringify({"source_revision":"1bc13d51","samples":results,"ship_launched":false,"rid_cause_proven":false},"  "));f.close();print(JSON.stringify(results));quit()
