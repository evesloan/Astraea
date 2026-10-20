extends RefCounted
# Run only after the unchanged receiver builder has completed every original gate.
# Exact original render meshes, material objects, source IDs and lights remain.
const INDEX_SHA256:="0934d8584fbbfc5cbddb5b676da3064a975f1d3613ebdd7eecfa852789730cdb"
static var index:Dictionary={}
static func adopt(visual:Node3D,file:String,ship:Node3D)->void:
 if index.is_empty():
  assert(FileAccess.get_sha256("res://data/architecture/startup_residency_20261020/source_contacts_world.json")==INDEX_SHA256)
  index=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/startup_residency_20261020/source_contacts_world.json"))
 var model:Dictionary=index.models[file]
 assert(FileAccess.get_sha256(file)==str(model.source_sha256))
 var manager:Node=ship.get_node("ShipSystems/ExactContactResidency")
 for path in model.meshes:
  var mesh:MeshInstance3D=visual.get_node(path)
  var old:StaticBody3D=mesh.get_node(model.old_contact_name)
  var shapes:=old.find_children("*","CollisionShape3D",true,false)
  assert(shapes.size()==1 and shapes[0].shape is ConcavePolygonShape3D)
  var hash:=HashingContext.new();hash.start(HashingContext.HASH_SHA256);hash.update(var_to_bytes(shapes[0].shape.get_faces()))
  assert(hash.finish().hex_encode()==str(model.meshes[path].faces_sha256),"Exact predecessor contact changed before residency")
  # Do not silently strip controller, state or physics-policy additions.
  assert(old.get_script()==null and old.get_meta_list().is_empty())
  assert(old.collision_layer==1 and old.collision_mask==1)
  old.free()
 manager.register_model(visual,model)
