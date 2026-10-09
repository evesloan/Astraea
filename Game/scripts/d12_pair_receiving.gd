extends RefCounted
# Candidate only. No controller changes. Guard hash must be finalized before activation.
static func build(ship:Node3D)->Node3D:
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/d12_pair/runtime_manifest.json"))
 var guard:Dictionary=data.guard_asset
 assert(guard.has("runtime_sha256") and str(guard.runtime_sha256).length()==64,"D12 guards must pass source/native/export gates before activation")
 var space:Node3D=ship.get_node("ShipSpace")
 assert(space.get_node_or_null(str(data.root_name))==null)
 for section in data.sections:
  assert(FileAccess.get_sha256("res://assets/models/"+str(section.model_file))==str(section.runtime_sha256))
 assert(FileAccess.get_sha256("res://assets/models/"+str(guard.model_file))==str(guard.runtime_sha256))
 var root:=Node3D.new();root.name=str(data.root_name);space.add_child(root)
 root.set_meta("operational_acceptance",false)
 for section in data.sections:
  var room:=Node3D.new();room.name=str(section.root_name);root.add_child(room)
  room.set_meta("programme_key",str(section.programme))
  ship.model(room,str(section.model_file),"Source",Vector3.ZERO)
 ship.model(root,str(guard.model_file),"AuthoredReceivingGuards",Vector3.ZERO)
 return root
