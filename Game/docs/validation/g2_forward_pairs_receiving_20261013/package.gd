extends RefCounted
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_forward_receiving_20261013/FORWARD.json"));assert(ship.find_child("Group2ForwardSupportedPairs",true,false)==null)
 for path in p.model_pins:assert(FileAccess.get_sha256("res://"+str(path))==str(p.model_pins[path]));assert(load("res://"+str(path)) is PackedScene)
 for site in p.sites:assert(FileAccess.get_sha256("res://assets/models/"+str(site.receiver_model))==str(site.receiver_sha256))
 var n:=Node3D.new();n.name="Group2ForwardSupportedPairs";ship.get_node("ShipSpace").add_child(n);n.set_meta("default_main_adoption",false);n.set_meta("registered_units_or_capacity",0);n.set_meta("operating_care_private_admission_or_services",false);n.set_meta("structural_capacity_or_lower_section_accepted",false)
 var frame:Node3D=(load("res://assets/group2_forward_receiving_20261013/FORWARD_ADJUNCT_FRAMES_r001.glb")as PackedScene).instantiate();frame.name="ForwardFrames";n.add_child(frame);load("res://scripts/static_contact_cache.gd").attach_group(frame,frame.find_children("*","MeshInstance3D",true,false));var lights:Array[Light3D]=[]
 for site in p.sites:
  var section:=Node3D.new();section.name=site.key;section.set_meta("group2_source_key",site.key);section.set_meta("capacity_migrated",false);section.set_meta("installed_acceptance",false);n.add_child(section)
  var visual:Node3D=(load("res://assets/group2_completion/"+str(site.key)+".glb")as PackedScene).instantiate();visual.name="RetainedSource";section.add_child(visual);load("res://scripts/static_contact_cache.gd").attach_group(visual,visual.find_children("*","MeshInstance3D",true,false));load("res://scripts/group2_care_programmes/package.gd").build(section,site.key,true)
  load("res://scripts/group2_forward_receiving_20261013/guard_window_successor.gd").apply(ship,n,site)
  for row in site.fixtures:
   var lens:MeshInstance3D=visual.find_child(str(row.source_fixture_part),true,false);assert(lens!=null and (lens.global_transform*lens.get_aabb()).grow(.05).has_point(v(row.world_xyz)))
   var light:=OmniLight3D.new();light.name=str(site.key)+"_"+str(row.name);n.add_child(light);light.position=v(row.world_xyz);light.light_color=Color(row.color[0],row.color[1],row.color[2]);light.light_energy=1;light.omni_range=10;light.visible=false;light.shadow_enabled=false;lights.append(light)
 load("res://scripts/receiving_source_lights.gd").register(lights,ship)
 return n
