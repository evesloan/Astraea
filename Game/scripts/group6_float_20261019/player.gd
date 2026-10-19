extends "res://scripts/group6_completion/player_water_seat_20261019.gd"
# Reference gameplay load, not canonical species mass or engineering approval.
@export var aquatic_reference_load_kg:=75.0
func _physics_process(delta:float)->void:
 if seated and jump_requested and is_instance_valid(parked_seat) and parked_seat.has_method("request_leave"):
  jump_requested=false;parked_seat.request_leave(self)
 super._physics_process(delta)
