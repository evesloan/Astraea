extends "res://scripts/group6_swimming_20261019/player.gd"
# Additive unselected successor; all retained swimming/seating/interaction code runs.
const STEP=preload("res://aquatic_tram_interior_20261026/integration/step_motion.gd")
var verified_stair_steps:=0
func _ready()->void:
	assert(FileAccess.get_sha256("res://scripts/player.gd") == "f1bd92d00ad355d5d3c87b57da5ff0e3aa76f9d48776a58f3515932c017a9566")
	assert(FileAccess.get_sha256("res://scripts/group6_completion/player_water_seat_20261019.gd") == "a7343f695751e4adf70e9219b16dda4e6ec6151305a4a5d5439dbcd1770be209")
	assert(FileAccess.get_sha256("res://scripts/group6_float_20261019/player.gd") == "f87d2746c1b47963ca93b6f1df15003b5171a0644ddb6bafacb3c7d930facde7")
	assert(FileAccess.get_sha256("res://scripts/group6_swimming_20261019/player.gd") == "fbcc72ff03a10325b9d195b7b9ab904868940e197c8b866076249321c5081f5c")
	super._ready()

func _physics_process(delta:float)->void:
	var can_step:=is_on_floor() and gameplay_input_enabled and not seated and not swimming and not jump_requested and not is_instance_valid(held_interaction)
	var before:=global_position
	var expected:=Vector3.ZERO
	if can_step:
		var wish:=Vector3(float(Input.is_physical_key_pressed(KEY_D))-float(Input.is_physical_key_pressed(KEY_A)),0,float(Input.is_physical_key_pressed(KEY_S))-float(Input.is_physical_key_pressed(KEY_W)))
		wish=(basis*wish).normalized()*3.1
		expected=Vector3(move_toward(velocity.x,wish.x,delta*16),0,move_toward(velocity.z,wish.z,delta*16))*delta
	super._physics_process(delta)
	if can_step and not seated and not swimming and velocity.y<=0:
		var travelled:=global_position-before;travelled.y=0
		var remaining:=expected-travelled
		if remaining.dot(expected)>0 and STEP.apply(self,remaining):verified_stair_steps+=1
