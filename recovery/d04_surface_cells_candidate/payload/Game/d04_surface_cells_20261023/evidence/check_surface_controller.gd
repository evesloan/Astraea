extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 assert(ProjectSettings.load_resource_pack("/tmp/astraea-laptop-contract-1bc13d51/Astraea-1bc13d51.pck"))
 var index:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://d04_detail_batches_20261022/runtime_r004/INDEX.json"));var row:Dictionary=index.rooms.values()[0]
 var host:Node3D=load("/tmp/surface_host.gd").new();root.add_child(host);host.set_meta("runtime_ready",true)
 var manager:Node=load("res://scripts/startup_residency_20261020/d04_detail_residency.gd").new();host.add_child(manager);manager.set_physics_process(false);host.d04_detail_residency=manager
 var wrapper:=Node3D.new();host.add_child(wrapper);var lo:Array=row.bounds_min;var hi:Array=row.bounds_max
 var entry:={"home":weakref(wrapper),"record":row,"detail":null,"hidden":0.0,"bounds":AABB(Vector3(lo[0],lo[1],lo[2]),Vector3(hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2]))};manager.entries.append(entry)
 for i in 119:manager.entries.append({"detail":null})
 manager._load_entry(entry);assert(entry.detail!=null)
 var light:=OmniLight3D.new();light.position=Vector3(10000,10000,10000);host.add_child(light)
 var c:Node=load("res://d04_surface_cells_20261023/controller.gd").new();host.add_child(c);c.setup(host);c._process(0);c.set_process(false)
 assert(c.statistics().resident_optimized_rooms==1 and entry.detail.get_meta("surface_cells").enabled)
 light.position.x+=1;c._process(0)
 assert(c.stopped and not entry.detail.get_meta("surface_cells").enabled)
 var stats:Dictionary=c.statistics();assert(stats.activations[0].saved_main_submissions>0)
 c.free();manager._release_entry(entry);assert(entry.detail==null);manager._load_entry(entry);assert(not entry.detail.has_meta("surface_cells"))
 var f:=FileAccess.open("/tmp/d04_surface_controller_check.json",FileAccess.WRITE);f.store_string(JSON.stringify({"status":"PASS","actual_d04_load_release_reload":true,"light_move_restores_original_before_render":true,"no_cache_survived_release":true,"stats":stats},"  "));f.close();host.free();print("SURFACE_CONTROLLER_PASS");quit()
