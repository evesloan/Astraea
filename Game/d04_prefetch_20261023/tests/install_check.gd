extends SceneTree
func _initialize()->void:
 var host:Node3D=load("res://d04_prefetch_20261023/tests/host.gd").new();root.add_child(host)
 var manager:Node=load("res://scripts/startup_residency_20261020/d04_detail_residency.gd").new();host.add_child(manager);manager.host=host;manager.index={"sentinel":17};manager.loads=12;manager.releases=7;manager.elapsed=.15
 for i in range(120):manager.entries.append({"id":i})
 host.d04_detail_residency=manager;host.set_meta("runtime_ready",true);host.set_meta("d04_exact_batches_installed",{})
 var identity:=manager.get_instance_id();var predecessor:Script=manager.get_script();var install:Script=load("res://d04_prefetch_20261023/install.gd")
 OS.unset_environment("ASTRAEA_D04_PREFETCH")
 var off:Dictionary=install.install(host)
 if off.installed or manager.get_script()!=predecessor:quit(1);return
 OS.set_environment("ASTRAEA_D04_PREFETCH","1")
 var result:Dictionary=install.install(host);manager.set_process(false);manager.set_physics_process(false)
 var ok:bool=result.installed and manager.get_instance_id()==identity and manager.entries.size()==120 and manager.entries[119].id==119 and manager.host==host and manager.loads==12 and manager.releases==7 and manager.index.sentinel==17 and is_equal_approx(manager.elapsed,.15)
 OS.unset_environment("ASTRAEA_D04_PREFETCH");host.free();print("D04_PREFETCH_INSTALL preserved=",ok);quit(0 if ok else 1)
