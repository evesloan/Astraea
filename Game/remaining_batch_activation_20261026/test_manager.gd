extends "res://scripts/remaining_batch_receiving.gd"
var installed_keys:Array[String]=[]
func _ensure_room(item:Dictionary)->void:
 var key:=str(item.key)
 if rooms[key].get_meta("stream_loaded",false):return
 installed_keys.append(key)
 rooms[key].set_meta("stream_loaded",true)
