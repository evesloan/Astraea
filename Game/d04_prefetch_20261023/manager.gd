extends "res://scripts/startup_residency_20261020/d04_detail_residency.gd"
# Opt-in: same manager node, records, shells, contact owner and release policy.
const MAX_READY_OR_PENDING:=2
const PREFETCH_METRES:=32.0
const DISPATCH_BUDGET_US:=2000
var requests:Dictionary={}
var activation_queue:Array[Dictionary]=[]
var verified_paths:Dictionary={}
var force_sync:=false
var stopped:=false
var request_count:=0
var stale_drops:=0
var activation_count:=0
var activation_max_us:=0
var activation_overruns:=0
var urgent_sync_loads:=0
var cache_hits:=0
var points_frame:Vector2i=Vector2i(-1,-1)
var cached_points:Array[Vector3]=[]
func _points()->Array[Vector3]:
 var frame:=Vector2i(Engine.get_process_frames(),Engine.get_physics_frames())
 if frame==points_frame:return cached_points
 points_frame=frame;cached_points=[]
 var result:Array[Vector3]=[]
 var actors:=host.get_node_or_null("ShipSpace/PersistentActors")
 if actors==null:return result
 var player:=actors.get_node_or_null("Player")as Node3D
 if player!=null:result.append(player.global_position)
 for body:RigidBody3D in actors.find_children("*","RigidBody3D",true,false):result.append(body.global_position)
 cached_points=result
 return result
func _near_any(entry:Dictionary,margin:float)->bool:
 for point in _points():
  if _near(point,entry.bounds,margin):return true
 return false
func _wanted(entry:Dictionary)->bool:
 var home:Node3D=entry.home.get_ref()
 return home!=null and home.is_inside_tree()and not is_instance_valid(entry.detail)and (entry.witness.is_on_screen()or _near_any(entry,ENTER))
func _prefetch_wanted(entry:Dictionary)->bool:
 var home:Node3D=entry.home.get_ref()
 return home!=null and home.is_inside_tree()and not is_instance_valid(entry.detail)and (_wanted(entry)or _near_any(entry,PREFETCH_METRES))
func _fail(message:String)->void:
 stopped=true;push_error("D04_PREFETCH_GUARD: "+message);get_tree().quit(2)
func _request(entry:Dictionary)->void:
 var path:String=entry.record.detail_path
 if stopped or requests.has(path):return
 if requests.size()>=MAX_READY_OR_PENDING and _wanted(entry):
  for old_path in requests.keys():
   if requests[old_path].scene!=null and not _wanted(requests[old_path].entry):requests.erase(old_path);stale_drops+=1;break
 if requests.size()>=MAX_READY_OR_PENDING:return
 if not verified_paths.has(path):
  if FileAccess.get_sha256(path)!=str(entry.record.detail_sha256):_fail("Exact detail hash differs: "+path);return
  verified_paths[path]=true
 var status:=ResourceLoader.load_threaded_request(path,"PackedScene",false,ResourceLoader.CACHE_MODE_REUSE)
 if status!=OK:_fail("Threaded request failed: "+path);return
 requests[path]={"entry":entry,"scene":null,"ready_us":0}
 request_count+=1
func _enqueue(entry:Dictionary)->void:
 if not activation_queue.has(entry):activation_queue.append(entry)
 _request(entry)
func _load_entry(entry:Dictionary)->void:
 if is_instance_valid(entry.detail)or stopped:return
 if force_sync or not host.get_meta("runtime_ready",false)or _near_any(entry,ENTER):
  var path:String=entry.record.detail_path
  if requests.has(path)and requests[path].scene!=null:
   var scene:PackedScene=requests[path].scene;requests.erase(path);cache_hits+=1;_activate(entry,scene)
  else:
   urgent_sync_loads+=1
   super._load_entry(entry)
  return
 _enqueue(entry)
func prepare_position(point:Vector3)->void:
 force_sync=true
 super.prepare_position(point)
 force_sync=false
func _activate(entry:Dictionary,scene:PackedScene)->void:
 var home:Node3D=entry.home.get_ref()
 if home==null or is_instance_valid(entry.detail):return
 var begin:=Time.get_ticks_usec()
 var detail:Node3D=scene.instantiate()
 if detail==null:_fail("Detail instantiate failed");return
 home.add_child(detail);detail.name="ResidentPrivateFurnishings"
 entry.detail=detail;entry.hidden=0.0;loads+=1;activation_count+=1
 var cost:=Time.get_ticks_usec()-begin;activation_max_us=maxi(activation_max_us,cost)
 if cost>DISPATCH_BUDGET_US:activation_overruns+=1
func _poll()->void:
 for path in requests.keys():
  var slot:Dictionary=requests[path]
  if slot.scene==null:
   var status:=ResourceLoader.load_threaded_get_status(path)
   if status==ResourceLoader.THREAD_LOAD_IN_PROGRESS:continue
   if status!=ResourceLoader.THREAD_LOAD_LOADED:_fail("Threaded resource failed: "+str(path));return
   # Never call get while IN_PROGRESS. Drain completed stale requests too.
   slot.scene=ResourceLoader.load_threaded_get(path)as PackedScene
   slot.ready_us=Time.get_ticks_usec()
   if slot.scene==null:_fail("Loaded detail is not a PackedScene");return
  if not _prefetch_wanted(slot.entry):
   requests.erase(path);stale_drops+=1
func _process(_delta:float)->void:
 if stopped or host==null or not host.get_meta("runtime_ready",false):return
 var begin:=Time.get_ticks_usec()
 _poll()
 if stopped:return
 for i in range(activation_queue.size()-1,-1,-1):
  if not _wanted(activation_queue[i]):activation_queue.remove_at(i)
 for entry in activation_queue:
  if Time.get_ticks_usec()-begin>=DISPATCH_BUDGET_US:break
  var path:String=entry.record.detail_path
  if requests.has(path)and requests[path].scene!=null:
   var scene:PackedScene=requests[path].scene;requests.erase(path);activation_queue.erase(entry)
   cache_hits+=1;_activate(entry,scene);break
 for entry in activation_queue:
  if requests.size()>=MAX_READY_OR_PENDING:break
  _request(entry)
 # Conservative nearby prefetch: no hidden nodes instantiated or whole-ship pool.
 if requests.size()<MAX_READY_OR_PENDING:
  var candidates:Array[Dictionary]=[]
  for entry in entries:
   if _prefetch_wanted(entry):candidates.append(entry)
  var points:=_points()
  if not points.is_empty():candidates.sort_custom(func(a,b):return points[0].distance_squared_to(a.bounds.get_center())<points[0].distance_squared_to(b.bounds.get_center()))
  for entry in candidates:
   if requests.size()>=MAX_READY_OR_PENDING or Time.get_ticks_usec()-begin>=DISPATCH_BUDGET_US:break
   _request(entry)
func prefetch_statistics()->Dictionary:
 var pending:=0;var ready:=0
 for slot in requests.values():
  if slot.scene==null:pending+=1
  else:ready+=1
 return {"pending":pending,"ready":ready,"limit":MAX_READY_OR_PENDING,"queued_entries":activation_queue.size(),"requests":request_count,"stale_drops":stale_drops,"activations":activation_count,"activation_max_us":activation_max_us,"activation_overruns":activation_overruns,"urgent_sync_loads":urgent_sync_loads,"cache_hits":cache_hits,"stopped":stopped,"RID_exhaustion_fixed":false}
