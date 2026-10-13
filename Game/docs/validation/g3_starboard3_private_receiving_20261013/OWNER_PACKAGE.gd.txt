extends RefCounted
static func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D,resolved_identities:Dictionary={},staff_authorization:Callable=Callable())->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_starboard3_private_20261011/PRIVATE.json"))
 assert(ship.find_child("Group3Starboard3Private",true,false)==null)
 var n:=Node3D.new();n.name="Group3Starboard3Private";ship.get_node("ShipSpace").add_child(n)
 n.set_meta("registered_berths_added",0);n.set_meta("authoritative_identity_mapping",false);n.set_meta("clinical_operational_acceptance",false)
 var operate:=not resolved_identities.is_empty()
 if operate:
  var keys:Array=["lift_persistent_id","lift_identity_prefix"]
  for q in p.door_bindings:keys.append(q.name)
  var seen:Dictionary={}
  for key in keys:
   assert(resolved_identities.has(key)and not str(resolved_identities[key]).is_empty());assert(not seen.has(str(resolved_identities[key])));seen[str(resolved_identities[key])]=true
 for file in p.model_pins:
  assert(FileAccess.get_sha256("res://assets/models/group3_starboard3_private_20261011/"+file)==p.model_pins[file])
  if operate and file=="AST-STF-G3-046.glb":continue
  var visual:Node3D=(load("res://assets/models/group3_starboard3_private_20261011/"+file)as PackedScene).instantiate();visual.name=file.trim_suffix(".glb");n.add_child(visual)
  for mesh in visual.find_children("*","MeshInstance3D",true,false):
   if operate and str(mesh.name).begins_with("landing_threshold_"):continue
   load("res://scripts/static_contact_cache.gd").attach(mesh)
 if operate:
  for q in p.source_sill_remainder_contacts:
   var a:Array=q.aabb;var b:=BoxShape3D.new();b.size=Vector3(a[1]-a[0],a[3]-a[2],a[5]-a[4]);b.margin=.001
   var body:=StaticBody3D.new();body.name=q.name;n.add_child(body);var c:=CollisionShape3D.new();c.shape=b;c.position=Vector3((a[0]+a[1])/2,(a[2]+a[3])/2,(a[4]+a[5])/2);body.add_child(c)
  var lift:Node3D=load("res://scripts/commons_lift.gd").new();lift.name="Starboard3Lift";lift.position=vec(p.lift_root_position);lift.rotation.y=p.lift_root_yaw
  for key in ["floor_heights","deck_numbers","stop_ids","stop_names","stop_codes"]:lift.get(key).assign(p.controller_binding[key])
  lift.gate_origin_xz=Vector2(p.controller_binding.gate_origin_xz[0],p.controller_binding.gate_origin_xz[1]);lift.cabin_file=p.controller_binding.cabin_file
  lift.persistent_id=StringName(resolved_identities.lift_persistent_id);lift.identity_prefix=resolved_identities.lift_identity_prefix;lift.district_label="Central starboard staff";n.add_child(lift)
  for q in p.door_bindings:
   var door:Node3D=load("res://scripts/group3_starboard3_private_20261011/entry_gate.gd").new();door.name=q.name;door.position=vec(q.position);door.rotation.y=q.yaw
   door.persistent_id=StringName(resolved_identities[q.name]);door.open_fraction=0;door.desired_open=false;door.can_enter=staff_authorization;n.add_child(door)
 var lights:Array[Light3D]=[]
 for q in p.fixtures:
  var l:=OmniLight3D.new();l.name=str(q.name)+"_PhysicalSource";n.add_child(l);l.position=vec(q.position);l.light_color=Color(q.color[0],q.color[1],q.color[2]);l.light_energy=q.energy;l.omni_range=q.range_m
  l.shadow_enabled=true;l.set_meta("fixture_powered",true);l.set_meta("source_fixture",q.name);lights.append(l)
 load("res://scripts/receiving_source_lights.gd").register(lights,ship)
 return n
