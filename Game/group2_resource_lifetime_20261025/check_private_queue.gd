extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var results:Array=[]
	for script_path:String in ["res://scripts/startup_residency_20261020/private_detail_residency.gd","res://scripts/startup_residency_20261020/d04_detail_residency.gd"]:
		var host:=Node3D.new();root.add_child(host)
		var home:=Node3D.new();host.add_child(home)
		var witness:=VisibleOnScreenNotifier3D.new();home.add_child(witness)
		var manager:Node=load(script_path).new();host.add_child(manager)
		manager.host=host;manager.set_physics_process(false)
		var entry:Dictionary={"home":weakref(home),"detail":null,"witness":witness}
		for i in range(8):manager._request_visible(entry)
		var deduplicated:bool=manager.pending_visible.size()==1
		for i in range(4):await process_frame
		var startup_held:bool=manager.pending_visible.size()==1 and manager.loads==0
		host.set_meta("runtime_ready",true)
		for i in range(3):await process_frame
		var stale_rejected:bool=manager.pending_visible.is_empty() and manager.stale_visible_requests==1 and manager.loads==0
		results.append({"script":script_path,"deduplicated":deduplicated,"held_until_ready":startup_held,"stale_request_rejected":stale_rejected})
		host.free()
	var ok:=true
	for result:Dictionary in results:
		if not result.deduplicated or not result.held_until_ready or not result.stale_request_rejected:ok=false
	print("PRIVATE_QUEUE_GUARDS ",JSON.stringify(results));quit(0 if ok else 1)
