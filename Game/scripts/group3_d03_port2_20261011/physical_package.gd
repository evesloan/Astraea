extends RefCounted
static func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D,resolved_ids:Dictionary={},apply_current_spine_patch:bool=false)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_d03_port2_20261011/CONNECTION.json"));var space:Node3D=ship.get_node("ShipSpace");assert(space.get_node_or_null("Group3D03Port2Connection")==null)
 assert(space.get_node_or_null(p.required_existing_port2_package)!=null)
 for file in p.model_pins:
  assert(FileAccess.get_sha256("res://assets/models/group3_d03_port2_20261011/"+file)==p.model_pins[file])
  assert(load("res://assets/models/group3_d03_port2_20261011/"+file) is PackedScene)
 if apply_current_spine_patch:
  assert(FileAccess.get_sha256("res://assets/models/AST-STF-009_pool_market_home_equipment.glb")==p.current_spine_sha256)
  var preflight:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_d03_port2_20261011/CURRENT_CELL_PREFLIGHT.json"))
  var current:Node3D=ship.get_node("ShipSpace/Districts/LowerStaffNetwork_WIP/LowerStaffEnclosure")
  for row in preflight.mesh_preimages:
   var mesh:MeshInstance3D=current.find_child(str(row.name),true,false);assert(mesh!=null)
   var bounds:AABB=mesh.global_transform*mesh.get_aabb();assert(bounds.position.distance_to(vec(row.min))<.0001 and bounds.end.distance_to(vec(row.max))<.0001)
 var n:=Node3D.new();n.name="Group3D03Port2Connection";space.add_child(n);n.set_meta("registered_berths_added",0);n.set_meta("authoritative_identity_mapping",false);n.set_meta("owner_current_spine_patch_applied",apply_current_spine_patch);n.set_meta("operating_doors_admitted",false);n.set_meta("default_main_adoption",true)
 var operate:=not resolved_ids.is_empty();var seen:Dictionary={}
 if operate:
  assert(apply_current_spine_patch,"Operation needs the owner-adopted exact current interface")
  for q in p.door_bindings:assert(resolved_ids.has(q.name)and not str(resolved_ids[q.name]).is_empty());assert(not seen.has(str(resolved_ids[q.name])));seen[str(resolved_ids[q.name])]=true
 if apply_current_spine_patch:
  assert(FileAccess.get_sha256("res://assets/models/AST-STF-009_pool_market_home_equipment.glb")==p.current_spine_sha256)
  var lower:Node3D=ship.get_node("ShipSpace/Districts/LowerStaffNetwork_WIP/LowerStaffEnclosure")
  for name in p.exact_current_meshes_to_replace:
   var mesh:MeshInstance3D=lower.find_child(name,true,false);assert(mesh!=null);mesh.free()
 for file in p.model_pins:
  assert(FileAccess.get_sha256("res://assets/models/group3_d03_port2_20261011/"+file)==p.model_pins[file])
  if(file=="AST-STF-G3-052.glb"and not apply_current_spine_patch)or(operate and file=="AST-STF-G3-055.glb"):continue
  var visual:Node3D=(load("res://assets/models/group3_d03_port2_20261011/"+file)as PackedScene).instantiate();visual.name=file.trim_suffix(".glb");n.add_child(visual)
  for mesh in visual.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
 if operate:
  for q in p.door_bindings:
   var door:Node3D=load("res://scripts/service_door.gd").new();door.name=q.name;door.position=vec(q.position);door.rotation.y=q.yaw;door.persistent_id=StringName(resolved_ids[q.name]);door.open_fraction=0;door.desired_open=false;n.add_child(door)
 var lights:Array[Light3D]=[]
 for q in p.fixtures:
  var l:=OmniLight3D.new();l.name=str(q.name)+"_PhysicalSource";n.add_child(l);l.position=vec(q.position);l.light_color=Color(q.color[0],q.color[1],q.color[2]);l.light_energy=q.energy;l.omni_range=q.range_m;l.visible=false;l.shadow_enabled=false;l.set_meta("fixture_powered",true);l.set_meta("source_fixture",q.name);lights.append(l)
 load("res://scripts/receiving_source_lights.gd").register(lights,ship)
 return n
