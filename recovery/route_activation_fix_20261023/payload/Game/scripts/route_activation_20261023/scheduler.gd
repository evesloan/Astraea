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
static func obtain(host:Node3D)->Node:
 if OS.get_environment("ASTRAEA_ROOM_ACTIVATION_QUEUE")!="1"or not host.get_meta("runtime_ready",false):return null
 var systems:Node=host.get_node("ShipSystems")
 var existing:=systems.get_node_or_null("VisibilityActivationQueue")
 if existing!=null:return existing
 var result:Node=load("res://scripts/route_activation_20261023/scheduler.gd").new();result.name="VisibilityActivationQueue";systems.add_child(result);return result
func enqueue(owner:Node,entry:Dictionary,identity:Node,kind:String)->void:
 var key:=str(owner.get_instance_id())+":"+str(identity.get_instance_id())
 if keys.has(key):duplicates+=1;return
 keys[key]=true;pending.append({"owner":weakref(owner),"entry":entry,"key":key,"kind":kind});peak_pending=maxi(peak_pending,pending.size())
func _process(_delta:float)->void:
 var begin:=Time.get_ticks_usec()
 while not pending.is_empty()and Time.get_ticks_usec()-begin<SOFT_BUDGET_US:
  var request:Dictionary=pending.pop_front();keys.erase(request.key)
  var owner:Node=request.owner.get_ref()
  if owner==null or not owner.is_inside_tree():stale+=1;continue
  var started:=Time.get_ticks_usec()
  var activated:bool=owner._activate_pending_visibility(request.entry)
  var cost:=Time.get_ticks_usec()-started
  if not activated:stale+=1;continue
  completed+=1;max_activation_us=maxi(max_activation_us,cost)
  if cost>SOFT_BUDGET_US:overruns+=1
  recent.append({"kind":request.kind,"activation_us":cost,"frame":Engine.get_process_frames()})
  if recent.size()>64:recent.pop_front()
  break # At most one actual activation across BOTH managers per frame.
func statistics()->Dictionary:
 return {"pending":pending.size(),"peak_pending":peak_pending,"completed":completed,"stale":stale,"duplicates":duplicates,"max_activation_us":max_activation_us,"overruns":overruns,"recent":recent.duplicate(true),"hard_frame_time_guarantee":false}
