extends SceneTree
class Host:
 extends Node3D
 var exact_texture_intern:RefCounted
class Witness:
 extends RefCounted
 var visible:=false
 func is_on_screen()->bool:return visible
var failures:Array=[]
func check(ok:bool,label:String)->void:
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
 var signatures:Array=[];var samples:Array=[];var weak_visuals:Array=[]
 OS.set_environment("ASTRAEA_ROOM_ACTIVATION_METRICS","1")
 for cycle in range(8):
  var optimized:=true
  OS.set_environment("ASTRAEA_STAGED_ROOM_ACTIVATION","1" if cycle>=2 else "0")
  for flag in ["ASTRAEA_ROOM_ACTIVATION_QUEUE","ASTRAEA_PRIVATE_CONTACT_SINGLE_PASS","ASTRAEA_PACKED_CONTACT_FACES"]:OS.set_environment(flag,"1" if optimized else "0")
  # Visibility arrivals, then shared queue. Real managers and real resources; controlled witness.
  rw.visible=true;pw.visible=true
  received._attach_visible_room(re);private_manager._load_visible(pe)
  var queue:Node=systems.get_node_or_null("VisibilityActivationQueue")
  if queue!=null:
   if cycle==2:
    rw.visible=false;pw.visible=false
    for tick in range(3):await process_frame
    check(not re.attached and pe.detail==null,"stale_visibility_rejected")
    rw.visible=true;pw.visible=true;received._attach_visible_room(re);private_manager._load_visible(pe)
   for tick in range(400):
    if re.attached and pe.detail!=null:break
    await process_frame
  check(re.attached and is_instance_valid(pe.detail),"visibility_activation")
  var visual:Node3D=room.get_meta("resident_visual")
  var pair:Array=[signature(visual),signature(pe.detail)];signatures.append(pair)
  check(pair==signatures[0],"exact_contacts_cycle "+str(cycle))
  weak_visuals=[weakref(visual),weakref(pe.detail)]
  var stages:Dictionary=room.get_meta("last_activation_metrics",{}).duplicate(true)
  visual=null
  rw.visible=false;pw.visible=false;received.refresh(8.1);private_manager.refresh(8.1)
  check(not re.attached and pe.detail==null,"release_cycle")
  check(weak_visuals[0].get_ref()==null and weak_visuals[1].get_ref()==null,"visuals_freed")
  # Explicit arrival must still finish collision creation synchronously with flags enabled.
  if cycle==7:
   received.prepare_position(re.bounds.position);private_manager.prepare_position(pe.bounds.position)
   check(re.attached and pe.detail!=null,"synchronous_prepare")
   received.refresh(8.1);private_manager.refresh(8.1)
  interner.flush();interner.prune_expired_references()
  private_manager.prune_expired_contacts()
  await physics_frame
  samples.append({"cycle":cycle,"optimized":optimized,"nodes":get_node_count(),"resources":Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT),"live_shapes":cache.live_shape_count(),"static_bytes":OS.get_static_memory_usage(),"texture_cache":interner.statistics(),"stages":stages,"staged":cycle>=2})
  check(room.get_instance_id()==room_id and home.get_instance_id()==home_id and shell.get_instance_id()==shell_id and signature(shell)==shell_sig,"persistent_shell_and_identity")
  check(room.get_meta("source_rest_slots")==unit.anchor_bindings,"rest_slots")
 var cancellation_receipts:Array=[]
 var q:Node=systems.get_node("VisibilityActivationQueue")
 for spec in [{"kind":"received_room","phase":"faces"},{"kind":"private_detail","phase":"faces"},{"kind":"received_room","phase":"commit"},{"kind":"private_detail","phase":"commit"}]:
  var kind:String=spec.kind
  rw.visible=kind=="received_room";pw.visible=kind=="private_detail"
  if rw.visible:received._attach_visible_room(re)
  else:private_manager._load_visible(pe)
  var reached:=false
  for tick in range(400):
   if q.active_job!=null and q.active_job.phase==spec.phase:
    reached=true;break
   await process_frame
  check(reached,"partial_stage_reached "+kind)
  var partial:WeakRef=weakref(q.active_job.visual) if q.active_job!=null and q.active_job.visual!=null else null
  var cancelled_at:String=q.active_job.phase if q.active_job!=null else "missing"
  rw.visible=false;pw.visible=false
  for tick in range(400):
   if q.active_job==null and q.pending.is_empty():break
   await process_frame
  check(partial!=null and partial.get_ref()==null,"partial_visual_released "+kind)
  check(not re.attached and pe.detail==null,"partial_not_committed "+kind)
  interner.flush();interner.prune_expired_references();private_manager.prune_expired_contacts()
  cancellation_receipts.append({"kind":kind,"cancelled_at":cancelled_at,"nodes":get_node_count(),"resources":Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT),"live_shapes":cache.live_shape_count()})
 # A synchronous safety arrival supersedes an already-partially prepared visibility job.
 rw.visible=true;pw.visible=true;received._attach_visible_room(re);private_manager._load_visible(pe)
 var prepared_partial:WeakRef
 for tick in range(400):
  if q.active_job!=null and q.active_job.phase=="faces":prepared_partial=weakref(q.active_job.visual);break
  await process_frame
 check(prepared_partial!=null,"safety_overlap_prepared")
 received.prepare_position(re.bounds.position);private_manager.prepare_position(pe.bounds.position)
 check(re.attached and pe.detail!=null,"safety_overlap_collision_ready")
 check([signature(room.get_meta("resident_visual")),signature(pe.detail)]==signatures[0],"safety_overlap_geometry")
 for tick in range(400):
  if q.active_job==null and q.pending.is_empty():break
  await process_frame
 check(prepared_partial.get_ref()==null,"superseded_partial_released")
 rw.visible=false;pw.visible=false;received.refresh(8.1);private_manager.refresh(8.1)
 interner.flush();interner.prune_expired_references();private_manager.prune_expired_contacts()
 check(cache.live_shape_count()==samples[3].live_shapes,"safety_overlap_shape_return")
 # Compare warmed optimized cycles; resources are global counts, not owner RID counts.
 for i in range(4,samples.size()):
  check(samples[i].nodes==samples[3].nodes,"node_return")
  check(samples[i].resources==samples[3].resources,"resource_return")
  check(samples[i].live_shapes==samples[3].live_shapes,"shape_return")
 var queue:Node=systems.get_node_or_null("VisibilityActivationQueue")
 var queue_stats:Dictionary=queue.statistics() if queue!=null else {}
 var seen_frames:Dictionary={}
 for event in queue_stats.get("recent",[]):
  check(not seen_frames.has(event.frame),"at_most_one_queued_activation_per_process_frame")
  seen_frames[event.frame]=true
 print("CONNECTED_RESULT ",JSON.stringify({"failures":failures,"received_room":str(room.name),"received_prototype":prototype.model_file,"private_room":record.room_id,"private_prototype":record.model_file,"samples":samples,"cancellations":cancellation_receipts,"queue":queue_stats,"renderer_visibility_tested":false,"full_ship":false}))
 host.free();await process_frame
 quit(0 if failures.is_empty() else 1)
