extends Node
const CELLS=preload("res://spatial_instance_cells_20261026/runtime.gd")
var light_provider:Callable
var last_result:Dictionary={}
func _enter_tree()->void:call_deferred("activate")
func _ready()->void:
 var source:Node3D=get_parent()
 if not source.tree_exiting.is_connected(release):source.tree_exiting.connect(release)
func activate()->void:
 var source:Node3D=get_parent()
 if source==null or not source.is_inside_tree() or source.has_meta("exact_instance_restore"):return
 if not light_provider.is_valid():return
 var snapshot:Dictionary=light_provider.call(source)
 if snapshot.has("failed"):
  push_error("Exact instance activation refused: "+str(snapshot.failed));return
 last_result=CELLS.compact(source,snapshot.lights)
func release()->void:
 if not CELLS.restore(get_parent()):
  push_error("Exact instance restoration failed before room release")
  get_tree().quit(1)
