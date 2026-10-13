extends RefCounted
static func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D,resolved_ids:Dictionary={})->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_d03_services_20261011/SERVICES.json"));var space:Node3D=ship.get_node("ShipSpace");assert(space.get_node_or_null("Group3D03FiveServices")==null)
 var n:=Node3D.new();n.name="Group3D03FiveServices";space.add_child(n);n.set_meta("registered_berths_added",0);n.set_meta("authoritative_identity_mapping",false)
 var operate:=not resolved_ids.is_empty();var seen:Dictionary={}
 if operate:
  for q in p.door_bindings:assert(resolved_ids.has(q.name)and not str(resolved_ids[q.name]).is_empty());assert(not seen.has(str(resolved_ids[q.name])));seen[str(resolved_ids[q.name])]=true
 for file in p.model_pins:
  assert(FileAccess.get_sha256("res://assets/models/group3_d03_services_20261011/"+file)==p.model_pins[file])
  if operate and file=="AST-STF-G3-051.glb":continue
  var visual:Node3D=(load("res://assets/models/group3_d03_services_20261011/"+file)as PackedScene).instantiate();visual.name=file.trim_suffix(".glb");n.add_child(visual)
  for mesh in visual.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
 if operate:
  for q in p.door_bindings:
   var door:Node3D=load("res://scripts/service_door.gd").new();door.name=q.name;door.position=vec(q.position);door.rotation.y=q.yaw;door.persistent_id=StringName(resolved_ids[q.name]);door.open_fraction=0;door.desired_open=false;n.add_child(door)
 var lights:Array[Light3D]=[]
 for q in p.fixtures:
  var l:=OmniLight3D.new();l.name=str(q.name)+"_PhysicalSource";n.add_child(l);l.position=vec(q.position);l.light_color=Color(q.color[0],q.color[1],q.color[2]);l.light_energy=q.energy;l.omni_range=q.range_m;l.shadow_enabled=true;l.set_meta("fixture_powered",true);l.set_meta("source_fixture",q.name);lights.append(l)
 load("res://scripts/receiving_source_lights.gd").register(lights,ship)
 return n
