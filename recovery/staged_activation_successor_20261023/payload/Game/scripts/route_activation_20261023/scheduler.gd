extends Node
# One shared main-thread queue for the two measured visibility paths.
const SOFT_BUDGET_US:=2000
var pending:Array[Dictionary]=[]
var keys:Dictionary={}
var completed:=0
var stale:=0
var duplicates:=0
var peak_pending:=0
var max_activation_us:=0
var overruns:=0
var recent:Array=[]
var active_job:RefCounted
var staged_cancelled:=0
var staged_failed:=0
var staged_max_slice_us:=0
static func obtain(host:Node3D)->Node:
 if OS.get_environment("ASTRAEA_ROOM_ACTIVATION_QUEUE")!="1"or not host.get_meta("runtime_ready",false):return null
 var systems:Node=host.get_node("ShipSystems")
 var existing:=systems.get_node_or_null("VisibilityActivationQueue")
 if existing!=null:return existing
 var result:Node=load("res://scripts/route_activation_20261023/scheduler.gd").new();result.name="VisibilityActivationQueue";systems.add_child(result);return result
func enqueue(owner:Node,entry:Dictionary,identity:Node,kind:String)->void:
 var key:=str(owner.get_instance_id())+":"+str(identity.get_instance_id())
 if keys.has(key):duplicates+=1;return
 keys[key]=true;pending.append({"owner":weakref(owner),"entry":entry,"key":key,"kind":kind,"identity":weakref(identity)});peak_pending=maxi(peak_pending,pending.size())
func _process(_delta:float)->void:
 if active_job!=null:
  _step_active_job();return
 var begin:=Time.get_ticks_usec()
 while not pending.is_empty()and Time.get_ticks_usec()-begin<SOFT_BUDGET_US:
  var request:Dictionary=pending.pop_front()
  var owner:Node=request.owner.get_ref()
  if owner==null or not owner.is_inside_tree():keys.erase(request.key);stale+=1;continue
  var job_script=load("res://scripts/route_activation_20261023/staged_job.gd")
  if OS.get_environment("ASTRAEA_STAGED_ROOM_ACTIVATION")=="1" and job_script.supported(request):
   active_job=job_script.new();active_job.configure(request);_step_active_job();return
  keys.erase(request.key)
  var started:=Time.get_ticks_usec()
  var activated:bool=owner._activate_pending_visibility(request.entry)
  var cost:=Time.get_ticks_usec()-started
  if not activated:stale+=1;continue
  completed+=1;max_activation_us=maxi(max_activation_us,cost)
  if cost>SOFT_BUDGET_US:overruns+=1
  var identity:Node=request.identity.get_ref()
  var details:Dictionary=identity.get_meta("last_activation_metrics",{}) if identity!=null else {}
  recent.append({"kind":request.kind,"room":str(identity.name) if identity!=null else "freed","activation_us":cost,"frame":Engine.get_process_frames(),"stages":details.duplicate(true)})
  if recent.size()>64:recent.pop_front()
  break # At most one actual activation across BOTH managers per frame.
func _step_active_job()->void:
 var start:=Time.get_ticks_usec()
 var done:bool=active_job.step(SOFT_BUDGET_US)
 var cost:=Time.get_ticks_usec()-start;staged_max_slice_us=maxi(staged_max_slice_us,cost)
 if cost>SOFT_BUDGET_US:overruns+=1
 if not done:return
 var identity:Node=active_job.request.identity.get_ref()
 keys.erase(active_job.request.key)
 if active_job.committed:completed+=1
 else:stale+=1
 if active_job.cancelled:staged_cancelled+=1
 if active_job.failed:staged_failed+=1
 recent.append({"kind":active_job.request.kind,"room":str(identity.name) if identity!=null else "freed","prototype":active_job.path,"staged":true,"committed":active_job.committed,"cancelled":active_job.cancelled,"failed":active_job.failed,"wall_us":Time.get_ticks_usec()-active_job.started_usec,"slices":active_job.metrics.duplicate(true),"frame":Engine.get_process_frames()})
 if recent.size()>64:recent.pop_front()
 active_job=null
func _notification(what:int)->void:
 if what==NOTIFICATION_PREDELETE and active_job!=null:active_job.dispose()
func statistics()->Dictionary:
 return {"staged_active":active_job!=null,"staged_cancelled":staged_cancelled,"staged_failed":staged_failed,"staged_max_slice_us":staged_max_slice_us,"pending":pending.size(),"peak_pending":peak_pending,"completed":completed,"stale":stale,"duplicates":duplicates,"max_activation_us":max_activation_us,"overruns":overruns,"recent":recent.duplicate(true),"hard_frame_time_guarantee":false}
