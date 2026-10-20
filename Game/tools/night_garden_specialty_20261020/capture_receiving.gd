extends "res://tools/night_garden_specialty_20261020/check_receiving.gd"
func run()->void:
 world=Node3D.new();root.add_child(world)
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/night_garden_specialty_d15_20261020/PACKAGE.json"))
 load_raw(p.receiving.model_file)
 for r in p.rooms:
  load_raw(r.model_file)
  for item in r.lights:
   var light:=SpotLight3D.new();light.position=Vector3(item.position[0],item.position[1],item.position[2]);light.rotation.x=-PI/2;light.light_color=Color(1,.93,.8);light.light_energy=item.energy;light.spot_range=item.range;light.spot_angle=70;world.add_child(light)
 for sign in [-1,1]:
  for z in [19,28,35,42,56.8,71.6,86.4,94]:
   var light:=SpotLight3D.new();light.position=Vector3(90.5 if z<26 else (87 if z==28 else 84),96.4,z*sign);light.rotation.x=-PI/2;light.light_color=Color(1,.94,.82);light.light_energy=1.1;light.spot_range=8;light.spot_angle=72;world.add_child(light)
 var env:=WorldEnvironment.new();var e:=Environment.new();e.background_mode=Environment.BG_COLOR;e.background_color=Color(.025,.035,.045);e.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;e.ambient_light_color=Color(.6,.65,.7);e.ambient_light_energy=.35;env.environment=e;world.add_child(env)
 root.size=Vector2i(1280,720)
 var cam:=Camera3D.new();cam.fov=78;world.add_child(cam);cam.current=true
 for shot in [{"name":"ROOM410_R002","from":Vector3(87.4,94.6,42),"to":Vector3(96.3,94.2,42)},{"name":"CONNECTED_APPROACH_R002","from":Vector3(90.5,94.6,16.5),"to":Vector3(89.0,94.5,29.5)}]:
  cam.position=shot.from;cam.look_at(shot.to)
  for frame in range(8):await process_frame
  await RenderingServer.frame_post_draw
  var out:="res://docs/validation/night_garden_specialty_20261020/"+str(shot.name)+".png"
  var err:=root.get_texture().get_image().save_png(out);assert(err==OK);print("CAPTURE_SAVED "+out)
 quit()
