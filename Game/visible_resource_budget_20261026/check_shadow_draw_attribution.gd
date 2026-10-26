extends SceneTree
var output:String
var samples:Array=[]
var camera:Camera3D
var weak_meshes:Array[WeakRef]=[]
func references(bank:Node3D)->Array[WeakRef]:
 var refs:Array[WeakRef]=[]
 for source:Node in bank.find_children("ExactStaticRenderOwner","Node3D",true,false):
  for row:Array in source.records:refs.append(weakref(row[1]))
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
 budget.set_process(false)
 await view("original_view")
 var light_count:=0
 for light:Light3D in budget.sources:
  if light.visible and light.shadow_enabled:
   light.set_meta("diagnostic_shadow_preimage",true);light.shadow_enabled=false;light_count+=1
 await view("shadow_attribution_only")
 for light:Light3D in budget.sources:
  if light.has_meta("diagnostic_shadow_preimage"):light.shadow_enabled=true;light.remove_meta("diagnostic_shadow_preimage")
 await view("restored_shadows")
 var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify({"samples":samples,"temporary_shadow_source_count":light_count,"scope":"Read-only rendering attribution fixture; originals restored; no production selection"},"\t"));f.close();host.free();quit()
