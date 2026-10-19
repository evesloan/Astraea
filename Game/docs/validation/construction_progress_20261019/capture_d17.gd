extends SceneTree
func _initialize()->void:call_deferred("run")
func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func run()->void:
 var world:=Node3D.new();root.add_child(world)
 var env:=WorldEnvironment.new();var e:=Environment.new();e.background_mode=Environment.BG_COLOR;e.background_color=Color(.055,.065,.08);e.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;e.ambient_light_color=Color(.85,.9,1);e.ambient_light_energy=.5;env.environment=e;world.add_child(env)
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D17_STARBOARD_STANDARD_CANDIDATE_20261019.json"))
 assert(FileAccess.get_sha256("res://assets/models/"+str(p.structure_file))==str(p.structure.export_sha256))
 var model:Node3D=load("res://assets/models/"+str(p.structure_file)).instantiate();world.add_child(model)
 var fore:Node3D=load("res://assets/group2_central_receiving_20261013/CENTRAL_ADJUNCT_RECEIVING_FRAME_r004.glb").instantiate();world.add_child(fore)
 for row in p.walls:
  var replacement:MeshInstance3D=model.find_child(str(row.replacement_name).replace(".","_"),true,false)
  if row.owner=="fore":
   var old:MeshInstance3D=fore.find_child(str(row.name),true,false);assert(old!=null);old.mesh=replacement.mesh
   replacement.free()
 for r in p.rooms:
  var home:=Node3D.new();home.position=v(r.rigid_room_transform.translation);home.rotation.y=PI;world.add_child(home)
  var room:Node3D=load("res://assets/models/"+str(p.source_room_model)).instantiate();home.add_child(room)
  for spec in [{"name":"HomeEntry","script":"guest_entry_door","at":Vector3(-63.175,102,35.6),"yaw":PI/2},{"name":"BathroomDoor","script":"guest_privacy_door","at":Vector3(-65.95,102,36.3),"yaw":PI}]:
   var door:Node3D=load("res://scripts/"+str(spec.script)+".gd").new();door.name=spec.name;door.persistent_id=StringName(str(r.allocation.proposed_runtime_id)+":"+str(spec.name));door.position=spec.at;door.rotation.y=spec.yaw;door.desired_open=false;door.open_fraction=0;home.add_child(door)
 var lamps:Array[OmniLight3D]=[]
 for row in p.fixture_instances:
  var marker:Node3D=model.find_child(row.name+"__LightExit",true,false);assert(marker!=null)
  var light:=OmniLight3D.new();world.add_child(light);light.global_position=marker.global_position;light.light_color=Color(row.color[0],row.color[1],row.color[2]);light.light_energy=row.energy;light.omni_range=row.range;lamps.append(light)
 var camera:=Camera3D.new();world.add_child(camera);camera.current=true;camera.fov=78;camera.far=250
 var canvas:=CanvasLayer.new();root.add_child(canvas);var label:=Label.new();label.text="ASTRAEA D17 • INTEGRATED SOURCE ff4aee89 • CONSTRUCTION WIP\nLocal geometry view · preview ambient light · not final visual/gameplay acceptance";label.position=Vector2(18,16);label.add_theme_font_size_override("font_size",17);label.add_theme_color_override("font_shadow_color",Color.BLACK);label.add_theme_constant_override("shadow_offset_x",2);label.add_theme_constant_override("shadow_offset_y",2);canvas.add_child(label)
 for view in [{"file":"D17_FORE_CIRCULATION.png","at":Vector3(61.25,103.65,-18),"look":Vector3(63.2,103.35,-45)},{"file":"D17_FORE_REVERSE.png","at":Vector3(61.3,103.65,-69),"look":Vector3(63.2,103.35,-42)}]:
  camera.position=view.at;camera.look_at(view.look)
  lamps.sort_custom(func(a,b):return a.position.distance_squared_to(camera.position)<b.position.distance_squared_to(camera.position))
  for i in range(lamps.size()):lamps[i].shadow_enabled=i<8
  for i in range(8):await process_frame
  await RenderingServer.frame_post_draw
  var img:=root.get_texture().get_image();assert(img.save_png("/workspace/construction-progress-20261019/"+str(view.file))==OK);print("CAPTURED ",view.file)
 quit()
