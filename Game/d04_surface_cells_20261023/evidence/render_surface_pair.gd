extends SceneTree
const H=preload("res://d04_surface_cells_20261023/batcher.gd")
func _initialize()->void:call_deferred("run")
func run()->void:
 assert(ProjectSettings.load_resource_pack("/tmp/astraea-laptop-contract-1bc13d51/Astraea-1bc13d51.pck"))
 var index:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://d04_detail_batches_20261022/runtime_r004/INDEX.json"));var keys:Array=index.rooms.keys();var results:Array=[]
 for sample:int in [0,60,119]:
  var row:Dictionary=index.rooms[keys[sample]];var view:=SubViewport.new();view.size=Vector2i(640,360);view.own_world_3d=true;view.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(view)
  var world:=Node3D.new();view.add_child(world);var env:=WorldEnvironment.new();env.environment=Environment.new();env.environment.background_mode=Environment.BG_COLOR;env.environment.background_color=Color(.12,.15,.19);env.environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;env.environment.ambient_light_color=Color.WHITE;env.environment.ambient_light_energy=1;world.add_child(env)
  var scene:Node3D=load(row.detail_path).instantiate();world.add_child(scene)
  var low:Array=row.detail_bounds_min;var hi:Array=row.detail_bounds_max;var center:=Vector3((low[0]+hi[0])/2,(low[1]+hi[1])/2,(low[2]+hi[2])/2)
  var cam:=Camera3D.new();world.add_child(cam);cam.position=center+Vector3(4,3,5);cam.look_at(center);cam.current=true
  var record:Dictionary=H.build(scene,[]);var images:Array=[];var draws:Array=[];var primitives:Array=[]
  for enabled:bool in [false,true]:
   H.set_enabled(scene,enabled)
   for i in 12:await process_frame
   await RenderingServer.frame_post_draw
   images.append(view.get_texture().get_image());draws.append(view.get_render_info(Viewport.RENDER_INFO_TYPE_VISIBLE,Viewport.RENDER_INFO_DRAW_CALLS_IN_FRAME));primitives.append(view.get_render_info(Viewport.RENDER_INFO_TYPE_VISIBLE,Viewport.RENDER_INFO_PRIMITIVES_IN_FRAME))
  var a:PackedByteArray=images[0].get_data();var b:PackedByteArray=images[1].get_data();assert(a.size()==b.size());var changed:=0;var max_delta:=0;var total_delta:=0
  for i in a.size():
   var delta:=absi(int(a[i])-int(b[i]));changed+=int(delta>0);max_delta=maxi(max_delta,delta);total_delta+=delta
  if sample==0:
   images[0].save_png("/tmp/D04_surface_before.png");images[1].save_png("/tmp/D04_surface_after.png")
  results.append({"room":keys[sample],"draws_before_after":draws,"primitives_before_after":primitives,"changed_channels":changed,"max_channel_delta":max_delta,"mean_channel_delta":float(total_delta)/a.size(),"channels":a.size(),"potential_saved":record.saved_submissions});view.free()
 var f:=FileAccess.open("/tmp/d04_surface_render_pairs.json",FileAccess.WRITE);f.store_string(JSON.stringify({"scope":"Three isolated actual D04 detail scenes; ambient only, fixed640x360; software Compatibility; not ship lighting or target FPS acceptance","rows":results},"  "));f.close();print("RENDER_PAIRS ",JSON.stringify(results));quit()
