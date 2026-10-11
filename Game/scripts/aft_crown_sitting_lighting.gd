extends RefCounted
static func build(ship:Node3D)->Node3D:
 var districts:Node3D=ship.get_node("ShipSpace/Districts")
 if districts.has_node("AftCrownSittingLighting"):return districts.get_node("AftCrownSittingLighting")
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/AFT_CROWN_SITTING_LIGHTING.json"))
 for f in p.model_pins:assert(FileAccess.get_sha256("res://assets/models/"+f)==p.model_pins[f])
 assert(districts.has_node("AftCrownSittingBays"))
 var n:=Node3D.new();n.name="AftCrownSittingLighting";districts.add_child(n)
 var visual:Node3D=load("res://scripts/d04_port_forward_homes_fifth.gd").visual(n,p.structure_file,p.structure.collision_policy)
 for item in p.fixture_instances:
  var marker:Node3D=visual.find_child(item.name+"__LightExit",true,false);assert(marker!=null)
  var lamp:=OmniLight3D.new();lamp.name=item.name+"__Light";n.add_child(lamp);lamp.global_position=marker.global_position
  lamp.light_color=Color(item.color[0],item.color[1],item.color[2]);lamp.light_energy=item.energy;lamp.omni_range=item.range;lamp.omni_attenuation=1.2
  lamp.visible=false;lamp.shadow_enabled=true;lamp.omni_shadow_mode=OmniLight3D.SHADOW_CUBE;lamp.shadow_bias=.03;lamp.shadow_normal_bias=.3
  lamp.set_meta("source_fixture",item.name);lamp.set_meta("fixture_powered",true)
 n.set_meta("scope","First-pass fixture lighting of two retained sitting bays;unchanged source geometry and eight-shadow-source budget")
 return n
