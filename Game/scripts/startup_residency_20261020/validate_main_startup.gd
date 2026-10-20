extends SceneTree
func _initialize():call_deferred("run")
func run():
 var ship:Node3D=load("res://scenes/ship_bounded_startup_20261020.tscn").instantiate()
 ship.set_script(load("res://scripts/startup_residency_20261020/ship.gd"))
 var started=Time.get_ticks_msec()
 root.add_child(ship)
 if not ship.get_meta("runtime_ready",false):await ship.runtime_ready
 print("BOUNDED_SHIP_READY ",JSON.stringify({"elapsed_ms":Time.get_ticks_msec()-started,"installation_ready":ship.get_node("ReceivedSectionInstallation").get_meta("installation_ready",false),"nodes":get_node_count(),"memory_bytes":OS.get_static_memory_usage(),"contacts":ship.exact_contact_residency.statistics()}))
 for i in range(120):await physics_frame
 print("BOUNDED_SHIP_SETTLED ",JSON.stringify({"nodes":get_node_count(),"memory_bytes":OS.get_static_memory_usage(),"contacts":ship.exact_contact_residency.statistics()}))
 ship.free();quit()
