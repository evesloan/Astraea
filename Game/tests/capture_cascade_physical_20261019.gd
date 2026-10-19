extends SceneTree
func _initialize()->void:call_deferred("run")
func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func run()->void:
 var world:=Node3D.new();root.add_child(world)
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_cascade_receiving_20261019/PACKAGE.json"))
 for file in ["res://assets/models/AquaticCompletion_r019.glb","res://assets/group6_cascade_receiving_20261019/"+str(p.source_file)]:world.add_child(load(file).instantiate())
 var env:=WorldEnvironment.new();var e:=Environment.new();e.background_mode=Environment.BG_COLOR;e.background_color=Color(.05,.07,.08);e.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;e.ambient_light_color=Color(.88,.94,1);e.ambient_light_energy=.5;env.environment=e;world.add_child(env)
 var light:=SpotLight3D.new();world.add_child(light);light.position=v(p.task_light.source_xyz);light.look_at(v(p.task_light.target_xyz),Vector3.UP);light.light_color=Color(.88,.94,1);light.light_energy=p.task_light.energy;light.spot_range=p.task_light.range_m;light.spot_angle=p.task_light.half_cone_degrees;light.shadow_enabled=true
 var camera:=Camera3D.new();world.add_child(camera);camera.current=true;camera.fov=78;camera.far=160
 var canvas:=CanvasLayer.new();root.add_child(canvas);var label:=Label.new();label.text="ASTRAEA D08 • RETAINED CASCADE CABINET • CONSTRUCTION WIP\nExact source on existing shoulder/hood · preview ambient · network unconnected";label.position=Vector2(18,16);label.add_theme_font_size_override("font_size",17);label.add_theme_color_override("font_shadow_color",Color.BLACK);label.add_theme_constant_override("shadow_offset_x",2);label.add_theme_constant_override("shadow_offset_y",2);canvas.add_child(label)
 for view in [{"file":"CASCADE_OPERATOR.png","at":Vector3(21.9,45.65,215.2),"look":Vector3(21.9,45.25,214.45)},{"file":"CASCADE_WEST_APPROACH.png","at":Vector3(20.4,45.65,215.6),"look":Vector3(21.9,45.15,214.45)}]:
  camera.position=view.at;camera.look_at(view.look)
  for i in range(8):await process_frame
  await RenderingServer.frame_post_draw
  assert(root.get_texture().get_image().save_png("/workspace/cascade-physical-receiving-20261019/"+str(view.file))==OK);print("CAPTURED ",view.file)
 quit()
