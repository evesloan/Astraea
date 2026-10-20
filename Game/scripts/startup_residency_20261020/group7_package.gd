extends RefCounted
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/consolidated_all_eight_20261013/G7_ADDITIONAL.json"))
 var n:Node3D=load("res://scripts/startup_residency_20261020/group7_completion.gd").build(ship)
 n.set_meta("default_runtime_adoption",true);n.set_meta("physical_source_models",88);n.set_meta("whole_group_or_primary_capacity_accepted",false);n.set_meta("strict_transit_failed_segments_held",5)
 for row in p.models:
  var path:String="res://assets/models/"+str(row.file);assert(FileAccess.get_sha256(path)==str(row.sha256));assert(not n.has_node(str(row.cell)))
  var visual:Node3D=(load(path)as PackedScene).instantiate();visual.name=str(row.cell);n.add_child(visual)
  for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
   var category:String=str(mesh.get_meta("extras",{}).get("contact_category",""))
   if category.begins_with("solid_"):load("res://scripts/startup_residency_20261020/group7_contact_source.gd").attach(mesh,path,visual,ship)
   elif category=="visual_lens":mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
 for row in p.doors:
  var door:Node3D=load("res://scripts/consolidated_all_eight_20261013/held_garden_door.gd").new();door.name=str(row.id);door.persistent_id=StringName(str(row.id));door.desired_open=false;door.open_fraction=0.;door.set_meta("operational_admission",false);n.add_child(door);door.position=v(row.origin);door.rotation.y=float(row.yaw)
 for row in p.lights:
  var light:=SpotLight3D.new();light.name=str(row.id);n.add_child(light);light.position=v(row.position);light.rotation.x=-PI/2;light.spot_range=float(row.range);light.spot_angle=float(row.angle);light.light_energy=float(row.energy);light.light_color=Color(row.color[0],row.color[1],row.color[2]);light.shadow_enabled=true;light.visible=false;light.set_meta("source_fixture",row.source_hardware);load("res://scripts/startup_residency_20261020/group7_completion.gd").register_new_light(ship,light)
 return n
