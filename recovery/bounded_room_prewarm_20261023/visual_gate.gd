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
func capture(path:String)->Image:
 await process_frame
 await RenderingServer.frame_post_draw
 var img:Image=root.get_texture().get_image();img.save_png(path);return img
func difference(a:Image,b:Image)->Dictionary:
 var aa:=a.get_data();var bb:=b.get_data();var changed:=0;var max_delta:=0
 for i in range(aa.size()):
  if aa[i]!=bb[i]:changed+=1;max_delta=maxi(max_delta,absi(int(aa[i])-int(bb[i])))
 return {"changed_channels":changed,"total_channels":aa.size(),"max_delta":max_delta}
func down_hit(host:Node3D,eye:Vector3)->bool:
 var query:=PhysicsRayQueryParameters3D.create(eye,eye-Vector3(0,3,0))
 return not host.get_world_3d().direct_space_state.intersect_ray(query).is_empty()
func shape_probe(shape:Shape3D,label:String)->Dictionary:
 var path:="/tmp/astraea-prebuilt-"+label+".res"
 var begin:=Time.get_ticks_usec();var saved:=ResourceSaver.save(shape,path);var save_us:=Time.get_ticks_usec()-begin
 begin=Time.get_ticks_usec();var cold:Shape3D=ResourceLoader.load(path,"Shape3D",ResourceLoader.CACHE_MODE_IGNORE);var load_us:=Time.get_ticks_usec()-begin
 var equal:bool=cold.get_faces().to_byte_array()==shape.get_faces().to_byte_array() and cold.margin==shape.margin
 var samples:Array=[]
 for source:Shape3D in [cold,shape,shape]:
  var body:=StaticBody3D.new();var collider:=CollisionShape3D.new();body.add_child(collider)
  begin=Time.get_ticks_usec();collider.shape=source;samples.append(Time.get_ticks_usec()-begin);body.free()
 cold=null
 return {"save_ok":saved==OK,"save_us":save_us,"cold_load_us":load_us,"assign_us_cold_existing_existing":samples,"exact_faces_margin":equal,"serialized_bytes":FileAccess.get_file_as_bytes(path).size()}
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
 var packed:PackedScene=load(str(room.get_meta("deferred_visual_path")))
 var local_box:AABB=load("res://scripts/deferred_home_visual.gd").bounds(packed);packed=null
 var rw:=VisibleOnScreenNotifier3D.new();rw.aabb=room.transform*local_box;host.add_child(rw)
 var re:Dictionary={"room":room,"parent":host,"bounds":room.transform*local_box,"witness":rw,"attached":false,"hidden_seconds":0.0,"meshes":prototype.mesh_batches};received.entries.append(re);rw.screen_entered.connect(received._on_screen_entered.bind(re))
 var record:Dictionary=private_manager.index.values()[0]
 var home:=Node3D.new();home.name=record.room_id;host.add_child(home)
 var shell:Node3D=private_manager.register_room(home,record.model_file)
 var pe:Dictionary=private_manager.entries[0];var pw:VisibleOnScreenNotifier3D=pe.witness
 root.size=Vector2i(960,540)
 var environment:=WorldEnvironment.new();environment.environment=Environment.new();environment.environment.background_mode=Environment.BG_COLOR;environment.environment.background_color=Color(.08,.1,.13);environment.environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;environment.environment.ambient_light_color=Color(.9,.88,.84);environment.environment.ambient_light_energy=.8;host.add_child(environment)
 var light:=DirectionalLight3D.new();light.rotation_degrees=Vector3(-45,-25,0);light.light_energy=.8;host.add_child(light)
 var camera:=Camera3D.new();camera.near=.05;camera.far=2000;camera.fov=75;host.add_child(camera);camera.current=true;camera.position=Vector3(5000,5000,5000)
 var received_center:=local_box.get_center();received_center.y=local_box.position.y+1.6
 var received_eye:=room.transform*(received_center+Vector3(0,0,-local_box.size.z*.3))
 var received_look:=room.transform*(received_center+Vector3(local_box.size.x*.12,0,local_box.size.z*.2))
 var private_eye:=Vector3((float(record.bounds_min[0])+float(record.bounds_max[0]))*.5,float(record.bounds_min[1])+1.8,float(record.bounds_min[2])+1.2)
 var private_look:=private_eye+Vector3(0,0,4)
 print("CAMERA_BOUNDS ",local_box," received ",received_eye," private ",private_eye)
 for flag in ["ASTRAEA_ROOM_ACTIVATION_QUEUE","ASTRAEA_PRIVATE_CONTACT_SINGLE_PASS","ASTRAEA_PACKED_CONTACT_FACES","ASTRAEA_ROOM_ACTIVATION_METRICS"]:OS.set_environment(flag,"1")
 var evidence:Array=[]
 var out:String=OS.get_environment("ASTRAEA_VISUAL_OUTPUT")+"/"
 for spec in [{"kind":"received","eye":received_eye,"look":received_look},{"kind":"private","eye":private_eye,"look":private_look}]:
  var eye:Vector3=spec.eye;var look:Vector3=spec.look
  var manager:Node=received if spec.kind=="received" else private_manager
  var entry:Dictionary=re if spec.kind=="received" else pe
  var watcher:VisibleOnScreenNotifier3D=rw if spec.kind=="received" else pw
  OS.set_environment("ASTRAEA_STAGED_ROOM_ACTIVATION","0");OS.set_environment("ASTRAEA_ROOM_PREWARM","0")
  camera.position=eye;camera.look_at(look);actor.position=eye
  received.prepare_position(eye);private_manager.prepare_position(eye)
  await physics_frame
  var baseline:Image=await capture(out+spec.kind+"_baseline.png")
  var baseline_hit:=down_hit(host,eye)
  var active:Node3D=room.get_meta("resident_visual") if spec.kind=="received" else pe.detail
  var baseline_signature:=signature(active);active=null
  var queue:Node=systems.get_node("VisibilityActivationQueue")
  for mode in ["warm","cold"]:
   camera.position=Vector3(5000,5000,5000);camera.look_at(camera.position+Vector3.FORWARD);actor.position=camera.position
   for tick in range(5):await process_frame
   received.refresh(8.1);private_manager.refresh(8.1)
   OS.set_environment("ASTRAEA_STAGED_ROOM_ACTIVATION","1");OS.set_environment("ASTRAEA_ROOM_PREWARM","1")
   if mode=="warm":
    actor.position=entry.bounds.end+Vector3(55.0 if spec.kind=="received" else 30.0,0,0)
    manager.refresh(0.2)
    for tick in range(1200):
     if queue.active_job!=null and queue.active_job.phase=="ready":break
     await process_frame
    check(queue.active_job!=null and queue.active_job.phase=="ready","prewarm_ready "+spec.kind)
    if queue.active_job==null:break
   camera.position=eye;camera.look_at(look)
   var started:=Time.get_ticks_usec();var frames:=0;var first_saved:=false;var first_diff:Dictionary={}
   # Actual notifier signals alone request visibility: no manual fake witness/near load.
   while frames<240:
    await process_frame;await RenderingServer.frame_post_draw;frames+=1
    if watcher.is_on_screen() and not first_saved:
     var first:Image=root.get_texture().get_image();first.save_png(out+spec.kind+"_"+mode+"_first_visible.png")
     first_diff=difference(baseline,first);first_saved=true
    var ready:bool=re.attached if spec.kind=="received" else is_instance_valid(pe.detail)
    if ready and first_saved:break
   var ready_us:=Time.get_ticks_usec()-started
   check(frames<240 and first_saved,"actual_notifier_arrival "+spec.kind+mode)
   await physics_frame
   var final_image:Image=await capture(out+spec.kind+"_"+mode+"_final.png")
   active=room.get_meta("resident_visual",null) if spec.kind=="received" else pe.detail
   if active!=null:check(signature(active)==baseline_signature,"final_signature "+spec.kind+mode)
   else:check(false,"missing_final "+spec.kind+mode)
   active=null
   var diff:=difference(baseline,final_image)
   check(diff.changed_channels==0,"strict_final_pixels "+spec.kind+mode)
   check(not first_diff.is_empty() and int(first_diff.get("changed_channels",-1))==0,"strict_first_visible_pixels "+spec.kind+mode)
   var arrival_hit:=down_hit(host,eye);check(arrival_hit==baseline_hit,"floor_ray "+spec.kind+mode)
   evidence.append({"kind":spec.kind,"mode":mode,"actual_notifier":true,"visible_ready_us_including_first_readback":ready_us,"frames":frames,"first_visible_difference":first_diff,"final_difference":diff,"baseline_floor_hit":baseline_hit,"arrival_floor_hit":arrival_hit})
  camera.position=Vector3(5000,5000,5000);camera.look_at(camera.position+Vector3.FORWARD);actor.position=camera.position
  for tick in range(5):await process_frame
  received.refresh(8.1);private_manager.refresh(8.1)
 print("PREWARM_VISUAL_RESULT ",JSON.stringify({"failures":failures,"evidence":evidence,"queue":systems.get_node("VisibilityActivationQueue").statistics(),"adapter":RenderingServer.get_video_adapter_name(),"full_ship":false,"target_fps":false}))
 host.free();await process_frame;quit(0 if failures.is_empty() else 1)
