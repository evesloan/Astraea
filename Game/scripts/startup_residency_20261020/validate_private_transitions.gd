extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var host:=Node3D.new();root.add_child(host)
 var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
 var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
 var actor:=Node3D.new();actor.name="Player";actors.add_child(actor);actor.position=Vector3(10000,10000,10000)
 var manager=load("res://scripts/startup_residency_20261020/private_detail_residency.gd").new();host.add_child(manager);manager.setup(host);manager.set_physics_process(false)
 for file in ["StarAtlasSpecialty_473.glb","StarAtlasSpecialty_569.glb","StarAtlasSpecialty_365.glb"]:
  var record:Dictionary=manager.index[file]
  var original:Node3D=load("res://scripts/star_atlas_specialty_first.gd").contact_visual(host,file)
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
  actor.position=bounds.get_center();manager.prepare_position(actor.position)
  await physics_frame
  for i in range(queries.size()):
   var got:=host.get_world_3d().direct_space_state.intersect_ray(queries[i])
   assert(got.is_empty()==expected[i].is_empty())
   if not got.is_empty():assert(got.position.distance_to(expected[i].position)<.001,"Split private contact ray changed")
  var entry:Dictionary=manager.entries[-1]
  var memory:=[]
  for cycle in range(10):
   var old_detail:WeakRef=weakref(entry.detail)
   actor.position=Vector3(10000,10000,10000);manager.refresh(9.0);await physics_frame
   assert(old_detail.get_ref()==null and entry.detail==null,"Private detail must truly free")
   assert(shell.find_children("*","MeshInstance3D",true,false).size()==shell_count)
   actor.position=bounds.get_center();manager.prepare_position(actor.position);await physics_frame
   memory.append(OS.get_static_memory_usage())
  assert(memory[-1]-memory[2]<2*1024*1024,"Private detail reload memory did not plateau")
  assert(ids==[home.get_instance_id(),door.get_instance_id(),lamp.get_instance_id()])
  assert(door.open_fraction==.37 and door.desired_open and home.get_meta("rest_slot_ids")==["persistent_test_rest"])
  print("PRIVATE_DETAIL_TRANSITIONS_PASS ",JSON.stringify({"model":file,"ray_samples":queries.size(),"cycles":10,"shell_meshes_always_present":shell_count,"state_and_ids_preserved":true,"memory":memory}))
  actor.position=Vector3(10000,10000,10000);manager.refresh(9.0);manager.entries.clear();home.free()
 host.free();quit()
