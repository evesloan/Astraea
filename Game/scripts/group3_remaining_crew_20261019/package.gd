extends RefCounted
static func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_remaining_crew_20261019/PACKAGE.json"))
 assert(ship.find_child("Group3RemainingCrewBank",true,false)==null)
 var n:=Node3D.new();n.name="Group3RemainingCrewBank";ship.get_node("ShipSpace").add_child(n)
 n.set_meta("physical_unassigned_rest_surfaces",366);n.set_meta("registered_berths_added",0);n.set_meta("C036_migration_applied",false);n.set_meta("authoritative_identity_mapping",false);n.set_meta("private_entry_admitted",false)
 for f in p.model_pins:
  var path:String="res://assets/group3_remaining_crew_20261019/"+f
  assert(FileAccess.get_sha256(path)==p.model_pins[f])
  var wrapper:=Node3D.new();wrapper.name=f.trim_suffix(".glb");wrapper.set_meta("catalogue_file",path);n.add_child(wrapper)
  var visual:Node3D=(load(path) as PackedScene).instantiate();wrapper.add_child(visual);ship._static_contacts(visual)
 for s in p.service_doors:
  var door:Node3D=load("res://scripts/group3_completion_20261011/bank_entry_gate.gd").new();door.name=s.name;door.persistent_id=StringName(s.physical_component_id)
  door.position=vec(s.position);door.rotation.y=s.yaw;door.open_fraction=0;door.desired_open=false;door.set_meta("source_allocation_key",s.allocation_key);n.add_child(door)
 var lights:Array[Light3D]=[]
 for f in p.fixtures:
  var l:=OmniLight3D.new();n.add_child(l);l.name=str(f.name)+"_PhysicalSource";l.position=vec(f.position)
  l.omni_range=f.range_m;l.light_energy=f.energy;l.light_color=Color(f.color[0],f.color[1],f.color[2]);l.visible=false;l.shadow_enabled=false
  l.set_meta("fixture_powered",true);l.set_meta("source_fixture",str(f.name));lights.append(l)
 load("res://scripts/receiving_source_lights.gd").register(lights,ship)
 return n
