extends SceneTree
var output:String
var resource_copies:Dictionary={}
func independent(r:Resource)->Resource:
 if r==null:return null
 var id:=r.get_instance_id()
 if not resource_copies.has(id):resource_copies[id]=r.duplicate(true)
 return resource_copies[id]
func _initialize()->void:
 for a:String in OS.get_cmdline_user_args():
  if a.begins_with("--output="):output=a.substr(9)
 call_deferred("run")
func own(node:Node,top:Node)->void:
 node.scene_file_path=""
 if node is MeshInstance3D:
  node.mesh=independent(node.mesh)
  node.material_override=independent(node.material_override)
  if node.has_meta("precompiled_fallback"):
   var records:Array=node.get_meta("precompiled_fallback")
   for row:Array in records:row[1]=independent(row[1]);row[2]=independent(row[2])
  for surface in node.mesh.get_surface_count():node.set_surface_override_material(surface,independent(node.get_surface_override_material(surface)))
 for child:Node in node.get_children():
  child.owner=top;own(child,top)
func count(node:Node)->int:return node.find_children("*","",true,false).size()+1
func run()->void:
 var host:Node3D=load("res://visible_resource_budget_20261026/bank_fixture_host.gd").new();root.add_child(host)
 var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
 var systems:=Node.new();systems.name="ShipSystems";host.add_child(systems)
 var budget:Node=load("res://scripts/lighting_budget.gd").new();budget.name="LocalShadowSourceBudget";systems.add_child(budget)
 var bank:Node3D=load("res://scripts/group3_remaining_crew_20261019/package.gd").build(host)
 await process_frame
 var original_count:=count(bank);var original_meshes:=bank.find_children("*","MeshInstance3D",true,false).size()
 var doors:Dictionary={}
 for child:Node in bank.get_children():
  if child.get_script()!=null:doors[child.name]={"id":child.get_instance_id(),"persistent_id":str(child.persistent_id),"pose":child.transform}
 var lights:Array=[]
 for light:Light3D in budget.sources:lights.append({"id":light.get_instance_id(),"kind":1,"mask":light.light_cull_mask,"reach":light.omni_range,"position":light.global_position,"managed_eight":true})
 var result:Dictionary=load("res://precompiled_bank_cells_20261026/compiler.gd").build(bank,lights)
 assert(not result.has("failed"),str(result))
 for name:String in doors:
  var door:Node3D=bank.get_node(name);assert(door.get_instance_id()==doors[name].id and str(door.persistent_id)==doors[name].persistent_id and door.transform==doors[name].pose)
 # Save only immutable visual wrappers; existing runtime still constructs original doors/lights.
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_remaining_crew_20261019/PACKAGE.json"))
 var outputs:Array=[]
 for file:String in data.model_pins:
  var wrapper:Node3D=bank.get_node(file.trim_suffix(".glb"));own(wrapper,wrapper)
  var packed:=PackedScene.new();assert(packed.pack(wrapper)==OK)
  var path:="res://precompiled_bank_cells_20261026/r005/"+file.trim_suffix(".glb")+".scn"
  assert(not FileAccess.file_exists(path),"Preserve existing precompiled artifact")
  assert(ResourceSaver.save(packed,path,ResourceSaver.FLAG_COMPRESS)==OK)
  outputs.append({"path":path,"sha256":FileAccess.get_sha256(path),"source_sha256":data.model_pins[file],"nodes":count(wrapper),"mesh_nodes":wrapper.find_children("*","MeshInstance3D",true,false).size()})
 var final_count:=count(bank)
 var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify({"original_nodes":original_count,"compiled_nodes":final_count,"nodes_removed":original_count-final_count,"original_mesh_nodes":original_meshes,"compiled_mesh_nodes":bank.find_children("*","MeshInstance3D",true,false).size(),"doors_preserved":doors.size(),"compilation":result,"outputs":outputs,"status":"UNSELECTED_OFFLINE_ARTIFACT_RELOAD_AND_APPEARANCE_PENDING"},"\t"));f.close();host.free();quit()
