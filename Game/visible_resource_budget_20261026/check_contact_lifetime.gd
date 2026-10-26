extends SceneTree
const Pool=preload("res://remaining_batch_activation_20261026/contact_partition.gd")
var output:String
func _initialize()->void:
 for arg:String in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.substr(9)
 call_deferred("run")
func run()->void:
 var host:=Node3D.new();host.name="ContactLifetimeFixture";root.add_child(host)
 var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
 var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
 var systems:=Node3D.new();systems.name="ShipSystems";host.add_child(systems)
 var initial:=OS.get_static_memory_usage()
 Pool.prepare_all(host)
 var loaded:=OS.get_static_memory_usage()
 var witnesses:Dictionary={};var ids:Dictionary={};var poses:Dictionary={};var hashes:Dictionary={}
 for key:String in Pool.prepared:
  witnesses[key]=weakref(Pool.prepared[key]);ids[key]=Pool.bodies[key].get_instance_id();poses[key]=Pool.bodies[key].global_transform
  hashes[key]=Pool.prepared[key].get_faces().to_byte_array().hex_encode().sha256_text()
 Pool.enable_release()
 await physics_frame
 await process_frame
 var released:=OS.get_static_memory_usage()
 for key:String in witnesses:
  assert(witnesses[key].get_ref()==null,"Inactive shape retained")
  assert(Pool.bodies[key].get_instance_id()==ids[key] and Pool.bodies[key].global_transform==poses[key])
  assert(Pool.bodies[key].collision_layer==0)
 var rows:Array=[]
 for key:String in Pool.index:
  var start:=Time.get_ticks_usec()
  while not Pool.prefetch(key):await process_frame
  var elapsed:=Time.get_ticks_usec()-start
  assert(Pool.prepared[key].get_faces().to_byte_array().hex_encode().sha256_text()==hashes[key],"Exact triangles changed")
  assert(Pool.bodies[key].get_instance_id()==ids[key] and Pool.bodies[key].global_transform==poses[key])
  witnesses[key]=weakref(Pool.prepared[key])
  Pool.bodies[key].collision_layer=1;Pool.bodies[key].collision_mask=1
  await physics_frame
  await physics_frame
  var faces:PackedVector3Array=Pool.prepared[key].get_faces()
  var chosen:=0;var area:=0.0
  for i in range(0,faces.size(),3):
   var size:float=(faces[i+1]-faces[i]).cross(faces[i+2]-faces[i]).length_squared()
   if size>area:area=size;chosen=i
  var a:Vector3=poses[key]*faces[chosen];var b:Vector3=poses[key]*faces[chosen+1];var c:Vector3=poses[key]*faces[chosen+2]
  var normal:Vector3=(b-a).cross(c-a).normalized();assert(normal.length()>.9)
  var center:Vector3=(a+b+c)/3.0
  var query:=PhysicsRayQueryParameters3D.create(center+normal*.5,center-normal*.5,1)
  query.hit_back_faces=true
  var hit:Dictionary=host.get_world_3d().direct_space_state.intersect_ray(query)
  print(JSON.stringify({"ray_key":key,"center":str(center),"normal":str(normal),"hit":str(hit),"expected_body":str(Pool.bodies[key])}))
  assert(not hit.is_empty() and hit.collider==Pool.bodies[key],"Reactivated exact shape must answer physics query")
  faces=PackedVector3Array();hit.clear()
  Pool.release_room(key)
  await physics_frame
  await process_frame
  assert(witnesses[key].get_ref()==null,"Reactivated resource retained")
  rows.append({"key":key,"prefetch_us":elapsed,"same_body_pose_and_triangles":true,"actual_physics_hit":true})
 var key:String=Pool.index.keys()[0]
 Pool.ensure_prepared(key)
 assert(Pool.prepared.has(key),"Synchronous nearby safety load failed")
 Pool.release_room(key)
 var second:String=Pool.index.keys()[1]
 Pool.prefetch(second)
 while not Pool.discard_pending():await process_frame
 assert(Pool.pending_key.is_empty())
 var stats:=Pool.statistics()
 Pool.release_prepared();host.free()
 await process_frame
 var f:=FileAccess.open(output,FileAccess.WRITE)
 f.store_string(JSON.stringify({"initial_static":initial,"loaded_static":loaded,"released_static":released,"released_bytes":loaded-released,"all_18_weakrefs_expired":true,"rows":rows,"statistics":stats,"final_static":OS.get_static_memory_usage(),"scope":"Exact resource/body lifetime fixture; no installed room/player acceptance"},"\t"));f.close();quit()
