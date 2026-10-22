extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 assert(ProjectSettings.load_resource_pack("/tmp/astraea-laptop-contract-1bc13d51/Astraea-1bc13d51.pck"))
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/startup_residency_20261020/private_shells_d04.json"))
 var rows:Array=[];var total_main:=0;var total_shadow:=0;var self_shadow:=0;var local_resources:=0
 for key in data.rooms:
  var record:Dictionary=data.rooms[key];var scene:PackedScene=load(record.detail_path);var state:=scene.get_state();var meshes:={};var shadows:={}
  for n in state.get_node_count():
   for p in state.get_node_property_count(n):
    if state.get_node_property_name(n,p)!="mesh":continue
    var mesh:Mesh=state.get_node_property_value(n,p)
    if mesh==null:continue
    meshes[mesh.get_instance_id()]=true
    if mesh.resource_local_to_scene:local_resources+=1
    if mesh is ArrayMesh and mesh.shadow_mesh!=null:
     shadows[mesh.shadow_mesh.get_instance_id()]=true
     if mesh.shadow_mesh==mesh:self_shadow+=1
  rows.append({"model":key,"main":meshes.size(),"shadow":shadows.size()});total_main+=meshes.size();total_shadow+=shadows.size()
  scene=null;state=null
  await process_frame
 var result:={"source_revision":"1bc13d51","rooms":rows.size(),"sum_per_room_main_mesh_resources":total_main,"sum_per_room_shadow_mesh_resources":total_shadow,"sum_per_room_mesh_resources":total_main+total_shadow,"resource_local_to_scene":local_resources,"self_shadow_meshes":self_shadow,"interpretation":"Serialized per-room sum, not measured simultaneous whole-ship residency. No whole ship instantiated; no RID cause or performance acceptance inferred.","rows":rows}
 var f:=FileAccess.open("/tmp/astraea-pack-inspection/D04_RESOURCE_CENSUS.json",FileAccess.WRITE);f.store_string(JSON.stringify(result,"  "));f.close();result.erase("rows");print(JSON.stringify(result));quit()
