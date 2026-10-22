extends SceneTree
const E="res://docs/validation/consolidated_construction_20261022/"
func _initialize():call_deferred("run")
func shot(name:String):
 await RenderingServer.frame_post_draw
 var p:=E+name+".png"
 assert(not FileAccess.file_exists(p))
 assert(root.get_texture().get_image().save_png(p)==OK)
func run():
 var source:=str(ProjectSettings.get_setting("application/run/main_scene"))
 var scene:Node=load(source).instantiate();root.add_child(scene);current_scene=scene
 var start:=Time.get_ticks_msec();var loading:=false;var ship:Node=null
 while true:
  await process_frame
  ship=scene.get_node_or_null("World360/Astraea")
  if not loading and Time.get_ticks_msec()-start>5000:
   loading=true;await shot("FULL_STARTUP_LOADING")
  if ship!=null and ship.get_meta("runtime_ready",false):break
 print("HANDOFF_RUNTIME_READY")
 var ready_at:=Time.get_ticks_msec()
 var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
 var before:=actor.global_position
 var e:=InputEventKey.new();e.physical_keycode=KEY_W;e.pressed=true;Input.parse_input_event(e)
 for frame in range(30):await physics_frame
 e=InputEventKey.new();e.physical_keycode=KEY_W;e.pressed=false;Input.parse_input_event(e)
 var moved:=actor.global_position.distance_to(before)
 while Time.get_ticks_msec()-ready_at<20000:await process_frame
 await shot("FULL_STARTUP_READY_UNFINISHED")
 var royalty:=ship.find_child("Royalty790UpperIntegratedWIP",true,false)
 var night:=ship.find_child("NightGardenD15SpecialtyReceiving20261020",true,false)
 var result:={"main":source,"runtime_ready":true,"tree_unpaused":not paused,"ready_seconds":float(ready_at-start)/1000,"settled_seconds":20,"player_forward_distance":moved,"vertical_change":actor.global_position.y-before.y,"player_on_floor":actor.is_on_floor(),"royalty_present":royalty!=null,"night_garden_present":night!=null,"view_gallery_held":ship.find_child("OuterViewGalleries20261022",true,false)==null,"windows_tested":false,"final_visual_acceptance":false,"audio_driver":"Dummy","renderer":"Godot4.6.3 GL Compatibility/Mesa software on Xorg dummy display"}
 if royalty!=null:
  actor.global_position=Vector3(100.5,106.55,41.5);actor.rotation.y=-1.9;actor.pitch=-.1;actor.camera.rotation.x=-.1
  for frame in range(20):await physics_frame
  await shot("ROYALTY_ACTUAL_MAIN_UNFINISHED")
  result["royalty_capture_camera_staged"]=true
 var f:=FileAccess.open(E+"FULL_STARTUP_RECEIPT.json",FileAccess.WRITE);f.store_string(JSON.stringify(result,"  ")+"\n");f.close()
 print("HANDOFF_STARTUP_COMPLETE ",JSON.stringify(result))
 quit(0 if not paused and royalty!=null and night!=null and moved>.05 and result.player_on_floor and absf(result.vertical_change)<.25 else 1)
