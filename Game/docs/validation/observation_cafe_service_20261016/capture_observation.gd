extends SceneTree
func _initialize()->void:call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await process_frame
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(8)
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_controls_enabled(false);actor.set_physics_process(false)
 var views:Array=[{"file":"OBSERVATION_GATEWAY_GAME.png","at":Vector3(58,61.03,432),"look":Vector3(48,62.5,432)},{"file":"OBSERVATION_AXIAL_APPROACH_GAME.png","at":Vector3(8,61.03,392),"look":Vector3(30,62.5,392)}]
 for view in views:
  actor.global_position=view.at;ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position);ship.get_node("ShipSystems/RemainingBatchStreaming").prepare_position(actor.global_position);await frames(4)
  var delta:Vector3=view.look-actor.camera.global_position;actor.rotation.y=atan2(-delta.x,-delta.z);actor.pitch=atan2(delta.y,Vector2(delta.x,delta.z).length());actor.camera.rotation.x=actor.pitch;await frames(12);await RenderingServer.frame_post_draw
  var img:=root.get_texture().get_image();var result:int=img.save_png("/workspace/recovery-evidence/"+str(view.file));assert(result==OK);print("CAPTURED ",view.file," ",img.get_size())
 quit(0)
