extends SceneTree
func _initialize()->void:call_deferred("run")
func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func run()->void:
 var world:=Node3D.new();root.add_child(world)
 var env:=WorldEnvironment.new();var e:=Environment.new();e.background_mode=Environment.BG_COLOR;e.background_color=Color(.04,.05,.065);e.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;e.ambient_light_color=Color(.8,.88,1);e.ambient_light_energy=.25;env.environment=e;world.add_child(env)
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_remaining_crew_20261019/PACKAGE.json"))
 for f in p.model_pins:
  var path:String="res://assets/group3_remaining_crew_20261019/"+f;assert(FileAccess.get_sha256(path)==p.model_pins[f]);world.add_child(load(path).instantiate())
 var street:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_d03_streets_20261011/STREETS.json"))
 for f in street.model_pins:
  var path:String="res://assets/models/group3_d03_streets_20261011/"+f;assert(FileAccess.get_sha256(path)==street.model_pins[f]);world.add_child(load(path).instantiate())
 var columns:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_CENTRAL_WEST_STAFF_CIRCUIT.json"))
 var context:Node3D=load("res://assets/models/"+str(columns.structure_file)).instantiate();world.add_child(context)
 for mesh in context.find_children("*","MeshInstance3D",true,false):
  if not str(mesh.name).begins_with("PCW_Column"):mesh.visible=false
 for s in p.service_doors:
  var door:Node3D=load("res://scripts/group3_completion_20261011/bank_entry_gate.gd").new();door.name=s.name;door.persistent_id=StringName(s.physical_component_id);door.position=v(s.position);door.rotation.y=s.yaw;door.open_fraction=0;door.desired_open=false;world.add_child(door)
 var lamps:Array[OmniLight3D]=[]
 for row in p.fixtures+street.fixtures:
  var l:=OmniLight3D.new();world.add_child(l);l.position=v(row.position);l.light_color=Color(row.color[0],row.color[1],row.color[2]);l.light_energy=row.energy;l.omni_range=row.range_m;lamps.append(l)
 var camera:=Camera3D.new();world.add_child(camera);camera.current=true;camera.fov=78;camera.far=180
 var canvas:=CanvasLayer.new();root.add_child(canvas);var label:=Label.new();label.text="ASTRAEA D03 • SOURCE RECEIVING CANDIDATE • CONSTRUCTION WIP\nExact crew / porch / street source geometry · preview ambient · no final acceptance";label.position=Vector2(18,16);label.add_theme_font_size_override("font_size",17);label.add_theme_color_override("font_shadow_color",Color.BLACK);label.add_theme_constant_override("shadow_offset_x",2);label.add_theme_constant_override("shadow_offset_y",2);canvas.add_child(label)
 var views:Array=[{"file":"D03_212_REST_COLUMN.png","at":Vector3(-96.8,13.65,-87.8),"look":Vector3(-102.4,13.0,-88.0)},{"file":"D03_212_ENTRY.png","at":Vector3(-100,13.65,-88),"look":Vector3(-91,13.3,-88)},{"file":"D03_70_OPPOSITE_BANK.png","at":Vector3(-75.2,13.65,-339.8),"look":Vector3(-69,13.0,-340)},{"file":"D03_STREET_PORCH.png","at":Vector3(-86,13.65,-88),"look":Vector3(-96,13.4,-88)}]
 for view in views:
  camera.position=view.at;camera.look_at(view.look);lamps.sort_custom(func(a,b):return a.position.distance_squared_to(camera.position)<b.position.distance_squared_to(camera.position))
  for i in lamps.size():lamps[i].visible=i<12;lamps[i].shadow_enabled=i<8
  for i in range(8):await process_frame
  await RenderingServer.frame_post_draw
  var img:=root.get_texture().get_image();assert(img.save_png("/workspace/crew-bank-receiving-20261019/"+str(view.file))==OK);print("CAPTURED ",view.file)
 quit()
