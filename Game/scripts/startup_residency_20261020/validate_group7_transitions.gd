extends SceneTree
func child(parent:Node,label:String)->Node3D:
 var node:=Node3D.new();node.name=label;parent.add_child(node);return node
func _initialize()->void:call_deferred("run")
func run()->void:
 var host:=child(root,"Host");var space:=child(host,"ShipSpace");child(space,"Districts")
 var actors:=child(space,"PersistentActors");var actor:=child(actors,"Player");actor.position=Vector3(63,52.6,-20.5)
 var systems:=child(host,"ShipSystems")
 var interner=load("res://scripts/startup_residency_20261020/exact_texture_intern.gd").new();node_added.connect(interner.observe)
 var baseline:=OS.get_static_memory_usage()
 var source:Node3D=load("res://scripts/consolidated_all_eight_20261013/package.gd").build(host);interner.flush()
 await physics_frame
 var original_bytes:=OS.get_static_memory_usage()-baseline
 var starts:=[];var ends:=[];var expected:=[]
 for model:Node3D in source.get_children():
  var meshes:=model.find_children("*","MeshInstance3D",true,false)
  if meshes.is_empty():continue
  var bounds:=AABB();var first:=true
  for mesh:MeshInstance3D in meshes:
   var box: AABB=mesh.global_transform*mesh.get_aabb();bounds=box if first else bounds.merge(box);first=false
  var point:=bounds.get_center();var start:=Vector3(point.x,bounds.end.y+1,point.z);var end:=Vector3(point.x,bounds.position.y-1,point.z)
  starts.append(start);ends.append(end);expected.append(host.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(start,end)))
 source.free();await physics_frame
 var manager=load("res://scripts/startup_residency_20261020/exact_contact_residency.gd").new();manager.name="ExactContactResidency";systems.add_child(manager);manager.setup(host);manager.set_physics_process(false)
 var before:=OS.get_static_memory_usage()
 var candidate:Node3D=load("res://scripts/startup_residency_20261020/group7_package.gd").build(host);interner.flush()
 await physics_frame
 var candidate_bytes:=OS.get_static_memory_usage()-before
 var ids:=[]
 for mesh in candidate.find_children("*","MeshInstance3D",true,false):ids.append(mesh.get_instance_id())
 var hits:=0
 for i in range(starts.size()):
  actor.position=expected[i].position if not expected[i].is_empty() else starts[i]
  manager.refresh();await physics_frame
  var got:=host.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(starts[i],ends[i]))
  assert(got.is_empty()==expected[i].is_empty(),"Ray presence differs "+str(i))
  if not got.is_empty():hits+=1;assert(got.position.distance_to(expected[i].position)<0.001)
 var memory:=[]
 for cycle in range(10):
  actor.position=Vector3(10000,10000,10000);manager.refresh();await physics_frame;assert(manager.statistics().active_cells==0)
  actor.position=Vector3(63,52.6,-20.5);manager.refresh();await physics_frame
  memory.append(OS.get_static_memory_usage())
 var final_ids:=[]
 for mesh in candidate.find_children("*","MeshInstance3D",true,false):final_ids.append(mesh.get_instance_id())
 assert(ids==final_ids);assert(int(memory[-1])-int(memory[2])<4*1024*1024)
 print("GROUP7_TRANSITIONS_PASS ",JSON.stringify({"models":starts.size(),"ray_samples":starts.size(),"matching_hits":hits,"original_allocation_bytes":original_bytes,"candidate_spawn_allocation_bytes":candidate_bytes,"all_original_visual_ids_persistent":true,"round_trips":10,"cycle_memory_bytes":memory,"contacts":manager.statistics()}))
 host.free();quit()
