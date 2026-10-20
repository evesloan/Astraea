extends SceneTree
func child(parent:Node,label:String)->Node3D:
 var node:=Node3D.new();node.name=label;parent.add_child(node);return node
func _initialize()->void:call_deferred("run")
func run()->void:
 var config:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/startup_residency_20261020/source_contact_candidates.json"))
 for row in config.models:
  var host:=child(root,"Host");var space:=child(host,"ShipSpace");var actors:=child(space,"PersistentActors");var actor:=child(actors,"Player");var systems:=child(host,"ShipSystems")
  var visual:Node3D=load(str(row.file)).instantiate();host.add_child(visual)
  var bounds:=AABB();var first:=true;var identities:=[]
  var before:=OS.get_static_memory_usage()
  for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
   identities.append([mesh.get_instance_id(),mesh.mesh.get_instance_id(),mesh.transform])
   var box:AABB=mesh.global_transform*mesh.get_aabb();bounds=box if first else bounds.merge(box);first=false
   var collide:bool=str(mesh.name) in row.collision_names if row.has("collision_names") else (mesh.visible and not str(mesh.name).begins_with("ALC_VisualFloor"))
   if collide:
    load("res://scripts/static_contact_cache.gd").attach(mesh)
    mesh.get_node("StaticContact").name=str(row.old_contact_name)
  await physics_frame
  var contact_bytes:=OS.get_static_memory_usage()-before
  var starts:=[];var ends:=[];var expected:=[]
  for x in range(1,8):
   for z in range(1,8):
    var at:=bounds.position+bounds.size*Vector3(float(x)/8,0,float(z)/8)
    var start:=Vector3(at.x,bounds.end.y+1,at.z);var end:=Vector3(at.x,bounds.position.y-1,at.z)
    starts.append(start);ends.append(end);expected.append(host.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(start,end)))
  var manager=load("res://scripts/startup_residency_20261020/exact_contact_residency.gd").new();manager.name="ExactContactResidency";systems.add_child(manager);manager.setup(host);manager.set_physics_process(false)
  load("res://scripts/startup_residency_20261020/immutable_source_contacts.gd").adopt(visual,str(row.file),host)
  var hits:=0
  for i in range(starts.size()):
   actor.position=expected[i].position if not expected[i].is_empty() else starts[i]
   manager.refresh();await physics_frame
   var got:=host.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(starts[i],ends[i]))
   assert(got.is_empty()==expected[i].is_empty(),"Exact receiver ray presence changed "+str(i))
   if not got.is_empty():assert(got.position.distance_to(expected[i].position)<0.001);hits+=1
  var memory:=[]
  for cycle in range(10):
   actor.position=Vector3(10000,10000,10000);manager.refresh();await physics_frame;assert(manager.statistics().active_cells==0)
   actor.position=bounds.get_center();manager.refresh();await physics_frame;assert(manager.statistics().active_cells>0)
   memory.append(OS.get_static_memory_usage())
  var after_ids:=[]
  for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):after_ids.append([mesh.get_instance_id(),mesh.mesh.get_instance_id(),mesh.transform])
  assert(identities==after_ids);assert(int(memory[-1])-int(memory[2])<4*1024*1024)
  actor.position=Vector3(10000,10000,10000);manager.refresh();await physics_frame
  print("SOURCE_CONTACT_TRANSITIONS_PASS ",JSON.stringify({"source":row.file,"ray_samples":49,"matching_hits":hits,"original_contact_bytes":contact_bytes,"after_release_delta_bytes":OS.get_static_memory_usage()-before,"cycles":10,"cycle_memory_bytes":memory,"visual_ids_mesh_resources_transforms_unchanged":true,"contacts":manager.statistics()}))
  host.free();await physics_frame
 quit()
