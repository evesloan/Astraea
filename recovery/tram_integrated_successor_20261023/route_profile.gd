extends Node
# Opt-in measurement on the existing integrated ship. Never changes admission,
# actor/car transforms, collision masks, residency policy or the motion controller.
const ROUTE := ["AFT_MIDSHIP", "CENTRAL", "FORE_MIDSHIP", "CENTRAL"]
const STATIONARY_FRAMES := 15
const SAMPLE_SCHEMA := 1
var ship:Node3D
var assembly:Node3D
var motor:Node3D
var safety:Node3D
var restraint:Node3D
var controls:Node3D
var passenger:CharacterBody3D
var viewport:Viewport
var received:Node
var private_rooms:Node
var contacts:Node
var stream:FileAccess
var result_path:String
var phase := "unconfigured"
var reason := ""
var leg := 0
var cycle := 0
var cycles := 2
var departure_count := 0
var arrival_count := 0
var start_us := 0
var previous_us := 0
var station_ready_us := 0
var snapshot_us := 0
var deadline_us := 0
var sample_overhead_max_us := 0
var snapshot_overhead_max_us := 0
var last_ids := {}
var state_index := 0
var completed := false
var snapshot_period_us := 1000000
var dwell_us := 12000000
var render_timing_enabled := false
var source_revision := ""
var expected_size:=Vector2i.ZERO

static func admission_error(a:Node3D,m:Node3D,s:Node3D,r:Node3D)->String:
 if a==null or m==null or s==null or r==null:return "missing original tram owners"
 if not bool(a.get_meta("tram_operations_admitted",false)):return str(a.get_meta("tram_operation_hold","tram operation not admitted"))
 if not bool(m.get_meta("integration_motion_admitted",false)):return "motion admission is held"
 if not bool(s.get_meta("integration_boarding_admitted",false)):return "boarding admission is held"
 if not bool(r.get_meta("integration_joint_admitted",false)):return "original cart joint admission is held"
 return ""

func configure(actual_ship:Node3D,unique_output:String,revision:String,repeat_cycles:int=2,measure_render_time:bool=false,expected_internal_size:Vector2i=Vector2i(1920,1080))->bool:
 if phase!="unconfigured":return false
 if FileAccess.file_exists(unique_output):reason="refuse overwrite of prior route evidence";return false
 ship=actual_ship;source_revision=revision;result_path=unique_output;cycles=repeat_cycles
 if cycles<2 or cycles>4:reason="use two to four repeated cycles";return false
 stream=FileAccess.open(result_path,FileAccess.WRITE)
 if stream==null:reason="cannot open unique output";return false
 if not ship.get_meta("runtime_ready",false):finish("BLOCKED","actual ship is not runtime_ready");return false
 assembly=ship.get_node_or_null("ShipSpace/Districts/Group4Completion") as Node3D
 if assembly!=null:
  motor=assembly.get_node_or_null("Group4LoadedSourceTravelActuator") as Node3D
  safety=assembly.get_node_or_null("Group4BoardingSafety") as Node3D
  restraint=assembly.get_node_or_null("Group4OriginalCartRestraint") as Node3D
  controls=assembly.get_node_or_null("Group4SourceOperatingControls") as Node3D
 passenger=ship.get_node_or_null("ShipSpace/PersistentActors/Player") as CharacterBody3D
 viewport=ship.get_viewport();expected_size=expected_internal_size
 write_event({"kind":"header","schema":SAMPLE_SCHEMA,"source_revision":source_revision,"source_contract_sha256":FileAccess.get_sha256("res://scripts/runtime_contracts_20261022/SOURCE_CONTRACTS.json"),"engine":Engine.get_version_info(),"adapter":RenderingServer.get_video_adapter_name(),"display_server":DisplayServer.get_name(),"internal_resolution":[viewport.size.x,viewport.size.y],"route":ROUTE,"cycles":cycles,"dwell_seconds":float(dwell_us)/1000000,"original_motion_plan_sha256":FileAccess.get_sha256("res://data/architecture/GROUP4_TRAVEL_SOURCE_CANDIDATE.json"),"measurement_scope":"real-clock passenger movement; no whole-ship or target performance acceptance"})
 var blocked:=admission_error(assembly,motor,safety,restraint)
 if not blocked.is_empty():finish("BLOCKED",blocked);return false
 if viewport.size!=expected_size:finish("BLOCKED","internal viewport differs from requested measurement size");return false
 if controls==null or passenger==null:finish("BLOCKED","original controls or passenger missing");return false
 if not controls.actor_aboard(passenger):finish("BLOCKED","original passenger must physically board; no repositioning performed");return false
 if motor.moving or motor.motion_fault or restraint.motion_fault:finish("BLOCKED","tram is moving or faulted before arming");return false
 received=ship.get_node_or_null("ShipSystems/ReceivedRoomResidency")
 private_rooms=ship.get_node_or_null("ShipSystems/PrivateDetailResidency")
 contacts=ship.get_node_or_null("ShipSystems/ExactContactResidency")
 start_us=Time.get_ticks_usec();previous_us=start_us;deadline_us=start_us+1800000000
 render_timing_enabled=measure_render_time
 if render_timing_enabled:RenderingServer.viewport_set_measure_render_time(viewport.get_viewport_rid(),true)
 phase="initial_stationary";process_physics_priority=20
 write_event({"kind":"armed","ticks_us":start_us,"position":xyz(passenger.global_position),"car_position":xyz(motor.vehicle.global_position),"initial_cursor_m":motor.cursor,"camera":camera_state(),"render_timing_enabled":render_timing_enabled})
 snapshot(true);return true

func _physics_process(_delta:float)->void:
 if phase in ["unconfigured","finished"]:return
 var blocked:=admission_error(assembly,motor,safety,restraint)
 if not blocked.is_empty():finish("ABORTED",blocked);return
 if viewport.size!=expected_size:finish("ABORTED","internal viewport changed during matched route");return
 if not is_instance_valid(passenger) or not controls.actor_aboard(passenger):finish("ABORTED","passenger left original physical car");return
 if motor.motion_fault or restraint.motion_fault:finish("ABORTED","original tram/controller reported motion fault");return
 if Time.get_ticks_usec()>deadline_us:finish("INCOMPLETE","bounded 30-minute profile limit; current motor target left under original control");return
 if phase=="final_settle":
  if Time.get_ticks_usec()-station_ready_us>=dwell_us:
   snapshot(true);settled_event();finish("COMPLETED","all repeated physical legs and final twelve-second settling recorded")
  return
 if phase=="travelling":
  if motor.moving:return
  phase="arrival_stationary";station_ready_us=0
 # The safety controller itself owns its 15-frame stationary witness. Do not
 # inspect docking before that witness or add synthetic stationary frames.
 if int(safety.stationary_frames)<STATIONARY_FRAMES:return
 if phase=="initial_stationary":
  if not safety._physical_dock_matches("CENTRAL"):finish("BLOCKED","physically boarded start must be the retained CENTRAL dock");return
  phase="dwell";station_ready_us=Time.get_ticks_usec();write_event({"kind":"initial_dock","ticks_us":station_ready_us,"station":"CENTRAL"});return
 if phase=="arrival_stationary":
  var station:String=ROUTE[leg]
  if not safety._physical_dock_matches(station):finish("ABORTED","stopped car does not match requested physical dock "+station);return
  arrival_count+=1;write_event({"kind":"arrival","ticks_us":Time.get_ticks_usec(),"cycle":cycle,"leg":leg,"station":station,"cursor_m":motor.cursor,"camera":camera_state()})
  snapshot(true);leg+=1
  if leg==ROUTE.size():leg=0;cycle+=1
  if cycle>=cycles:phase="final_settle";station_ready_us=Time.get_ticks_usec();return
  phase="dwell";station_ready_us=Time.get_ticks_usec();return
 if phase=="dwell" and Time.get_ticks_usec()-station_ready_us>=dwell_us:
  if not safety.unloaded_clear_to_depart() or not restraint.loaded_clear_to_depart():finish("BLOCKED","original closure/cart-restraint conditions not ready");return
  settled_event()
  var station:String=ROUTE[leg]
  var accepted:bool=controls.request_control(station,"",passenger)
  write_event({"kind":"departure_request","ticks_us":Time.get_ticks_usec(),"cycle":cycle,"leg":leg,"station":station,"accepted":accepted,"cursor_m":motor.cursor})
  if not accepted:finish("BLOCKED","original control rejected departure to "+station);return
  departure_count+=1;phase="travelling"

func _process(_delta:float)->void:
 if phase in ["unconfigured","finished"]:return
 var begin:=Time.get_ticks_usec()
 var row:={"kind":"frame","ticks_us":begin,"interval_us":begin-previous_us,"phase":phase,"cycle":cycle,"leg":leg,"state_index":state_index,"cursor_m":motor.cursor,"speed_m_s":motor.speed,"passenger_position":xyz(passenger.global_position),"passenger_car_local":xyz(motor.vehicle.to_local(passenger.global_position)),"camera":camera_state(),"nodes":Performance.get_monitor(Performance.OBJECT_NODE_COUNT),"objects":Performance.get_monitor(Performance.OBJECT_COUNT),"resources":Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT),"static_bytes":OS.get_static_memory_usage(),"process_ms":1000.0*Performance.get_monitor(Performance.TIME_PROCESS),"physics_ms":1000.0*Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS),"draws":viewport.get_render_info(Viewport.RENDER_INFO_TYPE_VISIBLE,Viewport.RENDER_INFO_DRAW_CALLS_IN_FRAME),"shadow_draws":viewport.get_render_info(Viewport.RENDER_INFO_TYPE_SHADOW,Viewport.RENDER_INFO_DRAW_CALLS_IN_FRAME),"primitives":viewport.get_render_info(Viewport.RENDER_INFO_TYPE_VISIBLE,Viewport.RENDER_INFO_PRIMITIVES_IN_FRAME),"render_setup_cpu_ms":RenderingServer.get_frame_setup_time_cpu(),"internal_resolution":[viewport.size.x,viewport.size.y],"max_fps":Engine.max_fps}
 if render_timing_enabled:
  row["viewport_render_cpu_ms"]=RenderingServer.viewport_get_measured_render_time_cpu(viewport.get_viewport_rid())
  row["viewport_render_gpu_ms"]=RenderingServer.viewport_get_measured_render_time_gpu(viewport.get_viewport_rid())
 write_event(row);previous_us=begin
 if begin-snapshot_us>=snapshot_period_us:snapshot(false)
 sample_overhead_max_us=maxi(sample_overhead_max_us,Time.get_ticks_usec()-begin)

func snapshot(force:bool)->void:
 var begin:=Time.get_ticks_usec();snapshot_us=begin
 var ids:={"received":[],"private":[]};var stats:={}
 if is_instance_valid(received):
  stats["received"]=received.statistics()
  for entry in received.entries:
   if entry.attached and is_instance_valid(entry.room):ids.received.append(str(entry.room.get_path()))
 if is_instance_valid(private_rooms):
  stats["private"]=private_rooms.statistics()
  for entry in private_rooms.entries:
   if is_instance_valid(entry.detail):ids.private.append(str(entry.record.room_id))
 if is_instance_valid(contacts):stats["contacts"]=contacts.statistics()
 for key in ids:ids[key].sort()
 var entered:={};var left:={}
 for key in ids:
  var prior:Array=last_ids.get(key,[]);entered[key]=[];left[key]=[]
  var prior_set:={};var current_set:={}
  for id in prior:prior_set[id]=true
  for id in ids[key]:current_set[id]=true
  for id in ids[key]:
   if not prior_set.has(id):entered[key].append(id)
  for id in prior:
   if not current_set.has(id):left[key].append(id)
 if force or ids!=last_ids:
  state_index+=1;write_event({"kind":"residency","ticks_us":begin,"state_index":state_index,"resident_ids":ids,"entered_ids":entered,"left_ids":left,"statistics":stats})
 else:write_event({"kind":"counters","ticks_us":begin,"state_index":state_index,"statistics":stats})
 last_ids=ids;var overhead:=Time.get_ticks_usec()-begin;snapshot_overhead_max_us=maxi(snapshot_overhead_max_us,overhead)
 write_event({"kind":"observer_cost","ticks_us":begin,"snapshot_us":overhead})
 stream.flush()

func settled_event()->void:
 write_event({"kind":"settled","ticks_us":Time.get_ticks_usec(),"cycle":cycle,"leg":leg,"station":controls.current_station(),"cursor_m":motor.cursor,"nodes":Performance.get_monitor(Performance.OBJECT_NODE_COUNT),"resources":Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT),"static_bytes":OS.get_static_memory_usage(),"camera":camera_state(),"state_index":state_index})
func camera_state()->Dictionary:
 if not is_instance_valid(passenger):return {}
 var camera:Camera3D=passenger.get_node_or_null("Camera3D") as Camera3D
 if camera==null:
  for item in passenger.get_children():
   if item is Camera3D:camera=item;break
 if camera==null:return {"available":false}
 return {"position":xyz(camera.global_position),"rotation":xyz(camera.global_rotation),"fov":camera.fov}
static func xyz(p:Vector3)->Array:return [p.x,p.y,p.z]
func write_event(row:Dictionary)->void:
 if stream!=null:stream.store_line(JSON.stringify(row))
func cancel()->void:
 finish("CANCELLED","observer removed; original vehicle/passenger controls and current motor target unchanged")
func finish(status:String,detail:String)->void:
 if phase=="finished":return
 reason=detail;completed=status=="COMPLETED";phase="finished"
 write_event({"kind":"result","status":status,"reason":reason,"departures":departure_count,"arrivals":arrival_count,"cycles_completed":cycle,"sample_overhead_max_us":sample_overhead_max_us,"snapshot_overhead_max_us":snapshot_overhead_max_us,"target_performance_accepted":false})
 if stream!=null:stream.flush();stream.close();stream=null
 # Measuring is opt-in and has no getter. The caller must dedicate ownership of
 # this viewport's profiling switch to the observer for its lifetime.
 if render_timing_enabled and is_instance_valid(viewport):RenderingServer.viewport_set_measure_render_time(viewport.get_viewport_rid(),false)
 print("TRAM_ROUTE_PROFILE ",status," ",reason)
func _exit_tree()->void:
 if phase!="finished" and stream!=null:finish("INCOMPLETE","observer tree exited before route completion")
