extends RefCounted
static func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D,resolved_ids:Dictionary={},sealed_load_predicates:Dictionary={})->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_clinical_full_20261011/CLINICAL.json"))
 var space:Node3D=ship.get_node("ShipSpace");assert(space.get_node_or_null("Group3CompleteClinical")==null)
 for name in p.required_prior_physical_packages:assert(space.get_node_or_null(name)!=null,"Full clinical successor requires retained fore/port2 physical interfaces")
 var prior:Node3D=space.get_node("Group3Port2ClinicalPhysical");var bounded:=prior.get_node_or_null(p.old_port2_clinical_visual_to_remove)
 assert(bounded!=null,"Old bounded port2 selection must be replaced exactly once");bounded.free()
 var n:=Node3D.new();n.name="Group3CompleteClinical";space.add_child(n);n.set_meta("registered_berths_added",0);n.set_meta("clinical_operational_acceptance",false);n.set_meta("held_starboard_return_spans",2)
 var operate:=not resolved_ids.is_empty();var seen:Dictionary={}
 if operate:
  for d in p.door_bindings:
   assert(resolved_ids.has(d.name)and not str(resolved_ids[d.name]).is_empty());assert(not seen.has(str(resolved_ids[d.name])));seen[str(resolved_ids[d.name])]=true
  for row in p.crossings:
   for d in row.dispatch_buttons:
    assert(resolved_ids.has(d.name)and not str(resolved_ids[d.name]).is_empty());assert(not seen.has(str(resolved_ids[d.name])));seen[str(resolved_ids[d.name])]=true
 for file in p.model_pins:
  assert(FileAccess.get_sha256("res://assets/models/group3_clinical_full_20261011/"+file)==p.model_pins[file])
  if file==p.source_slider_asset or(operate and file==p.static_fittings_asset):continue
  var visual:Node3D=(load("res://assets/models/group3_clinical_full_20261011/"+file)as PackedScene).instantiate();visual.name=file.trim_suffix(".glb");n.add_child(visual)
  for mesh in visual.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
 if operate:
  for row in p.crossings:
   var manager:Node3D=load("res://scripts/group3_clinical_full_20261011/crossing_buffer.gd").new();manager.name=row.programme_key;manager.bounds_xz=row.clear_buffer_bounds_xz;n.add_child(manager)
   if row.sealed_return_available and sealed_load_predicates.has(row.programme_key):manager.sealed_load_ready=sealed_load_predicates[row.programme_key]
   manager.set_meta("real_sealed_load_owner_predicate_required",true);manager.set_meta("support_span_return_hold",not row.sealed_return_available)
   for name in row.gates:
    var s:Dictionary=p.door_bindings.filter(func(d):return d.name==name)[0]
    var gate:Node3D=load("res://scripts/group3_clinical_full_20261011/sliding_gate.gd").new();gate.name=name;gate.position=vec(s.position);gate.rotation.y=s.yaw;gate.persistent_id=StringName(resolved_ids[name]);gate.open_fraction=0;gate.desired_open=false;gate.supervisor=manager;gate.flow_axis=s.axis;n.add_child(gate);manager.doors.append(gate)
   for s in row.dispatch_buttons:
    var button:Node3D=load("res://scripts/group3_fore_starboard_clinical_20261011/dispatch_button.gd").new();button.name=s.name;button.position=vec(s.position);button.supervisor=manager;button.flow_axis=s.axis;button.face_code="CLEAN"if s.axis=="clean"else"RETURN";button.persistent_id=StringName(resolved_ids[s.name]);n.add_child(button)
 var lights:Array[Light3D]=[]
 for q in p.fixtures:
  var l:=OmniLight3D.new();l.name=str(q.name)+"_PhysicalSource";n.add_child(l);l.position=vec(q.position);l.light_color=Color(q.color[0],q.color[1],q.color[2]);l.light_energy=q.energy;l.omni_range=q.range_m;l.shadow_enabled=true;l.set_meta("fixture_powered",true);l.set_meta("source_fixture",q.name);lights.append(l)
 load("res://scripts/receiving_source_lights.gd").register(lights,ship)
 return n
