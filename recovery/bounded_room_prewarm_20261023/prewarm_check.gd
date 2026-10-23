extends SceneTree
class Host:
 extends Node3D
 var exact_texture_intern:RefCounted
class Witness:
 extends RefCounted
 var visible:=false
 func is_on_screen()->bool:return visible
var failures:Array=[]
var checks:=0
var receipts:Array=[]
func check(ok:bool,label:String)->void:
 checks+=1
 if not ok:failures.append(label)
func _initialize()->void:call_deferred("run")
func signature(node:Node)->String:
 var hash:=HashingContext.new();hash.start(HashingContext.HASH_SHA256)
 for mesh:MeshInstance3D in node.find_children("*","MeshInstance3D",true,false):
  hash.update(str(node.get_path_to(mesh)).to_utf8_buffer());hash.update(var_to_bytes(mesh.transform))
  if mesh.mesh!=null:
   hash.update(mesh.mesh.get_faces().to_byte_array())
   for surface in range(mesh.mesh.get_surface_count()):
    var material:Material=mesh.get_active_material(surface)
    if material is BaseMaterial3D:hash.update(var_to_bytes([material.albedo_color,material.transparency,material.roughness,material.metallic]))
    elif material is ShaderMaterial:hash.update(material.shader.code.to_utf8_buffer())
 for c:CollisionShape3D in node.find_children("*","CollisionShape3D",true,false):
  hash.update(str(node.get_path_to(c)).to_utf8_buffer());hash.update(c.shape.get_faces().to_byte_array());hash.update(var_to_bytes(c.transform));hash.update(var_to_bytes(c.shape.margin))
 return hash.finish().hex_encode()
func run()->void:
 var pack:=PCKPacker.new();check(pack.pck_start(OS.get_environment("ASTRAEA_FIXTURE_OVERLAY"))==OK,"pack_start")
 var mapping:Array=JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("ASTRAEA_FIXTURE_MAP")))
 for row in mapping:
  check(FileAccess.get_sha256(row.source)==row.sha256,"mount_hash "+str(row.path))
  check(pack.add_file(row.path,row.source)==OK,"pack_add")
 check(pack.flush()==OK,"pack_flush")
 check(ProjectSettings.load_resource_pack(OS.get_environment("ASTRAEA_FIXTURE_BASE_PACK")),"retained_import_pack")
 check(ProjectSettings.load_resource_pack(OS.get_environment("ASTRAEA_FIXTURE_OVERLAY")),"successor_mount")
 if not failures.is_empty():print(failures);quit(2);return
 var interner=load("res://scripts/startup_residency_20261020/exact_texture_intern.gd").new()
 node_added.connect(interner.observe)
 var host:=Host.new();host.exact_texture_intern=interner;root.add_child(host);host.set_meta("runtime_ready",true)
 var systems:=Node.new();systems.name="ShipSystems";host.add_child(systems)
 var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
 var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
 var actor:=Node3D.new();actor.name="Player";actors.add_child(actor);actor.position=Vector3(5000,5000,5000)
 var received:Node=load("res://scripts/received_homes_20261015/residency.gd").new();host.add_child(received);received.host=host;received.actor=actor;received.set_physics_process(false)
 var private_manager:Node=load("res://scripts/startup_residency_20261020/private_detail_residency.gd").new();host.add_child(private_manager);private_manager.setup(host);private_manager.set_physics_process(false)
 var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/TIDAL_UNIT_CANDIDATES.json"))
 var unit:Dictionary=definition.units[0];var prototype:Dictionary={}
 for p in definition.prototypes:
  if p.key==unit.source_recipe_key:prototype=p;break
 var room:=Node3D.new();room.name=unit.rebuild_identity
 room.position=Vector3(unit.source_origin_world_xyz[0],unit.source_origin_world_xyz[1],unit.source_origin_world_xyz[2]);room.rotation.y=unit.source_yaw_godot
 room.set_meta("source_rest_slots",unit.anchor_bindings);room.set_meta("deferred_visual_path","res://assets/models/"+str(prototype.model_file));room.set_meta("deferred_visual_meshes",int(prototype.mesh_batches))
 var room_id:=room.get_instance_id();var rw:=Witness.new()
 var re:Dictionary={"room":room,"parent":host,"bounds":AABB(room.position,Vector3.ONE),"witness":rw,"attached":false,"hidden_seconds":0.0,"meshes":prototype.mesh_batches};received.entries.append(re)
 var record:Dictionary=private_manager.index.values()[0]
 var home:=Node3D.new();home.name=record.room_id;host.add_child(home)
 var shell:Node3D=private_manager.register_room(home,record.model_file)
 var pe:Dictionary=private_manager.entries[0];var pw:=Witness.new();pe.witness=pw
 var home_id:=home.get_instance_id();var shell_id:=shell.get_instance_id();var shell_sig:=signature(shell)
 var cache=load("res://scripts/static_contact_cache.gd")
 for flag in ["ASTRAEA_ROOM_ACTIVATION_QUEUE","ASTRAEA_PRIVATE_CONTACT_SINGLE_PASS","ASTRAEA_PACKED_CONTACT_FACES","ASTRAEA_STAGED_ROOM_ACTIVATION"]:OS.set_environment(flag,"1")
 OS.set_environment("ASTRAEA_ROOM_PREWARM","0")
 received._attach_visible_room_now(re);private_manager._load_entry(pe)
 var baseline:Array=[signature(room.get_meta("resident_visual")),signature(pe.detail)]
 await release_all(received,private_manager,actor,rw,pw,interner)
 var q:Node=systems.get_node("VisibilityActivationQueue")
 var limits=load("res://scripts/route_activation_20261023/prewarm_limits.gd")
 check(not q.prewarm_enabled(),"default_off")
 OS.set_environment("ASTRAEA_ROOM_PREWARM","1")
 var samples:Array=[]
 for cycle in range(3):
  for kind in ["received_room","private_detail"]:
   var manager:Node=received if kind=="received_room" else private_manager
   var entry:Dictionary=re if kind=="received_room" else pe
   var identity:Node=room if kind=="received_room" else home
   actor.position=entry.bounds.end+Vector3(55.0 if kind=="received_room" else 30.0,0,0)
   manager.refresh(0.2)
   var ready:bool=await wait_phase(q,"ready")
   check(ready,"ready_"+kind+str(cycle))
   if not ready:await finish(host,q);return
   var orphan:WeakRef=weakref(q.active_job.visual)
   check(not q.active_job.visual.is_inside_tree(),"complete_offtree_"+kind)
   check(not q.active_job.visual.find_children("*","CollisionShape3D",true,false).is_empty(),"body_before_ready_"+kind)
   check(not re.attached and pe.detail==null,"speculation_never_attached")
   var before_hits:int=q.prewarm_hits
   if cycle==0:manager.prepare_position(entry.bounds.position)
   elif cycle==1:
    if kind=="received_room":rw.visible=true;received._attach_visible_room(re)
    else:pw.visible=true;private_manager._load_visible(pe)
   else:
    if kind=="received_room":rw.visible=true
    else:pw.visible=true
    q.enqueue(manager,entry,identity,kind)
   var resident:Node=room.get_meta("resident_visual",null) if kind=="received_room" else pe.detail
   check(is_instance_valid(resident) and orphan.get_ref()==resident,"atomic_same_visual_"+kind)
   check(q.active_job==null and q.prewarm_hits==before_hits+1,"ready_consumed_once_"+kind)
   if is_instance_valid(resident):check(signature(resident)==baseline[0 if kind=="received_room" else 1],"exact_warm_geometry_"+kind)
   resident=null
   await release_all(received,private_manager,actor,rw,pw,interner)
   check(orphan.get_ref()==null,"warm_resource_release_"+kind)
  samples.append({"cycle":cycle,"nodes":get_node_count(),"resources":Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT),"shapes":cache.live_shape_count(),"static_bytes":OS.get_static_memory_usage()})
 # A truly cold visible arrival completes in this call, not several queue frames later.
 rw.visible=true;received._attach_visible_room(re)
 check(re.attached and room.has_meta("resident_visual"),"cold_received_immediate")
 pw.visible=true;private_manager._load_visible(pe)
 check(is_instance_valid(pe.detail),"cold_private_immediate")
 check([signature(room.get_meta("resident_visual")),signature(pe.detail)]==baseline,"cold_exact")
 await release_all(received,private_manager,actor,rw,pw,interner)
 # Cancel both a loaded orphan and an outstanding threaded request through real interest reversal.
 for target_phase in ["wait","configure","ready"]:
  for kind in ["received_room","private_detail"]:
   var manager:Node=received if kind=="received_room" else private_manager
   var entry:Dictionary=re if kind=="received_room" else pe
   actor.position=entry.bounds.end+Vector3(55.0 if kind=="received_room" else 30.0,0,0);manager.refresh(0.2)
   var reached:bool=await wait_phase(q,target_phase)
   check(reached,"cancel_phase_"+kind+target_phase)
   if not reached:await finish(host,q);return
   var weak:WeakRef=weakref(q.active_job.visual) if q.active_job.visual!=null else null
   actor.position=Vector3(5000,5000,5000);manager.refresh(0.2)
   await wait_idle(q)
   check(q.active_job==null and q.keys.is_empty(),"cancel_drained_"+kind+target_phase)
   check(weak==null or weak.get_ref()==null,"cancel_orphan_freed_"+kind+target_phase)
   check(not re.attached and pe.detail==null,"cancel_no_commit_"+kind+target_phase)
   receipts.append({"kind":kind,"cancel_phase":target_phase,"drained":q.active_job==null})
 # Partial safety arrival cancels the speculative owner and uses the original synchronous path.
 for kind in ["received_room","private_detail"]:
  var manager:Node=received if kind=="received_room" else private_manager
  var entry:Dictionary=re if kind=="received_room" else pe
  actor.position=entry.bounds.end+Vector3(55.0 if kind=="received_room" else 30.0,0,0);manager.refresh(0.2)
  var reached:bool=await wait_phase(q,"configure")
  check(reached,"safety_partial_"+kind)
  if not reached:await finish(host,q);return
  var orphan:WeakRef=weakref(q.active_job.visual)
  manager.prepare_position(entry.bounds.position)
  var resident:Node=room.get_meta("resident_visual",null) if kind=="received_room" else pe.detail
  check(is_instance_valid(resident),"safety_sync_"+kind)
  if is_instance_valid(resident):check(signature(resident)==baseline[0 if kind=="received_room" else 1],"safety_exact_"+kind)
  check(q.active_job!=null and q.active_job.cancelled,"safety_owner_retained_for_drain_"+kind)
  resident=null;await wait_idle(q)
  check(orphan.get_ref()==null,"safety_orphan_freed_"+kind)
  await release_all(received,private_manager,actor,rw,pw,interner)
 # Generation change rejects the old complete lease before original fallback.
 actor.position=re.bounds.end+Vector3(55,0,0);received.refresh(0.2)
 check(await wait_phase(q,"ready"),"generation_ready")
 if q.active_job==null:await finish(host,q);return
 var invalidated:WeakRef=weakref(q.active_job.visual);var old_hits:int=q.prewarm_hits
 re.prewarm_generation=int(re.get("prewarm_generation",0))+1
 received.prepare_position(re.bounds.position)
 check(re.attached and q.prewarm_hits==old_hits and invalidated.get_ref()==null,"generation_invalidated")
 await release_all(received,private_manager,actor,rw,pw,interner)
 # Existing visible complete residents are never evicted to make speculative room.
 rw.visible=true;received._attach_visible_room(re)
 var resident_id:int=room.get_meta("resident_visual").get_instance_id()
 actor.position=pe.bounds.end+Vector3(30,0,0);private_manager.refresh(0.2)
 check(await wait_phase(q,"ready"),"other_room_ready")
 received.refresh(8.1)
 check(re.attached and room.get_meta("resident_visual").get_instance_id()==resident_id,"visible_resident_not_evicted")
 actor.position=Vector3(5000,5000,5000);private_manager.refresh(0.2);await wait_idle(q)
 await release_all(received,private_manager,actor,rw,pw,interner)
 # Existing unsupported paths and independent flags remain excluded.
 var staged=load("res://scripts/route_activation_20261023/staged_job.gd")
 var request:Dictionary={"owner":weakref(received),"identity":weakref(room),"entry":re,"kind":"received_room"}
 room.set_meta("retained_group2_home",true);check(not staged.supported(request),"group2_excluded");room.remove_meta("retained_group2_home")
 OS.set_environment("ASTRAEA_PRIVATE_CONTACT_SINGLE_PASS","0")
 check(not staged.supported({"owner":weakref(private_manager),"identity":weakref(home),"entry":pe,"kind":"private_detail"}),"private_flag_excluded")
 OS.set_environment("ASTRAEA_PRIVATE_CONTACT_SINGLE_PASS","1")
 # Cheap admission excludes oversize and unknown neighbors BEFORE any ResourceLoader request.
 var source_path:String=str(room.get_meta("deferred_visual_path"))
 var original:Dictionary=limits.estimates[source_path].duplicate(true)
 limits.estimates[source_path].face_vertices=limits.MAX_FACE_VERTICES+1
 q.offer_prewarm(received,re,room,"received_room",true,4.0)
 check(q.warm_candidate.is_empty() and q.active_job==null,"oversize_no_allocation")
 limits.estimates[source_path]=original
 var unknown:=Node3D.new();unknown.set_meta("deferred_visual_path","res://assets/models/unregistered.glb")
 var ue:Dictionary={"room":unknown,"parent":host,"attached":false,"witness":Witness.new(),"prewarm_interest":false}
 q.offer_prewarm(received,ue,unknown,"received_room",true,1.0)
 q.offer_prewarm(received,re,room,"received_room",true,4.0)
 check(q.warm_candidate.get("key","")==q.request_key(received,room),"unknown_nearest_cannot_starve_known")
 q.offer_prewarm(received,re,room,"received_room",false,4.0);unknown.free()
 check(q.active_job==null and q.warm_candidate.is_empty(),"admission_cleanup")
 for sample in samples:
  check(sample.nodes==samples[0].nodes and sample.resources==samples[0].resources and sample.shapes==samples[0].shapes,"repeated_resource_return")
 check(room.get_instance_id()==room_id and home.get_instance_id()==home_id and shell.get_instance_id()==shell_id and signature(shell)==shell_sig,"persistent_identity_and_shell")
 check(room.get_meta("source_rest_slots")==unit.anchor_bindings,"rest_identity")
 receipts.append({"cycles":samples})
 await finish(host,q)
func wait_phase(queue:Node,target:String)->bool:
 for tick in range(1200):
  if queue.active_job!=null and queue.active_job.phase==target:return true
  await process_frame
 return false
func wait_idle(queue:Node)->void:
 for tick in range(1200):
  if queue.active_job==null and queue.pending.is_empty() and queue.warm_candidate.is_empty():return
  await process_frame
 check(false,"idle_timeout")
func release_all(received:Node,private_manager:Node,actor:Node3D,rw:RefCounted,pw:RefCounted,interner:RefCounted)->void:
 actor.position=Vector3(5000,5000,5000);rw.visible=false;pw.visible=false
 received.refresh(8.1);private_manager.refresh(8.1)
 interner.flush();interner.prune_expired_references();private_manager.prune_expired_contacts()
 await physics_frame
func finish(host:Node,queue:Node)->void:
 print("PREWARM_RESULT ",JSON.stringify({"checks":checks,"failures":failures,"receipts":receipts,"queue":queue.statistics(),"rendered":false,"full_ship":false,"hard_memory_cap":false,"fps_claim":false}))
 host.free();await process_frame
 quit(0 if failures.is_empty() else 1)
