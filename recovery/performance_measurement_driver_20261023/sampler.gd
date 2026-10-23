extends SceneTree
var scenario:Dictionary
var output:String
var probe:Node
var ship:Node3D
var viewport:Viewport
var samples:Array=[]
var residency_events:Array=[]
var previous_state:String=""
var sample_overhead_max_us:=0
var start_us:int
var ready_us:int
var initial_lights:Array=[]
func _initialize()->void:call_deferred("run")
func _node_added(node:Node)->void:
 if node.name=="D04SurfaceCellResearch" and node.get_script()!=null and node.get_script().resource_path=="res://d04_surface_cells_20261023/controller.gd":
  assert(not node.started and node.host==null,"Probe must attach before original setup")
  node.set_script(load(get_script().resource_path.get_base_dir()+"/controller_probe.gd"));probe=node
func residency(manager:Node)->Dictionary:
 var ids:Array[String]=[];var optimized:Array[String]=[]
 for entry:Dictionary in manager.entries:
  if not is_instance_valid(entry.detail):continue
  assert(entry.record.has("room_id"),"Exact persistent room ID required")
  ids.append(str(entry.record.room_id))
  if entry.detail.has_meta("surface_cells") and bool(entry.detail.get_meta("surface_cells").enabled):optimized.append(str(entry.record.room_id))
 ids.sort();optimized.sort()
 return {"resident_ids":ids,"optimized_ids":optimized,"loads":manager.loads,"releases":manager.releases}
func light_selection()->Array:
 var result:Array=[]
 var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 for light in budget.previously_active:
  if not is_instance_valid(light):continue
  result.append({"path":str(ship.get_path_to(light)),"visible":light.visible,"shadows":light.shadow_enabled,"powered":light.get_meta("fixture_powered",true),"energy":light.light_energy,"mask":light.light_cull_mask,"position":var_to_str(light.global_position),"range":light.omni_range if light is OmniLight3D else (light.spot_range if light is SpotLight3D else 0.0)})
 result.sort_custom(func(a,b):return str(a.path)<str(b.path))
 return result
func state()->Dictionary:
 return {"d04":residency(ship.d04_detail_residency),"private":residency(ship.private_detail_residency),"active_light_selection":light_selection(),"batch_stopped":probe.stopped if is_instance_valid(probe)else false,"activation_count":probe.reports.size() if is_instance_valid(probe)else 0}
func capture_state()->int:
 var selection:Array=light_selection()
 var encoded:=JSON.stringify([ship.d04_detail_residency.loads,ship.d04_detail_residency.releases,ship.private_detail_residency.loads,ship.private_detail_residency.releases,probe.reports.size() if is_instance_valid(probe)else 0,probe.stopped if is_instance_valid(probe)else false,selection])
 var current:Dictionary
 if encoded!=previous_state:
  current=state()
  residency_events.append({"ticks_us":Time.get_ticks_usec(),"state":current});previous_state=encoded
 return residency_events.size()-1
func save(status:String,reason:String="")->void:
 var f:=FileAccess.open(output,FileAccess.WRITE);assert(f!=null)
 f.store_string(JSON.stringify({"status":status,"reason":reason,"scenario":scenario,"mode":OS.get_environment("ASTRAEA_MEASUREMENT_MODE"),"batching":OS.get_environment("ASTRAEA_D04_SURFACE_CELLS"),"occlusion":OS.get_environment("ASTRAEA_OCCLUSION"),"adapter":RenderingServer.get_video_adapter_name(),"driver_start_us":start_us,"runtime_ready_us":ready_us,"initial_scene_lights":initial_lights,"samples":samples,"residency_events":residency_events,"controller":probe.telemetry() if is_instance_valid(probe)else {},"sampler_max_us":sample_overhead_max_us,"scope":"Instrumented fresh-process fixed-view measurement; no target acceptance implied"},"  "));f.close()
func run()->void:
 var args:=OS.get_cmdline_user_args();assert(args.size()==2,"scenario JSON and unique result path required")
 scenario=JSON.parse_string(FileAccess.get_file_as_string(args[0]));output=args[1];assert(not FileAccess.file_exists(output))
 assert(scenario.expected_actor_position is Array and (scenario.camera_pitch_degrees is float or scenario.camera_pitch_degrees is int))
 node_added.connect(_node_added);start_us=Time.get_ticks_usec()
 var bootstrap:Node=load("res://d04_surface_cells_20261023/bootstrap.tscn").instantiate();root.add_child(bootstrap)
 # Operator starts the existing menu. No automatic bypass of its readiness gate.
 while true:
  await process_frame
  if Time.get_ticks_usec()-start_us>int(scenario.startup_timeout_seconds)*1000000:save("BLOCKED","Readiness timeout; operator must start existing menu");quit(2);return
  var found:=root.find_children("Astraea","Node3D",true,false)
  if found.size()==1 and found[0].get_meta("runtime_ready",false):ship=found[0];break
 ready_us=Time.get_ticks_usec()
 var arm_deadline:=ready_us+int(scenario.arm_timeout_seconds)*1000000
 while not FileAccess.file_exists(output+".arm"):
  if Time.get_ticks_usec()>arm_deadline:save("BLOCKED","Capture was not armed after menu/navigation");quit(2);return
  await create_timer(.1).timeout
 for light:Light3D in ship.find_children("*","Light3D",true,false):initial_lights.append({"path":str(ship.get_path_to(light)),"visible":light.visible,"shadow":light.shadow_enabled,"energy":light.light_energy,"transform":var_to_str(light.global_transform),"mask":light.light_cull_mask,"range":light.omni_range if light is OmniLight3D else (light.spot_range if light is SpotLight3D else 0.0)})
 var actor:Node3D=ship.get_node("ShipSpace/PersistentActors/Player");viewport=ship.get_viewport()
 var expected:Array=scenario.expected_actor_position
 if actor.global_position.distance_to(Vector3(expected[0],expected[1],expected[2]))>float(scenario.actor_tolerance_m):save("BLOCKED","Actor position differs; no teleport performed");quit(2);return
 if viewport.size!=Vector2i(scenario.internal_resolution[0],scenario.internal_resolution[1]):save("BLOCKED","Actual internal resolution differs");quit(2);return
 if DisplayServer.window_get_size()!=Vector2i(scenario.expected_window_size[0],scenario.expected_window_size[1]) or viewport.get_parent().effects!=scenario.effects_enabled:save("BLOCKED","Actual window size or effects differs");quit(2);return
 actor.set_controls_enabled(false);actor.set_physics_process(false)
 for heading in scenario.headings_degrees:
  actor.rotation.y=deg_to_rad(float(heading));actor.camera.rotation.x=deg_to_rad(float(scenario.camera_pitch_degrees));actor.camera.fov=float(scenario.camera_fov)
  for phase:String in ["heading_settling","warm_sample"]:
   var seconds:float=scenario.warmup_seconds if phase=="heading_settling"else scenario.sample_seconds
   var end_us:=Time.get_ticks_usec()+int(seconds*1000000);var last_us:=Time.get_ticks_usec()
   while Time.get_ticks_usec()<end_us:
    await process_frame
    var now:=Time.get_ticks_usec();var overhead_start:=now;var event:=capture_state()
    samples.append({"ticks_us":now,"frame_interval_us":now-last_us,"heading":heading,"phase":phase,"state_index":event,"camera_transform":var_to_str(actor.camera.global_transform),"camera_fov":actor.camera.fov,"internal_resolution":[viewport.size.x,viewport.size.y],"window_size":var_to_str(DisplayServer.window_get_size()),"effects":viewport.get_parent().effects,"occlusion_enabled":viewport.use_occlusion_culling,"visible_draws":viewport.get_render_info(Viewport.RENDER_INFO_TYPE_VISIBLE,Viewport.RENDER_INFO_DRAW_CALLS_IN_FRAME),"shadow_draws":viewport.get_render_info(Viewport.RENDER_INFO_TYPE_SHADOW,Viewport.RENDER_INFO_DRAW_CALLS_IN_FRAME),"visible_primitives":viewport.get_render_info(Viewport.RENDER_INFO_TYPE_VISIBLE,Viewport.RENDER_INFO_PRIMITIVES_IN_FRAME),"shadow_primitives":viewport.get_render_info(Viewport.RENDER_INFO_TYPE_SHADOW,Viewport.RENDER_INFO_PRIMITIVES_IN_FRAME),"render_objects":viewport.get_render_info(Viewport.RENDER_INFO_TYPE_VISIBLE,Viewport.RENDER_INFO_OBJECTS_IN_FRAME),"process_seconds":Performance.get_monitor(Performance.TIME_PROCESS),"physics_seconds":Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS),"static_bytes":OS.get_static_memory_usage(),"node_count":get_node_count()})
    sample_overhead_max_us=maxi(sample_overhead_max_us,Time.get_ticks_usec()-overhead_start);last_us=now
 save("CAPTURED");quit()
