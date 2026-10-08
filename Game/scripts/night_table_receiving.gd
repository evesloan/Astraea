extends RefCounted
static func build(ship:Node3D)->Node3D:
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/night_table/runtime_manifest.json"))
 var path:String="res://assets/models/"+str(data.model_file)
 assert(FileAccess.get_sha256(path)==str(data.runtime_sha256))
 var space:Node3D=ship.get_node("ShipSpace")
 assert(space.get_node_or_null(str(data.root_name))==null)
 var root:=Node3D.new();root.name=str(data.root_name);space.add_child(root)
 root.set_meta("programme_key",str(data.programme));root.set_meta("historical_alias",str(data.historical_alias));root.set_meta("source_dining_places",240);root.set_meta("operational_acceptance",false)
 var model:Node3D=ship.model(root,str(data.model_file),"NightTableSource",Vector3(-31,61,216))
 for spec in data.lights:
  var light:Light3D=model.find_child(str(spec.runtime_name),true,false)as Light3D
  assert(light!=null)
  light.set_meta("source_light_name",str(spec.source_name));light.set_meta("source_import_energy",light.light_energy)
  light.light_energy=float(spec.energy);light.light_color=Color(spec.color[0],spec.color[1],spec.color[2]);light.shadow_enabled=true
  if light is SpotLight3D:light.spot_range=float(spec.range_m)
  elif light is OmniLight3D:light.omni_range=float(spec.range_m)
  else:assert(false,"Unexpected source light class")
 var material:=ShaderMaterial.new();material.shader=load("res://shaders/night_table_receiving_finish.gdshader")
 for t in data.textures:
  assert(FileAccess.get_sha256(str(t.file))==str(t.sha256));material.set_shader_parameter(str(t.role),load(str(t.file)))
 for id in data.floor_owners:
  var floor:Node3D=space.get_node("CompiledStructuralFloors_NotFinishedRooms/"+str(id))
  for mesh in floor.find_children("*","MeshInstance3D",true,false):
   if str(mesh.name)!="StructuralSidesAndUnderside":mesh.material_override=material
 return root
