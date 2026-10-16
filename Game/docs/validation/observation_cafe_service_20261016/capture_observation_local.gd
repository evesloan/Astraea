extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var world:=Node3D.new();root.add_child(world)
 var env:=WorldEnvironment.new();var e:=Environment.new();e.background_mode=Environment.BG_COLOR;e.background_color=Color(.035,.04,.05);e.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;e.ambient_light_color=Color(.85,.9,1.);e.ambient_light_energy=.2;env.environment=e;world.add_child(env)
 var cafe:Node3D=load("res://assets/models/SOL_D10_directory_10_source001.glb").instantiate();world.add_child(cafe)
 var receiver:Node3D=load("res://assets/observation_cafe_service_20261016/OBSERVATION_CAFE_SERVICE_RECEIVER_r001.glb").instantiate();world.add_child(receiver)
 for spec in [[Vector2(46,68),Vector3(31,61,432)],[Vector2(8,24),Vector3(0,61,392)]]:
  var floor_mesh:=MeshInstance3D.new();var plane:=PlaneMesh.new();plane.size=spec[0];floor_mesh.mesh=plane;floor_mesh.position=spec[1];var mat:=StandardMaterial3D.new();mat.albedo_color=Color(.45,.42,.36);mat.roughness=1;floor_mesh.material_override=mat;world.add_child(floor_mesh)
 var lights:Array=[];var source:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/dining_fixture_adaptation.json"))
 for room in source.rooms:
  if room.programme_key=="D10_directory_10":lights.append_array(room.lights)
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/observation_cafe_service_20261016/NATIVE_VERIFICATION.json"));lights.append_array(p.lights)
 var lamps:Array[SpotLight3D]=[]
 for row in lights:
  var lamp:=SpotLight3D.new();lamp.position=Vector3(row.at[0],row.at[1],row.at[2]);lamp.rotation.x=-PI/2;lamp.light_color=Color(row.colour[0],row.colour[1],row.colour[2]);lamp.light_energy=float(row.energy);lamp.spot_range=float(row.range);lamp.spot_angle=float(row.get("angle",70));lamp.shadow_enabled=false;world.add_child(lamp);lamps.append(lamp)
 var camera:=Camera3D.new();world.add_child(camera);camera.current=true;camera.fov=75
 var canvas:=CanvasLayer.new();root.add_child(canvas);var label:=Label.new();label.text="LOCAL GODOT GEOMETRY REVIEW • NOT FULL GAME / CRT ACCEPTANCE";label.position=Vector2(16,16);label.add_theme_color_override("font_color",Color.WHITE);label.add_theme_color_override("font_shadow_color",Color.BLACK);label.add_theme_constant_override("shadow_offset_x",2);label.add_theme_constant_override("shadow_offset_y",2);canvas.add_child(label)
 for view in [{"file":"OBSERVATION_GATEWAY_LOCAL_GODOT.png","at":Vector3(58,62.65,432),"look":Vector3(48,62.5,432)},{"file":"OBSERVATION_AXIAL_LOCAL_GODOT.png","at":Vector3(8,62.65,392),"look":Vector3(35,62.5,392)}]:
  camera.position=view.at;camera.look_at(view.look);lamps.sort_custom(func(a,b):return a.position.distance_squared_to(camera.position)<b.position.distance_squared_to(camera.position))
  for i in range(lamps.size()):lamps[i].shadow_enabled=i<8
  for i in range(8):await process_frame
  await RenderingServer.frame_post_draw
  var img:=root.get_texture().get_image();assert(img.save_png("/workspace/recovery-evidence/"+str(view.file))==OK);print("CAPTURED_LOCAL ",view.file)
 quit(0)
