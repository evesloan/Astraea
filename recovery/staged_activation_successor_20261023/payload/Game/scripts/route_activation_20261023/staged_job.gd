extends RefCounted
# One off-tree preparation lease. SceneTree mutation and resource construction stay on main thread.
var request:Dictionary
var visual:Node3D
var scene:PackedScene
var path:=""
var phase:="request"
var meshes:Array[Node]=[]
var opaque:Array[Node]=[]
var poses:Array[Transform3D]=[]
var cursor:=0
var key:="room:"
var faces:=PackedVector3Array()
var shape:Shape3D
var metrics:Array=[]
var cancelled:=false
var committed:=false
var failed:=false
var loaded_request:=false
var reuse:=false
var started_usec:=0
var cache=load("res://scripts/static_contact_cache.gd")
static func supported(r:Dictionary)->bool:
 if OS.get_environment("ASTRAEA_PACKED_CONTACT_FACES")!="1":return false
 var owner:Node=r.owner.get_ref();var identity:Node=r.identity.get_ref()
 if owner==null or identity==null:return false
 if r.kind=="received_room":return not identity.has_meta("retained_group2_home") and (identity.has_meta("deferred_visual_path") or identity.has_meta("deferred_visual_scene"))
 if r.kind!="private_detail" or OS.get_environment("ASTRAEA_PRIVATE_CONTACT_SINGLE_PASS")!="1":return false
 var script_path:String=owner.get_script().resource_path
 if script_path=="res://scripts/startup_residency_20261020/private_detail_residency.gd":return true
 if script_path=="res://scripts/night_garden_residency_20261022/manager.gd":return not owner.night_files.has(str(r.entry.record.model_file))
 return false
func configure(r:Dictionary)->void:
 request=r;started_usec=Time.get_ticks_usec()
 var identity:Node=r.identity.get_ref()
 if r.kind=="private_detail":path="res://assets/models/"+str(r.entry.record.model_file)
 elif identity.has_meta("deferred_visual_scene"):
  scene=identity.get_meta("deferred_visual_scene");path=scene.resource_path;phase="instantiate"
 else:path=str(identity.get_meta("deferred_visual_path"))
func wanted()->bool:
 var owner:Node=request.owner.get_ref();var identity:Node=request.identity.get_ref()
 if owner==null or identity==null or not owner.is_inside_tree():return false
 if request.kind=="received_room":return not request.entry.attached and not identity.has_meta("resident_visual") and request.entry.witness.is_on_screen()
 return identity.is_inside_tree() and not is_instance_valid(request.entry.detail) and request.entry.witness.is_on_screen()
func dispose()->void:
 if is_instance_valid(visual):visual.free()
 visual=null;scene=null;meshes.clear();opaque.clear();poses.clear();faces.clear();shape=null
 for old_key in cache.shapes.keys():
  if cache.shapes[old_key].get_ref()==null:cache.shapes.erase(old_key)
func stop(reason:String)->void:
 failed=true;push_error("Staged activation rejected: "+reason);dispose();phase="done"
func step(budget:int)->bool:
 if not wanted():cancelled=true
 # Godot cannot cancel a threaded request: drain completion without instantiation before next job.
 if cancelled and not loaded_request:
  var cancel_start:=Time.get_ticks_usec();dispose();phase="done"
  metrics.append({"stage":"cancel_dispose","us":Time.get_ticks_usec()-cancel_start,"frame":Engine.get_process_frames()})
  return true
 var started:=Time.get_ticks_usec();var label:=phase
 match phase:
  "request":
   if ResourceLoader.load_threaded_request(path,"PackedScene",false,ResourceLoader.CACHE_MODE_REUSE)!=OK:stop("resource request "+path)
   else:loaded_request=true;phase="wait"
  "wait":
   var status:=ResourceLoader.load_threaded_get_status(path)
   if status==ResourceLoader.THREAD_LOAD_LOADED:
    scene=ResourceLoader.load_threaded_get(path);loaded_request=false
    if cancelled:dispose();phase="done"
    elif scene==null:stop("null scene")
    else:phase="instantiate"
   elif status==ResourceLoader.THREAD_LOAD_FAILED or status==ResourceLoader.THREAD_LOAD_INVALID_RESOURCE:loaded_request=false;stop("load failed "+path)
  "instantiate":
   visual=scene.instantiate();scene=null
   if visual==null:stop("null instance")
   else:meshes=visual.find_children("*","MeshInstance3D",true,false);phase="configure"
   if request.kind=="received_room" and meshes.size()!=int(request.identity.get_ref().get_meta("deferred_visual_meshes")):stop("mesh count")
  "configure":
   var owner:Node=request.owner.get_ref();var identity:Node=request.identity.get_ref()
   var interner=owner.host.get("exact_texture_intern")
   while cursor<meshes.size():
    var mesh:MeshInstance3D=meshes[cursor];cursor+=1
    var collidable:=true
    if request.kind=="private_detail":
     var extra:Dictionary=mesh.get_meta("extras",{});var label_name:=str(mesh.name).to_lower().replace("_","").replace("-","").replace(".","").replace(" ","")
     if "previewground" in label_name or bool(extra.get("preview_only",false)) or bool(extra.get("presentation_only",false)) or bool(extra.get("exclude_from_production",false)):stop("presentation geometry");return true
     if str(visual.get_path_to(mesh)) in request.entry.record.shell_mesh_paths:mesh.mesh=null
     if str(extra.get("material_role",""))=="hospitality_glass":
      var glass:=ShaderMaterial.new();glass.shader=load("res://shaders/hospitality_glass.gdshader");mesh.material_override=glass
     collidable=bool(extra.get("runtime_collision",false)) and str(extra.get("collision_policy",""))!="no_collision_detail"
    else:
     var policy:Dictionary=identity.get_meta("deferred_visual_collision_policy",{})
     if not policy.is_empty() and not policy.has(str(mesh.name)):stop("missing collision policy");return true
     collidable=policy.is_empty() or bool(policy[str(mesh.name)].collide)
    if interner!=null:interner.intern_mesh(mesh)
    if collidable and mesh.mesh!=null:
     var is_opaque:=true
     for surface in range(mesh.mesh.get_surface_count()):
      var material:Material=mesh.get_active_material(surface)
      if not material is BaseMaterial3D or material.transparency!=BaseMaterial3D.TRANSPARENCY_DISABLED or material.albedo_color.a<.999:is_opaque=false
     if not is_opaque:cache.attach(mesh)
     else:
      var pose:Transform3D=mesh.transform;var parent:Node3D=mesh.get_parent()
      while parent!=visual:
       if parent==null:stop("contact ancestor");return true
       pose=parent.transform*pose;parent=parent.get_parent()
      opaque.append(mesh);poses.append(pose);key+=str(mesh.mesh.get_instance_id())+":"+var_to_bytes(pose).hex_encode()+";"
    if Time.get_ticks_usec()-started>=budget:break
   if cursor==meshes.size():
    cursor=0
    var reference:WeakRef=cache.shapes.get(key);shape=reference.get_ref() if reference!=null else null
    reuse=shape!=null
    phase="commit" if opaque.is_empty() else ("body" if reuse else "faces")
  "faces":
   while cursor<opaque.size():
    var mesh:MeshInstance3D=opaque[cursor]
    faces.append_array(poses[cursor]*mesh.mesh.get_faces());cursor+=1
    if Time.get_ticks_usec()-started>=budget:break
   if cursor==opaque.size():phase="shape"
  "shape":
   # Native shape construction cannot be preempted; its measured overrun is exposed.
   var triangles:=ConcavePolygonShape3D.new();triangles.set_faces(faces);shape=triangles;faces.clear();cache.shapes[key]=weakref(shape);phase="body"
  "body":
   if reuse:cache.shapes_reused+=1
   var body:=StaticBody3D.new();body.name="RoomStaticContacts";visual.add_child(body)
   var collider:=CollisionShape3D.new();collider.name="SharedRoomTriangles";collider.shape=shape;body.add_child(collider);cache.contacts_created+=1;phase="commit"
  "commit":
   var owner:Node=request.owner.get_ref();var identity:Node3D=request.identity.get_ref()
   if request.kind=="received_room":
    visual.name="ResidentAuthoredInterior";identity.add_child(visual);request.entry.parent.add_child(identity);request.entry.attached=true;request.entry.hidden_seconds=0.0;identity.set_meta("resident_visual",visual);owner.changes+=1
   else:
    visual.name="ResidentPrivateFurnishings";identity.add_child(visual);request.entry.detail=visual;request.entry.hidden=0.0;owner.loads+=1
   for body:Node3D in visual.find_children("*","StaticBody3D",true,false):body.force_update_transform()
   committed=true;visual=null;phase="done"
 var elapsed:=Time.get_ticks_usec()-started
 if label!="wait" or phase!="wait":metrics.append({"stage":label,"us":elapsed,"frame":Engine.get_process_frames(),"overrun":elapsed>budget})
 if phase=="done":
  if committed:
   var identity:Node=request.identity.get_ref()
   identity.set_meta("last_activation_metrics",{"staged":true,"room":str(identity.name),"prototype":path,"wall_us":Time.get_ticks_usec()-started_usec,"slices":metrics.duplicate(true)})
  dispose()
 return phase=="done"
