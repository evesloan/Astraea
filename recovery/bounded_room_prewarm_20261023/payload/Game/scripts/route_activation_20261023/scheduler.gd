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
var warm_candidate:Dictionary={}
var prewarm_hits:=0
var prewarm_misses:=0
var prewarm_rejected:=0
var prewarm_promotions:=0
var prewarm_verify_us:=0
var rejected_generations:Dictionary={}
var safety_overlaps:=0
var limits=load("res://scripts/route_activation_20261023/prewarm_limits.gd")
func prewarm_enabled()->bool:return limits.enabled()
func request_key(owner:Node,identity:Node)->String:return str(owner.get_instance_id())+":"+str(identity.get_instance_id())
func offer_prewarm(owner:Node,entry:Dictionary,identity:Node,kind:String,interest:bool,distance_squared:float)->void:
 entry.prewarm_interest=interest and prewarm_enabled()
 var key:=request_key(owner,identity)
 if not entry.prewarm_interest:
  if warm_candidate.get("key", "")==key:warm_candidate.clear()
  return
 if active_job!=null or keys.has(key):return
 var r:Dictionary={"owner":weakref(owner),"entry":entry,"key":key,"kind":kind,"identity":weakref(identity),"mode":"warm","distance_squared":distance_squared}
 if not load("res://scripts/route_activation_20261023/staged_job.gd").supported(r):return
 if limits.estimate(r).is_empty():return
 if rejected_generations.get(key, "")==limits.generation(r):return
 if warm_candidate.is_empty() or not bool(warm_candidate.entry.get("prewarm_interest",false)) or distance_squared<float(warm_candidate.distance_squared):warm_candidate=r
func consume_or_cancel(owner:Node,entry:Dictionary,identity:Node,kind:String)->bool:
 var arrival_started:=Time.get_ticks_usec()
 if not prewarm_enabled():return false
 var key:=request_key(owner,identity)
 if warm_candidate.get("key", "")==key:warm_candidate.clear()
 # A real arrival promotes the same owner. It must not be discarded as duplicate.
 if active_job!=null and active_job.request.key==key:
  prewarm_promotions+=1
  if active_job.phase=="ready":
   var ready:RefCounted=active_job;active_job=null;keys.erase(key)
   var begin:=Time.get_ticks_usec()
   var consumed:bool=ready.consume_ready()
   var cost:=Time.get_ticks_usec()-begin
   ready.metrics.append({"stage":"consume_ready","us":cost,"frame":Engine.get_process_frames(),"overrun":cost>SOFT_BUDGET_US})
   if consumed:
    prewarm_hits+=1;completed+=1;_record_warm(ready,"consumed")
    identity.set_meta("last_activation_metrics",{"staged":true,"prewarmed":true,"consume_us":cost,"slices":ready.metrics.duplicate(true)})
    var total_cost:=Time.get_ticks_usec()-arrival_started
    recent[-1].consume_total_us=total_cost
    identity.get_meta("last_activation_metrics").consume_total_us=total_cost
    max_activation_us=maxi(max_activation_us,total_cost)
    if total_cost>SOFT_BUDGET_US:overruns+=1
    return true
   ready.cancelled=true;ready.dispose();_record_warm(ready,"invalidated")
  else:
   # No cancellation API exists for threaded I/O: retain this owner until drained.
   # Synchronous safety fallback can temporarily overlap this one orphan.
   active_job.cancelled=true;safety_overlaps+=1
 entry.prewarm_interest=false
 prewarm_misses+=1
 return false
func record_cold(kind:String,identity:Node,started:int)->void:
 var cost:=Time.get_ticks_usec()-started;max_activation_us=maxi(max_activation_us,cost);completed+=1
 if cost>SOFT_BUDGET_US:overruns+=1
 recent.append({"kind":kind,"room":str(identity.name),"prewarm":"cold_fallback","activation_us":cost,"frame":Engine.get_process_frames()})
 if recent.size()>64:recent.pop_front()
func _record_warm(job:RefCounted,state:String)->void:
 recent.append({"kind":job.request.kind,"prototype":job.path,"prewarm":state,"committed":job.committed,"wall_us":Time.get_ticks_usec()-job.started_usec,"slices":job.metrics.duplicate(true),"frame":Engine.get_process_frames()})
 if recent.size()>64:recent.pop_front()
func _start_warm()->void:
 if warm_candidate.is_empty() or not prewarm_enabled():warm_candidate.clear();return
 var r:Dictionary=warm_candidate;warm_candidate={}
 if r.owner.get_ref()==null or r.identity.get_ref()==null:return
 if not bool(r.entry.get("prewarm_interest",false)):return
 var verification_started:=Time.get_ticks_usec()
 var estimate:Dictionary=limits.admission(r)
 var verification_us:=Time.get_ticks_usec()-verification_started;prewarm_verify_us+=verification_us
 staged_max_slice_us=maxi(staged_max_slice_us,verification_us)
 if verification_us>SOFT_BUDGET_US:overruns+=1
 if estimate.is_empty():
  recent.append({"kind":r.kind,"prewarm":"admission_rejected","verification_us":verification_us,"frame":Engine.get_process_frames()})
  if recent.size()>64:recent.pop_front()
  prewarm_rejected+=1;rejected_generations[r.key]=limits.generation(r)
  if rejected_generations.size()>64:rejected_generations.erase(rejected_generations.keys()[0])
  return
 r.admission=estimate
 var job:RefCounted=load("res://scripts/route_activation_20261023/staged_job.gd").new();job.configure(r);job.started_usec=verification_started
 job.metrics.append({"stage":"admission_verify","us":verification_us,"frame":Engine.get_process_frames(),"overrun":verification_us>SOFT_BUDGET_US})
 if not job.wanted():job.dispose();return
 keys[r.key]=true;active_job=job;_step_active_job()
static func obtain(host:Node3D)->Node:
 if OS.get_environment("ASTRAEA_ROOM_ACTIVATION_QUEUE")!="1"or not host.get_meta("runtime_ready",false):return null
 var systems:Node=host.get_node("ShipSystems")
 var existing:=systems.get_node_or_null("VisibilityActivationQueue")
 if existing!=null:return existing
 var result:Node=load("res://scripts/route_activation_20261023/scheduler.gd").new();result.name="VisibilityActivationQueue";systems.add_child(result);return result
func enqueue(owner:Node,entry:Dictionary,identity:Node,kind:String)->void:
 var key:=request_key(owner,identity)
 if prewarm_enabled():
  # In prewarm mode a cold visible arrival never waits behind speculative work.
  if consume_or_cancel(owner,entry,identity,kind):return
  owner._activate_pending_visibility(entry);return
 if keys.has(key):duplicates+=1;return
 keys[key]=true;pending.append({"owner":weakref(owner),"entry":entry,"key":key,"kind":kind,"identity":weakref(identity)});peak_pending=maxi(peak_pending,pending.size())
func _process(_delta:float)->void:
 if active_job!=null:
  # Actual visibility queued before opt-in/toggle takes priority over speculation.
  if not pending.is_empty() and active_job.request.get("mode", "visibility")=="warm":active_job.cancelled=true
  _step_active_job()
  return # Preserve one active-job slice/queued completion per process frame.
 var begin:=Time.get_ticks_usec()
 while not pending.is_empty()and Time.get_ticks_usec()-begin<SOFT_BUDGET_US:
  var request:Dictionary=pending.pop_front()
  var owner:Node=request.owner.get_ref()
  if owner==null or not owner.is_inside_tree():keys.erase(request.key);stale+=1;continue
  var job_script=load("res://scripts/route_activation_20261023/staged_job.gd")
  if not prewarm_enabled() and OS.get_environment("ASTRAEA_STAGED_ROOM_ACTIVATION")=="1" and job_script.supported(request):
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
  return # At most one queued activation across BOTH managers per frame.
 if pending.is_empty() and active_job==null:_start_warm()
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
 if what==NOTIFICATION_PREDELETE and active_job!=null:
  # Teardown cannot leave an outstanding loader owner. This may block shutdown;
  # ordinary cancellation polls nonblocking until the same request completes.
  if active_job.loaded_request:
   ResourceLoader.load_threaded_get(active_job.path);active_job.loaded_request=false
  active_job.dispose()
func statistics()->Dictionary:
 return {"prewarm_enabled":prewarm_enabled(),"prewarm_ready":active_job!=null and active_job.phase=="ready","prewarm_lease_limit":1,"prewarm_hits":prewarm_hits,"prewarm_misses":prewarm_misses,"prewarm_rejected":prewarm_rejected,"prewarm_promotions":prewarm_promotions,"prewarm_verify_us":prewarm_verify_us,"safety_overlaps":safety_overlaps,"estimated_byte_limit":limits.MAX_ESTIMATED_BYTES,"memory_hard_limit":false,"staged_active":active_job!=null,"staged_cancelled":staged_cancelled,"staged_failed":staged_failed,"staged_max_slice_us":staged_max_slice_us,"pending":pending.size(),"peak_pending":peak_pending,"completed":completed,"stale":stale,"duplicates":duplicates,"max_activation_us":max_activation_us,"overruns":overruns,"recent":recent.duplicate(true),"hard_frame_time_guarantee":false}
