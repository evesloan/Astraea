extends RefCounted
const INDEX_SHA256:="54e179240125a0f08ef37fcec2d83814cc7875cb6432afa002abf5c06e01609e"
static var index:Dictionary={}
static func attach(mesh:MeshInstance3D,path:String,visual:Node3D,ship:Node3D)->void:
 if index.is_empty():
  assert(FileAccess.get_sha256("res://data/architecture/startup_residency_20261020/group7_contacts.json")==INDEX_SHA256)
  index=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/startup_residency_20261020/group7_contacts.json"))
 var model:Dictionary=index.models[path.get_file()]
 assert(FileAccess.get_sha256(path)==str(model.source_sha256))
 var key:=str(visual.get_path_to(mesh))
 if model.meshes.has(key):
  var manager:Node=ship.get_node("ShipSystems/ExactContactResidency")
  manager.register_model(mesh,model.meshes[key])
 else:
  # Transparent materials preserve original MeshInstance3D parent semantics.
  load("res://scripts/static_contact_cache.gd").attach(mesh)
