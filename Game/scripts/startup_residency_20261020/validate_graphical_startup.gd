extends SceneTree
var captures := 0
func _initialize():call_deferred("run")
func capture(label: String):
 await RenderingServer.frame_post_draw
 var image := root.get_texture().get_image()
 assert(image.save_png("/workspace/shared/astraea_runtime_open/graphical_successor_r008_"+label+".png")==OK)
 print("GRAPHICAL_CAPTURE ",label)
func loading_probe():
 await create_timer(3.0,true).timeout
 await capture("loading")
func run():
 assert(DisplayServer.get_name()!="headless")
 print("NORMAL_RENDERER_STARTUP ",DisplayServer.get_name()," original conditional audit selection retained")
 var main:Node=load("res://scenes/main_bounded_startup_20261020.tscn").instantiate()
 var started=Time.get_ticks_msec()
 root.add_child(main)
 loading_probe()
 var ship:Node3D=main.get_node("World360/Astraea")
 if not ship.get_meta("runtime_ready",false):await ship.runtime_ready
 print("BOUNDED_SHIP_READY ",JSON.stringify({"elapsed_ms":Time.get_ticks_msec()-started,"installation_ready":ship.get_node("ReceivedSectionInstallation").get_meta("installation_ready",false),"nodes":get_node_count(),"memory_bytes":OS.get_static_memory_usage(),"contacts":ship.exact_contact_residency.statistics()}))
 await create_timer(5.0,true).timeout
 await capture("ready")
 await create_timer(15.0,true).timeout
 print("BOUNDED_SHIP_SETTLED ",JSON.stringify({"nodes":get_node_count(),"memory_bytes":OS.get_static_memory_usage(),"contacts":ship.exact_contact_residency.statistics()}))
 main.free();quit()
