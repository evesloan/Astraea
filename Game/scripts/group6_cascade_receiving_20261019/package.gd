extends RefCounted
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_cascade_receiving_20261019/PACKAGE.json"))
 assert(FileAccess.get_sha256("res://assets/models/AquaticCompletion_r019.glb")==p.required_annex_runtime_sha256)
 assert(FileAccess.get_sha256("res://assets/models/AST-AQU-015.glb")==p.required_registered_watercourse_sha256)
 var annex:Node3D=ship.get_node("ShipSpace/Districts/AquaticRiverSlideAnnex_WIP")
 assert(annex.get_node_or_null("Group6CascadePhysicalReceiving")==null)
 var n:=Node3D.new();n.name="Group6CascadePhysicalReceiving";annex.add_child(n)
 n.set_meta("cascade_onward_network_connected",false);n.set_meta("fluid_or_acoustic_operation_implemented",false);n.set_meta("mechanical_operation_enabled",false);n.set_meta("capacity_delta",0)
 var file:String="res://assets/group6_cascade_receiving_20261019/"+str(p.source_file)
 assert(FileAccess.get_sha256(file)==p.export_sha256)
 var visual:Node3D=(load(file)as PackedScene).instantiate();n.add_child(visual);n.set_meta("catalogue_file",file)
 var meshes:Array[Node]=visual.find_children("*","MeshInstance3D",true,false);assert(meshes.size()==18)
 for mesh:MeshInstance3D in meshes:
  assert(p.new_mesh_roles.has(str(mesh.name)))
  if p.new_mesh_roles[str(mesh.name)]=="fixture_lens":mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
  else:load("res://scripts/static_contact_cache.gd").attach(mesh)
 var light:=SpotLight3D.new();light.name="CascadeSourceTaskLight";n.add_child(light);light.position=v(p.task_light.source_xyz);light.look_at(n.to_global(v(p.task_light.target_xyz)),Vector3.UP)
 light.light_color=Color(.88,.94,1);light.light_energy=p.task_light.energy;light.spot_range=p.task_light.range_m;light.spot_angle=p.task_light.half_cone_degrees;light.visible=false;light.shadow_enabled=false
 light.set_meta("source_fixture","G6_CASCADE__task_lens");light.set_meta("fixture_powered",true)
 var lights:Array[Light3D]=[light];load("res://scripts/receiving_source_lights.gd").register(lights,ship)
 return n
