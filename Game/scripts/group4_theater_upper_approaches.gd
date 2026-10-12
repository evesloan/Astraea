extends RefCounted
const DATA:="res://data/architecture/GROUP4_THEATER_UPPER_SOURCE_CANDIDATE.json"
static func xyz(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(parent:Node3D,candidate_only:bool=false)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(DATA))
 if not p.active and not candidate_only:return null
 assert(not parent.has_node("Group4TheaterUpperExteriorProposal"),"Duplicate receiving assembly")
 var root:=Node3D.new();root.name="Group4TheaterUpperExteriorProposal";parent.add_child(root)
 var total:=0
 for spec in p.exports:
  var file:String=p.model_root+spec.file;assert(FileAccess.get_sha256(file)==spec.sha256)
  var model:Node3D=(load(file)as PackedScene).instantiate();model.name=spec.file.get_basename();root.add_child(model)
  var policies:Dictionary={};var contact_meshes:Array[Node]=[];var count:=0
  for key:String in spec.policies:policies[key.validate_node_name()]=spec.policies[key]
  for mesh:MeshInstance3D in model.find_children("*","MeshInstance3D",true,false):
   count+=1;assert(policies.has(str(mesh.name)))
   if policies[str(mesh.name)]!="no_collision_detail":contact_meshes.append(mesh)
  assert(count==spec.mesh_count);total+=count;load("res://scripts/static_contact_cache.gd").attach_group(model,contact_meshes)
 for spec in p.lights:
  var light:=SpotLight3D.new();light.name=spec.id;root.add_child(light);light.position=xyz(spec.position_world);light.basis=Basis.looking_at(Vector3.DOWN,Vector3.FORWARD);light.spot_angle=spec.full_cone_degrees*.5;light.spot_range=spec.range_m;light.light_energy=spec.godot_initial_energy;light.light_color=Color(spec.color_linear[0],spec.color_linear[1],spec.color_linear[2]);light.shadow_enabled=true;light.visible=false
  light.set_meta("fixture_powered",true);light.set_meta("source_fixture_semantic_id",spec.fixture);light.set_meta("source_blend_sha256",p.source_blend_sha256);light.set_meta("illumination_anchor",xyz(spec.illumination_anchor))
 assert(total==p.new_selected_mesh_count);root.set_meta("verified_source_members",total);root.set_meta("new_asset_owned_floor_m2",p.new_asset_owned_floor_m2);root.set_meta("doors_opened_or_replaced",false);root.set_meta("new_beam_load_approved",false)
 return root
