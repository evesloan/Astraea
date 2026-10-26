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
 var packed:PackedScene=load("res://assets/models/SunsetSpecialty_104.0_r002.scn");var cafe:Node3D=packed.instantiate();world.add_child(cafe)
 var bounds:=AABB();var first:=true
 for mesh:MeshInstance3D in cafe.find_children("*","MeshInstance3D",true,false):
  if mesh.mesh==null:continue
  var box:AABB=load("res://spatial_instance_cells_20261026/ship_rules.gd").pose(mesh,cafe)*mesh.get_aabb()
  bounds=box if first else bounds.merge(box);first=false
 var lamps:Array=[]
 var sun:=DirectionalLight3D.new();sun.rotation_degrees=Vector3(-35,-25,0);sun.light_energy=.9;sun.shadow_enabled=true;world.add_child(sun);lamps.append(sun)
 var lamp:=OmniLight3D.new();lamp.position=bounds.get_center()+Vector3(0,1,0);lamp.omni_range=25;lamp.light_energy=2;lamp.light_color=Color(1,.8,.6);lamp.shadow_enabled=true;world.add_child(lamp);lamps.append(lamp)
 var camera:=Camera3D.new();world.add_child(camera);camera.current=true;camera.fov=75
 camera.position=Vector3(-53,85.2,441)
 camera.look_at(Vector3(-54,84.7,443))
 rows.append({"bounds":str(bounds),"camera":str(camera.position)})
 await sample("original")
 var result:=CELLS.compact(cafe,lamps)
 rows.append({"candidate":result})
 await sample("instanced")
 assert(CELLS.restore(cafe));await sample("restored")
 var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify(rows,"\t"));f.close()
 world.free();packed=null
 for i in 3:await process_frame
 quit()
