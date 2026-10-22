extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 assert(ProjectSettings.load_resource_pack("/tmp/astraea-laptop-contract-1bc13d51/Astraea-1bc13d51.pck"))
 var host=load("res://scripts/d04_detail_batches_integration_20261022/fixture_host.gd").new();root.add_child(host)
 var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
 var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
 var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
 var player:=Node3D.new();player.name="Player";actors.add_child(player)
 host.exact_texture_intern=load("res://scripts/startup_residency_20261020/exact_texture_intern.gd").new()
 var manager=load("res://scripts/startup_residency_20261020/d04_detail_residency.gd").new();host.add_child(manager);manager.setup(host);host.d04_detail_residency=manager;manager.set_physics_process(false)
 var original_script=manager.get_script()
 await host._construction_step("structural_floor_builder.gd")
 assert(host.has_meta("d04_exact_batches_installed") and manager.get_script()==original_script and manager.entries.is_empty())
 var row:Dictionary=manager.index.values()[0]
 var wrapper:=Node3D.new();host.add_child(wrapper)
 var lo:Array=row.bounds_min;var hi:Array=row.bounds_max
 var bounds:=AABB(Vector3(lo[0],lo[1],lo[2]),Vector3(hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2]))
 var witness:=VisibleOnScreenNotifier3D.new();wrapper.add_child(witness)
 var entry:Dictionary={"home":weakref(wrapper),"record":row,"bounds":bounds,"witness":witness,"detail":null,"hidden":0.0};manager.entries.append(entry)
 player.position=bounds.get_center();manager.refresh(.2);assert(is_instance_valid(entry.detail) and manager.loads==1)
 var first_id:int=entry.detail.get_instance_id()
 player.position=bounds.end+Vector3(25,0,0);manager.refresh(.2);assert(is_instance_valid(entry.detail) and entry.detail.get_instance_id()==first_id)
 player.position=bounds.end+Vector3(70,0,0);manager.refresh(7.9);assert(is_instance_valid(entry.detail));manager.refresh(.2);assert(entry.detail==null and manager.releases==1)
 player.position=bounds.get_center();manager.refresh(.2);assert(is_instance_valid(entry.detail) and manager.loads==2)
 var receipt:Dictionary=host.get_meta("d04_exact_batches_installed");receipt.main_hook_executed=true;receipt.original_manager_script_retained=true;receipt.enter_keep_release_reload_passed=true;receipt.full_ship_launched=false
 host.free()
 var f:=FileAccess.open("/workspace/Astraea-recovered-e6274e77-20261021/Game/d04_detail_batches_20261022/evidence/INTEGRATION_CHECK.json",FileAccess.WRITE);f.store_string(JSON.stringify(receipt,"  "));f.close();print(JSON.stringify(receipt));quit()
