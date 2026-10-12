extends RefCounted
const DATA:="res://data/architecture/GROUP4_AFTMID_UPPER_SOURCE_CANDIDATE.json"
static func build(base:Node3D,candidate_only:bool=false)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(DATA))
 if not p.active and not candidate_only:return null
 var old:Node3D=base.get_node(p.original_model.get_basename())
 assert(FileAccess.get_sha256("res://source_derivatives/group4_completion_20261011/"+p.original_model)==p.original_model_sha256)
 assert(old.get_meta("verified_source_members")==p.original_mesh_count)
 var file:String=p.model_root+p.selected_model;assert(FileAccess.get_sha256(file)==p.selected_model_sha256)
 var node:Node3D=(load(file) as PackedScene).instantiate();node.name=p.selected_model.get_basename();base.add_child(node)
 var policies:Dictionary={};var meshes:Array[Node]=[];var count:=0
 for key:String in p.policies:policies[key.validate_node_name()]=p.policies[key]
 for mesh:MeshInstance3D in node.find_children("*","MeshInstance3D",true,false):
  count+=1;assert(policies.has(str(mesh.name)))
  if policies[str(mesh.name)]!="no_collision_detail":meshes.append(mesh)
 assert(count==policies.size());load("res://scripts/static_contact_cache.gd").attach_group(node,meshes)
 node.set_meta("verified_source_members",count);node.set_meta("original_station_identity","AFT_MIDSHIP")
 old.queue_free();return node
