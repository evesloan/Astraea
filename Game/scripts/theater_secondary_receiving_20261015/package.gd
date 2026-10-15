extends RefCounted
static func build(ship:Node3D)->Node3D:
 assert(ship.get_node_or_null("ShipSpace/Districts/TheaterSecondaryReceiving20261015")==null)
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/theater_secondary_receiving_20261015/NATIVE_VERIFICATION.json"));var group:=Node3D.new();group.name="TheaterSecondaryReceiving20261015";ship.get_node("ShipSpace/Districts").add_child(group)
 group.set_meta("default_main_adoption",true);group.set_meta("beam_load_capacity_accepted",false);group.set_meta("upper_or_secondary_doors_operating",false)
 for row in p.models:
  var path:String="res://assets/theater_secondary_receiving_20261015/"+str(row.file);assert(FileAccess.get_sha256(path)==str(row.sha256));var model:Node3D=(load(path)as PackedScene).instantiate();model.name=str(row.deck);group.add_child(model);var contacts:Array[Node]=[];var meshes:Array[Node]=model.find_children("*","MeshInstance3D",true,false);assert(meshes.size()==int(row.meshes))
  for mesh:MeshInstance3D in meshes:
   if not str(mesh.name).ends_with("_LENS"):contacts.append(mesh)
  load("res://scripts/static_contact_cache.gd").attach_group(model,contacts)
 var lights:Array[Light3D]=[]
 for row in p.lights:
  var lens:MeshInstance3D=group.find_child(str(row.fixture).validate_node_name(),true,false);assert(lens!=null)
  var light:=SpotLight3D.new();light.name=str(row.id);group.add_child(light);light.position=Vector3(row.position_world[0],row.position_world[1],row.position_world[2]);light.basis=Basis.looking_at(Vector3.DOWN,Vector3.FORWARD);light.spot_angle=float(row.full_cone_degrees)*.5;light.spot_range=float(row.range_m);light.light_energy=float(row.godot_initial_energy);light.light_color=Color(row.color_linear[0],row.color_linear[1],row.color_linear[2]);light.visible=false;light.shadow_enabled=false;light.set_meta("fixture_powered",true);lights.append(light)
 load("res://scripts/receiving_source_lights.gd").register(lights,ship)
 group.set_meta("source_models",3);group.set_meta("new_source_meshes",288);group.set_meta("source_floor_m2",549)
 return group
