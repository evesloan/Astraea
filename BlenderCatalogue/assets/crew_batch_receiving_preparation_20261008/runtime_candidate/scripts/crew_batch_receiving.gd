extends RefCounted
static func build(ship:Node3D)->Node3D:
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/crew_batch/runtime_manifest.json"))
 var space:Node3D=ship.get_node("ShipSpace")
 assert(space.get_node_or_null(str(data.root_name))==null)
 var root:=Node3D.new();root.name=str(data.root_name);space.add_child(root)
 root.set_meta("operational_acceptance",false)
 for section in data.sections:
  var path:String="res://assets/models/"+str(section.model_file)
  assert(FileAccess.get_sha256(path)==str(section.runtime_sha256))
  var room:=Node3D.new();room.name=str(section.root_name);root.add_child(room)
  room.set_meta("programme_key",str(section.programme));room.set_meta("receiving_hold",str(section.receiving_hold))
  var model:Node3D=ship.model(room,str(section.model_file),"Source",Vector3.ZERO)
  var index:int=0
  for spec in section.mounted_receiving_lights:
   var fixture:MeshInstance3D=model.find_child(str(spec.fixture_runtime_name),true,false)as MeshInstance3D
   assert(fixture!=null)
   var light:=OmniLight3D.new();light.name="MountedSourceFixture_%02d"%index;room.add_child(light)
   light.position=Vector3(spec.position[0],spec.position[1],spec.position[2])
   light.light_energy=float(spec.energy);light.omni_range=float(spec.range_m)
   light.light_color=Color(spec.color[0],spec.color[1],spec.color[2]);light.shadow_enabled=true
   light.set_meta("source_fixture",str(spec.fixture_source_name));index+=1
 return root
