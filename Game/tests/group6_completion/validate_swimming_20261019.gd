extends "res://tests/group6_completion/validate_water_care.gd"
var output_name:="LOCAL"
var motion:Array=[]
func key(code:int,down:bool)->void:
 var e:=InputEventKey.new();e.keycode=code;e.physical_keycode=code;e.pressed=down;Input.parse_input_event(e)
func travel(actor:CharacterBody3D,goal:Vector3,ascend:bool=false)->Dictionary:
 var old:Vector3=actor.global_position;var step:=0.0;var seen:Array=[];var frames:=0
 key(KEY_W,true);key(KEY_SPACE,ascend)
 for i in range(1200):
  var delta:Vector3=goal-actor.global_position
  if Vector2(delta.x,delta.z).length()<.18:break
  actor.rotation.y=atan2(-delta.x,-delta.z)
  await physics_frame;frames+=1
  step=maxf(step,actor.global_position.distance_to(old));old=actor.global_position
  if not seen.has(actor.water_state):seen.append(actor.water_state)
 key(KEY_W,false);key(KEY_SPACE,false)
 var result:Dictionary={"reached":Vector2(goal.x-old.x,goal.z-old.z).length()<.2,"frames":frames,"max_step":step,"states":seen,"end":[old.x,old.y,old.z]};motion.append(result);return result
func run()->void:
 var host:=LocalHost.new();root.add_child(host)
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
 var regions:Array=[]
 for r in data.regions:
  if r.id in ["D08_grand_pool_base","D08_grand_pool_wet"]:regions.append(r)
 assert(regions.size()==2)
 load("res://scripts/structural_floor_builder.gd").build_regions(host,host.stone,host.ivory,regions,{},"OriginalPoolFloors")
 var pool:Node3D=load("res://assets/models/AST-AQU-016.glb").instantiate();host.add_child(pool)
 for mesh:MeshInstance3D in pool.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
 var actor:CharacterBody3D=load("res://scripts/group6_swimming_20261019/player.gd").new();host.add_child(actor)
 await exercise(host,actor)
func extra_checks(_host:Node3D,_actor:CharacterBody3D)->void:pass
func exercise(host:Node3D,actor:CharacterBody3D)->void:
 actor.position=Vector3(-31,46.23,-460);actor.velocity=Vector3.ZERO
 for i in range(20):await physics_frame
 record("starts_on_original_dry_deck",actor.is_on_floor() and actor.water_state=="dry")
 var enter:Dictionary=await travel(actor,Vector3(-31,45.7,-452))
 record("normal_input_pool_entry",enter.reached and actor.swimming)
 record("entry_is_continuous",enter.max_step<.12)
 for i in range(180):await physics_frame
 record("surface_swim_settles",absf(actor.global_position.y-45.7)<.05 and not actor.head_under_water and actor.swimming)
 var blocker:=StaticBody3D.new();var contact:=CollisionShape3D.new();var box:=BoxShape3D.new();box.size=Vector3(2,.2,2);contact.shape=box;blocker.add_child(contact);host.add_child(blocker);blocker.global_position=actor.global_position+Vector3.UP*1.1
 for i in range(3):await physics_frame
 record("overhead_obstruction_prevents_standing",not actor.leave_swim() and actor.swimming)
 blocker.queue_free()
 for i in range(3):await physics_frame
 actor.camera.rotation.x=-.8;key(KEY_W,true)
 for i in range(90):await physics_frame
 key(KEY_W,false)
 record("look_and_move_submerges",actor.swimming and actor.head_under_water and actor.water_state=="submerged")
 actor.camera.rotation.x=0
 actor.set_controls_enabled(false)
 for i in range(180):await physics_frame
 record("input_suspend_retains_surface_support",actor.swimming and not actor.head_under_water and absf(actor.global_position.y-45.7)<.05)
 actor.set_controls_enabled(true)
 var leave:Dictionary=await travel(actor,Vector3(-31,46.2,-460),true)
 for i in range(90):await physics_frame
 record("surface_exit_over_retained_rim",leave.reached and not actor.swimming and actor.is_on_floor() and actor.water_state=="dry")
 record("exit_is_continuous",leave.max_step<.12)
 record("standing_shape_and_camera_restored",actor.body_collider.rotation.is_zero_approx() and is_equal_approx(actor.body_collider.position.y,.9) and absf(actor.camera.position.y-1.65)<.01)
 await extra_checks(host,actor)
 print("SWIM ROUTES ",motion)
 var result:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks,"errors":errors,"motion":motion}
 FileAccess.open("res://docs/validation/group6_swimming_20261019/"+output_name+".json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
 print("SWIMMING ",result.status," ",errors," END ",actor.global_position);quit(0 if errors.is_empty() else 1)
