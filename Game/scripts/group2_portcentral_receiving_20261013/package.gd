extends RefCounted
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_portcentral_receiving_20261013/PLAN.json"));assert(ship.find_child("Group2PortCentralSupportedPair",true,false)==null)
 for path in p.model_pins:assert(FileAccess.get_sha256("res://"+str(path))==str(p.model_pins[path]));assert(load("res://"+str(path))is PackedScene)
 assert(FileAccess.get_sha256("res://assets/models/"+str(p.receiver_model))==str(p.receiver_sha256))
 var n:=Node3D.new();n.name="Group2PortCentralSupportedPair";ship.get_node("ShipSpace").add_child(n);n.set_meta("default_main_adoption",true);n.set_meta("new_units_or_capacity",0);n.set_meta("operating_care_private_services_or_structuralcapacity",false)
 var frame:Node3D=(load("res://assets/group2_portcentral_receiving_20261013/PORTCENTRAL_RECEIVING_FRAME_r004.glb")as PackedScene).instantiate();frame.name="ReceivingFrame";n.add_child(frame);load("res://scripts/static_contact_cache.gd").attach_group(frame,frame.find_children("*","MeshInstance3D",true,false))
 var section:=Node3D.new();section.name=p.key;section.set_meta("group2_source_key",p.key);section.set_meta("capacity_migrated",false);section.set_meta("installed_acceptance",false);n.add_child(section)
 var visual:Node3D=(load("res://assets/group2_completion/"+str(p.key)+".glb")as PackedScene).instantiate();visual.name="RetainedSource";section.add_child(visual);load("res://scripts/static_contact_cache.gd").attach_group(visual,visual.find_children("*","MeshInstance3D",true,false));load("res://scripts/group2_care_programmes/package.gd").build(section,p.key,true)
 load("res://scripts/group2_portcentral_receiving_20261013/guard_window_successor.gd").apply(ship,n,p)
 var lights:Array[Light3D]=[]
 for row in p.fixtures:
  var lens:MeshInstance3D=visual.find_child(str(row.source_fixture_part),true,false);assert(lens!=null and(lens.global_transform*lens.get_aabb()).grow(.05).has_point(v(row.world_xyz)));var l:=OmniLight3D.new();l.name=row.name;n.add_child(l);l.position=v(row.world_xyz);l.light_color=Color(row.color[0],row.color[1],row.color[2]);l.light_energy=1;l.omni_range=10;l.visible=false;l.shadow_enabled=false;lights.append(l)
 load("res://scripts/receiving_source_lights.gd").register(lights,ship)
 return n
