extends SceneTree
func _initialize()->void:call_deferred("run")
func fingerprint(node:Node3D)->Dictionary:
 var meshes:Dictionary={};var contacts:Dictionary={}
 for m:MeshInstance3D in node.find_children("*","MeshInstance3D",true,false):
  if m.mesh!=null:
   var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(m.mesh.get_faces().to_byte_array());meshes[str(node.get_path_to(m))]={"faces":h.finish().hex_encode(),"pose":var_to_str(m.transform),"surfaces":m.mesh.get_surface_count()}
 for c:CollisionShape3D in node.find_children("*","CollisionShape3D",true,false):
  var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(c.shape.get_faces().to_byte_array());contacts[str(node.get_path_to(c))]={"faces":h.finish().hex_encode(),"pose":var_to_str(c.global_transform),"margin":c.shape.margin}
 return {"meshes":meshes,"contacts":contacts}
func run()->void:
 if not ProjectSettings.load_resource_pack("/tmp/astraea-laptop-contract-1bc13d51/Astraea-1bc13d51.pck"):quit(2);return
 if FileAccess.file_exists("res://runtime_source_contracts.pck"):ProjectSettings.load_resource_pack("res://runtime_source_contracts.pck")
 if not ProjectSettings.load_resource_pack("/tmp/route-activation-overlay.pck"):quit(2);return
 var index:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/startup_residency_20261020/private_shells.json")).rooms;var record:Dictionary=index.values()[0]
 var manager:Node=load("res://scripts/startup_residency_20261020/private_detail_residency.gd").new();root.add_child(manager);manager.set_physics_process(false)
 var cache:Script=load("res://scripts/static_contact_cache.gd")
 var results:Array=[];var signatures:Array=[]
 for enabled in [false,true]:
  OS.set_environment("ASTRAEA_PRIVATE_CONTACT_SINGLE_PASS","1"if enabled else "0")
  var home:=Node3D.new();root.add_child(home)
  var entry:={"home":weakref(home),"record":record,"detail":null,"hidden":0.0,"bounds":AABB()};manager.entries.clear();manager.entries.append(entry)
  var before:int=cache.contacts_created;var started:=Time.get_ticks_usec()
  manager.prepare_position(Vector3.ZERO)
  if entry.detail==null:quit(1);return
  var micros:=Time.get_ticks_usec()-started;signatures.append(fingerprint(entry.detail));results.append({"single_pass":enabled,"contact_groups_or_bodies_created":cache.contacts_created-before,"focused_us":micros})
  manager._release_entry(entry);home.free()
 OS.unset_environment("ASTRAEA_PRIVATE_CONTACT_SINGLE_PASS");manager.free()
 var same:bool=signatures[0]==signatures[1];var reduced:bool=results[1].contact_groups_or_bodies_created<results[0].contact_groups_or_bodies_created
 print("ROUTE_CONTACT_CHECK ",JSON.stringify({"same_final_geometry_and_contacts":same,"less_discarded_contact_work":reduced,"room":record.room_id,"results":results,"full_ship":false,"timings_not_target_fps":true}));quit(0 if same and reduced else 1)
