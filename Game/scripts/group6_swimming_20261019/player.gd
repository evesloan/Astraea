extends "res://scripts/group6_float_20261019/player.gd"
# Current first-person game envelope only. No species, drowning, hoist or save claim.
var swimming:=false
var water_volume_id:=""
var swim_transitions:=0
func _ready()->void:
 var pins:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_swimming_20261019/CONTRACT.json"))
 for file in pins.source_pins:assert(FileAccess.get_sha256("res://"+str(file))==str(pins.source_pins[file]))
 super._ready()
 water_field=load("res://scripts/group6_swimming_20261019/water_field.gd").new()
func update_water_state()->void:
 var sample:Dictionary=water_field.sample(global_position)
 water_volume_id=str(sample.get("id",""))
 water_depth_m=float(sample.get("depth_m",0)) if sample.get("wet",false) else 0.0
 head_under_water=water_depth_m>camera.position.y
 water_state="submerged" if head_under_water else ("swimming" if swimming else ("wading" if water_depth_m>0 else "dry"))
func ground_water_depth(sample:Dictionary)->float:
 if not sample.has("surface_y"):return 0
 var at:=Vector3(global_position.x,float(sample.surface_y)+.05,global_position.z)
 var ray:=PhysicsRayQueryParameters3D.create(at,Vector3(at.x,float(sample.bed_y)-.15,at.z),collision_mask,[get_rid()])
 var hit:=get_world_3d().direct_space_state.intersect_ray(ray)
 if hit.is_empty():return 0 # Missing physical bed is not accepted as a swim volume.
 return maxf(0,float(sample.surface_y)-float(hit.position.y))
func swim_space_clear()->bool:
 var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8
 var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.exclude=[get_rid()];q.collision_mask=collision_mask;q.margin=.005
 q.transform=Transform3D(global_basis*Basis(Vector3.RIGHT,PI/2),global_position+Vector3.UP*.3)
 return get_world_3d().direct_space_state.intersect_shape(q,1).is_empty()
func enter_swim()->bool:
 if is_instance_valid(held_interaction) or not swim_space_clear():return false
 swimming=true;swim_transitions+=1
 body_collider.rotation.x=PI/2;body_collider.position.y=.3
 jump_requested=false
 return true
func leave_swim()->bool:
 # Probe just above the supported sole; the floor itself is not a blockage.
 if not body_space_clear(global_position+Vector3.UP*.02,1.8):return false
 swimming=false;swim_transitions+=1;body_collider.rotation=Vector3.ZERO;body_collider.position.y=.9
 return true
func try_mount_parked_seat(seat:Area3D)->bool:
 var mounted:=super.try_mount_parked_seat(seat)
 if mounted:swimming=false;body_collider.rotation=Vector3.ZERO
 return mounted
func release_parked_seat_for_verified_arrival()->void:
 swimming=false;body_collider.rotation=Vector3.ZERO
 super.release_parked_seat_for_verified_arrival()
func _physics_process(delta:float)->void:
 if seated:
  super._physics_process(delta);return
 var sample:Dictionary=water_field.sample(global_position)
 var ground_depth:=ground_water_depth(sample)
 if not swimming and sample.get("wet",false) and float(sample.depth_m)>.95 and ground_depth>1.1:enter_swim()
 if swimming and is_on_floor() and ground_depth<.8:leave_swim()
 if not swimming:
  super._physics_process(delta)
  if not seated:camera.position.y=lerpf(camera.position.y,1.65,1-exp(-delta*10))
  return
 var wish:=Vector3.ZERO;var vertical_wish:=0.0
 if gameplay_input_enabled:
  var lateral:=float(Input.is_physical_key_pressed(KEY_D))-float(Input.is_physical_key_pressed(KEY_A))
  var forward:=float(Input.is_physical_key_pressed(KEY_W))-float(Input.is_physical_key_pressed(KEY_S))
  wish=(global_basis.x*lateral-global_basis.z*forward).limit_length(1)*1.8
  vertical_wish=(-camera.global_basis.z*forward).y*1.8
 var current:Vector3=sample.get("water_velocity",Vector3.ZERO)
 velocity.x=move_toward(velocity.x,wish.x+current.x,delta*5)
 velocity.z=move_toward(velocity.z,wish.z+current.z,delta*5)
 if sample.get("wet",false):
  if gameplay_input_enabled and Input.is_physical_key_pressed(KEY_SPACE):velocity.y=move_toward(velocity.y,2.4,delta*8)
  elif absf(vertical_wish)>.25:velocity.y=move_toward(velocity.y,vertical_wish,delta*5)
  else:velocity.y+=clampf((float(sample.surface_y)-.35-global_position.y)*10-velocity.y*5,-12,12)*delta
 else:velocity.y-=9.8*delta
 jump_requested=false
 move_and_slide()
 if global_position.y<fall_recovery_y:
  release_parked_seat_for_verified_arrival();position=spawn_position;velocity=Vector3.ZERO
 if not seated:camera.position.y=lerpf(camera.position.y,.45,1-exp(-delta*10))
 update_water_state();update_interaction(delta)
