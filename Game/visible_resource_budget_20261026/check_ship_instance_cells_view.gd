extends SceneTree
const CELLS=preload("res://spatial_instance_cells_20261026/ship_runtime.gd")
var output:String
var rows:Array=[]
func _initialize()->void:
 for arg:String in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.substr(9)
 root.size=Vector2i(1920,1080)
 call_deferred("run")
func sample(stage:String)->void:
 for i in 10:await process_frame
 var frames:Array=[];var draws:Array=[];var previous:=Time.get_ticks_usec()
 for i in 40:
  await process_frame
  var now:=Time.get_ticks_usec();frames.append((now-previous)/1000.0);previous=now
  draws.append(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))
 frames.sort();draws.sort()
 await RenderingServer.frame_post_draw
 var image:=root.get_texture().get_image();image.save_png(output.get_base_dir()+"/"+stage+".png")
 rows.append({"render_size":str(image.get_size()),"stage":stage,"median_ms":frames[20],"p95_ms":frames[38],"median_draws":draws[20],"primitives":Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME),"static_bytes":OS.get_static_memory_usage(),"video_bytes":Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED)})
func run()->void:
 root.size=Vector2i(1920,1080);root.content_scale_size=Vector2i(1920,1080);root.content_scale_mode=Window.CONTENT_SCALE_MODE_VIEWPORT
 var world:=Node3D.new();root.add_child(world)
 var env:=WorldEnvironment.new();var e:=Environment.new();e.background_mode=Environment.BG_COLOR;e.background_color=Color(.035,.04,.05);e.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;e.ambient_light_color=Color(.85,.9,1.);e.ambient_light_energy=.2;env.environment=e;world.add_child(env)
 var packed:PackedScene=load("res://assets/models/SOL_D10_directory_10_source001.glb");var cafe:Node3D=packed.instantiate();world.add_child(cafe)
 var specs:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/dining_fixture_adaptation.json"));var lamps:Array=[]
 for room:Dictionary in specs.rooms:
  if room.programme_key!="D10_directory_10":continue
  for row:Dictionary in room.lights:
   var lamp:=SpotLight3D.new();lamp.position=Vector3(row.at[0],row.at[1],row.at[2]);lamp.rotation.x=-PI/2;lamp.light_color=Color(row.colour[0],row.colour[1],row.colour[2]);lamp.light_energy=float(row.energy);lamp.spot_range=float(row.range);lamp.spot_angle=float(row.get("angle",70));lamp.shadow_enabled=false;world.add_child(lamp);lamps.append(lamp)
 var camera:=Camera3D.new();world.add_child(camera);camera.current=true;camera.fov=75;camera.position=Vector3(58,62.65,432);camera.look_at(Vector3(48,62.5,432))
 lamps.sort_custom(func(a,b):return a.position.distance_squared_to(camera.position)<b.position.distance_squared_to(camera.position))
 for i in lamps.size():lamps[i].shadow_enabled=i<8
 await sample("original")
 var result:=CELLS.compact(cafe,lamps)
 rows.append({"candidate":result})
 await sample("instanced")
 assert(CELLS.restore(cafe));await sample("restored")
 var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify(rows,"\t"));f.close()
 world.free();packed=null
 for i in 3:await process_frame
 quit()
