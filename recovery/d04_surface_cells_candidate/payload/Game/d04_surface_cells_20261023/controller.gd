extends Node
# Opt-in research successor: one existing D04 residency owner, no new streaming policy.
var host:Node3D
var manager:Node
var started:=false
var stopped:=false
var enabled:=false
var lights:Array=[]
var light_states:Dictionary={}
var observed:Dictionary={}
var reports:Array=[]
var guard_max_us:=0
var detail_poses:Dictionary={}
const HELPER=preload("res://d04_surface_cells_20261023/batcher.gd")
func setup(ship:Node3D)->void:
 host=ship;process_priority=1000000
 enabled=OS.get_environment("ASTRAEA_D04_SURFACE_CELLS")=="1"
 if not enabled:set_process(false)
func light_state(light:Light3D)->Array:
 return [light.global_transform,light.light_cull_mask,light.omni_range if light is OmniLight3D else (light.spot_range if light is SpotLight3D else 0.0)]
func _process(_delta:float)->void:
 if stopped or not host.get_meta("runtime_ready",false):return
 if not started:
  manager=host.d04_detail_residency
  assert(manager!=null and manager.entries.size()==120)
  for light:Light3D in host.find_children("*","Light3D",true,false):
   lights.append(light);light_states[light.get_instance_id()]=light_state(light)
  get_tree().node_added.connect(_node_added)
  started=true
 # Fail back before rendering if the captured light selection ceases to be valid.
 var guard_start:=Time.get_ticks_usec()
 for light in lights:
  if not is_instance_valid(light):
   restore_all("Light removed");return
  var state:Array=light_states[light.get_instance_id()]
  var reach:float=light.omni_range if light is OmniLight3D else (light.spot_range if light is SpotLight3D else 0.0)
  if light.global_transform!=state[0] or light.light_cull_mask!=state[1] or reach!=state[2]:
   restore_all("Light transform/range/layer changed");return
 guard_max_us=maxi(guard_max_us,Time.get_ticks_usec()-guard_start)
 for id in observed:
  var live:Node3D=observed[id].get_ref()
  if live!=null and live.global_transform!=detail_poses[id]:restore_all("Room transform changed");return
 for entry:Dictionary in manager.entries:
  if not is_instance_valid(entry.detail):continue
  var detail:Node3D=entry.detail;var id:=detail.get_instance_id()
  if observed.has(id):continue
  var lo:Array=entry.record.detail_bounds_min;var hi:Array=entry.record.detail_bounds_max
  var detail_bounds:AABB=detail.global_transform*AABB(Vector3(lo[0],lo[1],lo[2]),Vector3(hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2]))
  var local_lights:Array=[]
  for light in lights:
   if light is DirectionalLight3D:local_lights.append(light);continue
   var reach:float=light.omni_range if light is OmniLight3D else light.spot_range
   var p:Vector3=light.global_position;var bounds:AABB=detail_bounds
   if p.distance_squared_to(p.clamp(bounds.position,bounds.end))<=reach*reach:local_lights.append(light)
  var start:=Time.get_ticks_usec();var result:Dictionary=HELPER.build(detail,local_lights)
  HELPER.set_enabled(detail,true);observed[id]=weakref(detail);detail_poses[id]=detail.global_transform
  var row:={"room":entry.record.room_id,"saved_main_submissions":result.saved_submissions,"batch_count":result.batch_count,"light_rejections":result.light_rejections,"build_us":Time.get_ticks_usec()-start}
  reports.append(row);print("D04_SURFACE_CELL_ACTIVATED ",JSON.stringify(row))
  # At most one room activation per frame; no geometry cache survives its residency.
  break
 for id in observed.keys():
  if observed[id].get_ref()==null:observed.erase(id);detail_poses.erase(id)
func _node_added(node:Node)->void:
 if node is Light3D:restore_all("A new light was added")
func restore_all(reason:String)->void:
 for reference:WeakRef in observed.values():
  var detail:Node3D=reference.get_ref()
  if detail!=null:HELPER.set_enabled(detail,false)
 stopped=true;set_process(false);print("D04_SURFACE_CELLS_RESTORED ",reason)
func statistics()->Dictionary:
 return {"enabled":enabled and not stopped,"resident_optimized_rooms":observed.size(),"activations":reports,"known_lights":lights.size(),"light_guard_max_us":guard_max_us,"whole_ship_performance_accepted":false}
