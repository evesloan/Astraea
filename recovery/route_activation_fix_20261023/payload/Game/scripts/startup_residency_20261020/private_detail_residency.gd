extends Node
# Public/architectural render meshes, doors, lights and room IDs never unload.
# Only audited immutable catalogue furnishings are released, not detached/cached.
const DATA := "res://data/architecture/startup_residency_20261020/private_shells.json"
const ENTER := 24.0
const KEEP := 36.0
var host: Node3D
var index: Dictionary
var entries: Array[Dictionary] = []
var elapsed := 0.0
var loads := 0
var releases := 0
func setup(ship: Node3D) -> void:
 host=ship
 index=JSON.parse_string(FileAccess.get_file_as_string(DATA)).rooms
 process_physics_priority=-210
func accepts(file: String) -> bool: return index.has(file)
func contacts(visual: Node3D) -> void:
 var solids: Array[Node]=[]
 for mesh: MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
  var extra: Dictionary=mesh.get_meta("extras",{})
  if str(extra.get("material_role",""))=="hospitality_glass":
   var glass:=ShaderMaterial.new()
   glass.shader=load("res://shaders/hospitality_glass.gdshader")
   mesh.material_override=glass
  if bool(extra.get("runtime_collision",false)) and str(extra.get("collision_policy",""))!="no_collision_detail": solids.append(mesh)
 load("res://scripts/static_contact_cache.gd").attach_group(visual,solids)
func register_room(home: Node3D,file: String) -> Node3D:
 var record: Dictionary=index[file]
 assert(str(home.name)==str(record.room_id),"Exact source room allocation required")
 assert(FileAccess.get_sha256("res://assets/models/"+file)==str(record.sha256))
 assert(FileAccess.get_sha256(str(record.shell_path))==str(record.shell_sha256))
 var shell: Node3D=load(str(record.shell_path)).instantiate()
 home.add_child(shell)
 contacts(shell)
 load("res://scripts/static_room_occlusion.gd").install(shell)
 var lo: Array=record.bounds_min
 var hi: Array=record.bounds_max
 var box:=AABB(Vector3(lo[0],lo[1],lo[2]),Vector3(hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2]))
 var witness:=VisibleOnScreenNotifier3D.new()
 witness.name="PrivateDetailVisibility"
 var detail_lo:Array=record.detail_bounds_min
 var detail_hi:Array=record.detail_bounds_max
 witness.aabb=AABB(Vector3(detail_lo[0],detail_lo[1],detail_lo[2]),Vector3(detail_hi[0]-detail_lo[0],detail_hi[1]-detail_lo[1],detail_hi[2]-detail_lo[2]))
 home.add_child(witness)
 var entry: Dictionary={"home":weakref(home),"record":record,"bounds":home.global_transform*box,"witness":witness,"detail":null,"hidden":0.0}
 entries.append(entry)
 witness.screen_entered.connect(_request_visible.bind(entry))
 prepare_position(Vector3(63.0,52.6,-20.5))
 return shell
func _request_visible(entry: Dictionary) -> void:
 _load_visible.call_deferred(entry)
func _load_visible(entry: Dictionary) -> void:
 if not entry.witness.is_on_screen():return
 var queue:Node=load("res://scripts/route_activation_20261023/scheduler.gd").obtain(host)
 var home:Node=entry.home.get_ref()
 if queue!=null and home!=null:queue.enqueue(self,entry,home,"private_detail")
 else:_load_entry(entry)
func _activate_pending_visibility(entry:Dictionary)->bool:
 var home:Node=entry.home.get_ref()
 if home==null or not home.is_inside_tree()or is_instance_valid(entry.detail)or not entry.witness.is_on_screen():return false
 _load_entry(entry)
 return is_instance_valid(entry.detail)
func _load_entry(entry: Dictionary) -> void:
 if is_instance_valid(entry.detail): return
 var home: Node3D=entry.home.get_ref()
 if home==null:return
 # The unchanged helper still runs its presentation/collision policy gates.
 var helper:="res://scripts/route_activation_20261023/private_visual.gd"if OS.get_environment("ASTRAEA_PRIVATE_CONTACT_SINGLE_PASS")=="1"else "res://scripts/star_atlas_specialty_first.gd"
 var detail:Node3D=load(helper).contact_visual(home,str(entry.record.model_file))
 for contacts_node in detail.find_children("RoomStaticContacts","StaticBody3D",true,false): contacts_node.free()
 for path in entry.record.shell_mesh_paths: (detail.get_node(str(path)) as MeshInstance3D).mesh=null
 # Transparent contact children on retained detail meshes were installed by the
 # original helper; remove those before rebuilding the exact detail-only group.
 for contact in detail.find_children("StaticContact","StaticBody3D",true,false):contact.free()
 contacts(detail)
 detail.name="ResidentPrivateFurnishings"
 entry.detail=detail
 entry.hidden=0.0
 loads+=1
func _near(point: Vector3,box: AABB,margin: float) -> bool:
 return point.distance_squared_to(point.clamp(box.position,box.end))<=margin*margin
func prepare_position(point: Vector3) -> void:
 for entry in entries:
  if _near(point,entry.bounds,ENTER):_load_entry(entry)
func _physics_process(delta: float) -> void:
 elapsed+=delta
 if elapsed<.2:return
 refresh(elapsed)
 elapsed=0.0
func refresh(delta: float=0.2) -> void:
 var actor:=host.get_node_or_null("ShipSpace/PersistentActors/Player") as Node3D
 if actor==null:return
 var positions: Array[Vector3]=[actor.global_position]
 for body in host.get_node("ShipSpace/PersistentActors").find_children("*","RigidBody3D",true,false):positions.append(body.global_position)
 var requests:Array=[]
 for entry in entries:
  var live:=is_instance_valid(entry.detail)
  var near:=false
  for point in positions:
   if _near(point,entry.bounds,KEEP if live else ENTER):near=true
  var wanted:bool=near or entry.witness.is_on_screen()
  if wanted:
   entry.hidden=0.0
   if not live:requests.append({"entry":entry,"near":near})
  elif live:
   entry.hidden+=delta
   if entry.hidden>=8.0:_release_entry(entry)
 # Reclaim eligible details before any new activation; near collision safety unchanged.
 for request in requests:
  if request.near:_load_entry(request.entry)
  else:_load_visible(request.entry)
func _release_entry(entry: Dictionary) -> void:
 entry.detail.free()
 entry.detail=null
 releases+=1
 prune_expired_contacts()
func prune_expired_contacts() -> void:
 # Original grouped-contact keys include resource IDs. Expired weak entries
 # must not accumulate across repeated genuine resource unload/reload cycles.
 var cache=load("res://scripts/static_contact_cache.gd")
 for key in cache.shapes.keys():
  if cache.shapes[key].get_ref()==null:cache.shapes.erase(key)
func statistics() -> Dictionary:
 var active:=0
 for entry in entries:
  if is_instance_valid(entry.detail):active+=1
 return {"registered_private_interiors":entries.size(),"resident_interiors":active,"loads":loads,"releases":releases,"shells_doors_lights_ids_always_resident":true,"detail_released_not_cached":true}
