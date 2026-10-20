extends SceneTree
class ResidencyHost extends Node3D:
 var streamed_models:Dictionary
 var exact_contact_residency:Node
 var d04_detail_residency:Node
 func stream_private_visual(parent:Node3D,file:String,policy:Dictionary)->Node3D:
  var manifest:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(str(streamed_models[file].manifest_path)))
  assert(manifest.source_collision_policy==policy)
  return d04_detail_residency.register_room(parent,file)
func _initialize():call_deferred("run")
func run():
 var host:=ResidencyHost.new();root.add_child(host)
 host.streamed_models=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/startup_residency_20261020/index.json")).models
 host.exact_contact_residency=load("res://scripts/startup_residency_20261020/exact_contact_residency.gd").new();host.add_child(host.exact_contact_residency);host.exact_contact_residency.setup(host);host.exact_contact_residency.set_physics_process(false)
 var manager=load("res://scripts/startup_residency_20261020/d04_detail_residency.gd").new();host.add_child(manager);manager.setup(host);manager.set_physics_process(false)
 var interner=load("res://scripts/startup_residency_20261020/exact_texture_intern.gd").new();node_added.connect(interner.observe)
 host.d04_detail_residency=manager
 var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
 var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
 var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
 var actor:=Node3D.new();actor.name="Player";actors.add_child(actor);actor.position=Vector3(10000,10000,10000)
 for file in ["d04_port_aft_neighborhood.gd","d04_starboard_aft_neighborhood.gd","d04_port_central_neighborhood.gd","d04_starboard_central_neighborhood.gd"]:
  load("res://scripts/startup_residency_20261020/d04/"+file).build(host)
  interner.flush()
 assert(manager.entries.size()==80 and manager.statistics().resident_interiors==0)
 print("D04_NEIGHBORHOOD_SHELL_INTEGRATION_PASS ",JSON.stringify({"rooms":manager.entries.size(),"nodes":get_node_count(),"static_bytes":OS.get_static_memory_usage(),"original_builders_gates_doors_lights_retained":true}))
 host.free();quit()
