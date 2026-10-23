extends SceneTree
const BASE="/workspace/Astraea-recovered-e6274e77-20261021/recovery/contact_packed_successor_20261023/payload/Game/"
func _initialize()->void:call_deferred("run")
func fingerprint(n:Node)->Dictionary:
 var result:Dictionary={}
 for c:CollisionShape3D in n.find_children("*","CollisionShape3D",true,false):
  result[str(n.get_path_to(c))]={"faces":c.shape.get_faces().to_byte_array(),"pose":var_to_bytes(c.global_transform),"margin":c.shape.margin}
 return result
func run()->void:
 if not ProjectSettings.load_resource_pack("/tmp/astraea-laptop-contract-1bc13d51/Astraea-1bc13d51.pck"):quit(2);return
 if FileAccess.file_exists("res://runtime_source_contracts.pck"):ProjectSettings.load_resource_pack("res://runtime_source_contracts.pck")
 var pack:=PCKPacker.new();pack.pck_start("/tmp/contact-packed-overlay.pck")
 for path in ["scripts/route_activation_20261023/packed_contacts.gd","scripts/route_activation_20261023/scheduler.gd","scripts/deferred_home_visual.gd"]:pack.add_file("res://"+path,BASE+path)
 pack.flush();ProjectSettings.load_resource_pack("/tmp/contact-packed-overlay.pck")
 var candidate=load("res://scripts/route_activation_20261023/packed_contacts.gd")
 var cache=load("res://scripts/static_contact_cache.gd")
 for path in ["scripts/route_activation_20261023/scheduler.gd","scripts/deferred_home_visual.gd"]:
  var script:Script=load("res://"+path)
  if not script.can_instantiate():quit(3);return
 var record:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/startup_residency_20261020/private_shells.json")).rooms.values()[0]
 var prototype:PackedScene=load("res://assets/models/"+str(record.model_file))
 var signatures:Array=[];var times:Array=[]
 for enabled in [false,true,false,true]:
  cache.shapes.clear()
  var visual:Node3D=prototype.instantiate();root.add_child(visual)
  visual.position=Vector3(10,20,30)
  var meshes:Array[Node]=visual.find_children("*","MeshInstance3D",true,false)
  OS.set_environment("ASTRAEA_PACKED_CONTACT_FACES","1" if enabled else "0")
  var begin:=Time.get_ticks_usec();candidate.attach_group(visual,meshes);times.append({"packed":enabled,"contact_us":Time.get_ticks_usec()-begin})
  signatures.append(fingerprint(visual));visual.free()
 var same:bool=signatures[0]==signatures[1] and signatures[0]==signatures[2] and signatures[0]==signatures[3]
 var room:=Node3D.new();room.name="FocusedRetainedRoom";root.add_child(room)
 room.set_meta("deferred_visual_scene",prototype)
 var count_root:Node=prototype.instantiate();room.set_meta("deferred_visual_meshes",count_root.find_children("*","MeshInstance3D",true,false).size());count_root.free()
 OS.set_environment("ASTRAEA_ROOM_ACTIVATION_METRICS","1")
 var deferred=load("res://scripts/deferred_home_visual.gd");deferred.ensure(room)
 var detail:Node3D=room.get_meta("resident_visual")
 var second:=Node3D.new();root.add_child(second);second.set_meta("deferred_visual_scene",prototype);second.set_meta("deferred_visual_meshes",room.get_meta("deferred_visual_meshes"));deferred.ensure(second)
 var other:Node3D=second.get_meta("resident_visual")
 var shared:bool=detail.get_node("RoomStaticContacts/SharedRoomTriangles").shape==other.get_node("RoomStaticContacts/SharedRoomTriangles").shape
 var stages:Dictionary=room.get_meta("last_activation_metrics")
 same=same and shared and stages.room=="FocusedRetainedRoom" and stages.prototype==prototype.resource_path
 deferred.release(room);deferred.release(second);room.free();second.free()
 print("STAGES_AND_REUSE ",JSON.stringify({"stages":stages,"same_live_shape":shared}))
 print("PACKED_CONTACT_CHECK ",JSON.stringify({"room":record.room_id,"exact_faces_transforms_margins":same,"times_cloud_only":times,"live_shapes_after_release":cache.live_shape_count()}))
 quit(0 if same and cache.live_shape_count()==0 else 1)
