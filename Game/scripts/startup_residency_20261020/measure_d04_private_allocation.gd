extends SceneTree
class ResidencyHost extends Node3D:
 var streamed_models:Dictionary
 var exact_contact_residency:Node
func _initialize():call_deferred("run")
func run():
 var host:=ResidencyHost.new();root.add_child(host)
 host.streamed_models=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/startup_residency_20261020/index.json")).models
 host.exact_contact_residency=load("res://scripts/startup_residency_20261020/exact_contact_residency.gd").new();host.add_child(host.exact_contact_residency);host.exact_contact_residency.setup(host);host.exact_contact_residency.set_physics_process(false)
 var manager=load("res://scripts/startup_residency_20261020/d04_detail_residency.gd").new();host.add_child(manager);manager.setup(host);manager.set_physics_process(false)
 var interner=load("res://scripts/startup_residency_20261020/exact_texture_intern.gd").new();node_added.connect(interner.observe)
 var baseline:=OS.get_static_memory_usage()
 var group:=Node3D.new();host.add_child(group)
 for file in manager.index:
  var manifest:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(str(host.streamed_models[file].manifest_path)))
  var wrapper:=Node3D.new();group.add_child(wrapper)
  var visual:Node3D=load("res://scripts/startup_residency_20261020/original_visual_contacts.gd").instantiate_visual(file,manifest)
  wrapper.add_child(visual);host.exact_contact_residency.register_model(wrapper,manifest);interner.flush()
 var original_bytes:=OS.get_static_memory_usage()-baseline
 var original_nodes:=group.find_children("*","Node",true,false).size()
 group.free();host.exact_contact_residency.entries.clear();await process_frame
 interner.prune_expired_references()
 var shell_baseline:=OS.get_static_memory_usage()
 group=Node3D.new();host.add_child(group)
 for file in manager.index:
  var home:=Node3D.new();home.name=manager.index[file].room_id;group.add_child(home)
  manager.register_room(home,file);interner.flush()
 assert(manager.statistics().resident_interiors==0)
 var shell_bytes:=OS.get_static_memory_usage()-shell_baseline
 print("D04_PRIVATE_ALLOCATION ",JSON.stringify({"rooms":manager.index.size(),"original_all_visuals_bytes":original_bytes,"shell_only_bytes":shell_bytes,"original_nodes":original_nodes,"shell_nodes":group.find_children("*","Node",true,false).size(),"detail_residency":manager.statistics(),"contacts":host.exact_contact_residency.statistics()}))
 host.free();quit()
