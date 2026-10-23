extends SceneTree
func _initialize()->void:call_deferred("run")
func signature(node:Node3D)->Dictionary:
 var rows:Dictionary={}
 for mesh:MeshInstance3D in node.find_children("*","MeshInstance3D",true,false):
  var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(mesh.mesh.get_faces().to_byte_array())
  rows[str(node.get_path_to(mesh))]={"pose":var_to_str(mesh.transform),"faces":h.finish().hex_encode(),"surfaces":mesh.mesh.get_surface_count(),"mesh_id":mesh.mesh.get_instance_id()}
 return rows
func run()->void:
 var args:=OS.get_cmdline_user_args()
 if args.size()>0:
  if not ProjectSettings.load_resource_pack(args[0]):quit(2);return
 var index:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://d04_detail_batches_20261022/runtime_r004/INDEX.json"));var row:Dictionary=index.rooms.values()[0]
 var host:=Node3D.new();root.add_child(host);host.set_meta("runtime_ready",true)
 var manager:Node=load("res://d04_prefetch_20261023/tests/probe_manager.gd").new();host.add_child(manager);manager.host=host;manager.set_process(false);manager.set_physics_process(false)
 var wrapper:=Node3D.new();host.add_child(wrapper)
 var entry:={"home":weakref(wrapper),"record":row,"detail":null,"hidden":0.0,"bounds":AABB(),"wanted":true,"prefetch":true};manager.entries.append(entry);manager._load_entry(entry)
 var deadline:=Time.get_ticks_msec()+10000
 while entry.detail==null and Time.get_ticks_msec()<deadline:manager._process(0);await create_timer(.005).timeout
 if entry.detail==null:host.free();quit(1);return
 var packed:PackedScene=ResourceLoader.load(str(row.detail_path),"PackedScene",ResourceLoader.CACHE_MODE_REUSE);var control:Node3D=packed.instantiate()
 var actual:=signature(entry.detail);var expected:=signature(control);var equal:bool=actual==expected
 control.free();packed=null;manager._release_entry(entry)
 var cleared:bool=entry.detail==null and manager.requests.is_empty()
 print("D04_PREFETCH_RETAINED ",JSON.stringify({"room":row.room_id,"meshes":actual.size(),"exact_geometry_transforms_and_shared_mesh_ids":equal,"release_clears_owner_and_ready_pool":cleared,"stats":manager.prefetch_statistics(),"ship_run":false}))
 host.free();quit(0 if equal and cleared else 1)
