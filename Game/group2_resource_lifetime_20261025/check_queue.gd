extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var host:=Node3D.new();root.add_child(host);host.set_meta("runtime_ready",true)
	var actor:=Node3D.new();host.add_child(actor)
	var manager:Node=load("res://scripts/received_homes_20261015/residency.gd").new()
	host.add_child(manager);manager.set_physics_process(false);manager.host=host;manager.actor=actor
	var room:=Node3D.new()
	var witness:=VisibleOnScreenNotifier3D.new();host.add_child(witness)
	var entry:Dictionary={"room":room,"parent":host,"witness":witness,"bounds":AABB(Vector3(1000,1000,1000),Vector3.ONE),"attached":false,"hidden_seconds":0.0}
	for i in range(8):manager._on_screen_entered(entry)
	var deduplicated:bool=manager.pending_visible.size()==1
	await process_frame
	var delayed:bool=not entry.attached
	for i in range(4):await process_frame
	var stale_rejected:bool=not entry.attached and room.get_parent()==null and manager.pending_visible.is_empty() and manager.stale_visible_requests==1
	entry.bounds=AABB(Vector3(-1,-1,-1),Vector3(2,2,2))
	var near_admitted:bool=manager._attach_visible_room(entry) and entry.attached and room.get_parent()==host
	var duplicate_rejected:bool=not manager._attach_visible_room(entry)
	var result:={"deduplicated":deduplicated,"waited_for_renderer_frames":delayed,"stale_request_rejected":stale_rejected,"near_room_admitted_synchronously":near_admitted,"duplicate_attach_rejected":duplicate_rejected}
	print("RECEIVED_QUEUE_GUARDS ",JSON.stringify(result))
	host.free()
	quit(0 if deduplicated and delayed and stale_rejected and near_admitted and duplicate_rejected else 1)
