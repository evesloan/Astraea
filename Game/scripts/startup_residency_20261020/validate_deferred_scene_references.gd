extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var host:=Node3D.new();root.add_child(host)
 var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
 var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
 var group:=Node3D.new();group.name="StarAtlasRoomCandidates";districts.add_child(group)
 var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_UNITS.json"))
 var prototype:Dictionary=definition.prototypes[0]
 var path:="res://assets/models/"+str(prototype.model_file)
 var packed:PackedScene=load(path)
 var reference:WeakRef=weakref(packed)
 var bounds:AABB=load("res://scripts/deferred_home_visual.gd").bounds(packed)
 var room:=Node3D.new();room.name="ExactPersistentRoom";group.add_child(room)
 room.set_meta("deferred_visual_scene",packed);room.set_meta("deferred_visual_bounds",bounds);room.set_meta("deferred_visual_meshes",int(prototype.mesh_batches));room.set_meta("source_rest_slots",["retained_rest"])
 var original_id:=room.get_instance_id()
 packed=null
 var receipt:Dictionary=load("res://scripts/startup_residency_20261020/deferred_scene_references.gd").release_unused_scene_owners(host)
 assert(receipt.demoted_room_scene_owners==1 and reference.get_ref()==null,"PackedScene owner did not release")
 var helper=load("res://scripts/deferred_home_visual.gd")
 var memory:=[]
 for cycle in range(10):
  helper.ensure(room)
  var visual:Node3D=room.get_meta("resident_visual")
  assert(visual.find_children("*","MeshInstance3D",true,false).size()==int(prototype.mesh_batches))
  var old:WeakRef=weakref(visual)
  helper.release(room)
  assert(old.get_ref()==null and not room.has_meta("resident_visual"))
  var cache=load("res://scripts/static_contact_cache.gd")
  for key in cache.shapes.keys():
   if cache.shapes[key].get_ref()==null:cache.shapes.erase(key)
  await physics_frame
  memory.append(OS.get_static_memory_usage())
 assert(room.get_instance_id()==original_id and room.get_meta("source_rest_slots")==["retained_rest"])
 assert(memory[-1]-memory[2]<1024*1024)
 print("DEFERRED_SCENE_REFERENCE_PASS ",JSON.stringify({"scene_resource_released":true,"room_identity_preserved":true,"original_loader_round_trips":10,"memory":memory,"source":path}))
 host.free();quit()
