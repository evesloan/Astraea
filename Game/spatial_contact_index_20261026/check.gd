extends SceneTree
var checks:=0
var failures:Array=[]
var output:String
func require(ok:bool,label:String)->void:
 checks+=1
 if not ok:failures.append(label);push_error(label)
func _initialize()->void:
 for a:String in OS.get_cmdline_user_args():
  if a.begins_with("--output="):output=a.substr(9)
 call_deferred("run")
func run()->void:
 var host:=Node3D.new();root.add_child(host)
 var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
 var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
 var player:=Node3D.new();player.name="Player";actors.add_child(player)
 var bank:=Node3D.new();space.add_child(bank)
 var geometry:=BoxMesh.new();geometry.size=Vector3(6,2,6);geometry.material=StandardMaterial3D.new()
 var shape:=geometry.create_trimesh_shape();shape.margin=.017;shape.backface_collision=true
 for i in 7666:
  var mesh:=MeshInstance3D.new();mesh.mesh=geometry;mesh.position=Vector3((i%50-25)*50,0,(i/50-76)*50);bank.add_child(mesh)
  var body:=StaticBody3D.new();body.name="StaticContact";mesh.add_child(body)
  var contact:=CollisionShape3D.new();contact.name="SharedShape";contact.shape=shape;body.add_child(contact)
 var manager=load("res://scripts/startup_contact_residency_20261022/manager.gd").new();host.add_child(manager);manager.setup(host);manager.set_physics_process(false);manager.adopt(bank)
 require(manager.entries.size()==7666,"All exact static contacts indexed")
 var original_ids:Array=[]
 for e:Dictionary in manager.entries:original_ids.append([e.mesh.get_ref().get_instance_id(),e.collider.get_ref().get_instance_id(),e.sha256,e.margin,e.backface])
 var witnesses:Array=[]
 for point:Vector3 in [Vector3.ZERO,Vector3(-48,0,-48),Vector3(500,0,500),Vector3(100000,100000,100000),Vector3(-1250,0,-3800)]:
  player.position=point
  compare(manager,[player.global_position]);witnesses.append(manager.statistics())
 # Same-call explicit preparation after parent/mesh movement must use new world bounds.
 var e:Dictionary=manager.entries[0];var mesh:MeshInstance3D=e.mesh.get_ref()
 bank.position=Vector3(123,7,321);bank.rotation.y=.3;mesh.position+=Vector3(12,0,0)
 var destination:Vector3=(mesh.global_transform*mesh.get_aabb()).get_center()
 manager.prepare_position(destination)
 require(e.collider.get_ref().shape!=null,"Synchronous moved/scaled-parent arrival loads exact contact")
 require(e.bounds==mesh.global_transform*mesh.get_aabb(),"Moved geometry reindexed before query")
 player.global_position=destination;compare(manager,[player.global_position])
 var cart:=RigidBody3D.new();cart.freeze=true;actors.add_child(cart);cart.global_position=destination
 player.position=Vector3(100000,100000,100000);compare(manager,[player.global_position,cart.global_position]);require(e.collider.get_ref().shape!=null,"Remote rigid actor retains support")
 cart.free();compare(manager,[player.global_position]);require(e.collider.get_ref().shape==null,"Teleport away releases previous active contacts")
 e.collider.get_ref().shape=shape
 manager.refresh();require(e.collider.get_ref().shape==null,"Externally restored distant shape enters exact release ownership")
 manager.prepare_position(destination)
 var retained:Shape3D=e.collider.get_ref().shape
 manager.unregister(e);manager.refresh()
 require(e.collider.get_ref().shape==retained and not manager.indexed.has(e.index_id),"Roof handoff removes index ownership and preserves restored contact")
 var baseline=load("res://spatial_contact_index_20261026/baseline_manager.gd").new();host.add_child(baseline);baseline.setup(host);baseline.set_physics_process(false);baseline.entries=manager.entries
 player.global_position=destination
 for i in 5:
  var body:=RigidBody3D.new();body.freeze=true;actors.add_child(body);body.position=Vector3(100*i,0,100*i)
 manager.refresh()
 var indexed_times:Array=[];var baseline_times:Array=[]
 for i in 20:
  var start:int=Time.get_ticks_usec();manager.refresh();indexed_times.append(Time.get_ticks_usec()-start)
  start=Time.get_ticks_usec();baseline.refresh();baseline_times.append(Time.get_ticks_usec()-start)
 indexed_times.sort();baseline_times.sort()
 var old_size:Vector3=geometry.size;geometry.size=old_size+Vector3.ONE
 require(manager.entries.all(func(row:Dictionary)->bool:return bool(row.bounds_dirty)),"Shared resource invalidates all indexed owners once")
 geometry.size=old_size;manager.refresh()
 var removed:Dictionary=manager.entries.back();var removed_id:int=removed.index_id;removed.mesh.get_ref().free();manager.refresh()
 require(not manager.indexed.has(removed_id) and not manager.active_entries.has(removed_id),"Freed geometry removes stale index ownership")
 var large_root:=Node3D.new();space.add_child(large_root)
 var large:=MeshInstance3D.new();var huge:=BoxMesh.new();huge.size=Vector3(1000,1000,1000);huge.material=StandardMaterial3D.new();large.mesh=huge;large_root.add_child(large)
 var large_body:=StaticBody3D.new();large_body.name="StaticContact";large.add_child(large_body)
 var large_contact:=CollisionShape3D.new();large_contact.name="SharedShape";large_contact.shape=huge.create_trimesh_shape();large_body.add_child(large_contact)
 manager.adopt(large_root);manager.refresh();require(manager.oversized.has(large.get_instance_id()),"Long geometry uses exact oversized fallback")
 manager.prepare_position(Vector3(499,0,0));require(large_contact.shape!=null,"Long cross-bin contact remains synchronously available")
 manager.unregister(manager.indexed[large.get_instance_id()]);large_root.free()

 var result:={"checks":checks,"failures":failures,"witnesses":witnesses,"final":manager.statistics(),"indexed_refresh_median_us":(indexed_times[9]+indexed_times[10])/2.0,"baseline_refresh_median_us":(baseline_times[9]+baseline_times[10])/2.0,"timing_scope":"Headless 7666-contact fixture; not game FPS; unchanged source exact shapes and same positions"}
 if not output.is_empty():var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify(result,"  "));f.close()
 print("SPATIAL_CONTACT_RESULT ",JSON.stringify(result));host.free();quit(0 if failures.is_empty() else 1)
func compare(manager:Node,positions:Array[Vector3])->void:
 var wanted:Dictionary={}
 for e:Dictionary in manager.entries:
  var mesh:MeshInstance3D=e.mesh.get_ref();var contact:CollisionShape3D=e.collider.get_ref()
  var box:AABB=mesh.global_transform*mesh.get_aabb()
  var eligible:=false
  for p:Vector3 in positions:
   if manager._near(p,box,manager.KEEP if contact.shape!=null else manager.ENTER):eligible=true;break
  wanted[e.index_id]=eligible
 manager.refresh()
 for e:Dictionary in manager.entries:
  var contact:CollisionShape3D=e.collider.get_ref()
  require((contact.shape!=null)==wanted[e.index_id],"Indexed eligibility equals original full scan")
  if contact.shape!=null:require(is_equal_approx(contact.shape.margin,e.margin) and contact.shape.backface_collision==e.backface,"Exact contact flags retained")
