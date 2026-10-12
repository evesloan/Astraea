extends "res://scripts/guest_entry_door.gd"
func _ready()->void:
	open_fraction=0;desired_open=false;door_description="booked dining door"
	super._ready()
