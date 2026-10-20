extends "res://scripts/startup_residency_20261020/private_detail_residency.gd"
# Original public structures and every non-source_fitting mesh remain resident.
# Contact cells remain independently bounded; only immutable private visuals unload.
func setup(ship: Node3D) -> void:
 host=ship
 assert(FileAccess.get_sha256("res://data/architecture/startup_residency_20261020/private_shells_d04.json")=="4f41f4c70165883e6789174225ed2a6172b6e659d8302b586434a68488cdbfdb")
 index=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/startup_residency_20261020/private_shells_d04.json")).rooms
 process_physics_priority=-210
func register_room(home: Node3D,file: String) -> Node3D:
 var record: Dictionary=index[file]
 assert(str(home.name)==str(record.room_id))
 assert(FileAccess.get_sha256("res://assets/models/"+file)==str(record.sha256))
 assert(FileAccess.get_sha256(str(record.shell_path))==str(record.shell_sha256))
 var source:Dictionary=host.streamed_models[file]
 assert(FileAccess.get_sha256(str(source.manifest_path))==str(source.manifest_sha256))
 var manifest:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(str(source.manifest_path)))
 var wrapper:=Node3D.new()
 wrapper.name="PrivateAuthoredVisual"
 wrapper.set_meta("catalogue_file",file)
 wrapper.set_meta("exact_batched_source_sha256",record.sha256)
 home.add_child(wrapper)
 var shell:Node3D=load(str(record.shell_path)).instantiate()
 wrapper.add_child(shell)
 _apply_shell_policy(shell,manifest)
 host.exact_contact_residency.register_model(wrapper,manifest)
 load("res://scripts/static_room_occlusion.gd").install(shell)
 var lo:Array=record.bounds_min;var hi:Array=record.bounds_max
 var box:=AABB(Vector3(lo[0],lo[1],lo[2]),Vector3(hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2]))
 var witness:=VisibleOnScreenNotifier3D.new()
 witness.name="PrivateDetailVisibility"
 var dlo:Array=record.detail_bounds_min;var dhi:Array=record.detail_bounds_max
 witness.aabb=AABB(Vector3(dlo[0],dlo[1],dlo[2]),Vector3(dhi[0]-dlo[0],dhi[1]-dlo[1],dhi[2]-dlo[2]))
 wrapper.add_child(witness)
 var entry:Dictionary={"home":weakref(wrapper),"record":record,"manifest":manifest,"bounds":wrapper.global_transform*box,"witness":witness,"detail":null,"hidden":0.0}
 entries.append(entry)
 witness.screen_entered.connect(_request_visible.bind(entry))
 if _near(Vector3(63.0,52.6,-20.5),entry.bounds,ENTER):_load_entry(entry)
 return wrapper
func _apply_shell_policy(shell:Node3D,manifest:Dictionary)->void:
 for mesh:MeshInstance3D in shell.find_children("*","MeshInstance3D",true,false):
  assert(manifest.source_collision_policy.has(str(mesh.name)))
  var spec:Dictionary=manifest.source_collision_policy[str(mesh.name)]
  if str(spec.get("role",""))=="hospitality_glass":
   var glass:=ShaderMaterial.new();glass.shader=load("res://shaders/hospitality_glass.gdshader");mesh.material_override=glass
  if str(spec.get("category",""))=="light_source":mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
 for row in manifest.retained_transparent_contacts:
  if shell.has_node(str(row.source_path)):load("res://scripts/static_contact_cache.gd").attach(shell.get_node(str(row.source_path)))
func _load_entry(entry:Dictionary)->void:
 if is_instance_valid(entry.detail):return
 var wrapper:Node3D=entry.home.get_ref()
 if wrapper==null:return
 assert(FileAccess.get_sha256(str(entry.record.detail_path))==str(entry.record.detail_sha256))
 var detail:Node3D=load(str(entry.record.detail_path)).instantiate()
 wrapper.add_child(detail)
 detail.name="ResidentPrivateFurnishings"
 entry.detail=detail
 entry.hidden=0.0
 loads+=1
