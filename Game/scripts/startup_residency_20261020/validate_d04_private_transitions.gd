extends SceneTree
class ResidencyHost extends Node3D:
 var streamed_models:Dictionary
 var exact_contact_residency:Node
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var host:=ResidencyHost.new();root.add_child(host)
 host.streamed_models=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/startup_residency_20261020/index.json")).models
 host.exact_contact_residency=load("res://scripts/startup_residency_20261020/exact_contact_residency.gd").new();host.add_child(host.exact_contact_residency);host.exact_contact_residency.setup(host);host.exact_contact_residency.set_physics_process(false)
 var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
 var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
 var actor:=Node3D.new();actor.name="Player";actors.add_child(actor);actor.position=Vector3(10000,10000,10000)
 var manager=load("res://scripts/startup_residency_20261020/d04_detail_residency.gd").new();host.add_child(manager);manager.setup(host);manager.set_physics_process(false)
 for file in ["D04_PORT_AFT_HOME_882_r001.glb","D04_STARBOARD_CENTRAL_HOME_884_r001.glb","D04_STARBOARD_FORWARD_HOME_883_r001.glb"]:
  var record:Dictionary=manager.index[file]
  var manifest:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(str(host.streamed_models[file].manifest_path)))
  var original:Node3D=load("res://scripts/d04_port_forward_homes_fifth.gd").visual(host,file,manifest.source_collision_policy)
  var lo:Array=record.bounds_min;var hi:Array=record.bounds_max
  var bounds:=AABB(Vector3(lo[0],lo[1],lo[2]),Vector3(hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2]))
  await physics_frame
  var queries:=[];var expected:=[]
  for x in range(1,8):
   for z in range(1,8):
    var point:=bounds.position+bounds.size*Vector3(float(x)/8,0,float(z)/8)
    var query:=PhysicsRayQueryParameters3D.create(Vector3(point.x,bounds.end.y+1,point.z),Vector3(point.x,bounds.position.y-1,point.z))
    queries.append(query);expected.append(host.get_world_3d().direct_space_state.intersect_ray(query))
  original.free()
  var home:=Node3D.new();home.name=record.room_id;host.add_child(home)
  home.set_meta("rest_slot_ids",["persistent_test_rest"])
  var door:Node3D=load("res://scripts/guest_entry_door.gd").new();door.name="PersistentEntryDoor";door.persistent_id=&"private_transition_test_entry";door.position=Vector3(5000,5000,5000);home.add_child(door);door.process_mode=Node.PROCESS_MODE_DISABLED;door.open_fraction=.37;door.desired_open=true
  var lamp:=OmniLight3D.new();home.add_child(lamp)
  var ids:=[home.get_instance_id(),door.get_instance_id(),lamp.get_instance_id()]
  var shell:Node3D=manager.register_room(home,file)
  var shell_count:=shell.find_children("*","MeshInstance3D",true,false).size()
  assert(manager.statistics().resident_interiors==0)
  actor.position=bounds.get_center();manager.prepare_position(actor.position);host.exact_contact_residency.prepare_position(actor.position)
  await physics_frame
  for i in range(queries.size()):
   var got:=host.get_world_3d().direct_space_state.intersect_ray(queries[i])
   assert(got.is_empty()==expected[i].is_empty())
   if not got.is_empty():assert(got.position.distance_to(expected[i].position)<.001,"Split private contact ray changed")
  var entry:Dictionary=manager.entries[-1]
  var memory:=[]
  for cycle in range(10):
   var old_detail:WeakRef=weakref(entry.detail)
   actor.position=Vector3(10000,10000,10000);manager.refresh(9.0);host.exact_contact_residency.refresh();await physics_frame
   assert(old_detail.get_ref()==null and entry.detail==null,"Private detail must truly free")
   assert(shell.find_children("*","MeshInstance3D",true,false).size()==shell_count)
   actor.position=bounds.get_center();manager.prepare_position(actor.position);host.exact_contact_residency.prepare_position(actor.position);await physics_frame
   memory.append(OS.get_static_memory_usage())
  assert(memory[-1]-memory[2]<2*1024*1024,"Private detail reload memory did not plateau")
  assert(ids==[home.get_instance_id(),door.get_instance_id(),lamp.get_instance_id()])
  assert(door.open_fraction==.37 and door.desired_open and home.get_meta("rest_slot_ids")==["persistent_test_rest"])
  print("D04_PRIVATE_DETAIL_TRANSITIONS_PASS ",JSON.stringify({"model":file,"ray_samples":queries.size(),"cycles":10,"shell_meshes_always_present":shell_count,"state_and_ids_preserved":true,"memory":memory}))
  actor.position=Vector3(10000,10000,10000);manager.refresh(9.0);host.exact_contact_residency.refresh();manager.entries.clear();host.exact_contact_residency.entries.clear();home.free()
 host.free();quit()
