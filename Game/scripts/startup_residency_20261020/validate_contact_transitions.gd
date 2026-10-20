extends SceneTree
func _initialize():call_deferred("run")
func run():
 var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(OS.get_cmdline_user_args()[0]))
 var host=Node3D.new();root.add_child(host)
 var space=Node3D.new();space.name="ShipSpace";host.add_child(space)
 var actors=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
 var actor=Node3D.new();actor.name="Player";actors.add_child(actor)
 var source:Node3D=load(d.model_file).instantiate();host.add_child(source)
 var policy:Dictionary=d.get("source_collision_policy",{})
 for mesh:MeshInstance3D in source.find_children("*","MeshInstance3D",true,false):
  if not policy.is_empty() and str(policy[str(mesh.name)].get("role",""))=="hospitality_glass":
   var material=ShaderMaterial.new();material.shader=load("res://shaders/hospitality_glass.gdshader");mesh.material_override=material
  var collide:bool=bool(policy[str(mesh.name)].collide) if not policy.is_empty() else (mesh.visible and not str(mesh.name).begins_with("ALC_VisualFloor"))
  if collide:load("res://scripts/static_contact_cache.gd").attach(mesh)
 var bounds=AABB();var first=true
 for mesh:MeshInstance3D in source.find_children("*","MeshInstance3D",true,false):
  var b=mesh.global_transform*mesh.get_aabb();bounds=b if first else bounds.merge(b);first=false
 await physics_frame
 var expected=[];var starts=[];var ends=[]
 for x in range(1,8):
  for z in range(1,8):
   var at=bounds.position+bounds.size*Vector3(float(x)/8,0,float(z)/8)
   var start=Vector3(at.x,bounds.end.y+1,at.z);var end=Vector3(at.x,bounds.position.y-1,at.z)
   starts.append(start);ends.append(end)
   expected.append(host.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(start,end)))
 source.free()
 var visual:Node3D
 if "--original-visuals" in OS.get_cmdline_user_args():
  visual=Node3D.new();host.add_child(visual)
  var original_visual:Node3D=load("res://scripts/startup_residency_20261020/original_visual_contacts.gd").instantiate_visual(str(d.model_file).get_file(),d)
  visual.add_child(original_visual)
 else:
  visual=load(d.visual_path).instantiate();host.add_child(visual)
 var manager=load("res://scripts/startup_residency_20261020/exact_contact_residency.gd").new();host.add_child(manager);manager.setup(host)
 manager.set_physics_process(false)
 manager.register_model(visual,d)
 actor.position=bounds.get_center();manager.refresh()
 await physics_frame
 var hits=0
 for i in range(starts.size()):
  var got=host.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(starts[i],ends[i]))
  assert(got.is_empty()==expected[i].is_empty(),"Ray presence differs at "+str(i))
  if not got.is_empty():
   hits+=1;assert(got.position.distance_to(expected[i].position)<0.001,"Ray height differs")
 var visible_count=visual.find_children("*","MeshInstance3D",true,false).size()
 var light_ids=[]
 for light in visual.find_children("*","Light3D",true,false):light_ids.append(light.get_instance_id())
 var memory=[]
 for cycle in range(10):
  actor.position=Vector3(10000,10000,10000);manager.refresh();await physics_frame
  assert(manager.statistics().active_cells==0)
  actor.position=bounds.get_center();manager.refresh();await physics_frame
  assert(manager.statistics().active_cells>0)
  assert(visual.find_children("*","MeshInstance3D",true,false).size()==visible_count)
  memory.append(OS.get_static_memory_usage())
 var final_ids=[]
 for light in visual.find_children("*","Light3D",true,false):final_ids.append(light.get_instance_id())
 assert(light_ids==final_ids,"Persistent light identities changed")
 assert(int(memory[-1])-int(memory[2])<4*1024*1024,"Memory increased across repeated contact transitions")
 var cart=RigidBody3D.new();cart.freeze=true;actors.add_child(cart);cart.global_position=bounds.get_center()
 actor.position=Vector3(10000,10000,10000);manager.refresh();assert(manager.statistics().active_cells>0,"Persistent body lost supporting contacts")
 cart.free();manager.refresh();assert(manager.statistics().active_cells==0)
 print("CONTACT_TRANSITIONS ",JSON.stringify({"model":d.model_file,"ray_samples":starts.size(),"matching_hits":hits,"round_trips":10,"light_ids_retained":light_ids.size(),"visual_meshes_always_present":visible_count,"cycle_memory_bytes":memory,"statistics":manager.statistics(),"passed":true}))
 host.free();quit()
