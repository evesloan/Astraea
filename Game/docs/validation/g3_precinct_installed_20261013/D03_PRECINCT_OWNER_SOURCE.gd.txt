extends RefCounted
# Scoped construction handoff. The shared ship root never calls this module.
# Integration owner adopts its missing-only floors and street selection together.
static func vec(a:Array)->Vector3:
 return Vector3(float(a[0]),float(a[1]),float(a[2]))
static func build(ship:Node3D)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_completion_20261011/D03_PRECINCT.json"))
 var space:Node3D=ship.get_node("ShipSpace")
 assert(space.get_node_or_null("Group3D03ReceivingPrecincts")==null)
 var n:=Node3D.new();n.name="Group3D03ReceivingPrecincts";space.add_child(n)
 n.set_meta("construction_handoff",true);n.set_meta("registered_berths_added",0)
 n.set_meta("default_main_adoption",false);n.set_meta("full_clean_used_network_accepted",false)
 for file in p.model_pins:
  assert(FileAccess.get_sha256("res://assets/models/group3_completion_20261011/"+file)==p.model_pins[file])
  ship.model(n,"group3_completion_20261011/"+file,file.trim_suffix(".glb"),Vector3.ZERO)
 for item in p.service_doors:
  var door:Node3D=load("res://scripts/service_door.gd").new()
  door.name=item.name;door.position=vec(item.position);door.rotation.y=float(item.yaw)
  door.persistent_id=StringName(item.id);door.open_fraction=0.0;door.desired_open=false
  n.add_child(door)
 var lights:Array[Light3D]=[]
 for f in p.fixtures:
  var light:=OmniLight3D.new();light.name=str(f.name)+"_PhysicalSource";n.add_child(light)
  light.position=vec(f.position);light.light_color=Color(f.color[0],f.color[1],f.color[2])
  light.light_energy=float(f.energy);light.omni_range=float(f.range_m);light.shadow_enabled=true
  light.set_meta("fixture_powered",true);light.set_meta("source_fixture",str(f.name))
  lights.append(light)
 load("res://scripts/receiving_source_lights.gd").register(lights,ship)
 return n
