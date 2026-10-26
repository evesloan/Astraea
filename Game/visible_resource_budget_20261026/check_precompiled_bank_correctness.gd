extends SceneTree
var output:String
var samples:Array=[]
var camera:Camera3D
var weak_meshes:Array[WeakRef]=[]
func references(bank:Node3D)->Array[WeakRef]:
 var refs:Array[WeakRef]=[]
 for node:MeshInstance3D in bank.find_children("*","MeshInstance3D",true,false):
  if node.mesh!=null:refs.append(weakref(node.mesh))
 return refs
func _initialize()->void:
 for arg:String in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.substr(9)
 call_deferred("run")
func sample(stage:String)->void:samples.append({"stage":stage,"static_bytes":OS.get_static_memory_usage(),"nodes":Performance.get_monitor(Performance.OBJECT_NODE_COUNT),"video_bytes":Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED)})
func view(stage:String)->void:
 for i in 10:await process_frame
 var frames:Array=[];var draws:Array=[];var primitives:Array=[];var previous:=Time.get_ticks_usec()
 for i in 40:
  await process_frame
  var now:=Time.get_ticks_usec();frames.append((now-previous)/1000.0);previous=now
  draws.append(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME));primitives.append(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME))
 frames.sort();draws.sort();primitives.sort()
 await RenderingServer.frame_post_draw
 var image:=root.get_texture().get_image();image.save_png(output.get_base_dir()+"/"+stage+".png")
 samples.append({"stage":stage,"render_size":str(image.get_size()),"median_ms":frames[20],"p95_ms":frames[38],"draws":draws[20],"primitives":primitives[20]})
func contact_samples(bank:Node3D)->Array:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_remaining_crew_20261019/PACKAGE.json"))
 var rays:Array=[]
 for row:Dictionary in p.rest_surfaces:rays.append(Vector3(row.surface[0],row.surface[1],row.surface[2]))
 for row:Dictionary in p.instances:
  var at:=Vector3(row.position[0],row.position[1],row.position[2]);var b:=Basis(Vector3.UP,row.yaw)
  for x in [0.0,5.0,7.0,9.0,11.0,13.9]:rays.append(at+b*Vector3(x,0,0))
 var samples:Array=[]
 for at:Vector3 in rays:
  var hit:=bank.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.035,at-Vector3.UP*.035))
  samples.append({"empty":hit.is_empty(),"position":hit.get("position",Vector3.ZERO),"normal":hit.get("normal",Vector3.ZERO),"bank_owned":not hit.is_empty() and bank.is_ancestor_of(hit.collider)})
 return samples
func run()->void:
 root.size=Vector2i(1920,1080);root.content_scale_size=Vector2i(1920,1080);root.content_scale_mode=Window.CONTENT_SCALE_MODE_VIEWPORT
 var host:Node3D=load("res://visible_resource_budget_20261026/bank_fixture_host.gd").new();root.add_child(host)
 var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
 var systems:=Node.new();systems.name="ShipSystems";host.add_child(systems)
 var budget:Node=load("res://scripts/lighting_budget.gd").new();budget.name="LocalShadowSourceBudget";systems.add_child(budget)
 sample("before")
 var bank:Node3D=load("res://scripts/group3_remaining_crew_20261019/package.gd").build(host)
 await physics_frame;sample("original")
 var environment:=WorldEnvironment.new();environment.environment=Environment.new();environment.environment.background_mode=Environment.BG_COLOR;environment.environment.background_color=Color(.04,.04,.04);environment.environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;environment.environment.ambient_light_color=Color.WHITE;environment.environment.ambient_light_energy=.35;host.add_child(environment)
 camera=Camera3D.new();host.add_child(camera);camera.position=Vector3(-72.5,13.6,-340);camera.look_at(Vector3(-78,13.6,-340));camera.current=true;camera.fov=75
 budget.actor=camera;budget.refresh()
 await view("original_view")
 var near_pose:=camera.transform
 camera.position=Vector3(0,900,40);camera.look_at(Vector3(0,50,0));camera.far=2000;budget.refresh()
 await view("original_wide")
 camera.transform=near_pose;budget.refresh()
 var before_contacts:=contact_samples(bank)
 var doors:Dictionary={}
 for child:Node in bank.get_children():
  if child.get_script()!=null:doors[child.name]={"id":child.get_instance_id(),"persistent_id":str(child.persistent_id),"pose":child.transform}
 var lights:Array=[]
 for light:Light3D in budget.sources:lights.append({"id":light.get_instance_id(),"kind":1,"mask":light.light_cull_mask,"reach":light.omni_range,"position":light.global_position,"managed_eight":true})
 var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_remaining_crew_20261019/PACKAGE.json"))
 var original_refs:Array[WeakRef]=[]
 for file:String in definition.model_pins:
  var wrapper:Node3D=bank.get_node(file.trim_suffix(".glb"));original_refs.append_array(references(wrapper));wrapper.free()
 for i in 3:await process_frame
 var freed:=0
 for reference:WeakRef in original_refs:
  if reference.get_ref()==null:freed+=1
 assert(freed==original_refs.size(),"Original imported mesh resources retained")
 var start:=Time.get_ticks_usec()
 for file:String in definition.model_pins:
  var packed:PackedScene=load("res://precompiled_bank_cells_20261026/r005/"+file.trim_suffix(".glb")+".scn")
  var wrapper:Node3D=packed.instantiate();packed=null;bank.add_child(wrapper)
 var checked_vertices:=0;var maximum_delta:=0.0
 for mesh:MeshInstance3D in bank.find_children("*","MeshInstance3D",true,false):
  if not mesh.has_meta("precompiled_fallback"):continue
  var actual:PackedVector3Array=load("res://precompiled_bank_cells_20261026/merge.gd").raw_faces(mesh.mesh)
  var cursor:=0
  for record:Array in mesh.get_meta("precompiled_fallback"):
   var original:PackedVector3Array=load("res://precompiled_bank_cells_20261026/merge.gd").raw_faces(record[1])
   for vertex:Vector3 in original:
    assert(cursor<actual.size())
    var delta:float=(record[0]*vertex).distance_to(mesh.transform*actual[cursor]);maximum_delta=maxf(maximum_delta,delta)
    assert(delta<.00005,"Source-space geometry exceeds established canonical-transform tolerance")
    cursor+=1;checked_vertices+=1
  assert(cursor==actual.size())
 var result:Dictionary=load("res://precompiled_bank_cells_20261026/select_lighting.gd").apply(bank,lights)
 result.source_space_vertices_checked=checked_vertices;result.maximum_source_space_delta_m=maximum_delta
 result.load_select_us=Time.get_ticks_usec()-start;result.original_mesh_resources_released=freed
 for name:String in doors:
  var door:Node3D=bank.get_node(name);assert(door.get_instance_id()==doors[name].id and str(door.persistent_id)==doors[name].persistent_id and door.transform==doors[name].pose)
 await physics_frame;await physics_frame;sample("compiled")
 var after_contacts:=contact_samples(bank);assert(before_contacts==after_contacts,"Retained floor/rest contact geometry changed")
 result.contact_ray_comparisons=before_contacts.size()
 await view("compiled_view")
 camera.position=Vector3(0,900,40);camera.look_at(Vector3(0,50,0));budget.refresh()
 await view("compiled_wide")
 camera.transform=near_pose;budget.refresh()
 weak_meshes=references(bank)
 var denied:=0
 var actor:=CharacterBody3D.new();host.add_child(actor)
 for name:String in doors:
  var door:Node3D=bank.get_node(name);actor.global_position=door.to_global(Vector3(0,.03,-2.2));door.interact(actor)
  assert(door.authorization_denied and not door.desired_open);denied+=1
 result.original_external_gate_denials=denied
 var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify({"samples":samples,"result":result,"door_identity_checks":doors.size(),"default_selected":false},"\t"));f.close()
 host.free()
 for i in 3:await process_frame
 for reference:WeakRef in weak_meshes:assert(reference.get_ref()==null,"Direct renderer source resource retained after owner teardown")
 result.mesh_release_checks=weak_meshes.size()
 f=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify({"samples":samples,"result":result,"door_identity_checks":doors.size(),"default_selected":false},"\t"));f.close();quit()
